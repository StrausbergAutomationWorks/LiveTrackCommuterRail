"""Config flow: region, then operator, then a key only where one is needed.

! THE LIST WILL GROW (Lee, 2026-10-02), so the user never scrolls every
commuter railroad there is: a region first, then only the operators that
serve it. A region appears only if at least one operator serves it, and an
operator already set up is not offered again.

! THE KEY. Entered here and stored in the config entry, Home Assistant's own
store for a UI-configured integration's credentials. Never logged (the
coordinator logs exception TYPES only, because aiohttp puts the URL and its
query in the message), redacted in diagnostics, and replaced through the
re-authentication flow when the operator refuses it.
"""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_API_KEY,
    CONF_OPERATOR,
    CONF_REGION,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_PARKED,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SHOW_PARKED,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    REQUEST_TIMEOUT,
    USER_AGENT,
)
from .coordinator import AuthError, fetch_feed
from .operators import OPERATORS, Operator, operators_in, regions_in_use
from .operators.base import SOURCE_DIGITRAFFIC, SOURCE_ENTUR, SOURCE_IRISH_RAIL, SOURCE_NS, SOURCE_TRAFIKVERKET
from .shared_irish_rail import get_shared_irish_rail_client, release_shared_irish_rail_client
from saw_livetrack.entur import CLIENT_NAME as ENTUR_CLIENT_NAME
from saw_livetrack.irish_rail import KeyedError as IrishRailError
from saw_livetrack.trafikverket import check_key as trafikverket_check_key
from saw_livetrack.ns import check_key as ns_check_key

_KEY_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))


def _dropdown(options: list[SelectOptionDict]) -> SelectSelector:
    return SelectSelector(SelectSelectorConfig(
        options=options, mode=SelectSelectorMode.DROPDOWN, sort=False))


