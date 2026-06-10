from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class LocaleInfo:
    code: str
    name: str
    host: str
    region: str
    marketplace: str
    locale_tag: str


LOCALE_METADATA: Mapping[str, LocaleInfo] = {
    "au": LocaleInfo(
        code="au",
        name="Australia",
        host="webservices.amazon.com.au",
        region="us-west-2",
        marketplace="www.amazon.com.au",
        locale_tag="en_AU",
    ),
    "be": LocaleInfo(
        code="be",
        name="Belgium",
        host="webservices.amazon.com.be",
        region="eu-west-1",
        marketplace="www.amazon.com.be",
        locale_tag="nl_BE",
    ),
    "br": LocaleInfo(
        code="br",
        name="Brazil",
        host="webservices.amazon.com.br",
        region="us-east-1",
        marketplace="www.amazon.com.br",
        locale_tag="pt_BR",
    ),
    "ca": LocaleInfo(
        code="ca",
        name="Canada",
        host="webservices.amazon.ca",
        region="us-east-1",
        marketplace="www.amazon.ca",
        locale_tag="en_CA",
    ),
    "eg": LocaleInfo(
        code="eg",
        name="Egypt",
        host="webservices.amazon.eg",
        region="eu-west-1",
        marketplace="www.amazon.eg",
        locale_tag="ar_EG",
    ),
    "fr": LocaleInfo(
        code="fr",
        name="France",
        host="webservices.amazon.fr",
        region="eu-west-1",
        marketplace="www.amazon.fr",
        locale_tag="fr_FR",
    ),
    "de": LocaleInfo(
        code="de",
        name="Germany",
        host="webservices.amazon.de",
        region="eu-west-1",
        marketplace="www.amazon.de",
        locale_tag="de_DE",
    ),
    "in": LocaleInfo(
        code="in",
        name="India",
        host="webservices.amazon.in",
        region="eu-west-1",
        marketplace="www.amazon.in",
        locale_tag="en_IN",
    ),
    "ie": LocaleInfo(
        code="ie",
        name="Ireland",
        host="webservices.amazon.ie",
        region="eu-west-1",
        marketplace="www.amazon.ie",
        locale_tag="en_IE",
    ),
    "it": LocaleInfo(
        code="it",
        name="Italy",
        host="webservices.amazon.it",
        region="eu-west-1",
        marketplace="www.amazon.it",
        locale_tag="it_IT",
    ),
    "jp": LocaleInfo(
        code="jp",
        name="Japan",
        host="webservices.amazon.co.jp",
        region="us-west-2",
        marketplace="www.amazon.co.jp",
        locale_tag="ja_JP",
    ),
    "mx": LocaleInfo(
        code="mx",
        name="Mexico",
        host="webservices.amazon.com.mx",
        region="us-east-1",
        marketplace="www.amazon.com.mx",
        locale_tag="es_MX",
    ),
    "nl": LocaleInfo(
        code="nl",
        name="Netherlands",
        host="webservices.amazon.nl",
        region="eu-west-1",
        marketplace="www.amazon.nl",
        locale_tag="nl_NL",
    ),
    "pl": LocaleInfo(
        code="pl",
        name="Poland",
        host="webservices.amazon.pl",
        region="eu-west-1",
        marketplace="www.amazon.pl",
        locale_tag="pl_PL",
    ),
    "sg": LocaleInfo(
        code="sg",
        name="Singapore",
        host="webservices.amazon.sg",
        region="us-west-2",
        marketplace="www.amazon.sg",
        locale_tag="en_SG",
    ),
    "sa": LocaleInfo(
        code="sa",
        name="Saudi Arabia",
        host="webservices.amazon.sa",
        region="eu-west-1",
        marketplace="www.amazon.sa",
        locale_tag="ar_SA",
    ),
    "es": LocaleInfo(
        code="es",
        name="Spain",
        host="webservices.amazon.es",
        region="eu-west-1",
        marketplace="www.amazon.es",
        locale_tag="es_ES",
    ),
    "se": LocaleInfo(
        code="se",
        name="Sweden",
        host="webservices.amazon.se",
        region="eu-west-1",
        marketplace="www.amazon.se",
        locale_tag="sv_SE",
    ),
    "tr": LocaleInfo(
        code="tr",
        name="Turkey",
        host="webservices.amazon.com.tr",
        region="eu-west-1",
        marketplace="www.amazon.com.tr",
        locale_tag="tr_TR",
    ),
    "ae": LocaleInfo(
        code="ae",
        name="United Arab Emirates",
        host="webservices.amazon.ae",
        region="eu-west-1",
        marketplace="www.amazon.ae",
        locale_tag="ar_AE",
    ),
    "uk": LocaleInfo(
        code="uk",
        name="United Kingdom",
        host="webservices.amazon.co.uk",
        region="eu-west-1",
        marketplace="www.amazon.co.uk",
        locale_tag="en_GB",
    ),
    "us": LocaleInfo(
        code="us",
        name="United States",
        host="webservices.amazon.com",
        region="us-east-1",
        marketplace="www.amazon.com",
        locale_tag="en_US",
    ),
}

DEFAULT_LOCALE_CODE = "us"


def _normalize_locale_key(value: str) -> str:
    normalized = (value or "").strip().lower()
    return normalized.replace("-", "_")


def _build_locale_aliases() -> dict[str, LocaleInfo]:
    aliases: dict[str, LocaleInfo] = {}
    for code, info in LOCALE_METADATA.items():
        aliases[_normalize_locale_key(code)] = info
        aliases[_normalize_locale_key(info.locale_tag)] = info
    return aliases


_LOCALE_ALIAS_MAP = _build_locale_aliases()


def locale_info(code: str) -> LocaleInfo | None:
    return _LOCALE_ALIAS_MAP.get(_normalize_locale_key(code))


def list_locales() -> list[LocaleInfo]:
    return sorted(LOCALE_METADATA.values(), key=lambda obj: (obj.code, obj.name))


def locale_codes() -> list[str]:
    return sorted(LOCALE_METADATA.keys())
