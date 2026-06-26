from __future__ import annotations

from datetime import date, datetime


DATE_FMT = "%Y-%m-%d"


def parse_date(value: str) -> date:
    return datetime.strptime(value, DATE_FMT).date()


def today() -> date:
    return date.today()


def days_until(target: date, start: date | None = None) -> int:
    current = start or today()
    return (target - current).days


def date_range(start: date, days: int) -> list[date]:
    from datetime import timedelta

    return [start + timedelta(days=offset) for offset in range(max(days, 0))]

