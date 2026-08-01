# API coverage

Source: official Spaceship OpenAPI input (SHA-256 `d4025290f62a5d14ad17142e2d75a59c19504f61066dfdaf7fab3d357cb75eeb`), retrieved `2026-08-01`.

This table accounts for every documented operation in the pinned Spaceship OpenAPI file. The 38 stable operations ship as fixed commands and are implemented from official documentation but remain live-unverified. The two HTTP-501 operations stay registered only so the tool can refuse them locally and explain the provider limit.

| Family | Method | Path | OperationId | Shipped command | Status |
|---|---|---|---|---|---|
| Async Operations | GET | /v1/async-operations/{operationId} | getAsyncOperationDetails | qwayk-spaceship-safe-agent-cli async-operations status | Implemented / live-unverified |
| Contacts | GET | /v1/contacts/{contact} | readDetails | qwayk-spaceship-safe-agent-cli contacts get | Implemented / live-unverified |
| Contacts | PUT | /v1/contacts | saveDetails | qwayk-spaceship-safe-agent-cli contacts save | Implemented / live-unverified |
| Contacts attributes | GET | /v1/contacts/attributes/{contact} | readAttributeDetails | qwayk-spaceship-safe-agent-cli contacts attributes get | Implemented / live-unverified |
| Contacts attributes | PUT | /v1/contacts/attributes | saveContactAttributes | qwayk-spaceship-safe-agent-cli contacts attributes set | Implemented / live-unverified |
| DNS records | DELETE | /v1/dns/records/{domain} | deleteRecords | qwayk-spaceship-safe-agent-cli dns delete-records | Implemented / live-unverified |
| DNS records | GET | /v1/dns/records/{domain} | getResourceRecordsList | qwayk-spaceship-safe-agent-cli dns list-records | Implemented / live-unverified |
| DNS records | PUT | /v1/dns/records/{domain} | saveRecords | qwayk-spaceship-safe-agent-cli dns set-records | Implemented / live-unverified |
| Domain Availability | GET | /v1/domains/{domain}/available | checkSingleDomainAvailability | qwayk-spaceship-safe-agent-cli domains check-availability | Implemented / live-unverified |
| Domain Availability | POST | /v1/domains/available | checkDomainsAvailability | qwayk-spaceship-safe-agent-cli domains check-domains | Implemented / live-unverified |
| Domain Management | DELETE | /v1/domains/{domain} | domainDelete | qwayk-spaceship-safe-agent-cli domains delete | Developer preview — unavailable (official description says HTTP 501) |
| Domain Management | GET | /v1/domains | getDomainList | qwayk-spaceship-safe-agent-cli domains list | Implemented / live-unverified |
| Domain Management | GET | /v1/domains/{domain} | getDomainInfo | qwayk-spaceship-safe-agent-cli domains get | Implemented / live-unverified |
| Domain Management | POST | /v1/domains/{domain} | domainCreate | qwayk-spaceship-safe-agent-cli domains create | Implemented / live-unverified |
| Domain Management | POST | /v1/domains/{domain}/renew | domainRenew | qwayk-spaceship-safe-agent-cli domains renew | Implemented / live-unverified |
| Domain Management | POST | /v1/domains/{domain}/restore | domainRestore | qwayk-spaceship-safe-agent-cli domains restore | Implemented / live-unverified |
| Domain Settings | PUT | /v1/domains/{domain}/autorenew | updateAutorenewal | qwayk-spaceship-safe-agent-cli domains set-autorenew | Implemented / live-unverified |
| Domain Settings | PUT | /v1/domains/{domain}/contacts | setDomainContacts | qwayk-spaceship-safe-agent-cli domains set-contacts | Implemented / live-unverified |
| Domain Settings | PUT | /v1/domains/{domain}/nameservers | setDomainNameservers | qwayk-spaceship-safe-agent-cli domains set-nameservers | Implemented / live-unverified |
| Domain Settings | PUT | /v1/domains/{domain}/privacy/email-protection-preference | updateDomainEmailProtectionPreference | qwayk-spaceship-safe-agent-cli domains set-email-protection | Implemented / live-unverified |
| Domain Settings | PUT | /v1/domains/{domain}/privacy/preference | updateDomainPrivacyPreference | qwayk-spaceship-safe-agent-cli domains set-privacy | Implemented / live-unverified |
| Domain Transfer | GET | /v1/domains/{domain}/transfer | getTransferInfo | qwayk-spaceship-safe-agent-cli domains transfer get | Implemented / live-unverified |
| Domain Transfer | GET | /v1/domains/{domain}/transfer/auth-code | getAuthCode | qwayk-spaceship-safe-agent-cli domains transfer auth-code | Implemented / live-unverified |
| Domain Transfer | POST | /v1/domains/{domain}/transfer | transferRequest | qwayk-spaceship-safe-agent-cli domains transfer request | Implemented / live-unverified |
| Domain Transfer | PUT | /v1/domains/{domain}/transfer/lock | updateTransferLock | qwayk-spaceship-safe-agent-cli domains transfer lock | Implemented / live-unverified |
| Personal Nameservers | DELETE | /v1/domains/{domain}/personal-nameservers/{currentHost} | deleteDomainPersonalNameserverHostInfo | qwayk-spaceship-safe-agent-cli domains personal-nameservers delete-host | Implemented / live-unverified |
| Personal Nameservers | GET | /v1/domains/{domain}/personal-nameservers | getDomainPersonalNameservers | qwayk-spaceship-safe-agent-cli domains personal-nameservers list | Implemented / live-unverified |
| Personal Nameservers | GET | /v1/domains/{domain}/personal-nameservers/{currentHost} | getDomainPersonalNameserverHostInfo | qwayk-spaceship-safe-agent-cli domains personal-nameservers get-host | Developer preview — unavailable (official description says HTTP 501) |
| Personal Nameservers | PUT | /v1/domains/{domain}/personal-nameservers/{currentHost} | updateDomainPersonalNameserverHostInfo | qwayk-spaceship-safe-agent-cli domains personal-nameservers update-host | Implemented / live-unverified |
| SellerHub | DELETE | /v1/sellerhub/domains/{domain} | deleteSellerHubDomain | qwayk-spaceship-safe-agent-cli sellerhub delete-domain | Implemented / live-unverified |
| SellerHub | GET | /v1/sellerhub/domains | getSellerHubDomainList | qwayk-spaceship-safe-agent-cli sellerhub list-domains | Implemented / live-unverified |
| SellerHub | GET | /v1/sellerhub/domains/reports/sold | getSoldDomains | qwayk-spaceship-safe-agent-cli sellerhub list-sold-domains | Implemented / live-unverified |
| SellerHub | GET | /v1/sellerhub/domains/{domain} | getSellerHubDomain | qwayk-spaceship-safe-agent-cli sellerhub get-domain | Implemented / live-unverified |
| SellerHub | GET | /v1/sellerhub/safepay-transactions | getSafePayTransactionList | qwayk-spaceship-safe-agent-cli sellerhub safepay list | Implemented / live-unverified |
| SellerHub | GET | /v1/sellerhub/safepay-transactions/{transactionId} | getSafePayTransaction | qwayk-spaceship-safe-agent-cli sellerhub safepay get | Implemented / live-unverified |
| SellerHub | GET | /v1/sellerhub/verification-records | getVerificationRecords | qwayk-spaceship-safe-agent-cli sellerhub verification-records | Implemented / live-unverified |
| SellerHub | PATCH | /v1/sellerhub/domains/{domain} | updateSellerHubDomain | qwayk-spaceship-safe-agent-cli sellerhub update-domain | Implemented / live-unverified |
| SellerHub | POST | /v1/sellerhub/checkout-links | createCheckoutLink | qwayk-spaceship-safe-agent-cli sellerhub create-checkout-link | Implemented / live-unverified |
| SellerHub | POST | /v1/sellerhub/domains | createSellerHubDomain | qwayk-spaceship-safe-agent-cli sellerhub create-domain | Implemented / live-unverified |
| SellerHub | POST | /v1/sellerhub/safepay-transactions | createSafePayTransaction | qwayk-spaceship-safe-agent-cli sellerhub safepay create | Implemented / live-unverified |
