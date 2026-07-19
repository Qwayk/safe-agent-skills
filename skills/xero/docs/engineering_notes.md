# Engineering notes

## 2026-07-19 — generated command boundary

- The official 16.1.0 release contains 477 callable operations across 12 executable specs and one callback-only webhook spec.
- Five older AU Payroll operations remain in coverage but use current Leave Applications v2 and Timesheets 2.0 replacements instead of duplicate commands.
- The eInvoicing registrations page identifies a bodyless `PUT` for RegisterByBusinessNumber. The manual supplement uses that exact method and does not invent a body schema.
- Practice Manager 3.1, Xero HQ, and Xero Tax are kept access-gated and docs-only because the pinned release has no machine-readable contracts for safe complete inventories.
- Payment Services stays in the Accounting catalog but is marked certified-partner access.
- Current official overlays record regional reports and CIS settings, closed Bank Feeds and Finance access, payroll role/product conditions, Projects provisioning, legacy Expense Claims access, BankAccountAdmin conditions, and the Custom Connection journals exception.

## 2026-07-19 — runtime safety

- PKCE, paid Custom Connection, and App Store tokens use separate files.
- Custom Connections discover one exact organisation and omit `xero-tenant-id`; normal PKCE connections require an exact discovered tenant.
- All non-GET operations use saved plans. Collection creates and other actions without a reliable exact GET carry a no-snapshot warning.
- File plans bind the file name, size, request media type, file media type, and byte hash; apply refuses changed bytes before any provider write.
- Provider acceptance is recorded as `accepted_not_stronger_state` unless follow-up evidence supports more.
- Sensitive provider responses mask every leaf in normal stdout and receipts; full read content requires an owner-only protected output file.
- Request bodies and uploads stop locally above Xero's current 10 MB global request limit.
