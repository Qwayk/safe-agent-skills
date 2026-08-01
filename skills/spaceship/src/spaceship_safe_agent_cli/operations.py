from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OperationSpec:
    command: tuple[str, ...]
    method: str
    path_template: str
    operation_id: str
    status: str
    read_like: bool = False
    body: bool = False
    query_params: tuple[str, ...] = ()
    help_text: str = ""

    @property
    def stable(self) -> bool:
        return self.status == "Stable"

    @property
    def path_params(self) -> tuple[str, ...]:
        params: list[str] = []
        for segment in self.path_template.split("/"):
            if segment.startswith("{") and segment.endswith("}"):
                params.append(segment[1:-1])
        return tuple(params)


OFFICIAL_OPERATIONS: list[OperationSpec] = [
    OperationSpec(
        ("async-operations", "status"),
        "GET",
        "/v1/async-operations/{operationId}",
        "getAsyncOperationDetails",
        "Stable",
        query_params=(),
        help_text="Read async operation status",
    ),
    OperationSpec(("contacts", "get"), "GET", "/v1/contacts/{contact}", "readDetails", "Stable", help_text="Read contact"),
    OperationSpec(("contacts", "save"), "PUT", "/v1/contacts", "saveDetails", "Stable", body=True, help_text="Save contact"),
    OperationSpec(
        ("contacts", "attributes", "get"),
        "GET",
        "/v1/contacts/attributes/{contact}",
        "readAttributeDetails",
        "Stable",
        help_text="Read contact attribute details",
    ),
    OperationSpec(
        ("contacts", "attributes", "set"),
        "PUT",
        "/v1/contacts/attributes",
        "saveContactAttributes",
        "Stable",
        body=True,
        help_text="Set contact attributes",
    ),
    OperationSpec(
        ("dns", "delete-records"),
        "DELETE",
        "/v1/dns/records/{domain}",
        "deleteRecords",
        "Stable",
        body=True,
        help_text="Delete all DNS records",
    ),
    OperationSpec(("dns", "list-records"), "GET", "/v1/dns/records/{domain}", "getResourceRecordsList", "Stable", query_params=("take", "skip", "orderBy"), help_text="List DNS records"),
    OperationSpec(
        ("dns", "set-records"),
        "PUT",
        "/v1/dns/records/{domain}",
        "saveRecords",
        "Stable",
        body=True,
        help_text="Replace all DNS records",
    ),
    OperationSpec(
        ("domains", "check-availability"),
        "GET",
        "/v1/domains/{domain}/available",
        "checkSingleDomainAvailability",
        "Stable",
        help_text="Check one domain availability",
    ),
    OperationSpec(
        ("domains", "check-domains"),
        "POST",
        "/v1/domains/available",
        "checkDomainsAvailability",
        "Stable",
        read_like=True,
        body=True,
        help_text="Check multiple domain availability (read-like)",
    ),
    OperationSpec(("domains", "delete"), "DELETE", "/v1/domains/{domain}", "domainDelete", "HTTP-501", help_text="Delete domain (unavailable: 501)"),
    OperationSpec(
        ("domains", "list"),
        "GET",
        "/v1/domains",
        "getDomainList",
        "Stable",
        query_params=("take", "skip", "orderBy"),
        help_text="List domains",
    ),
    OperationSpec(("domains", "get"), "GET", "/v1/domains/{domain}", "getDomainInfo", "Stable", help_text="Get domain details"),
    OperationSpec(
        ("domains", "create"),
        "POST",
        "/v1/domains/{domain}",
        "domainCreate",
        "Stable",
        body=True,
        help_text="Create a new domain registration",
    ),
    OperationSpec(("domains", "renew"), "POST", "/v1/domains/{domain}/renew", "domainRenew", "Stable", body=True, help_text="Renew a domain"),
    OperationSpec(("domains", "restore"), "POST", "/v1/domains/{domain}/restore", "domainRestore", "Stable", body=False, help_text="Restore a deleted domain"),
    OperationSpec(
        ("domains", "set-autorenew"),
        "PUT",
        "/v1/domains/{domain}/autorenew",
        "updateAutorenewal",
        "Stable",
        body=True,
        help_text="Set domain auto-renew",
    ),
    OperationSpec(
        ("domains", "set-contacts"),
        "PUT",
        "/v1/domains/{domain}/contacts",
        "setDomainContacts",
        "Stable",
        body=True,
        help_text="Set domain contacts",
    ),
    OperationSpec(
        ("domains", "set-nameservers"),
        "PUT",
        "/v1/domains/{domain}/nameservers",
        "setDomainNameservers",
        "Stable",
        body=True,
        help_text="Set domain nameservers",
    ),
    OperationSpec(
        ("domains", "set-email-protection"),
        "PUT",
        "/v1/domains/{domain}/privacy/email-protection-preference",
        "updateDomainEmailProtectionPreference",
        "Stable",
        body=True,
        help_text="Set email privacy preference",
    ),
    OperationSpec(
        ("domains", "set-privacy"),
        "PUT",
        "/v1/domains/{domain}/privacy/preference",
        "updateDomainPrivacyPreference",
        "Stable",
        body=True,
        help_text="Set WHOIS privacy preference",
    ),
    OperationSpec(("domains", "transfer", "get"), "GET", "/v1/domains/{domain}/transfer", "getTransferInfo", "Stable", help_text="Read transfer state"),
    OperationSpec(("domains", "transfer", "auth-code"), "GET", "/v1/domains/{domain}/transfer/auth-code", "getAuthCode", "Stable", help_text="Read transfer auth code metadata"),
    OperationSpec(
        ("domains", "transfer", "request"),
        "POST",
        "/v1/domains/{domain}/transfer",
        "transferRequest",
        "Stable",
        body=True,
        help_text="Submit transfer request",
    ),
    OperationSpec(
        ("domains", "transfer", "lock"),
        "PUT",
        "/v1/domains/{domain}/transfer/lock",
        "updateTransferLock",
        "Stable",
        body=True,
        help_text="Update transfer lock",
    ),
    OperationSpec(
        ("domains", "personal-nameservers", "delete-host"),
        "DELETE",
        "/v1/domains/{domain}/personal-nameservers/{currentHost}",
        "deleteDomainPersonalNameserverHostInfo",
        "Stable",
        body=False,
        help_text="Delete a personal nameserver host",
    ),
    OperationSpec(
        ("domains", "personal-nameservers", "list"),
        "GET",
        "/v1/domains/{domain}/personal-nameservers",
        "getDomainPersonalNameservers",
        "Stable",
        help_text="List personal nameservers",
    ),
    OperationSpec(
        ("domains", "personal-nameservers", "get-host"),
        "GET",
        "/v1/domains/{domain}/personal-nameservers/{currentHost}",
        "getDomainPersonalNameserverHostInfo",
        "HTTP-501",
        help_text="Read personal host details (unavailable: 501)",
    ),
    OperationSpec(
        ("domains", "personal-nameservers", "update-host"),
        "PUT",
        "/v1/domains/{domain}/personal-nameservers/{currentHost}",
        "updateDomainPersonalNameserverHostInfo",
        "Stable",
        body=True,
        help_text="Update a personal nameserver host",
    ),
    OperationSpec(
        ("sellerhub", "delete-domain"),
        "DELETE",
        "/v1/sellerhub/domains/{domain}",
        "deleteSellerHubDomain",
        "Stable",
        body=False,
        help_text="Delete SellerHub domain",
    ),
    OperationSpec(("sellerhub", "list-domains"), "GET", "/v1/sellerhub/domains", "getSellerHubDomainList", "Stable", query_params=("take", "skip"), help_text="List SellerHub domains"),
    OperationSpec(
        ("sellerhub", "list-sold-domains"),
        "GET",
        "/v1/sellerhub/domains/reports/sold",
        "getSoldDomains",
        "Stable",
        query_params=("take", "cursor", "saleDateTimeFrom", "saleDateTimeTo"),
        help_text="List SellerHub sold domains",
    ),
    OperationSpec(
        ("sellerhub", "get-domain"),
        "GET",
        "/v1/sellerhub/domains/{domain}",
        "getSellerHubDomain",
        "Stable",
        help_text="Read SellerHub domain details",
    ),
    OperationSpec(
        ("sellerhub", "safepay", "list"),
        "GET",
        "/v1/sellerhub/safepay-transactions",
        "getSafePayTransactionList",
        "Stable",
        query_params=("take", "skip"),
        help_text="List SafePay transactions",
    ),
    OperationSpec(
        ("sellerhub", "safepay", "get"),
        "GET",
        "/v1/sellerhub/safepay-transactions/{transactionId}",
        "getSafePayTransaction",
        "Stable",
        help_text="Read SafePay transaction",
    ),
    OperationSpec(
        ("sellerhub", "verification-records"),
        "GET",
        "/v1/sellerhub/verification-records",
        "getVerificationRecords",
        "Stable",
        help_text="Read verification records",
    ),
    OperationSpec(("sellerhub", "update-domain"), "PATCH", "/v1/sellerhub/domains/{domain}", "updateSellerHubDomain", "Stable", body=True, help_text="Update SellerHub listing"),
    OperationSpec(
        ("sellerhub", "create-checkout-link"),
        "POST",
        "/v1/sellerhub/checkout-links",
        "createCheckoutLink",
        "Stable",
        body=True,
        help_text="Create checkout link",
    ),
    OperationSpec(
        ("sellerhub", "create-domain"),
        "POST",
        "/v1/sellerhub/domains",
        "createSellerHubDomain",
        "Stable",
        body=True,
        help_text="Create SellerHub listing",
    ),
    OperationSpec(
        ("sellerhub", "safepay", "create"),
        "POST",
        "/v1/sellerhub/safepay-transactions",
        "createSafePayTransaction",
        "Stable",
        body=True,
        help_text="Create SafePay transaction",
    ),
]
