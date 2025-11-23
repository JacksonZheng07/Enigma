"""Format normalized records into Enigma's SMB ontology contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from normalization.cleaner import Cleaner

STATE_ABBREVIATIONS = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "district of columbia": "DC",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
}

CORPORATE_SUFFIXES = {
    "LLC",
    "L.L.C",
    "INC",
    "INC.",
    "CO",
    "CO.",
    "CORP",
    "CORP.",
    "CORPORATION",
    "COMPANY",
    "LTD",
    "LTD.",
}


def format_records(
    records: Iterable[dict[str, object]],
    provider: str,
    provider_path: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Return (ontology_records, metadata_records) for downstream ingestion."""
    ontology: list[dict[str, object]] = []
    extras: list[dict[str, object]] = []
    for record in records:
        canonical, metadata = format_record(record, provider, provider_path)
        ontology.append(canonical)
        extras.append(metadata)
    return ontology, extras


def format_record(
    record: dict[str, object],
    provider: str,
    provider_path: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    """Convert a normalized record into the SMB ontology schema."""
    cleaned = Cleaner.clean_record(record or {})

    legal_name = _normalize_legal_name(
        cleaned.get("legal_name")
        or cleaned.get("business_name")
        or cleaned.get("entity_name")
    )
    brand_name = _normalize_brand_name(
        cleaned.get("brand_name")
        or cleaned.get("business_name_2")
        or cleaned.get("doing_business_as")
        or cleaned.get("dba")
        or cleaned.get("business_name")
    )

    dba_name = _normalize_legal_name(
        cleaned.get("business_name_2") or cleaned.get("dba") or cleaned.get("dba_name")
    )

    brand_aliases = _build_aliases(
        cleaned.get("business_name"),
        cleaned.get("business_name_2"),
        cleaned.get("dba"),
    )
    category = _title_case(cleaned.get("industry"))

    street_address = _build_street_address(cleaned)
    city = _title_case(cleaned.get("address_city"))
    state = _normalize_state(cleaned.get("address_state") or cleaned.get("state"))
    zip_code, zip_plus_4 = _normalize_zip(cleaned.get("zip_code"))
    latitude = _normalize_coordinate(cleaned.get("latitude"), -90.0, 90.0)
    longitude = _normalize_coordinate(cleaned.get("longitude"), -180.0, 180.0)
    phone_number = _normalize_phone(
        cleaned.get("contact_phone_number")
        or cleaned.get("phone")
        or cleaned.get("phone_number")
    )

    canonical_address = _build_canonical_address(street_address, city, state, zip_code)

    entity_status = _normalize_entity_status(cleaned.get("license_status"))
    state_of_incorp = state or _normalize_state(cleaned.get("state_of_incorporation"))
    ein = _normalize_ein(cleaned.get("ein"))

    provider_record_id = _provider_record_id(cleaned)

    aliases_used = {
        "legal_entity_name_source": cleaned.get("business_name"),
        "brand_name_source": cleaned.get("business_name_2") or cleaned.get("business_name"),
        "address_components": {
            "address_building": cleaned.get("address_building"),
            "address_street_name": cleaned.get("address_street_name"),
            "secondary_address_street_name": cleaned.get("secondary_address_street_name"),
        },
    }

    ontology_record = {
        "canonical_legal_entity_name": legal_name,
        "canonical_brand_name": brand_name or legal_name,
        "brand_aliases": brand_aliases,
        "category": category,
        "dba_name": dba_name,
        "entity_status": entity_status,
        "state_of_incorporation": state_of_incorp,
        "ein": ein,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "zip_plus_4": zip_plus_4,
        "canonical_address": canonical_address,
        "latitude": latitude,
        "longitude": longitude,
        "phone_number": phone_number,
        "provider": provider,
        "provider_record_id": provider_record_id,
    }

    metadata_record = {
        "provider": provider,
        "provider_record_id": provider_record_id,
        "provider_path": str(provider_path),
        "aliases_used": aliases_used,
        "raw_record": cleaned,
    }

    return ontology_record, metadata_record


def _normalize_legal_name(value: object) -> str | None:
    if not value:
        return None
    name = _strip_noise(str(value))
    return _title_case(name)


def _normalize_brand_name(value: object) -> str | None:
    if not value:
        return None
    name = _strip_noise(str(value))
    tokens = name.split()
    while tokens and tokens[-1].replace(".", "").upper() in CORPORATE_SUFFIXES:
        tokens.pop()
    cleaned = " ".join(tokens) or name
    return _title_case(cleaned)


def _strip_noise(value: str) -> str:
    value = value.replace("&", " & ")
    value = re.sub(r"[^A-Za-z0-9&' ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _title_case(value: object) -> str | None:
    if not value:
        return None
    return str(value).strip().title()


def _build_aliases(*values: object) -> list[str]:
    aliases: list[str] = []
    for value in values:
        normalized = _normalize_brand_name(value)
        if normalized and normalized not in aliases:
            aliases.append(normalized)
    return aliases


def _build_street_address(record: dict[str, object]) -> str | None:
    def assemble(building: object, primary: object, secondary: object) -> str | None:
        parts: list[str] = []
        for value in (building, primary, secondary):
            if value:
                parts.append(str(value).strip())
        if not parts:
            return None
        address = " ".join(parts)
        return re.sub(r"\s+", " ", address).strip().upper()

    primary = assemble(
        record.get("address_building"),
        record.get("address_street_name"),
        record.get("secondary_address_street_name"),
    )
    if primary:
        return primary

    # Fall back to any pre-composed street addresses if individual segments are missing.
    for key in ("street_address", "mailing_address", "mail_address"):
        if record.get(key):
            address = str(record[key]).strip()
            if address:
                return re.sub(r"\s+", " ", address).strip().upper()
    return None


def _normalize_state(value: object) -> str | None:
    if not value:
        return None
    text = str(value).strip()
    if len(text) == 2 and text.isalpha():
        return text.upper()
    lookup = STATE_ABBREVIATIONS.get(text.lower())
    if lookup:
        return lookup
    return None


def _normalize_zip(value: object) -> tuple[str | None, str | None]:
    if not value:
        return (None, None)
    text = str(value).strip()
    if len(text) == 10 and "-" in text:
        left, right = text.split("-", 1)
        return (left[:5], right[:4])
    if len(text) == 9 and text.isdigit():
        return (text[:5], text[5:])
    if len(text) == 5 and text.isdigit():
        return (text, None)
    return (None, None)


def _normalize_coordinate(value: object, lower: float, upper: float) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if lower <= number <= upper:
        return number
    return None


def _normalize_phone(value: object) -> str | None:
    if not value:
        return None
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits if len(digits) == 10 else None


def _normalize_entity_status(value: object) -> str | None:
    if not value:
        return None
    text = str(value).strip().upper()
    if text in {"ACTIVE", "INACTIVE"}:
        return text
    return text or None


def _normalize_ein(value: object) -> str | None:
    if not value:
        return None
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return digits if len(digits) == 9 else None


def _provider_record_id(record: dict[str, object]) -> str | None:
    preferred_keys = [
        "provider_record_id",
        "dca_license_number",
        "license_number",
        "license_id",
        "record_id",
        "id",
    ]
    for key in preferred_keys:
        value = record.get(key)
        if value:
            return str(value)
    return None


def _build_canonical_address(
    street: str | None,
    city: str | None,
    state: str | None,
    zip_code: str | None,
) -> str | None:
    parts = [part for part in [street, city, state, zip_code] if part]
    if not parts:
        return None
    return ", ".join(parts)