async def _check_digitraffic(hass, op: Operator) -> str | None:
    """One GET of the positions the shared client reads (keyless): None on HTTP
    200, else an error code. Digitraffic refuses a request without gzip (406) and
    asks callers to identify themselves (the client's DEFAULT_USER)."""
    headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip",
               **(op.static_headers or {})}
    try:
        async with async_get_clientsession(hass).get(
            op.positions_url, headers=headers,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
            return None if resp.status == 200 else "cannot_connect"
    except (aiohttp.ClientError, TimeoutError):
        return "cannot_connect"


async def _check_entur(hass, op: Operator) -> str | None:
    """One GET of the trip updates the shared Entur client reads (keyless): None on HTTP 200, else an error code.
    Entur asks every request to name its client (ET-Client-Name, the shared client's one name)."""
    headers = {"User-Agent": USER_AGENT, "ET-Client-Name": ENTUR_CLIENT_NAME}
    try:
        async with async_get_clientsession(hass).get(
            op.positions_url, headers=headers,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as resp:
            return None if resp.status == 200 else "cannot_connect"
    except (aiohttp.ClientError, TimeoutError):
        return "cannot_connect"


async def _check_irish_rail(hass, op: Operator) -> str | None:
    """One read of Irish Rail's trains through the SHARED client (keyless; within a minute of another Live Track
    integration's read it is that read, costing no request): None when it answers, else cannot_connect. The claim is
    given back at once; the entry claims again when it loads."""
    client = get_shared_irish_rail_client(hass, op.irish_rail_consumer)
    try:
        await hass.async_add_executor_job(client.for_consumer, op.irish_rail_consumer)
    except IrishRailError:
        return "cannot_connect"
    finally:
        release_shared_irish_rail_client(hass, op.irish_rail_consumer)
    return None


async def _check_key(hass, op: Operator, key: str) -> str | None:
    """None when the operator accepts the key, else an error code."""
    if op.source == SOURCE_IRISH_RAIL:
        return await _check_irish_rail(hass, op)
    if op.source == SOURCE_DIGITRAFFIC:
        return await _check_digitraffic(hass, op)
    if op.source == SOURCE_ENTUR:
        return await _check_entur(hass, op)
    if op.source == SOURCE_TRAFIKVERKET:
        # One small read with the key (the key in the request body, never in a message; blocking, so the executor).
        error = await hass.async_add_executor_job(trafikverket_check_key, key)
        return "invalid_auth" if error == "invalid_key" else error
    if op.source == SOURCE_NS:
        # One vehicle read with the key (in the header, never in a message; blocking, so the executor).
        error = await hass.async_add_executor_job(ns_check_key, key)
        return "invalid_auth" if error == "invalid_key" else error
    params = {op.key_param: key} if op.needs_key else None
    try:
        feed = await fetch_feed(async_get_clientsession(hass), op.positions_url, params)
    except AuthError:
        return "invalid_auth"
    return None if feed is not None else "cannot_connect"


class CommuterRailConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._region: str | None = None
        self._op: Operator | None = None

    def _available(self, region: str) -> list[Operator]:
        taken = self._async_current_ids()
        return [op for op in operators_in(region) if op.id not in taken]

    async def async_step_user(self, user_input: dict[str, Any] | None = None
                              ) -> ConfigFlowResult:
        regions = {code: label for code, label in regions_in_use().items()
                   if self._available(code)}
        if not regions:
            return self.async_abort(reason="all_configured")
        if user_input is not None:
            self._region = user_input[CONF_REGION]
            return await self.async_step_operator()
        schema = vol.Schema({vol.Required(CONF_REGION): _dropdown(
            [SelectOptionDict(value=c, label=l) for c, l in regions.items()])})
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_operator(self, user_input: dict[str, Any] | None = None
                                  ) -> ConfigFlowResult:
        choices = self._available(self._region or "")
        if user_input is not None:
            self._op = OPERATORS[user_input[CONF_OPERATOR]]
            await self.async_set_unique_id(self._op.id)
            self._abort_if_unique_id_configured()
            if self._op.needs_key:
                return await self.async_step_credentials()
            if await _check_key(self.hass, self._op, "") == "cannot_connect":
                return self.async_abort(reason="cannot_connect")
            return self.async_create_entry(title=self._op.name,
                                           data={CONF_OPERATOR: self._op.id})
        schema = vol.Schema({vol.Required(CONF_OPERATOR): _dropdown(
            [SelectOptionDict(value=op.id, label=op.name) for op in choices])})
        return self.async_show_form(step_id="operator", data_schema=schema)

    async def async_step_credentials(self, user_input: dict[str, Any] | None = None
                                     ) -> ConfigFlowResult:
        op = self._op
        assert op is not None
        errors: dict[str, str] = {}
        if user_input is not None:
            key = user_input[CONF_API_KEY].strip()
            error = await _check_key(self.hass, op, key)
            if error is None:
                return self.async_create_entry(
                    title=op.name, data={CONF_OPERATOR: op.id, CONF_API_KEY: key})
            errors["base"] = error
        return self.async_show_form(
            step_id="credentials",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): _KEY_SELECTOR}),
            errors=errors,
            description_placeholders={"operator": op.name,
                                      "key_url": op.key_url or "",
                                      "terms_url": op.terms_url or ""},
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        self._op = OPERATORS[entry_data[CONF_OPERATOR]]
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None
                                        ) -> ConfigFlowResult:
        op = self._op
        assert op is not None
        errors: dict[str, str] = {}
        if user_input is not None:
            key = user_input[CONF_API_KEY].strip()
            error = await _check_key(self.hass, op, key)
            if error is None:
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(), data_updates={CONF_API_KEY: key})
            errors["base"] = error
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): _KEY_SELECTOR}),
            errors=errors,
            description_placeholders={"operator": op.name, "key_url": op.key_url or ""},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return CommuterRailOptionsFlow()


class CommuterRailOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None
                              ) -> ConfigFlowResult:
        if user_input is not None:
            user_input[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])
            return self.async_create_entry(title="", data=user_input)
        cur = self.config_entry.options
        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL,
                         default=cur.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)):
                NumberSelector(NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL, step=1,
                    unit_of_measurement="s", mode=NumberSelectorMode.BOX)),
            vol.Required(CONF_SHOW_PARKED,
                         default=cur.get(CONF_SHOW_PARKED, DEFAULT_SHOW_PARKED)):
                BooleanSelector(),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
