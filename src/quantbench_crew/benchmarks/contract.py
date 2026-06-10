"""The Strategy contract and point-in-time panel data.

This is the keystone seam between the coder and the bench: every generated
implementation must satisfy ``Strategy``, and every dataset reaches it as a
``PanelData``. Both are dependency-free on purpose — generated candidates run
inside a sandbox where only the stdlib exists, so the data API they program
against must be reproducible there as a small duck type.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class PanelData:
    """Point-in-time wrapper over long-format (date, asset, fields) records.

    The access API is deliberately tiny — ``dates``, ``assets``, ``value``,
    ``history``, ``up_to`` — and is the contract surface generated strategies
    code against. ``up_to`` is the point-in-time discipline: it returns a
    panel containing no information after ``as_of``.
    """

    _frames: dict[date, dict[str, dict[str, float]]]
    _dates: tuple[date, ...]

    @classmethod
    def from_records(
        cls, records: Iterable[tuple[date, str, Mapping[str, float]]]
    ) -> "PanelData":
        frames: dict[date, dict[str, dict[str, float]]] = {}
        for record_date, asset, fields in records:
            frames.setdefault(record_date, {}).setdefault(asset, {}).update(
                {str(field): float(value) for field, value in fields.items()}
            )
        return cls(_frames=frames, _dates=tuple(sorted(frames)))

    def dates(self) -> tuple[date, ...]:
        return self._dates

    def assets(self) -> tuple[str, ...]:
        names: set[str] = set()
        for frame in self._frames.values():
            names.update(frame)
        return tuple(sorted(names))

    def value(
        self, as_of: date, asset: str, field: str, default: float | None = None
    ) -> float | None:
        return self._frames.get(as_of, {}).get(asset, {}).get(field, default)

    def history(
        self, asset: str, field: str, end: date, periods: int
    ) -> tuple[float, ...]:
        """Return the last ``periods`` values of ``field`` at dates <= end."""

        values = [
            self._frames[d][asset][field]
            for d in self._dates
            if d <= end and field in self._frames[d].get(asset, {})
        ]
        return tuple(values[-periods:])

    def up_to(self, as_of: date) -> "PanelData":
        """Point-in-time view: drop every frame after ``as_of``."""

        kept = {d: frame for d, frame in self._frames.items() if d <= as_of}
        return PanelData(_frames=kept, _dates=tuple(d for d in self._dates if d <= as_of))


@runtime_checkable
class Strategy(Protocol):
    """Contract every generated implementation must satisfy.

    Implementations must be deterministic given (data, params, seed) and must
    not look ahead: weights as of time t may use only data up to t.
    """

    def fit(self, data: PanelData, train_end: date) -> None:
        """Estimate parameters using data up to train_end only."""
        ...

    def weights(self, data: PanelData, as_of: date) -> dict[str, float]:
        """Return target weights keyed by asset id, using data up to as_of."""
        ...
