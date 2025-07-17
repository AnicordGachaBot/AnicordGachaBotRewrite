from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from datetime import datetime


__all__ = ('BlacklistData',)


@dataclass
class BlacklistData:
    reason: str
    lasts_until: datetime | None
    blacklist_type: Literal['guild', 'user']
