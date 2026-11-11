"""The operator registry. No Home Assistant imports.

Adding a railroad is one adapter module plus one line here. Before it ships:
may it be shipped at all (its licence, linked from `terms_url`), and what does
it cost the user (a key or not). Record both in the SSOT.

! An operator's `id` becomes its config entry's unique_id and part of every
entity name. Never change one once released.
"""

from __future__ import annotations

from .base import REGIONS, Obs, Operator
from .flytoget import FLYTOGET
from .go_ahead_norge import GO_AHEAD_NORGE
from .irish_rail import IRISH_RAIL
from .metra import METRA
from .nictd import NICTD
from .ns import NS
from .qr_citytrain import QR_CITYTRAIN
from .renfe import RENFE_OPERATORS
from .sweden import SWEDEN
from .vr_lahijunat import VR_LAHIJUNAT
from .vy import VY

OPERATORS: dict[str, Operator] = {op.id: op for op in (METRA, NICTD, QR_CITYTRAIN,
                                                        VR_LAHIJUNAT, *RENFE_OPERATORS,
                                                        VY, GO_AHEAD_NORGE, FLYTOGET, *SWEDEN,
                                                        IRISH_RAIL, NS)}


def regions_in_use() -> dict[str, str]:
    """{region code: label} for every region at least one operator serves,
    sorted by label, so the setup list never offers an empty region."""
    used = {code for op in OPERATORS.values() for code in op.regions}
    unknown = used - REGIONS.keys()
    if unknown:
        raise ValueError(f"region codes without a label: {sorted(unknown)}")
    return dict(sorted(((c, REGIONS[c]) for c in used), key=lambda kv: kv[1]))


def operators_in(region: str) -> list[Operator]:
    """Operators serving a region, sorted by name."""
    return sorted((op for op in OPERATORS.values() if region in op.regions),
                  key=lambda op: op.name.lower())


__all__ = ["OPERATORS", "REGIONS", "Obs", "Operator", "operators_in",
           "regions_in_use"]
