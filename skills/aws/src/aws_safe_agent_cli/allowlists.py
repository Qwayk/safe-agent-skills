from __future__ import annotations

from dataclasses import dataclass


def parse_csv_list(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    parts = [part.strip() for part in raw.split(",")]
    return tuple(part for part in parts if part)


@dataclass(frozen=True)
class AllowLists:
    accounts: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()

    def check(self, *, account_id: str, region_name: str) -> list[str]:
        reasons: list[str] = []
        if self.accounts and account_id not in self.accounts:
            reasons.append(f"account {account_id} is not in AWS_ALLOWED_ACCOUNTS")
        if self.regions and region_name not in self.regions:
            reasons.append(f"region {region_name} is not in AWS_ALLOWED_REGIONS")
        return reasons

