# API coverage (operations → CLI)

## Summary

- Provider: Shopify
- API: Admin GraphQL
- Pinned API version: `2026-01`
- Canonical inventory snapshot: `docs/official_operations_2026-01_2026-03-04.txt`
- Total operations in snapshot: 761 (270 queries, 491 mutations)
- Last audited (UTC): 2026-06-04
- Mutation safety: plan first. Live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available.

## Mapping (complete)

| Operation | CLI command | Safety gates |
|---|---|---|
| `mutation:abandonmentEmailStateUpdate` | `shopify-admin-api-tool mutation abandonment-email-state-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:abandonmentUpdateActivitiesDeliveryStatuses` | `shopify-admin-api-tool mutation abandonment-update-activities-delivery-statuses` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:appPurchaseOneTimeCreate` | `shopify-admin-api-tool mutation app-purchase-one-time-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:appRevokeAccessScopes` | `shopify-admin-api-tool mutation app-revoke-access-scopes` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:appSubscriptionCancel` | `shopify-admin-api-tool mutation app-subscription-cancel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:appSubscriptionCreate` | `shopify-admin-api-tool mutation app-subscription-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:appSubscriptionLineItemUpdate` | `shopify-admin-api-tool mutation app-subscription-line-item-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:appSubscriptionTrialExtend` | `shopify-admin-api-tool mutation app-subscription-trial-extend` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:appUninstall` | `shopify-admin-api-tool mutation app-uninstall` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:appUsageRecordCreate` | `shopify-admin-api-tool mutation app-usage-record-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:articleCreate` | `shopify-admin-api-tool mutation article-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:articleDelete` | `shopify-admin-api-tool mutation article-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:articleUpdate` | `shopify-admin-api-tool mutation article-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:backupRegionUpdate` | `shopify-admin-api-tool mutation backup-region-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:blogCreate` | `shopify-admin-api-tool mutation blog-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:blogDelete` | `shopify-admin-api-tool mutation blog-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:blogUpdate` | `shopify-admin-api-tool mutation blog-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:bulkOperationCancel` | `shopify-admin-api-tool mutation bulk-operation-cancel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:bulkOperationRunMutation` | `shopify-admin-api-tool mutation bulk-operation-run-mutation` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:bulkOperationRunQuery` | `shopify-admin-api-tool mutation bulk-operation-run-query` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:bulkProductResourceFeedbackCreate` | `shopify-admin-api-tool mutation bulk-product-resource-feedback-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:carrierServiceCreate` | `shopify-admin-api-tool mutation carrier-service-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:carrierServiceDelete` | `shopify-admin-api-tool mutation carrier-service-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:carrierServiceUpdate` | `shopify-admin-api-tool mutation carrier-service-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:cartTransformCreate` | `shopify-admin-api-tool mutation cart-transform-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:cartTransformDelete` | `shopify-admin-api-tool mutation cart-transform-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:catalogContextUpdate` | `shopify-admin-api-tool mutation catalog-context-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:catalogCreate` | `shopify-admin-api-tool mutation catalog-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:catalogDelete` | `shopify-admin-api-tool mutation catalog-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:catalogUpdate` | `shopify-admin-api-tool mutation catalog-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:checkoutBrandingUpsert` | `shopify-admin-api-tool mutation checkout-branding-upsert` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionAddProducts` | `shopify-admin-api-tool mutation collection-add-products` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionAddProductsV2` | `shopify-admin-api-tool mutation collection-add-products-v2` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionCreate` | `shopify-admin-api-tool mutation collection-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionDelete` | `shopify-admin-api-tool mutation collection-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionDuplicate` | `shopify-admin-api-tool mutation collection-duplicate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionPublish` | `shopify-admin-api-tool mutation collection-publish` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionRemoveProducts` | `shopify-admin-api-tool mutation collection-remove-products` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionReorderProducts` | `shopify-admin-api-tool mutation collection-reorder-products` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionUnpublish` | `shopify-admin-api-tool mutation collection-unpublish` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:collectionUpdate` | `shopify-admin-api-tool mutation collection-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:combinedListingUpdate` | `shopify-admin-api-tool mutation combined-listing-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:commentApprove` | `shopify-admin-api-tool mutation comment-approve` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:commentDelete` | `shopify-admin-api-tool mutation comment-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:commentNotSpam` | `shopify-admin-api-tool mutation comment-not-spam` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:commentSpam` | `shopify-admin-api-tool mutation comment-spam` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companiesDelete` | `shopify-admin-api-tool mutation companies-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyAddressDelete` | `shopify-admin-api-tool mutation company-address-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyAssignCustomerAsContact` | `shopify-admin-api-tool mutation company-assign-customer-as-contact` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyAssignMainContact` | `shopify-admin-api-tool mutation company-assign-main-contact` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactAssignRole` | `shopify-admin-api-tool mutation company-contact-assign-role` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactAssignRoles` | `shopify-admin-api-tool mutation company-contact-assign-roles` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactCreate` | `shopify-admin-api-tool mutation company-contact-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactDelete` | `shopify-admin-api-tool mutation company-contact-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactRemoveFromCompany` | `shopify-admin-api-tool mutation company-contact-remove-from-company` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactRevokeRole` | `shopify-admin-api-tool mutation company-contact-revoke-role` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactRevokeRoles` | `shopify-admin-api-tool mutation company-contact-revoke-roles` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactUpdate` | `shopify-admin-api-tool mutation company-contact-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyContactsDelete` | `shopify-admin-api-tool mutation company-contacts-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyCreate` | `shopify-admin-api-tool mutation company-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyDelete` | `shopify-admin-api-tool mutation company-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationAssignAddress` | `shopify-admin-api-tool mutation company-location-assign-address` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationAssignRoles` | `shopify-admin-api-tool mutation company-location-assign-roles` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationAssignStaffMembers` | `shopify-admin-api-tool mutation company-location-assign-staff-members` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationAssignTaxExemptions` | `shopify-admin-api-tool mutation company-location-assign-tax-exemptions` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationCreate` | `shopify-admin-api-tool mutation company-location-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationCreateTaxRegistration` | `shopify-admin-api-tool mutation company-location-create-tax-registration` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationDelete` | `shopify-admin-api-tool mutation company-location-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationRemoveStaffMembers` | `shopify-admin-api-tool mutation company-location-remove-staff-members` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationRevokeRoles` | `shopify-admin-api-tool mutation company-location-revoke-roles` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationRevokeTaxExemptions` | `shopify-admin-api-tool mutation company-location-revoke-tax-exemptions` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationRevokeTaxRegistration` | `shopify-admin-api-tool mutation company-location-revoke-tax-registration` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationTaxSettingsUpdate` | `shopify-admin-api-tool mutation company-location-tax-settings-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationUpdate` | `shopify-admin-api-tool mutation company-location-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyLocationsDelete` | `shopify-admin-api-tool mutation company-locations-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyRevokeMainContact` | `shopify-admin-api-tool mutation company-revoke-main-contact` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:companyUpdate` | `shopify-admin-api-tool mutation company-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:consentPolicyUpdate` | `shopify-admin-api-tool mutation consent-policy-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerAddTaxExemptions` | `shopify-admin-api-tool mutation customer-add-tax-exemptions` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerAddressCreate` | `shopify-admin-api-tool mutation customer-address-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerAddressDelete` | `shopify-admin-api-tool mutation customer-address-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerAddressUpdate` | `shopify-admin-api-tool mutation customer-address-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerCancelDataErasure` | `shopify-admin-api-tool mutation customer-cancel-data-erasure` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerCreate` | `shopify-admin-api-tool mutation customer-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerDelete` | `shopify-admin-api-tool mutation customer-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerEmailMarketingConsentUpdate` | `shopify-admin-api-tool mutation customer-email-marketing-consent-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerGenerateAccountActivationUrl` | `shopify-admin-api-tool mutation customer-generate-account-activation-url` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerMerge` | `shopify-admin-api-tool mutation customer-merge` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerPaymentMethodCreditCardCreate` | `shopify-admin-api-tool mutation customer-payment-method-credit-card-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerPaymentMethodCreditCardUpdate` | `shopify-admin-api-tool mutation customer-payment-method-credit-card-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerPaymentMethodGetUpdateUrl` | `shopify-admin-api-tool mutation customer-payment-method-get-update-url` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerPaymentMethodPaypalBillingAgreementCreate` | `shopify-admin-api-tool mutation customer-payment-method-paypal-billing-agreement-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerPaymentMethodPaypalBillingAgreementUpdate` | `shopify-admin-api-tool mutation customer-payment-method-paypal-billing-agreement-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerPaymentMethodRemoteCreate` | `shopify-admin-api-tool mutation customer-payment-method-remote-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerPaymentMethodRevoke` | `shopify-admin-api-tool mutation customer-payment-method-revoke` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerPaymentMethodSendUpdateEmail` | `shopify-admin-api-tool mutation customer-payment-method-send-update-email` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerRemoveTaxExemptions` | `shopify-admin-api-tool mutation customer-remove-tax-exemptions` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerReplaceTaxExemptions` | `shopify-admin-api-tool mutation customer-replace-tax-exemptions` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerRequestDataErasure` | `shopify-admin-api-tool mutation customer-request-data-erasure` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerSegmentMembersQueryCreate` | `shopify-admin-api-tool mutation customer-segment-members-query-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerSendAccountInviteEmail` | `shopify-admin-api-tool mutation customer-send-account-invite-email` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerSet` | `shopify-admin-api-tool mutation customer-set` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerSmsMarketingConsentUpdate` | `shopify-admin-api-tool mutation customer-sms-marketing-consent-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerUpdate` | `shopify-admin-api-tool mutation customer-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:customerUpdateDefaultAddress` | `shopify-admin-api-tool mutation customer-update-default-address` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:dataSaleOptOut` | `shopify-admin-api-tool mutation data-sale-opt-out` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:delegateAccessTokenCreate` | `shopify-admin-api-tool mutation delegate-access-token-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:delegateAccessTokenDestroy` | `shopify-admin-api-tool mutation delegate-access-token-destroy` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryCustomizationActivation` | `shopify-admin-api-tool mutation delivery-customization-activation` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryCustomizationCreate` | `shopify-admin-api-tool mutation delivery-customization-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryCustomizationDelete` | `shopify-admin-api-tool mutation delivery-customization-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryCustomizationUpdate` | `shopify-admin-api-tool mutation delivery-customization-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryProfileCreate` | `shopify-admin-api-tool mutation delivery-profile-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryProfileRemove` | `shopify-admin-api-tool mutation delivery-profile-remove` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryProfileUpdate` | `shopify-admin-api-tool mutation delivery-profile-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryPromiseParticipantsUpdate` | `shopify-admin-api-tool mutation delivery-promise-participants-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryPromiseProviderUpsert` | `shopify-admin-api-tool mutation delivery-promise-provider-upsert` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliverySettingUpdate` | `shopify-admin-api-tool mutation delivery-setting-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:deliveryShippingOriginAssign` | `shopify-admin-api-tool mutation delivery-shipping-origin-assign` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticActivate` | `shopify-admin-api-tool mutation discount-automatic-activate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticAppCreate` | `shopify-admin-api-tool mutation discount-automatic-app-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticAppUpdate` | `shopify-admin-api-tool mutation discount-automatic-app-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticBasicCreate` | `shopify-admin-api-tool mutation discount-automatic-basic-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticBasicUpdate` | `shopify-admin-api-tool mutation discount-automatic-basic-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticBulkDelete` | `shopify-admin-api-tool mutation discount-automatic-bulk-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticBxgyCreate` | `shopify-admin-api-tool mutation discount-automatic-bxgy-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticBxgyUpdate` | `shopify-admin-api-tool mutation discount-automatic-bxgy-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticDeactivate` | `shopify-admin-api-tool mutation discount-automatic-deactivate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticDelete` | `shopify-admin-api-tool mutation discount-automatic-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticFreeShippingCreate` | `shopify-admin-api-tool mutation discount-automatic-free-shipping-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountAutomaticFreeShippingUpdate` | `shopify-admin-api-tool mutation discount-automatic-free-shipping-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeActivate` | `shopify-admin-api-tool mutation discount-code-activate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeAppCreate` | `shopify-admin-api-tool mutation discount-code-app-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeAppUpdate` | `shopify-admin-api-tool mutation discount-code-app-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeBasicCreate` | `shopify-admin-api-tool mutation discount-code-basic-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeBasicUpdate` | `shopify-admin-api-tool mutation discount-code-basic-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeBulkActivate` | `shopify-admin-api-tool mutation discount-code-bulk-activate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeBulkDeactivate` | `shopify-admin-api-tool mutation discount-code-bulk-deactivate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeBulkDelete` | `shopify-admin-api-tool mutation discount-code-bulk-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeBxgyCreate` | `shopify-admin-api-tool mutation discount-code-bxgy-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeBxgyUpdate` | `shopify-admin-api-tool mutation discount-code-bxgy-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeDeactivate` | `shopify-admin-api-tool mutation discount-code-deactivate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeDelete` | `shopify-admin-api-tool mutation discount-code-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeFreeShippingCreate` | `shopify-admin-api-tool mutation discount-code-free-shipping-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeFreeShippingUpdate` | `shopify-admin-api-tool mutation discount-code-free-shipping-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountCodeRedeemCodeBulkDelete` | `shopify-admin-api-tool mutation discount-code-redeem-code-bulk-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:discountRedeemCodeBulkAdd` | `shopify-admin-api-tool mutation discount-redeem-code-bulk-add` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:disputeEvidenceUpdate` | `shopify-admin-api-tool mutation dispute-evidence-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderBulkAddTags` | `shopify-admin-api-tool mutation draft-order-bulk-add-tags` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderBulkDelete` | `shopify-admin-api-tool mutation draft-order-bulk-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderBulkRemoveTags` | `shopify-admin-api-tool mutation draft-order-bulk-remove-tags` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderCalculate` | `shopify-admin-api-tool mutation draft-order-calculate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderComplete` | `shopify-admin-api-tool mutation draft-order-complete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderCreate` | `shopify-admin-api-tool mutation draft-order-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderCreateFromOrder` | `shopify-admin-api-tool mutation draft-order-create-from-order` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderDelete` | `shopify-admin-api-tool mutation draft-order-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderDuplicate` | `shopify-admin-api-tool mutation draft-order-duplicate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderInvoicePreview` | `shopify-admin-api-tool mutation draft-order-invoice-preview` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderInvoiceSend` | `shopify-admin-api-tool mutation draft-order-invoice-send` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:draftOrderUpdate` | `shopify-admin-api-tool mutation draft-order-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:eventBridgeServerPixelUpdate` | `shopify-admin-api-tool mutation event-bridge-server-pixel-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:eventBridgeWebhookSubscriptionCreate` | `shopify-admin-api-tool mutation event-bridge-webhook-subscription-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:eventBridgeWebhookSubscriptionUpdate` | `shopify-admin-api-tool mutation event-bridge-webhook-subscription-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fileAcknowledgeUpdateFailed` | `shopify-admin-api-tool mutation file-acknowledge-update-failed` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fileCreate` | `shopify-admin-api-tool mutation file-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fileDelete` | `shopify-admin-api-tool mutation file-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fileUpdate` | `shopify-admin-api-tool mutation file-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:flowTriggerReceive` | `shopify-admin-api-tool mutation flow-trigger-receive` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentCancel` | `shopify-admin-api-tool mutation fulfillment-cancel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentConstraintRuleCreate` | `shopify-admin-api-tool mutation fulfillment-constraint-rule-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentConstraintRuleDelete` | `shopify-admin-api-tool mutation fulfillment-constraint-rule-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentConstraintRuleUpdate` | `shopify-admin-api-tool mutation fulfillment-constraint-rule-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentCreate` | `shopify-admin-api-tool mutation fulfillment-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentCreateV2` | `shopify-admin-api-tool mutation fulfillment-create-v2` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentEventCreate` | `shopify-admin-api-tool mutation fulfillment-event-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderAcceptCancellationRequest` | `shopify-admin-api-tool mutation fulfillment-order-accept-cancellation-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderAcceptFulfillmentRequest` | `shopify-admin-api-tool mutation fulfillment-order-accept-fulfillment-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderCancel` | `shopify-admin-api-tool mutation fulfillment-order-cancel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderClose` | `shopify-admin-api-tool mutation fulfillment-order-close` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderHold` | `shopify-admin-api-tool mutation fulfillment-order-hold` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderLineItemsPreparedForPickup` | `shopify-admin-api-tool mutation fulfillment-order-line-items-prepared-for-pickup` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderMerge` | `shopify-admin-api-tool mutation fulfillment-order-merge` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderMove` | `shopify-admin-api-tool mutation fulfillment-order-move` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderOpen` | `shopify-admin-api-tool mutation fulfillment-order-open` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderRejectCancellationRequest` | `shopify-admin-api-tool mutation fulfillment-order-reject-cancellation-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderRejectFulfillmentRequest` | `shopify-admin-api-tool mutation fulfillment-order-reject-fulfillment-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderReleaseHold` | `shopify-admin-api-tool mutation fulfillment-order-release-hold` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderReschedule` | `shopify-admin-api-tool mutation fulfillment-order-reschedule` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderSplit` | `shopify-admin-api-tool mutation fulfillment-order-split` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderSubmitCancellationRequest` | `shopify-admin-api-tool mutation fulfillment-order-submit-cancellation-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrderSubmitFulfillmentRequest` | `shopify-admin-api-tool mutation fulfillment-order-submit-fulfillment-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrdersReroute` | `shopify-admin-api-tool mutation fulfillment-orders-reroute` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentOrdersSetFulfillmentDeadline` | `shopify-admin-api-tool mutation fulfillment-orders-set-fulfillment-deadline` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentServiceCreate` | `shopify-admin-api-tool mutation fulfillment-service-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentServiceDelete` | `shopify-admin-api-tool mutation fulfillment-service-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentServiceUpdate` | `shopify-admin-api-tool mutation fulfillment-service-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentTrackingInfoUpdate` | `shopify-admin-api-tool mutation fulfillment-tracking-info-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:fulfillmentTrackingInfoUpdateV2` | `shopify-admin-api-tool mutation fulfillment-tracking-info-update-v2` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:giftCardCreate` | `shopify-admin-api-tool mutation gift-card-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:giftCardCredit` | `shopify-admin-api-tool mutation gift-card-credit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:giftCardDeactivate` | `shopify-admin-api-tool mutation gift-card-deactivate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:giftCardDebit` | `shopify-admin-api-tool mutation gift-card-debit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:giftCardSendNotificationToCustomer` | `shopify-admin-api-tool mutation gift-card-send-notification-to-customer` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:giftCardSendNotificationToRecipient` | `shopify-admin-api-tool mutation gift-card-send-notification-to-recipient` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:giftCardUpdate` | `shopify-admin-api-tool mutation gift-card-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryActivate` | `shopify-admin-api-tool mutation inventory-activate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryAdjustQuantities` | `shopify-admin-api-tool mutation inventory-adjust-quantities` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryBulkToggleActivation` | `shopify-admin-api-tool mutation inventory-bulk-toggle-activation` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryDeactivate` | `shopify-admin-api-tool mutation inventory-deactivate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryItemUpdate` | `shopify-admin-api-tool mutation inventory-item-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryMoveQuantities` | `shopify-admin-api-tool mutation inventory-move-quantities` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventorySetOnHandQuantities` | `shopify-admin-api-tool mutation inventory-set-on-hand-quantities` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventorySetQuantities` | `shopify-admin-api-tool mutation inventory-set-quantities` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventorySetScheduledChanges` | `shopify-admin-api-tool mutation inventory-set-scheduled-changes` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentAddItems` | `shopify-admin-api-tool mutation inventory-shipment-add-items` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentCreate` | `shopify-admin-api-tool mutation inventory-shipment-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentCreateInTransit` | `shopify-admin-api-tool mutation inventory-shipment-create-in-transit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentDelete` | `shopify-admin-api-tool mutation inventory-shipment-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentMarkInTransit` | `shopify-admin-api-tool mutation inventory-shipment-mark-in-transit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentReceive` | `shopify-admin-api-tool mutation inventory-shipment-receive` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentRemoveItems` | `shopify-admin-api-tool mutation inventory-shipment-remove-items` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentSetTracking` | `shopify-admin-api-tool mutation inventory-shipment-set-tracking` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryShipmentUpdateItemQuantities` | `shopify-admin-api-tool mutation inventory-shipment-update-item-quantities` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferCancel` | `shopify-admin-api-tool mutation inventory-transfer-cancel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferCreate` | `shopify-admin-api-tool mutation inventory-transfer-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferCreateAsReadyToShip` | `shopify-admin-api-tool mutation inventory-transfer-create-as-ready-to-ship` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferDelete` | `shopify-admin-api-tool mutation inventory-transfer-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferDuplicate` | `shopify-admin-api-tool mutation inventory-transfer-duplicate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferEdit` | `shopify-admin-api-tool mutation inventory-transfer-edit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferMarkAsReadyToShip` | `shopify-admin-api-tool mutation inventory-transfer-mark-as-ready-to-ship` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferRemoveItems` | `shopify-admin-api-tool mutation inventory-transfer-remove-items` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:inventoryTransferSetItems` | `shopify-admin-api-tool mutation inventory-transfer-set-items` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:locationActivate` | `shopify-admin-api-tool mutation location-activate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:locationAdd` | `shopify-admin-api-tool mutation location-add` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:locationDeactivate` | `shopify-admin-api-tool mutation location-deactivate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:locationDelete` | `shopify-admin-api-tool mutation location-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:locationEdit` | `shopify-admin-api-tool mutation location-edit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:locationLocalPickupDisable` | `shopify-admin-api-tool mutation location-local-pickup-disable` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:locationLocalPickupEnable` | `shopify-admin-api-tool mutation location-local-pickup-enable` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketCreate` | `shopify-admin-api-tool mutation market-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketCurrencySettingsUpdate` | `shopify-admin-api-tool mutation market-currency-settings-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketDelete` | `shopify-admin-api-tool mutation market-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketLocalizationsRegister` | `shopify-admin-api-tool mutation market-localizations-register` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketLocalizationsRemove` | `shopify-admin-api-tool mutation market-localizations-remove` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketRegionDelete` | `shopify-admin-api-tool mutation market-region-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketRegionsCreate` | `shopify-admin-api-tool mutation market-regions-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketRegionsDelete` | `shopify-admin-api-tool mutation market-regions-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketUpdate` | `shopify-admin-api-tool mutation market-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketWebPresenceCreate` | `shopify-admin-api-tool mutation market-web-presence-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketWebPresenceDelete` | `shopify-admin-api-tool mutation market-web-presence-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketWebPresenceUpdate` | `shopify-admin-api-tool mutation market-web-presence-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingActivitiesDeleteAllExternal` | `shopify-admin-api-tool mutation marketing-activities-delete-all-external` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingActivityCreate` | `shopify-admin-api-tool mutation marketing-activity-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingActivityCreateExternal` | `shopify-admin-api-tool mutation marketing-activity-create-external` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingActivityDeleteExternal` | `shopify-admin-api-tool mutation marketing-activity-delete-external` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingActivityUpdate` | `shopify-admin-api-tool mutation marketing-activity-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingActivityUpdateExternal` | `shopify-admin-api-tool mutation marketing-activity-update-external` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingActivityUpsertExternal` | `shopify-admin-api-tool mutation marketing-activity-upsert-external` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingEngagementCreate` | `shopify-admin-api-tool mutation marketing-engagement-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:marketingEngagementsDelete` | `shopify-admin-api-tool mutation marketing-engagements-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:menuCreate` | `shopify-admin-api-tool mutation menu-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:menuDelete` | `shopify-admin-api-tool mutation menu-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:menuUpdate` | `shopify-admin-api-tool mutation menu-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metafieldDefinitionCreate` | `shopify-admin-api-tool mutation metafield-definition-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metafieldDefinitionDelete` | `shopify-admin-api-tool mutation metafield-definition-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metafieldDefinitionPin` | `shopify-admin-api-tool mutation metafield-definition-pin` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metafieldDefinitionUnpin` | `shopify-admin-api-tool mutation metafield-definition-unpin` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metafieldDefinitionUpdate` | `shopify-admin-api-tool mutation metafield-definition-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metafieldsDelete` | `shopify-admin-api-tool mutation metafields-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metafieldsSet` | `shopify-admin-api-tool mutation metafields-set` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metaobjectBulkDelete` | `shopify-admin-api-tool mutation metaobject-bulk-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metaobjectCreate` | `shopify-admin-api-tool mutation metaobject-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metaobjectDefinitionCreate` | `shopify-admin-api-tool mutation metaobject-definition-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metaobjectDefinitionDelete` | `shopify-admin-api-tool mutation metaobject-definition-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metaobjectDefinitionUpdate` | `shopify-admin-api-tool mutation metaobject-definition-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metaobjectDelete` | `shopify-admin-api-tool mutation metaobject-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metaobjectUpdate` | `shopify-admin-api-tool mutation metaobject-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:metaobjectUpsert` | `shopify-admin-api-tool mutation metaobject-upsert` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:mobilePlatformApplicationCreate` | `shopify-admin-api-tool mutation mobile-platform-application-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:mobilePlatformApplicationDelete` | `shopify-admin-api-tool mutation mobile-platform-application-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:mobilePlatformApplicationUpdate` | `shopify-admin-api-tool mutation mobile-platform-application-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderCancel` | `shopify-admin-api-tool mutation order-cancel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderCapture` | `shopify-admin-api-tool mutation order-capture` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderClose` | `shopify-admin-api-tool mutation order-close` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderCreate` | `shopify-admin-api-tool mutation order-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderCreateMandatePayment` | `shopify-admin-api-tool mutation order-create-mandate-payment` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderCreateManualPayment` | `shopify-admin-api-tool mutation order-create-manual-payment` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderCustomerRemove` | `shopify-admin-api-tool mutation order-customer-remove` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderCustomerSet` | `shopify-admin-api-tool mutation order-customer-set` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderDelete` | `shopify-admin-api-tool mutation order-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditAddCustomItem` | `shopify-admin-api-tool mutation order-edit-add-custom-item` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditAddLineItemDiscount` | `shopify-admin-api-tool mutation order-edit-add-line-item-discount` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditAddShippingLine` | `shopify-admin-api-tool mutation order-edit-add-shipping-line` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditAddVariant` | `shopify-admin-api-tool mutation order-edit-add-variant` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditBegin` | `shopify-admin-api-tool mutation order-edit-begin` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditCommit` | `shopify-admin-api-tool mutation order-edit-commit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditRemoveDiscount` | `shopify-admin-api-tool mutation order-edit-remove-discount` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditRemoveLineItemDiscount` | `shopify-admin-api-tool mutation order-edit-remove-line-item-discount` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditRemoveShippingLine` | `shopify-admin-api-tool mutation order-edit-remove-shipping-line` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditSetQuantity` | `shopify-admin-api-tool mutation order-edit-set-quantity` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditUpdateDiscount` | `shopify-admin-api-tool mutation order-edit-update-discount` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderEditUpdateShippingLine` | `shopify-admin-api-tool mutation order-edit-update-shipping-line` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderInvoiceSend` | `shopify-admin-api-tool mutation order-invoice-send` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderMarkAsPaid` | `shopify-admin-api-tool mutation order-mark-as-paid` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderOpen` | `shopify-admin-api-tool mutation order-open` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderRiskAssessmentCreate` | `shopify-admin-api-tool mutation order-risk-assessment-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:orderUpdate` | `shopify-admin-api-tool mutation order-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:pageCreate` | `shopify-admin-api-tool mutation page-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:pageDelete` | `shopify-admin-api-tool mutation page-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:pageUpdate` | `shopify-admin-api-tool mutation page-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:paymentCustomizationActivation` | `shopify-admin-api-tool mutation payment-customization-activation` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:paymentCustomizationCreate` | `shopify-admin-api-tool mutation payment-customization-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:paymentCustomizationDelete` | `shopify-admin-api-tool mutation payment-customization-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:paymentCustomizationUpdate` | `shopify-admin-api-tool mutation payment-customization-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:paymentReminderSend` | `shopify-admin-api-tool mutation payment-reminder-send` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:paymentTermsCreate` | `shopify-admin-api-tool mutation payment-terms-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:paymentTermsDelete` | `shopify-admin-api-tool mutation payment-terms-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:paymentTermsUpdate` | `shopify-admin-api-tool mutation payment-terms-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:priceListCreate` | `shopify-admin-api-tool mutation price-list-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:priceListDelete` | `shopify-admin-api-tool mutation price-list-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:priceListFixedPricesAdd` | `shopify-admin-api-tool mutation price-list-fixed-prices-add` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:priceListFixedPricesByProductUpdate` | `shopify-admin-api-tool mutation price-list-fixed-prices-by-product-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:priceListFixedPricesDelete` | `shopify-admin-api-tool mutation price-list-fixed-prices-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:priceListFixedPricesUpdate` | `shopify-admin-api-tool mutation price-list-fixed-prices-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:priceListUpdate` | `shopify-admin-api-tool mutation price-list-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:privacyFeaturesDisable` | `shopify-admin-api-tool mutation privacy-features-disable` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productBundleCreate` | `shopify-admin-api-tool mutation product-bundle-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productBundleUpdate` | `shopify-admin-api-tool mutation product-bundle-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productChangeStatus` | `shopify-admin-api-tool mutation product-change-status` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productCreate` | `shopify-admin-api-tool mutation product-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productCreateMedia` | `shopify-admin-api-tool mutation product-create-media` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productDelete` | `shopify-admin-api-tool mutation product-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productDeleteMedia` | `shopify-admin-api-tool mutation product-delete-media` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productDuplicate` | `shopify-admin-api-tool mutation product-duplicate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productFeedCreate` | `shopify-admin-api-tool mutation product-feed-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productFeedDelete` | `shopify-admin-api-tool mutation product-feed-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productFullSync` | `shopify-admin-api-tool mutation product-full-sync` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productJoinSellingPlanGroups` | `shopify-admin-api-tool mutation product-join-selling-plan-groups` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productLeaveSellingPlanGroups` | `shopify-admin-api-tool mutation product-leave-selling-plan-groups` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productOptionUpdate` | `shopify-admin-api-tool mutation product-option-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productOptionsCreate` | `shopify-admin-api-tool mutation product-options-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productOptionsDelete` | `shopify-admin-api-tool mutation product-options-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productOptionsReorder` | `shopify-admin-api-tool mutation product-options-reorder` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productPublish` | `shopify-admin-api-tool mutation product-publish` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productReorderMedia` | `shopify-admin-api-tool mutation product-reorder-media` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productSet` | `shopify-admin-api-tool mutation product-set` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productUnpublish` | `shopify-admin-api-tool mutation product-unpublish` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productUpdate` | `shopify-admin-api-tool mutation product-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productUpdateMedia` | `shopify-admin-api-tool mutation product-update-media` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantAppendMedia` | `shopify-admin-api-tool mutation product-variant-append-media` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantDetachMedia` | `shopify-admin-api-tool mutation product-variant-detach-media` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantJoinSellingPlanGroups` | `shopify-admin-api-tool mutation product-variant-join-selling-plan-groups` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantLeaveSellingPlanGroups` | `shopify-admin-api-tool mutation product-variant-leave-selling-plan-groups` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantRelationshipBulkUpdate` | `shopify-admin-api-tool mutation product-variant-relationship-bulk-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantsBulkCreate` | `shopify-admin-api-tool mutation product-variants-bulk-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantsBulkDelete` | `shopify-admin-api-tool mutation product-variants-bulk-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantsBulkReorder` | `shopify-admin-api-tool mutation product-variants-bulk-reorder` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:productVariantsBulkUpdate` | `shopify-admin-api-tool mutation product-variants-bulk-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:pubSubServerPixelUpdate` | `shopify-admin-api-tool mutation pub-sub-server-pixel-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:pubSubWebhookSubscriptionCreate` | `shopify-admin-api-tool mutation pub-sub-webhook-subscription-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:pubSubWebhookSubscriptionUpdate` | `shopify-admin-api-tool mutation pub-sub-webhook-subscription-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:publicationCreate` | `shopify-admin-api-tool mutation publication-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:publicationDelete` | `shopify-admin-api-tool mutation publication-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:publicationUpdate` | `shopify-admin-api-tool mutation publication-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:publishablePublish` | `shopify-admin-api-tool mutation publishable-publish` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:publishablePublishToCurrentChannel` | `shopify-admin-api-tool mutation publishable-publish-to-current-channel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:publishableUnpublish` | `shopify-admin-api-tool mutation publishable-unpublish` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:publishableUnpublishToCurrentChannel` | `shopify-admin-api-tool mutation publishable-unpublish-to-current-channel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:quantityPricingByVariantUpdate` | `shopify-admin-api-tool mutation quantity-pricing-by-variant-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:quantityRulesAdd` | `shopify-admin-api-tool mutation quantity-rules-add` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:quantityRulesDelete` | `shopify-admin-api-tool mutation quantity-rules-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:refundCreate` | `shopify-admin-api-tool mutation refund-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:removeFromReturn` | `shopify-admin-api-tool mutation remove-from-return` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnApproveRequest` | `shopify-admin-api-tool mutation return-approve-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnCancel` | `shopify-admin-api-tool mutation return-cancel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnClose` | `shopify-admin-api-tool mutation return-close` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnCreate` | `shopify-admin-api-tool mutation return-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnDeclineRequest` | `shopify-admin-api-tool mutation return-decline-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnLineItemRemoveFromReturn` | `shopify-admin-api-tool mutation return-line-item-remove-from-return` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnProcess` | `shopify-admin-api-tool mutation return-process` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnRefund` | `shopify-admin-api-tool mutation return-refund` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnReopen` | `shopify-admin-api-tool mutation return-reopen` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:returnRequest` | `shopify-admin-api-tool mutation return-request` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:reverseDeliveryCreateWithShipping` | `shopify-admin-api-tool mutation reverse-delivery-create-with-shipping` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:reverseDeliveryShippingUpdate` | `shopify-admin-api-tool mutation reverse-delivery-shipping-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:reverseFulfillmentOrderDispose` | `shopify-admin-api-tool mutation reverse-fulfillment-order-dispose` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:savedSearchCreate` | `shopify-admin-api-tool mutation saved-search-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:savedSearchDelete` | `shopify-admin-api-tool mutation saved-search-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:savedSearchUpdate` | `shopify-admin-api-tool mutation saved-search-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:scriptTagCreate` | `shopify-admin-api-tool mutation script-tag-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:scriptTagDelete` | `shopify-admin-api-tool mutation script-tag-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:scriptTagUpdate` | `shopify-admin-api-tool mutation script-tag-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:segmentCreate` | `shopify-admin-api-tool mutation segment-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:segmentDelete` | `shopify-admin-api-tool mutation segment-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:segmentUpdate` | `shopify-admin-api-tool mutation segment-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:sellingPlanGroupAddProductVariants` | `shopify-admin-api-tool mutation selling-plan-group-add-product-variants` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:sellingPlanGroupAddProducts` | `shopify-admin-api-tool mutation selling-plan-group-add-products` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:sellingPlanGroupCreate` | `shopify-admin-api-tool mutation selling-plan-group-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:sellingPlanGroupDelete` | `shopify-admin-api-tool mutation selling-plan-group-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:sellingPlanGroupRemoveProductVariants` | `shopify-admin-api-tool mutation selling-plan-group-remove-product-variants` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:sellingPlanGroupRemoveProducts` | `shopify-admin-api-tool mutation selling-plan-group-remove-products` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:sellingPlanGroupUpdate` | `shopify-admin-api-tool mutation selling-plan-group-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:serverPixelCreate` | `shopify-admin-api-tool mutation server-pixel-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:serverPixelDelete` | `shopify-admin-api-tool mutation server-pixel-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shippingPackageDelete` | `shopify-admin-api-tool mutation shipping-package-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shippingPackageMakeDefault` | `shopify-admin-api-tool mutation shipping-package-make-default` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shippingPackageUpdate` | `shopify-admin-api-tool mutation shipping-package-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shopLocaleDisable` | `shopify-admin-api-tool mutation shop-locale-disable` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shopLocaleEnable` | `shopify-admin-api-tool mutation shop-locale-enable` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shopLocaleUpdate` | `shopify-admin-api-tool mutation shop-locale-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shopPolicyUpdate` | `shopify-admin-api-tool mutation shop-policy-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shopResourceFeedbackCreate` | `shopify-admin-api-tool mutation shop-resource-feedback-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:shopifyPaymentsPayoutAlternateCurrencyCreate` | `shopify-admin-api-tool mutation shopify-payments-payout-alternate-currency-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:stagedUploadTargetGenerate` | `shopify-admin-api-tool mutation staged-upload-target-generate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:stagedUploadTargetsGenerate` | `shopify-admin-api-tool mutation staged-upload-targets-generate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:stagedUploadsCreate` | `shopify-admin-api-tool mutation staged-uploads-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:standardMetafieldDefinitionEnable` | `shopify-admin-api-tool mutation standard-metafield-definition-enable` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:standardMetaobjectDefinitionEnable` | `shopify-admin-api-tool mutation standard-metaobject-definition-enable` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:storeCreditAccountCredit` | `shopify-admin-api-tool mutation store-credit-account-credit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:storeCreditAccountDebit` | `shopify-admin-api-tool mutation store-credit-account-debit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:storefrontAccessTokenCreate` | `shopify-admin-api-tool mutation storefront-access-token-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:storefrontAccessTokenDelete` | `shopify-admin-api-tool mutation storefront-access-token-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingAttemptCreate` | `shopify-admin-api-tool mutation subscription-billing-attempt-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleBulkCharge` | `shopify-admin-api-tool mutation subscription-billing-cycle-bulk-charge` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleBulkSearch` | `shopify-admin-api-tool mutation subscription-billing-cycle-bulk-search` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleCharge` | `shopify-admin-api-tool mutation subscription-billing-cycle-charge` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleContractDraftCommit` | `shopify-admin-api-tool mutation subscription-billing-cycle-contract-draft-commit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleContractDraftConcatenate` | `shopify-admin-api-tool mutation subscription-billing-cycle-contract-draft-concatenate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleContractEdit` | `shopify-admin-api-tool mutation subscription-billing-cycle-contract-edit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleEditDelete` | `shopify-admin-api-tool mutation subscription-billing-cycle-edit-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleEditsDelete` | `shopify-admin-api-tool mutation subscription-billing-cycle-edits-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleScheduleEdit` | `shopify-admin-api-tool mutation subscription-billing-cycle-schedule-edit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleSkip` | `shopify-admin-api-tool mutation subscription-billing-cycle-skip` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionBillingCycleUnskip` | `shopify-admin-api-tool mutation subscription-billing-cycle-unskip` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractActivate` | `shopify-admin-api-tool mutation subscription-contract-activate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractAtomicCreate` | `shopify-admin-api-tool mutation subscription-contract-atomic-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractCancel` | `shopify-admin-api-tool mutation subscription-contract-cancel` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractCreate` | `shopify-admin-api-tool mutation subscription-contract-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractExpire` | `shopify-admin-api-tool mutation subscription-contract-expire` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractFail` | `shopify-admin-api-tool mutation subscription-contract-fail` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractPause` | `shopify-admin-api-tool mutation subscription-contract-pause` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractProductChange` | `shopify-admin-api-tool mutation subscription-contract-product-change` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractSetNextBillingDate` | `shopify-admin-api-tool mutation subscription-contract-set-next-billing-date` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionContractUpdate` | `shopify-admin-api-tool mutation subscription-contract-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftCommit` | `shopify-admin-api-tool mutation subscription-draft-commit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftDiscountAdd` | `shopify-admin-api-tool mutation subscription-draft-discount-add` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftDiscountCodeApply` | `shopify-admin-api-tool mutation subscription-draft-discount-code-apply` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftDiscountRemove` | `shopify-admin-api-tool mutation subscription-draft-discount-remove` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftDiscountUpdate` | `shopify-admin-api-tool mutation subscription-draft-discount-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftFreeShippingDiscountAdd` | `shopify-admin-api-tool mutation subscription-draft-free-shipping-discount-add` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftFreeShippingDiscountUpdate` | `shopify-admin-api-tool mutation subscription-draft-free-shipping-discount-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftLineAdd` | `shopify-admin-api-tool mutation subscription-draft-line-add` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftLineRemove` | `shopify-admin-api-tool mutation subscription-draft-line-remove` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftLineUpdate` | `shopify-admin-api-tool mutation subscription-draft-line-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:subscriptionDraftUpdate` | `shopify-admin-api-tool mutation subscription-draft-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:tagsAdd` | `shopify-admin-api-tool mutation tags-add` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:tagsRemove` | `shopify-admin-api-tool mutation tags-remove` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:taxAppConfigure` | `shopify-admin-api-tool mutation tax-app-configure` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:taxSummaryCreate` | `shopify-admin-api-tool mutation tax-summary-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:themeCreate` | `shopify-admin-api-tool mutation theme-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:themeDelete` | `shopify-admin-api-tool mutation theme-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:themeDuplicate` | `shopify-admin-api-tool mutation theme-duplicate` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:themeFilesCopy` | `shopify-admin-api-tool mutation theme-files-copy` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:themeFilesDelete` | `shopify-admin-api-tool mutation theme-files-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:themeFilesUpsert` | `shopify-admin-api-tool mutation theme-files-upsert` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:themePublish` | `shopify-admin-api-tool mutation theme-publish` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:themeUpdate` | `shopify-admin-api-tool mutation theme-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:transactionVoid` | `shopify-admin-api-tool mutation transaction-void` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:translationsRegister` | `shopify-admin-api-tool mutation translations-register` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:translationsRemove` | `shopify-admin-api-tool mutation translations-remove` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectBulkDeleteAll` | `shopify-admin-api-tool mutation url-redirect-bulk-delete-all` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectBulkDeleteByIds` | `shopify-admin-api-tool mutation url-redirect-bulk-delete-by-ids` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectBulkDeleteBySavedSearch` | `shopify-admin-api-tool mutation url-redirect-bulk-delete-by-saved-search` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectBulkDeleteBySearch` | `shopify-admin-api-tool mutation url-redirect-bulk-delete-by-search` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectCreate` | `shopify-admin-api-tool mutation url-redirect-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectDelete` | `shopify-admin-api-tool mutation url-redirect-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectImportCreate` | `shopify-admin-api-tool mutation url-redirect-import-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectImportSubmit` | `shopify-admin-api-tool mutation url-redirect-import-submit` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:urlRedirectUpdate` | `shopify-admin-api-tool mutation url-redirect-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:validationCreate` | `shopify-admin-api-tool mutation validation-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:validationDelete` | `shopify-admin-api-tool mutation validation-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:validationUpdate` | `shopify-admin-api-tool mutation validation-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webPixelCreate` | `shopify-admin-api-tool mutation web-pixel-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webPixelDelete` | `shopify-admin-api-tool mutation web-pixel-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webPixelUpdate` | `shopify-admin-api-tool mutation web-pixel-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webPresenceCreate` | `shopify-admin-api-tool mutation web-presence-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webPresenceDelete` | `shopify-admin-api-tool mutation web-presence-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webPresenceUpdate` | `shopify-admin-api-tool mutation web-presence-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webhookSubscriptionCreate` | `shopify-admin-api-tool mutation webhook-subscription-create` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webhookSubscriptionDelete` | `shopify-admin-api-tool mutation webhook-subscription-delete` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `mutation:webhookSubscriptionUpdate` | `shopify-admin-api-tool mutation webhook-subscription-update` | plan first; live apply needs the mutation risk flags plus `--ack-no-snapshot` when no saved snapshot is available (see `docs/safety_model.md`) |
| `query:abandonedCheckouts` | `shopify-admin-api-tool query abandoned-checkouts` | read-only |
| `query:abandonedCheckoutsCount` | `shopify-admin-api-tool query abandoned-checkouts-count` | read-only |
| `query:abandonment` | `shopify-admin-api-tool query abandonment` | read-only |
| `query:abandonmentByAbandonedCheckoutId` | `shopify-admin-api-tool query abandonment-by-abandoned-checkout-id` | read-only |
| `query:app` | `shopify-admin-api-tool query app` | read-only |
| `query:appByHandle` | `shopify-admin-api-tool query app-by-handle` | read-only |
| `query:appByKey` | `shopify-admin-api-tool query app-by-key` | read-only |
| `query:appDiscountType` | `shopify-admin-api-tool query app-discount-type` | read-only |
| `query:appDiscountTypes` | `shopify-admin-api-tool query app-discount-types` | read-only |
| `query:appDiscountTypesNodes` | `shopify-admin-api-tool query app-discount-types-nodes` | read-only |
| `query:appInstallation` | `shopify-admin-api-tool query app-installation` | read-only |
| `query:appInstallations` | `shopify-admin-api-tool query app-installations` | read-only |
| `query:article` | `shopify-admin-api-tool query article` | read-only |
| `query:articleAuthors` | `shopify-admin-api-tool query article-authors` | read-only |
| `query:articleTags` | `shopify-admin-api-tool query article-tags` | read-only |
| `query:articles` | `shopify-admin-api-tool query articles` | read-only |
| `query:assignedFulfillmentOrders` | `shopify-admin-api-tool query assigned-fulfillment-orders` | read-only |
| `query:automaticDiscount` | `shopify-admin-api-tool query automatic-discount` | read-only |
| `query:automaticDiscountNode` | `shopify-admin-api-tool query automatic-discount-node` | read-only |
| `query:automaticDiscountNodes` | `shopify-admin-api-tool query automatic-discount-nodes` | read-only |
| `query:automaticDiscountSavedSearches` | `shopify-admin-api-tool query automatic-discount-saved-searches` | read-only |
| `query:automaticDiscounts` | `shopify-admin-api-tool query automatic-discounts` | read-only |
| `query:availableBackupRegions` | `shopify-admin-api-tool query available-backup-regions` | read-only |
| `query:availableCarrierServices` | `shopify-admin-api-tool query available-carrier-services` | read-only |
| `query:availableLocales` | `shopify-admin-api-tool query available-locales` | read-only |
| `query:backupRegion` | `shopify-admin-api-tool query backup-region` | read-only |
| `query:blog` | `shopify-admin-api-tool query blog` | read-only |
| `query:blogs` | `shopify-admin-api-tool query blogs` | read-only |
| `query:blogsCount` | `shopify-admin-api-tool query blogs-count` | read-only |
| `query:bulkOperation` | `shopify-admin-api-tool query bulk-operation` | read-only |
| `query:bulkOperations` | `shopify-admin-api-tool query bulk-operations` | read-only |
| `query:businessEntities` | `shopify-admin-api-tool query business-entities` | read-only |
| `query:businessEntity` | `shopify-admin-api-tool query business-entity` | read-only |
| `query:carrierService` | `shopify-admin-api-tool query carrier-service` | read-only |
| `query:carrierServices` | `shopify-admin-api-tool query carrier-services` | read-only |
| `query:cartTransforms` | `shopify-admin-api-tool query cart-transforms` | read-only |
| `query:cashTrackingSession` | `shopify-admin-api-tool query cash-tracking-session` | read-only |
| `query:cashTrackingSessions` | `shopify-admin-api-tool query cash-tracking-sessions` | read-only |
| `query:catalog` | `shopify-admin-api-tool query catalog` | read-only |
| `query:catalogOperations` | `shopify-admin-api-tool query catalog-operations` | read-only |
| `query:catalogs` | `shopify-admin-api-tool query catalogs` | read-only |
| `query:catalogsCount` | `shopify-admin-api-tool query catalogs-count` | read-only |
| `query:channel` | `shopify-admin-api-tool query channel` | read-only |
| `query:channels` | `shopify-admin-api-tool query channels` | read-only |
| `query:checkoutBranding` | `shopify-admin-api-tool query checkout-branding` | read-only |
| `query:checkoutProfile` | `shopify-admin-api-tool query checkout-profile` | read-only |
| `query:checkoutProfiles` | `shopify-admin-api-tool query checkout-profiles` | read-only |
| `query:codeDiscountNode` | `shopify-admin-api-tool query code-discount-node` | read-only |
| `query:codeDiscountNodeByCode` | `shopify-admin-api-tool query code-discount-node-by-code` | read-only |
| `query:codeDiscountNodes` | `shopify-admin-api-tool query code-discount-nodes` | read-only |
| `query:codeDiscountSavedSearches` | `shopify-admin-api-tool query code-discount-saved-searches` | read-only |
| `query:collection` | `shopify-admin-api-tool query collection` | read-only |
| `query:collectionByHandle` | `shopify-admin-api-tool query collection-by-handle` | read-only |
| `query:collectionByIdentifier` | `shopify-admin-api-tool query collection-by-identifier` | read-only |
| `query:collectionRulesConditions` | `shopify-admin-api-tool query collection-rules-conditions` | read-only |
| `query:collectionSavedSearches` | `shopify-admin-api-tool query collection-saved-searches` | read-only |
| `query:collections` | `shopify-admin-api-tool query collections` | read-only |
| `query:collectionsCount` | `shopify-admin-api-tool query collections-count` | read-only |
| `query:comment` | `shopify-admin-api-tool query comment` | read-only |
| `query:comments` | `shopify-admin-api-tool query comments` | read-only |
| `query:companies` | `shopify-admin-api-tool query companies` | read-only |
| `query:companiesCount` | `shopify-admin-api-tool query companies-count` | read-only |
| `query:company` | `shopify-admin-api-tool query company` | read-only |
| `query:companyContact` | `shopify-admin-api-tool query company-contact` | read-only |
| `query:companyContactRole` | `shopify-admin-api-tool query company-contact-role` | read-only |
| `query:companyLocation` | `shopify-admin-api-tool query company-location` | read-only |
| `query:companyLocations` | `shopify-admin-api-tool query company-locations` | read-only |
| `query:consentPolicy` | `shopify-admin-api-tool query consent-policy` | read-only |
| `query:consentPolicyRegions` | `shopify-admin-api-tool query consent-policy-regions` | read-only |
| `query:currentAppInstallation` | `shopify-admin-api-tool query current-app-installation` | read-only |
| `query:currentBulkOperation` | `shopify-admin-api-tool query current-bulk-operation` | read-only |
| `query:currentStaffMember` | `shopify-admin-api-tool query current-staff-member` | read-only |
| `query:customer` | `shopify-admin-api-tool query customer` | read-only |
| `query:customerAccountPage` | `shopify-admin-api-tool query customer-account-page` | read-only |
| `query:customerAccountPages` | `shopify-admin-api-tool query customer-account-pages` | read-only |
| `query:customerByIdentifier` | `shopify-admin-api-tool query customer-by-identifier` | read-only |
| `query:customerMergeJobStatus` | `shopify-admin-api-tool query customer-merge-job-status` | read-only |
| `query:customerMergePreview` | `shopify-admin-api-tool query customer-merge-preview` | read-only |
| `query:customerPaymentMethod` | `shopify-admin-api-tool query customer-payment-method` | read-only |
| `query:customerSavedSearches` | `shopify-admin-api-tool query customer-saved-searches` | read-only |
| `query:customerSegmentMembers` | `shopify-admin-api-tool query customer-segment-members` | read-only |
| `query:customerSegmentMembersQuery` | `shopify-admin-api-tool query customer-segment-members-query` | read-only |
| `query:customerSegmentMembership` | `shopify-admin-api-tool query customer-segment-membership` | read-only |
| `query:customers` | `shopify-admin-api-tool query customers` | read-only |
| `query:customersCount` | `shopify-admin-api-tool query customers-count` | read-only |
| `query:deletionEvents` | `shopify-admin-api-tool query deletion-events` | read-only |
| `query:deliveryCustomization` | `shopify-admin-api-tool query delivery-customization` | read-only |
| `query:deliveryCustomizations` | `shopify-admin-api-tool query delivery-customizations` | read-only |
| `query:deliveryProfile` | `shopify-admin-api-tool query delivery-profile` | read-only |
| `query:deliveryProfiles` | `shopify-admin-api-tool query delivery-profiles` | read-only |
| `query:deliveryPromiseParticipants` | `shopify-admin-api-tool query delivery-promise-participants` | read-only |
| `query:deliveryPromiseProvider` | `shopify-admin-api-tool query delivery-promise-provider` | read-only |
| `query:deliveryPromiseSettings` | `shopify-admin-api-tool query delivery-promise-settings` | read-only |
| `query:deliverySettings` | `shopify-admin-api-tool query delivery-settings` | read-only |
| `query:discountCodesCount` | `shopify-admin-api-tool query discount-codes-count` | read-only |
| `query:discountNode` | `shopify-admin-api-tool query discount-node` | read-only |
| `query:discountNodes` | `shopify-admin-api-tool query discount-nodes` | read-only |
| `query:discountNodesCount` | `shopify-admin-api-tool query discount-nodes-count` | read-only |
| `query:discountRedeemCodeBulkCreation` | `shopify-admin-api-tool query discount-redeem-code-bulk-creation` | read-only |
| `query:discountRedeemCodeSavedSearches` | `shopify-admin-api-tool query discount-redeem-code-saved-searches` | read-only |
| `query:dispute` | `shopify-admin-api-tool query dispute` | read-only |
| `query:disputeEvidence` | `shopify-admin-api-tool query dispute-evidence` | read-only |
| `query:disputes` | `shopify-admin-api-tool query disputes` | read-only |
| `query:domain` | `shopify-admin-api-tool query domain` | read-only |
| `query:draftOrder` | `shopify-admin-api-tool query draft-order` | read-only |
| `query:draftOrderAvailableDeliveryOptions` | `shopify-admin-api-tool query draft-order-available-delivery-options` | read-only |
| `query:draftOrderSavedSearches` | `shopify-admin-api-tool query draft-order-saved-searches` | read-only |
| `query:draftOrderTag` | `shopify-admin-api-tool query draft-order-tag` | read-only |
| `query:draftOrders` | `shopify-admin-api-tool query draft-orders` | read-only |
| `query:draftOrdersCount` | `shopify-admin-api-tool query draft-orders-count` | read-only |
| `query:event` | `shopify-admin-api-tool query event` | read-only |
| `query:events` | `shopify-admin-api-tool query events` | read-only |
| `query:eventsCount` | `shopify-admin-api-tool query events-count` | read-only |
| `query:fileSavedSearches` | `shopify-admin-api-tool query file-saved-searches` | read-only |
| `query:files` | `shopify-admin-api-tool query files` | read-only |
| `query:financeAppAccessPolicy` | `shopify-admin-api-tool query finance-app-access-policy` | read-only |
| `query:financeKycInformation` | `shopify-admin-api-tool query finance-kyc-information` | read-only |
| `query:fulfillment` | `shopify-admin-api-tool query fulfillment` | read-only |
| `query:fulfillmentConstraintRules` | `shopify-admin-api-tool query fulfillment-constraint-rules` | read-only |
| `query:fulfillmentOrder` | `shopify-admin-api-tool query fulfillment-order` | read-only |
| `query:fulfillmentOrders` | `shopify-admin-api-tool query fulfillment-orders` | read-only |
| `query:fulfillmentService` | `shopify-admin-api-tool query fulfillment-service` | read-only |
| `query:giftCard` | `shopify-admin-api-tool query gift-card` | read-only |
| `query:giftCardConfiguration` | `shopify-admin-api-tool query gift-card-configuration` | read-only |
| `query:giftCards` | `shopify-admin-api-tool query gift-cards` | read-only |
| `query:giftCardsCount` | `shopify-admin-api-tool query gift-cards-count` | read-only |
| `query:inventoryItem` | `shopify-admin-api-tool query inventory-item` | read-only |
| `query:inventoryItems` | `shopify-admin-api-tool query inventory-items` | read-only |
| `query:inventoryLevel` | `shopify-admin-api-tool query inventory-level` | read-only |
| `query:inventoryProperties` | `shopify-admin-api-tool query inventory-properties` | read-only |
| `query:inventoryShipment` | `shopify-admin-api-tool query inventory-shipment` | read-only |
| `query:inventoryTransfer` | `shopify-admin-api-tool query inventory-transfer` | read-only |
| `query:inventoryTransfers` | `shopify-admin-api-tool query inventory-transfers` | read-only |
| `query:job` | `shopify-admin-api-tool query job` | read-only |
| `query:location` | `shopify-admin-api-tool query location` | read-only |
| `query:locationByIdentifier` | `shopify-admin-api-tool query location-by-identifier` | read-only |
| `query:locations` | `shopify-admin-api-tool query locations` | read-only |
| `query:locationsAvailableForDeliveryProfiles` | `shopify-admin-api-tool query locations-available-for-delivery-profiles` | read-only |
| `query:locationsAvailableForDeliveryProfilesConnection` | `shopify-admin-api-tool query locations-available-for-delivery-profiles-connection` | read-only |
| `query:locationsCount` | `shopify-admin-api-tool query locations-count` | read-only |
| `query:manualHoldsFulfillmentOrders` | `shopify-admin-api-tool query manual-holds-fulfillment-orders` | read-only |
| `query:market` | `shopify-admin-api-tool query market` | read-only |
| `query:marketByGeography` | `shopify-admin-api-tool query market-by-geography` | read-only |
| `query:marketLocalizableResource` | `shopify-admin-api-tool query market-localizable-resource` | read-only |
| `query:marketLocalizableResources` | `shopify-admin-api-tool query market-localizable-resources` | read-only |
| `query:marketLocalizableResourcesByIds` | `shopify-admin-api-tool query market-localizable-resources-by-ids` | read-only |
| `query:marketingActivities` | `shopify-admin-api-tool query marketing-activities` | read-only |
| `query:marketingActivity` | `shopify-admin-api-tool query marketing-activity` | read-only |
| `query:marketingEvent` | `shopify-admin-api-tool query marketing-event` | read-only |
| `query:marketingEvents` | `shopify-admin-api-tool query marketing-events` | read-only |
| `query:markets` | `shopify-admin-api-tool query markets` | read-only |
| `query:marketsResolvedValues` | `shopify-admin-api-tool query markets-resolved-values` | read-only |
| `query:menu` | `shopify-admin-api-tool query menu` | read-only |
| `query:menus` | `shopify-admin-api-tool query menus` | read-only |
| `query:metafieldDefinition` | `shopify-admin-api-tool query metafield-definition` | read-only |
| `query:metafieldDefinitionTypes` | `shopify-admin-api-tool query metafield-definition-types` | read-only |
| `query:metafieldDefinitions` | `shopify-admin-api-tool query metafield-definitions` | read-only |
| `query:metaobject` | `shopify-admin-api-tool query metaobject` | read-only |
| `query:metaobjectByHandle` | `shopify-admin-api-tool query metaobject-by-handle` | read-only |
| `query:metaobjectDefinition` | `shopify-admin-api-tool query metaobject-definition` | read-only |
| `query:metaobjectDefinitionByType` | `shopify-admin-api-tool query metaobject-definition-by-type` | read-only |
| `query:metaobjectDefinitions` | `shopify-admin-api-tool query metaobject-definitions` | read-only |
| `query:metaobjects` | `shopify-admin-api-tool query metaobjects` | read-only |
| `query:mobilePlatformApplication` | `shopify-admin-api-tool query mobile-platform-application` | read-only |
| `query:mobilePlatformApplications` | `shopify-admin-api-tool query mobile-platform-applications` | read-only |
| `query:node` | `shopify-admin-api-tool query node` | read-only |
| `query:nodes` | `shopify-admin-api-tool query nodes` | read-only |
| `query:onlineStore` | `shopify-admin-api-tool query online-store` | read-only |
| `query:order` | `shopify-admin-api-tool query order` | read-only |
| `query:orderByIdentifier` | `shopify-admin-api-tool query order-by-identifier` | read-only |
| `query:orderEditSession` | `shopify-admin-api-tool query order-edit-session` | read-only |
| `query:orderPaymentStatus` | `shopify-admin-api-tool query order-payment-status` | read-only |
| `query:orderSavedSearches` | `shopify-admin-api-tool query order-saved-searches` | read-only |
| `query:orders` | `shopify-admin-api-tool query orders` | read-only |
| `query:ordersCount` | `shopify-admin-api-tool query orders-count` | read-only |
| `query:page` | `shopify-admin-api-tool query page` | read-only |
| `query:pages` | `shopify-admin-api-tool query pages` | read-only |
| `query:pagesCount` | `shopify-admin-api-tool query pages-count` | read-only |
| `query:paymentCustomization` | `shopify-admin-api-tool query payment-customization` | read-only |
| `query:paymentCustomizations` | `shopify-admin-api-tool query payment-customizations` | read-only |
| `query:paymentTermsTemplates` | `shopify-admin-api-tool query payment-terms-templates` | read-only |
| `query:pendingOrdersCount` | `shopify-admin-api-tool query pending-orders-count` | read-only |
| `query:pointOfSaleDevice` | `shopify-admin-api-tool query point-of-sale-device` | read-only |
| `query:priceList` | `shopify-admin-api-tool query price-list` | read-only |
| `query:priceLists` | `shopify-admin-api-tool query price-lists` | read-only |
| `query:primaryMarket` | `shopify-admin-api-tool query primary-market` | read-only |
| `query:privacySettings` | `shopify-admin-api-tool query privacy-settings` | read-only |
| `query:product` | `shopify-admin-api-tool query product` | read-only |
| `query:productByHandle` | `shopify-admin-api-tool query product-by-handle` | read-only |
| `query:productByIdentifier` | `shopify-admin-api-tool query product-by-identifier` | read-only |
| `query:productDuplicateJob` | `shopify-admin-api-tool query product-duplicate-job` | read-only |
| `query:productFeed` | `shopify-admin-api-tool query product-feed` | read-only |
| `query:productFeeds` | `shopify-admin-api-tool query product-feeds` | read-only |
| `query:productOperation` | `shopify-admin-api-tool query product-operation` | read-only |
| `query:productResourceFeedback` | `shopify-admin-api-tool query product-resource-feedback` | read-only |
| `query:productSavedSearches` | `shopify-admin-api-tool query product-saved-searches` | read-only |
| `query:productTags` | `shopify-admin-api-tool query product-tags` | read-only |
| `query:productTypes` | `shopify-admin-api-tool query product-types` | read-only |
| `query:productVariant` | `shopify-admin-api-tool query product-variant` | read-only |
| `query:productVariantByIdentifier` | `shopify-admin-api-tool query product-variant-by-identifier` | read-only |
| `query:productVariants` | `shopify-admin-api-tool query product-variants` | read-only |
| `query:productVariantsCount` | `shopify-admin-api-tool query product-variants-count` | read-only |
| `query:productVendors` | `shopify-admin-api-tool query product-vendors` | read-only |
| `query:products` | `shopify-admin-api-tool query products` | read-only |
| `query:productsCount` | `shopify-admin-api-tool query products-count` | read-only |
| `query:publicApiVersions` | `shopify-admin-api-tool query public-api-versions` | read-only |
| `query:publication` | `shopify-admin-api-tool query publication` | read-only |
| `query:publications` | `shopify-admin-api-tool query publications` | read-only |
| `query:publicationsCount` | `shopify-admin-api-tool query publications-count` | read-only |
| `query:publishedProductsCount` | `shopify-admin-api-tool query published-products-count` | read-only |
| `query:refund` | `shopify-admin-api-tool query refund` | read-only |
| `query:return` | `shopify-admin-api-tool query return` | read-only |
| `query:returnCalculate` | `shopify-admin-api-tool query return-calculate` | read-only |
| `query:returnReasonDefinitions` | `shopify-admin-api-tool query return-reason-definitions` | read-only |
| `query:returnableFulfillment` | `shopify-admin-api-tool query returnable-fulfillment` | read-only |
| `query:returnableFulfillments` | `shopify-admin-api-tool query returnable-fulfillments` | read-only |
| `query:reverseDelivery` | `shopify-admin-api-tool query reverse-delivery` | read-only |
| `query:reverseFulfillmentOrder` | `shopify-admin-api-tool query reverse-fulfillment-order` | read-only |
| `query:scriptTag` | `shopify-admin-api-tool query script-tag` | read-only |
| `query:scriptTags` | `shopify-admin-api-tool query script-tags` | read-only |
| `query:segment` | `shopify-admin-api-tool query segment` | read-only |
| `query:segmentFilterSuggestions` | `shopify-admin-api-tool query segment-filter-suggestions` | read-only |
| `query:segmentFilters` | `shopify-admin-api-tool query segment-filters` | read-only |
| `query:segmentMigrations` | `shopify-admin-api-tool query segment-migrations` | read-only |
| `query:segmentValueSuggestions` | `shopify-admin-api-tool query segment-value-suggestions` | read-only |
| `query:segments` | `shopify-admin-api-tool query segments` | read-only |
| `query:segmentsCount` | `shopify-admin-api-tool query segments-count` | read-only |
| `query:sellingPlanGroup` | `shopify-admin-api-tool query selling-plan-group` | read-only |
| `query:sellingPlanGroups` | `shopify-admin-api-tool query selling-plan-groups` | read-only |
| `query:serverPixel` | `shopify-admin-api-tool query server-pixel` | read-only |
| `query:shop` | `shopify-admin-api-tool query shop` | read-only |
| `query:shopBillingPreferences` | `shopify-admin-api-tool query shop-billing-preferences` | read-only |
| `query:shopLocales` | `shopify-admin-api-tool query shop-locales` | read-only |
| `query:shopPayPaymentRequestReceipt` | `shopify-admin-api-tool query shop-pay-payment-request-receipt` | read-only |
| `query:shopPayPaymentRequestReceipts` | `shopify-admin-api-tool query shop-pay-payment-request-receipts` | read-only |
| `query:shopifyFunction` | `shopify-admin-api-tool query shopify-function` | read-only |
| `query:shopifyFunctions` | `shopify-admin-api-tool query shopify-functions` | read-only |
| `query:shopifyPaymentsAccount` | `shopify-admin-api-tool query shopify-payments-account` | read-only |
| `query:shopifyqlQuery` | `shopify-admin-api-tool query shopifyql-query` | read-only |
| `query:staffMember` | `shopify-admin-api-tool query staff-member` | read-only |
| `query:staffMembers` | `shopify-admin-api-tool query staff-members` | read-only |
| `query:standardMetafieldDefinitionTemplates` | `shopify-admin-api-tool query standard-metafield-definition-templates` | read-only |
| `query:storeCreditAccount` | `shopify-admin-api-tool query store-credit-account` | read-only |
| `query:subscriptionBillingAttempt` | `shopify-admin-api-tool query subscription-billing-attempt` | read-only |
| `query:subscriptionBillingAttempts` | `shopify-admin-api-tool query subscription-billing-attempts` | read-only |
| `query:subscriptionBillingCycle` | `shopify-admin-api-tool query subscription-billing-cycle` | read-only |
| `query:subscriptionBillingCycleBulkResults` | `shopify-admin-api-tool query subscription-billing-cycle-bulk-results` | read-only |
| `query:subscriptionBillingCycles` | `shopify-admin-api-tool query subscription-billing-cycles` | read-only |
| `query:subscriptionContract` | `shopify-admin-api-tool query subscription-contract` | read-only |
| `query:subscriptionContracts` | `shopify-admin-api-tool query subscription-contracts` | read-only |
| `query:subscriptionDraft` | `shopify-admin-api-tool query subscription-draft` | read-only |
| `query:taxonomy` | `shopify-admin-api-tool query taxonomy` | read-only |
| `query:tenderTransactions` | `shopify-admin-api-tool query tender-transactions` | read-only |
| `query:theme` | `shopify-admin-api-tool query theme` | read-only |
| `query:themes` | `shopify-admin-api-tool query themes` | read-only |
| `query:translatableResource` | `shopify-admin-api-tool query translatable-resource` | read-only |
| `query:translatableResources` | `shopify-admin-api-tool query translatable-resources` | read-only |
| `query:translatableResourcesByIds` | `shopify-admin-api-tool query translatable-resources-by-ids` | read-only |
| `query:urlRedirect` | `shopify-admin-api-tool query url-redirect` | read-only |
| `query:urlRedirectImport` | `shopify-admin-api-tool query url-redirect-import` | read-only |
| `query:urlRedirectSavedSearches` | `shopify-admin-api-tool query url-redirect-saved-searches` | read-only |
| `query:urlRedirects` | `shopify-admin-api-tool query url-redirects` | read-only |
| `query:urlRedirectsCount` | `shopify-admin-api-tool query url-redirects-count` | read-only |
| `query:validation` | `shopify-admin-api-tool query validation` | read-only |
| `query:validations` | `shopify-admin-api-tool query validations` | read-only |
| `query:webPixel` | `shopify-admin-api-tool query web-pixel` | read-only |
| `query:webPresences` | `shopify-admin-api-tool query web-presences` | read-only |
| `query:webhookSubscription` | `shopify-admin-api-tool query webhook-subscription` | read-only |
| `query:webhookSubscriptions` | `shopify-admin-api-tool query webhook-subscriptions` | read-only |
| `query:webhookSubscriptionsCount` | `shopify-admin-api-tool query webhook-subscriptions-count` | read-only |
