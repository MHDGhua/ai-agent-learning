from typing import Any, TypeVar

T = TypeVar("T")


def _enum_member(fallback: T, name: str) -> T:
    return getattr(type(fallback), name, fallback)


def parse_risk_level(raw_value: Any, fallback: T) -> T:
    text = str(raw_value or "").strip()
    if "高" in text:
        return _enum_member(fallback, "HIGH")
    if "低" in text:
        return _enum_member(fallback, "LOW")
    if "中" in text:
        return _enum_member(fallback, "MEDIUM")
    return fallback


def parse_success_probability(raw_value: Any, fallback: T) -> T:
    text = str(raw_value or "").strip()
    if "高" in text:
        return _enum_member(fallback, "HIGH")
    if "低" in text:
        return _enum_member(fallback, "LOW")
    if "中" in text:
        return _enum_member(fallback, "MEDIUM")
    return fallback
