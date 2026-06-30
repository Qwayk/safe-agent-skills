from __future__ import annotations

import unittest
import argparse
from pathlib import Path

from wix_safe_agent_cli.cli import build_parser


class TestWixSkillWrapper(unittest.TestCase):
    @staticmethod
    def _skill_path(root: Path) -> Path:
        candidates = [
            root / "skills" / "wix" / "SKILL.md",
            root / "SKILL.md",
        ]
        for path in candidates:
            if path.exists():
                return path
        raise AssertionError("Missing shipped wrapper file at skills/wix/SKILL.md or SKILL.md")

    @classmethod
    def _skill_text(cls, root: Path) -> str:
        return cls._skill_path(root).read_text(encoding="utf-8")

    @staticmethod
    def _expected_command_names() -> list[str]:
        return [
            "onboarding",
            "auth check",
            "auth token create",
            "auth token request",
            "auth token refresh",
            "auth token inspect",
            "auth token set",
            "auth token status",
            "runs list",
            "runs show",
            "contacts list",
            "contacts get",
            "contacts query",
            "contacts list-facets",
            "contacts query-facets",
            "contacts get-bulk-job",
            "contacts preview-merge",
            "contacts create",
            "contacts update",
            "contacts delete",
            "contacts merge",
            "contacts label",
            "contacts unlabel",
            "contacts bulk-delete",
            "contacts bulk-update",
            "contacts bulk-label-unlabel",
            "form-schemas list",
            "form-schemas get",
            "form-schemas query",
            "form-schemas count",
            "form-schemas get-deleted",
            "form-schemas list-deleted",
            "form-schemas query-deleted",
            "form-schemas count-deleted",
            "form-schemas list-providers-configs",
            "form-schemas get-summary",
            "form-schemas create",
            "form-schemas bulk-create",
            "form-schemas update",
            "form-schemas clone",
            "form-schemas bulk-clone",
            "form-schemas delete",
            "form-schemas bulk-delete",
            "form-schemas restore",
            "form-schemas remove-from-trash",
            "form-schemas bulk-remove-deleted-field",
            "chat-settings get",
            "chat-settings query",
            "chat-settings create",
            "chat-settings update",
            "chat-settings delete",
            "interactive-form-sessions create",
            "interactive-form-sessions create-streamed",
            "interactive-form-sessions send-message",
            "interactive-form-sessions send-message-streamed",
            "interactive-form-sessions generate-summary",
            "intake-forms query",
            "intake-forms create-customer-submission-link",
            "intake-forms archive",
            "intake-forms unarchive",
            "intake-forms update-expiration-period",
            "intake-forms delete",
            "intake-form-submissions query",
            "intake-form-submissions search",
            "intake-form-submissions count-by-intake-form-ids",
            "intake-form-submissions list-data-by-contacts",
            "intake-form-submissions cancel",
            "intake-form-submissions extend",
            "intake-form-submissions exempt",
            "intake-form-submissions delete",
            "community-groups list",
            "community-groups get",
            "community-groups get-by-slug",
            "community-groups query",
            "community-groups create",
            "community-groups update",
            "community-groups delete",
            "community-group-rules list",
            "community-group-rules create-or-replace",
            "community-group-requests list",
            "community-group-requests query",
            "community-group-requests approve",
            "community-group-requests reject",
            "community-group-members list",
            "community-group-members list-memberships",
            "community-group-members query",
            "community-group-members query-memberships",
            "community-group-members add",
            "community-group-members remove",
            "community-group-roles assign",
            "community-group-roles unassign",
            "community-join-requests list",
            "community-join-requests query",
            "community-join-requests approve",
            "community-join-requests reject",
            "community-membership-questions list",
            "community-membership-questions list-answers",
            "community-membership-questions create-or-replace",
            "community-comments create",
            "community-comments get",
            "community-comments update",
            "community-comments delete",
            "community-comments moderate-draft-content",
            "community-comments query",
            "community-comments mark",
            "community-comments unmark",
            "community-comments hide",
            "community-comments publish",
            "community-comments count",
            "community-comments list-by-resource",
            "community-comments get-thread",
            "community-comments bulk-publish",
            "community-comments bulk-hide",
            "community-comments bulk-delete",
            "community-comments bulk-moderate-draft-content",
            "community-comments bulk-move-by-filter",
            "community-reports get",
            "community-reports query",
            "community-reports count-by-reason-types",
            "community-reports create",
            "community-reports update",
            "community-reports upsert",
            "community-reports delete",
            "community-reports bulk-delete-by-filter",
            "community-reviews get",
            "community-reviews query",
            "community-reviews count",
            "community-reviews create",
            "community-reviews update",
            "community-reviews delete",
            "community-reviews bulk-create",
            "community-reviews bulk-delete",
            "community-reviews remove-reply",
            "community-reviews set-reply",
            "community-reviews update-moderation-status",
            "community-reviews bulk-update-moderation-status",
            "community-review-requests create",
            "community-review-requests get",
            "community-review-requests delete",
            "community-review-requests query",
            "community-review-requests count",
            "community-review-requests bulk-cancel-by-filter",
            "community-moderation-rules create",
            "community-moderation-rules get",
            "community-moderation-rules update",
            "community-moderation-rules delete",
            "community-moderation-rules query",
            "community-moderation-rules check-content",
            "inbox-conversations get",
            "inbox-conversations get-or-create",
            "inbox-messages list",
            "inbox-messages send",
            "loyalty-program get",
            "loyalty-program premium-features",
            "loyalty-program update",
            "loyalty-program activate",
            "loyalty-program pause",
            "loyalty-program enable-points-expiration",
            "loyalty-program disable-points-expiration",
            "loyalty-earning-rules list",
            "loyalty-earning-rules get",
            "loyalty-earning-rules create",
            "loyalty-earning-rules update",
            "loyalty-earning-rules delete",
            "loyalty-earning-rules bulk-create",
            "loyalty-earning-rules create-custom",
            "loyalty-earning-rules delete-automation",
            "loyalty-tiers list",
            "loyalty-tiers get",
            "loyalty-tiers create",
            "loyalty-tiers update",
            "loyalty-tiers delete",
            "loyalty-tiers bulk-create",
            "loyalty-tiers get-program",
            "loyalty-tiers create-program-settings",
            "loyalty-tiers get-program-settings",
            "loyalty-tiers update-program-settings",
            "loyalty-accounts list",
            "loyalty-accounts get",
            "loyalty-accounts query",
            "loyalty-accounts search",
            "loyalty-accounts count",
            "loyalty-accounts get-program-totals",
            "loyalty-accounts get-current-member-account",
            "loyalty-accounts get-by-secondary-id",
            "loyalty-accounts create",
            "loyalty-accounts adjust-points",
            "loyalty-accounts bulk-adjust-points",
            "loyalty-accounts earn-points",
            "loyalty-transactions get",
            "loyalty-transactions query",
            "loyalty-social-media list",
            "loyalty-social-media create",
            "loyalty-imports get",
            "loyalty-imports query",
            "loyalty-imports create-file-url",
            "loyalty-imports create",
            "loyalty-imports execute",
            "loyalty-imports get-error-file-download-url",
            "loyalty-rewards list",
            "loyalty-rewards get",
            "loyalty-rewards query",
            "loyalty-rewards create",
            "loyalty-rewards bulk-create",
            "loyalty-rewards update",
            "loyalty-rewards delete",
            "loyalty-checkout-discounts query",
            "loyalty-checkout-discounts apply",
            "loyalty-coupons get",
            "loyalty-coupons query",
            "loyalty-coupons get-current-member",
            "loyalty-coupons redeem-current-member",
            "loyalty-coupons redeem",
            "loyalty-coupons delete",
            "email-subscriptions query",
            "email-subscriptions upsert",
            "email-subscriptions bulk-upsert",
            "email-subscriptions generate-unsubscribe-link",
            "members list",
            "members get",
            "members query",
            "members get-my",
            "members create",
            "members update",
            "members delete",
            "members delete-my",
            "members bulk-delete",
            "members approve",
            "members block",
            "members mute",
            "members unmute",
            "members disconnect",
            "members delete-addresses",
            "members delete-emails",
            "members delete-phones",
            "members bulk-approve",
            "members bulk-block",
            "members bulk-delete-by-filter",
            "members join-community",
            "members leave-community",
            "members update-member-slug",
            "members update-my-slug",
            "activity-counters get",
            "activity-counters query",
            "activity-counters set",
            "badges-v4 get",
            "badges-v4 query",
            "badges-v4 create",
            "badges-v4 update",
            "badges-v4 delete",
            "badges-v4 move",
            "badge-assignments query",
            "badge-assignments create",
            "badge-assignments delete",
            "badge-assignments bulk-create",
            "badge-assignments bulk-delete",
            "badge-assignments bulk-update-tags",
            "badge-assignments bulk-update-tags-by-filter",
            "member-reports query",
            "member-reports report",
            "member-reports delete",
            "members-followers follow",
            "members-followers unfollow",
            "members-followers list-followers",
            "members-followers list-following",
            "members-followers list-my-followers",
            "members-followers list-my-following",
            "members-followers query-connections",
            "members-followers query-my-connections",
            "user-members query",
            "member-authentication send-set-password-email",
            "member-abouts create",
            "member-abouts get",
            "member-abouts update",
            "member-abouts delete",
            "member-abouts query",
            "member-abouts get-my",
            "member-privacy get-default",
            "member-privacy set-default",
            "member-privacy get-settings",
            "member-privacy set-settings",
            "member-custom-fields create",
            "member-custom-fields update",
            "member-custom-fields delete",
            "member-custom-fields get",
            "member-custom-fields hide",
            "member-custom-fields list",
            "member-custom-fields update-order",
            "member-custom-field-applications create",
            "member-custom-field-applications update",
            "member-custom-field-applications delete",
            "member-custom-field-applications get",
            "member-custom-field-applications list-applications",
            "member-custom-field-applications get-members",
            "member-custom-field-applications get-roles",
            "member-custom-field-suggestions query",
            "member-custom-field-suggestions list",
            "contact-extended-fields get",
            "contact-extended-fields list",
            "contact-extended-fields query",
            "contact-extended-fields find-or-create",
            "contact-extended-fields update",
            "contact-extended-fields delete",
            "contact-notes get",
            "contact-notes query",
            "contact-notes create",
            "contact-notes update",
            "contact-notes delete",
            "contact-attachments get",
            "contact-attachments list",
            "contact-attachments generate-upload-url",
            "contact-attachments delete",
            "crm-tasks create",
            "crm-tasks get",
            "crm-tasks update",
            "crm-tasks delete",
            "crm-tasks query",
            "crm-tasks count",
            "crm-tasks move-after",
            "crm-pipelines create",
            "crm-pipelines get",
            "crm-pipelines update",
            "crm-pipelines delete",
            "crm-pipelines query",
            "crm-pipelines bulk-update-tags",
            "crm-pipelines bulk-update-tags-by-filter",
            "crm-cards create",
            "crm-cards get",
            "crm-cards update",
            "crm-cards delete",
            "crm-cards query",
            "crm-cards search",
            "crm-cards bulk-update-tags",
            "crm-cards bulk-update-tags-by-filter",
            "crm-cards move",
            "crm-cards search-by-stage",
            "ai-site-chat-widget-settings get",
            "ai-site-chat-widget-settings set",
            "ai-site-chat-widget-settings-v2 get",
            "ai-site-chat-widget-settings-v2 update",
            "ai-site-chat-conversations get",
            "ai-site-chat-messages list",
            "ai-site-chat-messages bulk-create",
            "ai-site-chat-messages bulk-get-by-inbox",
            "ai-site-chat-messages media-upload-url",
            "app-installations query",
            "app-installations search",
            "app-installation get-installed",
            "app-installation is-permitted",
            "app-installation install",
            "app-installation install-from-share-url",
            "app-installation uninstall",
            "app-installation bulk-install",
            "app-installation bulk-uninstall",
            "app-instance get",
            "bi-event send",
            "embedded-scripts get",
            "embedded-scripts embed",
            "custom-embeds list",
            "custom-embeds get",
            "custom-embeds create",
            "custom-embeds update",
            "custom-embeds delete",
            "secrets list",
            "secrets get-value",
            "secrets create",
            "secrets patch",
            "secrets delete",
            "sender-emails list",
            "sender-emails get",
            "sender-emails create",
            "sender-emails delete",
            "sender-emails get-or-create",
            "sender-emails send-verification-code",
            "sender-emails verify",
            "sender-details list",
            "sender-details get",
            "sender-details create",
            "sender-details update",
            "sender-details delete",
            "sender-details get-default",
            "sender-details mark-default",
            "sending-domains get",
            "sending-domains query",
            "sending-domains authenticate",
            "marketing-consent get",
            "marketing-consent query",
            "marketing-consent get-by-identifier",
            "marketing-consent create",
            "marketing-consent update",
            "marketing-consent delete",
            "marketing-consent upsert",
            "marketing-consent bulk-upsert",
            "marketing-consent remove",
            "referral-program get",
            "referral-program get-premium-features",
            "referral-program get-ai-social-media-posts-suggestions",
            "referral-program activate",
            "referral-program pause",
            "referral-program generate-ai-social-media-posts-suggestions",
            "referral-program update",
            "referral-rewards get",
            "referral-rewards query",
            "referring-customers get",
            "referring-customers query",
            "referring-customers get-by-referral-code",
            "referring-customers generate-for-contact",
            "referring-customers delete",
            "referred-friends get",
            "referred-friends query",
            "referred-friends get-by-contact-id",
            "referred-friends create",
            "referred-friends update",
            "referred-friends delete",
            "referral-tracker get",
            "referral-tracker query",
            "referral-tracker get-statistics",
            "email-campaigns list",
            "email-campaigns get",
            "email-campaigns get-audience",
            "email-campaigns list-statistics",
            "email-campaigns list-recipients",
            "email-campaigns pause-scheduling",
            "email-campaigns reschedule",
            "email-campaigns send-test",
            "email-campaigns publish",
            "email-campaigns reuse",
            "email-campaigns delete",
            "email-campaigns identify-sender-address",
            "donation-campaigns get",
            "donation-campaigns get-metrics",
            "donation-campaigns query",
            "donation-campaigns create",
            "donation-campaigns update",
            "donation-campaigns bulk-create",
            "donation-campaigns bulk-update",
            "donation-campaigns bulk-update-tags",
            "donation-campaigns bulk-update-tags-by-filter",
            "benefit-items get",
            "benefit-items list",
            "benefit-items query",
            "benefit-items count",
            "benefit-items create",
            "benefit-items update",
            "benefit-items delete",
            "benefit-items bulk-create",
            "benefit-items bulk-delete",
            "benefit-items bulk-update",
            "benefit-items bulk-delete-by-filter",
            "balances get",
            "balances list",
            "balances query",
            "balances change",
            "balances revert-change",
            "gift-cards create",
            "gift-cards get",
            "gift-cards query",
            "gift-cards search",
            "gift-cards count",
            "gift-cards disable",
            "gift-cards send-email",
            "coupons get",
            "coupons query",
            "coupons create",
            "coupons update",
            "coupons delete",
            "coupons bulk-create",
            "coupons bulk-delete",
            "pricing-plans get",
            "pricing-plans query",
            "pricing-plans search",
            "pricing-plans count",
            "pricing-plans create",
            "pricing-plans update",
            "pricing-plans delete",
            "pricing-plans bulk-update",
            "orders search",
            "orders get",
            "orders create",
            "orders update",
            "orders cancel",
            "orders bulk-update",
            "payments transactions-list",
            "bookings-time-slots-v2 list-availability",
            "bookings-time-slots-v2 get-availability",
            "bookings-time-slots-v2 list-event",
            "bookings-time-slots-v2 get-event",
            "bookings-time-slots-v2 list-multi-service",
            "bookings-time-slots-v2 get-multi-service",
            "bookings-reader-v2 query-extended-bookings",
            "bookings-reader-v2 count-extended-bookings",
            "bookings-writer-v2 create",
            "bookings-writer-v2 bulk-create",
            "bookings-writer-v2 bulk-calculate-allowed-actions",
            "bookings-writer-v2 bulk-confirm-or-decline",
            "bookings-writer-v2 confirm-or-decline",
            "bookings-writer-v2 confirm",
            "bookings-writer-v2 decline",
            "bookings-writer-v2 cancel",
            "bookings-writer-v2 reschedule",
            "bookings-writer-v2 mark-pending",
            "bookings-writer-v2 set-submission-id",
            "bookings-writer-v2 update-extended-fields",
            "bookings-writer-v2 update-participants",
            "bookings-writer-v2 create-multi-service",
            "bookings-writer-v2 get-multi-service",
            "bookings-writer-v2 get-multi-service-availability",
            "bookings-writer-v2 add-to-multi-service",
            "bookings-writer-v2 remove-from-multi-service",
            "bookings-writer-v2 cancel-multi-service",
            "bookings-writer-v2 confirm-multi-service",
            "bookings-writer-v2 decline-multi-service",
            "bookings-writer-v2 reschedule-multi-service",
            "bookings-writer-v2 mark-multi-service-pending",
            "bookings-writer-v2 bulk-get-multi-service-allowed-actions",
            "bookings-writer-v2 get-anonymous-action-token",
            "bookings-writer-v2 get-anonymous",
            "bookings-writer-v2 get-service-anonymous",
            "bookings-writer-v2 cancel-anonymous",
            "bookings-writer-v2 reschedule-anonymous",
            "bookings-policies get",
            "bookings-policies query",
            "bookings-policies count",
            "bookings-policies strictest",
            "bookings-policies create",
            "bookings-policies update",
            "bookings-policies delete",
            "bookings-policies set-default",
            "bookings-policy-snapshots list",
            "bookings-attendance get",
            "bookings-attendance query",
            "bookings-attendance count",
            "bookings-attendance set",
            "bookings-attendance bulk-set",
            "bookings-attendance delete",
            "bookings-attendance bulk-delete",
            "bookings-waitlist list",
            "bookings-waitlist register",
            "bookings-waitlist leave",
            "bookings-waitlist book",
            "calendar-schedules-v3 get",
            "calendar-schedules-v3 query",
            "calendar-schedules-v3 create",
            "calendar-schedules-v3 update",
            "calendar-schedules-v3 cancel",
            "calendar-schedule-time-frames-v3 get",
            "calendar-schedule-time-frames-v3 list",
            "calendar-events-v3 create",
            "calendar-events-v3 get",
            "calendar-events-v3 update",
            "calendar-events-v3 query",
            "calendar-events-v3 list",
            "calendar-events-v3 bulk-create",
            "calendar-events-v3 bulk-update",
            "calendar-events-v3 bulk-cancel",
            "calendar-events-v3 cancel",
            "calendar-events-v3 list-by-contact",
            "calendar-events-v3 list-by-member",
            "calendar-events-v3 restore-defaults",
            "calendar-events-v3 split-recurring",
            "calendar-event-views-v3 get",
            "calendar-participations-v3 create",
            "calendar-participations-v3 get",
            "calendar-participations-v3 update",
            "calendar-participations-v3 delete",
            "calendar-participations-v3 query",
            "bookings-external-calendars-v2 list-providers",
            "bookings-external-calendars-v2 connect-by-credentials",
            "bookings-external-calendars-v2 connect-by-oauth",
            "bookings-external-calendars-v2 list-connections",
            "bookings-external-calendars-v2 get-connection",
            "bookings-external-calendars-v2 update-sync-config",
            "bookings-external-calendars-v2 list-calendars",
            "bookings-external-calendars-v2 list-events",
            "bookings-external-calendars-v2 disconnect",
            "bookings-service-options-v1 get",
            "bookings-service-options-v1 get-by-service-id",
            "bookings-service-options-v1 query",
            "bookings-service-options-v1 create",
            "bookings-service-options-v1 update",
            "bookings-service-options-v1 delete",
            "bookings-service-options-v1 clone",
            "bookings-services-v2 get",
            "bookings-services-v2 query",
            "bookings-services-v2 search",
            "bookings-services-v2 count",
            "bookings-services-v2 create",
            "bookings-services-v2 update",
            "bookings-services-v2 delete",
            "bookings-services-v2 bulk-create",
            "bookings-services-v2 bulk-update",
            "bookings-services-v2 bulk-update-by-filter",
            "bookings-services-v2 bulk-delete",
            "bookings-services-v2 bulk-delete-by-filter",
            "bookings-services-v2 query-policies",
            "bookings-services-v2 query-locations",
            "bookings-services-v2 query-categories",
            "bookings-services-v2 set-service-locations",
            "bookings-services-v2 enable-pricing-plans",
            "bookings-services-v2 disable-pricing-plans",
            "bookings-services-v2 set-custom-slug",
            "bookings-services-v2 validate-slug",
            "bookings-services-v2 clone",
            "bookings-services-v2 create-add-on-group",
            "bookings-services-v2 delete-add-on-group",
            "bookings-services-v2 list-add-on-groups-by-service-id",
            "bookings-services-v2 set-add-ons-for-group",
            "bookings-services-v2 update-add-on-group",
            "bookings-resources-v2 get",
            "bookings-resources-v2 query",
            "bookings-resources-v2 search",
            "bookings-resources-v2 count",
            "bookings-resources-v2 create",
            "bookings-resources-v2 update",
            "bookings-resources-v2 delete",
            "bookings-resources-v2 bulk-create",
            "bookings-resources-v2 bulk-update",
            "bookings-resources-v2 bulk-delete",
            "bookings-resource-types-v2 get",
            "bookings-resource-types-v2 query",
            "bookings-resource-types-v2 count",
            "bookings-resource-types-v2 create",
            "bookings-resource-types-v2 update",
            "bookings-resource-types-v2 delete",
            "bookings-staff-members get",
            "bookings-staff-members query",
            "bookings-staff-members search",
            "bookings-staff-members count",
            "bookings-staff-members get-deleted",
            "bookings-staff-members list-deleted",
            "bookings-staff-members create",
            "bookings-staff-members update",
            "bookings-staff-members delete",
            "bookings-staff-members assign-working-hours-schedule",
            "bookings-staff-members bulk-update-tags",
            "bookings-staff-members bulk-update-tags-by-filter",
            "bookings-staff-members connect-to-user",
            "bookings-staff-members disconnect-from-user",
            "bookings-staff-members remove-from-trash",
            "stores-products-v3 get",
            "stores-products-v3 get-by-slug",
            "stores-products-v3 get-all-products-category",
            "stores-products-v3 query",
            "stores-products-v3 search",
            "stores-products-v3 count",
            "stores-products-v3 create",
            "stores-products-v3 update",
            "stores-products-v3 delete",
            "stores-products-v3 bulk-create",
            "stores-products-v3 bulk-delete",
            "stores-products-v3 bulk-update",
            "stores-products-v3 create-with-inventory",
            "stores-products-v3 update-with-inventory",
            "stores-products-v3 bulk-create-with-inventory",
            "stores-products-v3 bulk-update-with-inventory",
            "stores-products-v3 bulk-add-info-sections",
            "stores-products-v3 bulk-add-info-sections-by-filter",
            "stores-products-v3 bulk-add-to-categories-by-filter",
            "stores-products-v3 bulk-adjust-variants-by-filter",
            "stores-products-v3 bulk-delete-by-filter",
            "stores-products-v3 bulk-remove-info-sections",
            "stores-products-v3 bulk-remove-info-sections-by-filter",
            "stores-products-v3 bulk-remove-from-categories-by-filter",
            "stores-products-v3 bulk-update-variants-by-filter",
            "stores-products-v3 bulk-update-by-filter",
            "read-only-variants-v3 query",
            "read-only-variants-v3 search",
            "brands-v3 get",
            "brands-v3 query",
            "brands-v3 create",
            "brands-v3 update",
            "brands-v3 delete",
            "brands-v3 bulk-create",
            "brands-v3 bulk-delete",
            "brands-v3 bulk-update",
            "brands-v3 get-or-create",
            "brands-v3 bulk-get-or-create",
            "ribbons-v3 get",
            "ribbons-v3 query",
            "ribbons-v3 create",
            "ribbons-v3 update",
            "ribbons-v3 delete",
            "ribbons-v3 bulk-create",
            "ribbons-v3 bulk-delete",
            "ribbons-v3 bulk-update",
            "ribbons-v3 get-or-create",
            "ribbons-v3 bulk-get-or-create",
            "stores-info-sections-v3 get",
            "stores-info-sections-v3 query",
            "stores-info-sections-v3 create",
            "stores-info-sections-v3 update",
            "stores-info-sections-v3 delete",
            "stores-info-sections-v3 bulk-create",
            "stores-info-sections-v3 bulk-delete",
            "stores-info-sections-v3 bulk-update",
            "stores-info-sections-v3 get-or-create",
            "stores-info-sections-v3 bulk-get-or-create",
            "customizations-v3 get",
            "customizations-v3 query",
            "customizations-v3 create",
            "customizations-v3 update",
            "customizations-v3 delete",
            "customizations-v3 bulk-create",
            "customizations-v3 bulk-update",
            "customizations-v3 add-choices",
            "customizations-v3 bulk-add-choices",
            "customizations-v3 remove-choices",
            "customizations-v3 set-choices",
            "categories get",
            "categories get-by-slug",
            "categories query",
            "categories search",
            "categories count",
            "categories list-trees",
            "categories get-arranged-items",
            "categories list-categories-for-item",
            "categories list-categories-for-items",
            "categories list-items-in-category",
            "categories create",
            "categories update",
            "categories delete",
            "categories bulk-update",
            "categories update-visibility",
            "categories bulk-show",
            "categories bulk-add-items-to-category",
            "categories bulk-add-item-to-categories",
            "categories bulk-remove-items-from-category",
            "categories bulk-remove-item-from-categories",
            "categories move",
            "categories set-arranged-items",
            "stores-inventory-items-v3 get",
            "stores-inventory-items-v3 query",
            "stores-inventory-items-v3 search",
            "stores-inventory-items-v3 create",
            "stores-inventory-items-v3 update",
            "stores-inventory-items-v3 delete",
            "stores-locations-v3 get",
            "stores-locations-v3 query",
            "catalog-versioning get",
            "order-billing get-order-refundability",
            "order-billing calculate-refund",
            "order-billing authorize-charge-with-saved-payment-method",
            "order-billing capture-authorized-payments",
            "order-billing void-authorized-payments",
            "order-billing generate-receipts",
            "order-billing redeem-gift-card",
            "order-billing refund-payments",
            "campaign-validation validate-link",
            "campaign-validation validate-html-links",
            "events-settings get",
            "events-settings update",
            "portfolio-settings get",
            "portfolio-settings update",
            "portfolio-collections create",
            "portfolio-collections get",
            "portfolio-collections update",
            "portfolio-collections delete",
            "portfolio-collections query",
            "portfolio-collections list",
            "portfolio-projects create",
            "portfolio-projects get",
            "portfolio-projects update",
            "portfolio-projects delete",
            "portfolio-projects query",
            "portfolio-projects list",
            "portfolio-projects bulk-update",
            "portfolio-project-items create",
            "portfolio-project-items get",
            "portfolio-project-items update",
            "portfolio-project-items delete",
            "portfolio-project-items list",
            "portfolio-project-items bulk-create",
            "portfolio-project-items bulk-update",
            "portfolio-project-items bulk-delete",
            "portfolio-project-items duplicate",
            "suppliers-hub-products get",
            "suppliers-hub-products query",
            "suppliers-hub-products search",
            "suppliers-hub-products query-categories",
            "suppliers-hub-products create",
            "suppliers-hub-products update",
            "suppliers-hub-products delete",
            "suppliers-hub-products bulk-create",
            "suppliers-hub-products bulk-update",
            "suppliers-hub-products bulk-delete",
            "suppliers-hub-products bulk-add-to-store",
            "suppliers-hub-products bulk-update-tags",
            "suppliers-hub-products bulk-update-tags-by-filter",
            "suppliers-hub-suppliers get",
            "suppliers-hub-suppliers query",
            "suppliers-hub-suppliers create",
            "suppliers-hub-suppliers update",
            "suppliers-hub-suppliers delete",
            "suppliers-hub-suppliers bulk-create",
            "suppliers-hub-suppliers bulk-update",
            "suppliers-hub-suppliers bulk-delete",
            "suppliers-hub-suppliers bulk-update-tags",
            "suppliers-hub-suppliers bulk-update-tags-by-filter",
            "suppliers-hub-marketplace-provider-submissions submit-generated-mockups",
            "events-v3 create",
            "events-v3 get",
            "events-v3 update",
            "events-v3 delete",
            "events-v3 query",
            "events-v3 bulk-cancel-by-filter",
            "events-v3 bulk-delete-by-filter",
            "events-v3 cancel",
            "events-v3 clone",
            "events-v3 count-by-status",
            "events-v3 get-by-slug",
            "events-v3 list-by-category",
            "events-v3 publish-draft",
            "events-ticket-definitions-v3 create",
            "events-ticket-definitions-v3 get",
            "events-ticket-definitions-v3 update",
            "events-ticket-definitions-v3 delete",
            "events-ticket-definitions-v3 query",
            "events-ticket-definitions-v3 bulk-delete-by-filter",
            "events-ticket-definitions-v3 change-currency",
            "events-ticket-definitions-v3 count",
            "events-ticket-definitions-v3 reorder",
            "events-categories create",
            "events-categories bulk-create",
            "events-categories update",
            "events-categories delete",
            "events-categories query",
            "events-categories assign-events",
            "events-categories unassign-events",
            "events-categories bulk-assign-events",
            "events-categories bulk-unassign-events",
            "events-categories get",
            "events-categories reorder-events",
            "events-schedule-items get",
            "events-schedule-items query",
            "events-schedule-items add",
            "events-schedule-items create-bookmark",
            "events-schedule-items delete-bookmark",
            "events-schedule-items delete",
            "events-schedule-items discard-draft",
            "events-schedule-items list-bookmarks",
            "events-schedule-items list",
            "events-schedule-items publish-draft",
            "events-schedule-items reschedule-draft",
            "events-schedule-items update",
            "events-policies-v2 create",
            "events-policies-v2 get",
            "events-policies-v2 update",
            "events-policies-v2 delete",
            "events-policies-v2 query",
            "events-policies-v2 reorder",
            "events-staff-members create",
            "events-staff-members get",
            "events-staff-members update",
            "events-staff-members delete",
            "events-staff-members query",
            "events-guests query",
            "events-rsvps-v2 create",
            "events-rsvps-v2 get",
            "events-rsvps-v2 update",
            "events-rsvps-v2 delete",
            "events-rsvps-v2 query",
            "events-rsvps-v2 search",
            "events-rsvps-v2 bulk-update",
            "events-rsvps-v2 bulk-delete-by-filter",
            "events-rsvps-v2 check-in",
            "events-rsvps-v2 cancel-check-in",
            "events-rsvps-v2 count",
            "events-rsvps-v2 list-summary",
            "events-ticket-reservations create",
            "events-ticket-reservations get",
            "events-ticket-reservations delete",
            "events-ticket-reservations bulk-update-tags",
            "events-ticket-reservations bulk-update-tags-by-filter",
            "events-ticket-reservations cancel",
            "events-tickets get",
            "events-tickets list",
            "events-tickets update",
            "events-tickets bulk-update",
            "events-tickets check-in",
            "events-tickets delete-check-in",
            "events-orders list",
            "events-orders get",
            "events-orders update",
            "events-orders bulk-update",
            "events-orders confirm",
            "events-orders get-summary",
            "events-orders get-checkout-options",
            "events-orders list-available-tickets",
            "events-orders query-available-tickets",
            "events-orders create-reservation",
            "events-orders cancel-reservation",
            "events-orders checkout",
            "events-orders update-checkout",
            "events-orders get-invoice",
            "events-forms get-form",
            "events-forms discard-draft",
            "events-forms add-control",
            "events-forms update-control",
            "events-forms delete-control",
            "events-forms update-messages",
            "events-forms publish-draft",
            "restaurants-menus list",
            "restaurants-menus get",
            "restaurants-menus query",
            "restaurants-menus create",
            "restaurants-menus update",
            "restaurants-menus delete",
            "restaurants-menus bulk-create",
            "restaurants-menus bulk-update",
            "restaurants-menus duplicate",
            "restaurants-menus update-extended-fields",
            "restaurants-sections list",
            "restaurants-sections get",
            "restaurants-sections query",
            "restaurants-sections create",
            "restaurants-sections update",
            "restaurants-sections delete",
            "restaurants-sections bulk-create",
            "restaurants-sections bulk-delete",
            "restaurants-sections bulk-update",
            "restaurants-sections duplicate",
            "restaurants-items list",
            "restaurants-items get",
            "restaurants-items query",
            "restaurants-items search",
            "restaurants-items count",
            "restaurants-items create",
            "restaurants-items update",
            "restaurants-items delete",
            "restaurants-items bulk-create",
            "restaurants-items bulk-delete",
            "restaurants-items bulk-update",
            "restaurants-item-labels list",
            "restaurants-item-labels get",
            "restaurants-item-labels query",
            "restaurants-item-labels create",
            "restaurants-item-labels update",
            "restaurants-item-labels delete",
            "restaurants-item-variants list",
            "restaurants-item-variants get",
            "restaurants-item-variants query",
            "restaurants-item-variants count",
            "restaurants-item-variants create",
            "restaurants-item-variants update",
            "restaurants-item-variants delete",
            "restaurants-item-variants bulk-create",
            "restaurants-item-variants bulk-delete",
            "restaurants-item-variants bulk-update",
            "restaurants-item-modifiers list",
            "restaurants-item-modifiers get",
            "restaurants-item-modifiers query",
            "restaurants-item-modifiers count",
            "restaurants-item-modifiers create",
            "restaurants-item-modifiers update",
            "restaurants-item-modifiers delete",
            "restaurants-item-modifiers bulk-create",
            "restaurants-item-modifiers bulk-delete",
            "restaurants-item-modifiers bulk-update",
            "restaurants-item-modifier-groups list",
            "restaurants-item-modifier-groups get",
            "restaurants-item-modifier-groups query",
            "restaurants-item-modifier-groups count",
            "restaurants-item-modifier-groups create",
            "restaurants-item-modifier-groups update",
            "restaurants-item-modifier-groups delete",
            "restaurants-item-modifier-groups bulk-create",
            "restaurants-item-modifier-groups bulk-update",
            "restaurants-online-order-operation-groups get",
            "restaurants-online-order-operation-groups query",
            "restaurants-online-order-operation-groups create",
            "restaurants-online-order-operation-groups update",
            "restaurants-online-order-operation-groups delete",
            "restaurants-online-order-operation-groups bulk-create",
            "restaurants-online-order-operation-groups bulk-delete",
            "restaurants-online-order-operation-groups bulk-update",
            "restaurants-online-order-operation-groups bulk-update-tags",
            "restaurants-online-order-operation-groups bulk-update-tags-by-filter",
            "restaurants-online-order-operations get",
            "restaurants-online-order-operations list",
            "restaurants-online-order-operations query",
            "restaurants-online-order-operations first-available-time-slot-per-fulfillment-type",
            "restaurants-online-order-operations first-available-time-slots-per-operation",
            "restaurants-online-order-operations first-available-time-slots-per-menu",
            "restaurants-online-order-operations available-time-slots-for-date",
            "restaurants-online-order-operations available-dates-in-range",
            "restaurants-online-order-operations validate-address",
            "restaurants-online-order-operations update",
            "restaurants-online-order-operations delete",
            "restaurants-online-order-operations bulk-update-tags",
            "restaurants-online-order-operations bulk-update-tags-by-filter",
            "restaurants-online-order-menu-ordering-settings get",
            "restaurants-online-order-menu-ordering-settings update",
            "restaurants-online-order-menu-ordering-settings query",
            "restaurants-online-order-menu-ordering-settings list-menus-availability-status",
            "restaurants-online-order-menu-ordering-settings bulk-update",
            "restaurants-online-order-menu-ordering-settings bulk-update-tags",
            "restaurants-online-order-menu-ordering-settings bulk-update-tags-by-filter",
            "restaurants-online-order-menu-ordering-settings update-extended-fields",
            "restaurants-online-order-menu-ordering-settings upsert-by-menu-id",
            "restaurants-online-order-fulfillment-methods list",
            "restaurants-online-order-fulfillment-methods get",
            "restaurants-online-order-fulfillment-methods query",
            "restaurants-online-order-fulfillment-methods list-available-for-address",
            "restaurants-online-order-fulfillment-methods get-accumulated-availability",
            "restaurants-online-order-fulfillment-methods get-combined-availability",
            "restaurants-online-order-fulfillment-methods get-aggregated-availability",
            "restaurants-online-order-fulfillment-methods create",
            "restaurants-online-order-fulfillment-methods bulk-create",
            "restaurants-online-order-fulfillment-methods update",
            "restaurants-online-order-fulfillment-methods delete",
            "restaurants-online-order-fulfillment-methods bulk-update-tags",
            "restaurants-online-order-fulfillment-methods bulk-update-tags-by-filter",
            "restaurants-online-order-availability-exceptions get",
            "restaurants-online-order-availability-exceptions query",
            "restaurants-online-order-availability-exceptions create",
            "restaurants-online-order-availability-exceptions bulk-create",
            "restaurants-online-order-availability-exceptions update",
            "restaurants-online-order-availability-exceptions bulk-update",
            "restaurants-online-order-availability-exceptions delete",
            "restaurants-online-order-availability-exceptions bulk-update-tags",
            "restaurants-online-order-availability-exceptions bulk-update-tags-by-filter",
            "restaurants-online-order-service-fees calculate",
            "restaurants-online-order-service-fees list",
            "restaurants-online-order-service-fees get",
            "restaurants-online-order-service-fees query",
            "restaurants-online-order-service-fees create",
            "restaurants-online-order-service-fees bulk-create",
            "restaurants-online-order-service-fees update",
            "restaurants-online-order-service-fees bulk-update",
            "restaurants-online-order-service-fees delete",
            "restaurants-online-order-service-fees bulk-delete",
            "restaurants-online-order-service-fees bulk-update-tags",
            "restaurants-online-order-service-fees bulk-update-tags-by-filter",
            "restaurants-online-order-notification-recipients get",
            "restaurants-online-order-notification-recipients query",
            "restaurants-online-order-notification-recipients create",
            "restaurants-online-order-notification-recipients bulk-create",
            "restaurants-online-order-notification-recipients update",
            "restaurants-online-order-notification-recipients bulk-update",
            "restaurants-online-order-notification-recipients delete",
            "restaurants-online-order-notification-recipients bulk-delete",
            "restaurants-online-order-notification-recipients bulk-update-tags",
            "restaurants-online-order-notification-recipients bulk-update-tags-by-filter",
            "restaurants-reservations create",
            "restaurants-reservations get",
            "restaurants-reservations update",
            "restaurants-reservations delete",
            "restaurants-reservations query",
            "restaurants-reservations list",
            "restaurants-reservations search",
            "restaurants-reservations bulk-archive",
            "restaurants-reservations bulk-unarchive",
            "restaurants-reservations cancel",
            "restaurants-reservations create-held",
            "restaurants-reservations reserve",
            "restaurants-reservation-locations get",
            "restaurants-reservation-locations update",
            "restaurants-reservation-locations query",
            "restaurants-reservation-locations list",
            "restaurants-reservation-time-slots check",
            "restaurants-reservation-time-slots get-scheduled",
            "restaurants-reservation-time-slots get",
            "restaurants-reservation-experiences create",
            "restaurants-reservation-experiences get",
            "restaurants-reservation-experiences update",
            "restaurants-reservation-experiences query",
            "restaurants-reservation-experiences search",
            "restaurants-reservation-experiences bulk-update-tags",
            "restaurants-reservation-experiences bulk-update-tags-by-filter",
            "restaurants-reservation-experiences get-by-slug",
            "blog-posts-stats get",
            "blog-posts-stats query",
            "blog-posts-stats list",
            "blog-posts-stats get-by-slug",
            "blog-posts-stats get-metrics",
            "blog-posts-stats get-total",
            "blog-posts-stats query-count",
            "blog-draft-posts create",
            "blog-draft-posts get",
            "blog-draft-posts update",
            "blog-draft-posts delete",
            "blog-draft-posts query",
            "blog-draft-posts list",
            "blog-draft-posts bulk-create",
            "blog-draft-posts bulk-delete",
            "blog-draft-posts bulk-update",
            "blog-draft-posts get-deleted",
            "blog-draft-posts list-deleted",
            "blog-draft-posts publish",
            "blog-draft-posts remove-from-trash-bin",
            "blog-draft-posts restore-from-trash-bin",
            "blog-categories create",
            "blog-categories get",
            "blog-categories update",
            "blog-categories delete",
            "blog-categories query",
            "blog-categories list",
            "blog-categories get-by-slug",
            "blog-tags get",
            "blog-tags delete",
            "blog-tags query",
            "blog-tags create",
            "blog-tags get-by-label",
            "blog-tags get-by-slug",
            "blog-likes create",
            "blog-likes get",
            "blog-likes delete",
            "blog-likes query",
            "blog-likes delete-by-fqdn-entity-id",
            "market-listing search",
            "editor-deep-link create",
            "site-plugins get-placement-status",
            "app-permissions list",
            "app-permissions create",
            "app-permissions delete",
            "contact-labels query",
            "contact-labels list",
            "contact-labels find-or-create",
            "contact-labels get",
            "contact-labels update",
            "contact-labels delete",
            "data-permissions get",
            "data-permissions get-my",
            "data-permissions update",
            "data-permissions add-special",
            "data-permissions update-special",
            "data-permissions remove-special",
            "data-sharing list-policies",
            "data-sharing get-policy",
            "data-sharing list-shared-collections",
            "data-sharing create-policy",
            "data-sharing update-policy",
            "data-sharing delete-policy",
            "data-sharing connect",
            "data-sharing disconnect",
            "data-indexes list",
            "data-indexes create",
            "data-indexes drop",
            "data-folders get",
            "data-folders create",
            "data-folders update",
            "data-folders delete",
            "data-folders create-collection-reference",
            "data-folders get-collection-references",
            "data-folders delete-collection-reference",
            "data-extension-schemas list",
            "data-extension-schemas create",
            "data-extension-schemas update",
            "data-extension-schemas delete-user-defined-fields",
            "ai-credits get-balance",
            "analytics-data get",
            "analytics-sessions get-list-job-result",
            "analytics-sessions list-async",
            "analytics-sessions mark-recordings-deleted",
            "analytics-sessions mark-session-recorded",
            "analytics-semantic-models list",
            "analytics-semantic-models get",
            "analytics-semantic-models query",
            "automation-storage-items create",
            "automation-storage-items get",
            "automation-storage-items query",
            "automation-storage-items bulk-update-tags",
            "automation-storage-items bulk-update-tags-by-filter",
            "automation-storage-items update-counter-by",
            "automation-storage-items update-value",
            "automations-v2 create",
            "automations-v2 get",
            "automations-v2 update",
            "automations-v2 delete",
            "automations-v2 query",
            "automations-v2 validate",
            "async-jobs get",
            "async-jobs list-items",
            "branches get-default",
            "branches get",
            "branches query",
            "site-search search",
            "accounts get",
            "accounts list-child-accounts",
            "contributors query",
            "contributors remove",
            "contributors change-role",
            "contributors change-contributor-location",
            "form-submissions get-submission",
            "form-submissions query-submissions-by-namespace",
            "form-submissions count-submissions",
            "form-submissions get-media-upload-url",
            "form-submissions create-submission",
            "form-submissions update-submission",
            "form-submissions delete-submission",
            "form-submissions confirm-submission",
            "form-submissions bulk-mark-submissions-as-seen",
            "files list",
            "files get",
            "files batch-get",
            "files search",
            "files query",
            "files list-deleted",
            "files update",
            "files bulk-delete",
            "files bulk-restore",
            "files generate-upload-url",
            "files generate-resumable-upload-url",
            "files import",
            "files generate-download-url",
            "media-folders list",
            "media-folders get",
            "media-folders search",
            "media-folders query",
            "media-folders list-deleted",
            "media-folders create",
            "media-folders update",
            "media-folders bulk-delete",
            "media-folders bulk-restore",
            "media-folders generate-download-url",
            "rich-content-ricos convert-from",
            "rich-content-ricos convert-to",
            "rich-content-ricos validate",
            "pro-gallery list-galleries",
            "pro-gallery get-gallery",
            "pro-gallery create-gallery",
            "pro-gallery update-gallery",
            "pro-gallery delete-gallery",
            "pro-gallery list-gallery-items",
            "pro-gallery get-gallery-item",
            "pro-gallery create-gallery-item",
            "pro-gallery update-gallery-item",
            "pro-gallery delete-gallery-item",
            "pro-gallery bulk-delete-gallery-items",
            "notifications notify",
            "locations list",
            "locations query",
            "locations get",
            "locations create",
            "locations update",
            "locations archive",
            "locations set-default",
            "tags list",
            "tags get",
            "tags create",
            "tags update",
            "tags delete",
            "sites query",
            "sites count",
            "site-properties get",
            "site-properties update-business-contact",
            "site-properties update-business-profile",
            "site-properties update-business-schedule",
            "site-properties update-consent-policy",
            "cookie-consent-policy get-cookie-banner-settings",
            "cookie-consent-policy update-cookie-banner-settings",
            "cookie-consent-policy get-cmp-config",
            "cookie-consent-policy update-cmp-config",
            "cookie-consent-policy create-consent-config",
            "cookie-consent-policy get-consent-config",
            "cookie-consent-policy update-consent-config",
            "cookie-consent-policy delete-consent-config",
            "cookie-consent-policy query-consent-configs",
            "cookie-consent-policy bulk-create-consent-configs",
            "cookie-consent-policy bulk-delete-consent-configs",
            "cookie-consent-policy bulk-update-consent-configs",
            "cookie-consent-policy bulk-update-consent-config-tags",
            "cookie-consent-policy bulk-update-consent-config-tags-by-filter",
            "cookie-consent-policy list-apps-and-storage",
            "multilingual-locale-settings get",
            "multilingual-locale-settings set-mode",
            "multilingual-locale-settings update",
            "multilingual-locales create",
            "multilingual-locales get",
            "multilingual-locales update",
            "multilingual-locales delete",
            "multilingual-locales query",
            "multilingual-locales bulk-create",
            "multilingual-locales bulk-delete",
            "multilingual-locales bulk-update",
            "multilingual-locales create-new-primary",
            "multilingual-locales get-new-primary-status",
            "multilingual-locales list-supported",
            "multilingual-locales set-visitor-primary",
            "multilingual-translation-schemas create",
            "multilingual-translation-schemas get",
            "multilingual-translation-schemas update",
            "multilingual-translation-schemas delete",
            "multilingual-translation-schemas query",
            "multilingual-translation-schemas list-site",
            "multilingual-translation-schemas get-by-key",
            "multilingual-translation-contents create",
            "multilingual-translation-contents get",
            "multilingual-translation-contents update",
            "multilingual-translation-contents delete",
            "multilingual-translation-contents query",
            "multilingual-translation-contents search",
            "multilingual-translation-contents bulk-create",
            "multilingual-translation-contents bulk-delete",
            "multilingual-translation-contents bulk-update",
            "multilingual-translation-contents bulk-update-by-key",
            "multilingual-translation-contents update-by-key",
            "multilingual-translation-published-contents query",
            "multilingual-machine-translation translate",
            "multilingual-machine-translation bulk-translate",
            "multilingual-machine-translation-credit-data get",
            "multilingual-machine-translation-credit-data check-sufficient",
            "online-programs-programs create",
            "online-programs-programs get",
            "online-programs-programs update",
            "online-programs-programs delete",
            "online-programs-programs query",
            "online-programs-programs search",
            "online-programs-programs count",
            "online-programs-programs bulk-update",
            "online-programs-programs archive",
            "online-programs-programs duplicate",
            "online-programs-programs end",
            "online-programs-programs list-samples",
            "online-programs-programs publish",
            "online-programs-instructor-v2 create",
            "online-programs-instructor-v2 update",
            "online-programs-instructor-v2 query",
            "online-programs-instructor-v2 assign",
            "online-programs-instructor-v2 change-program-instructors",
            "online-programs-instructor-v2 invite",
            "online-programs-instructor-v2 list",
            "online-programs-instructor-v2 unassign",
            "b2b-site-transfer transfer",
            "partner-profiles create",
            "partner-profiles update",
            "partner-profiles delete",
            "partner-profiles get-current",
            "partner-profiles get-public",
            "partner-profiles find-public-by-slug",
            "viewer-cache invalidate",
            "viewer-seo-tags resolve-item",
            "viewer-seo-tags resolve-static",
            "dashboard-favorite-list create",
            "dashboard-favorite-list update",
            "dashboard-favorite-list delete",
            "dashboard-favorite-list add-favorite",
            "dashboard-favorite-list delete-favorite",
            "dashboard-favorite-list get",
            "faq-category-v2 create",
            "faq-category-v2 get",
            "faq-category-v2 update",
            "faq-category-v2 delete",
            "faq-category-v2 query",
            "faq-category-v2 list",
            "faq-category-v2 update-extended-fields",
            "faq-question-entry-v2 list",
            "faq-question-entry-v2 create",
            "faq-question-entry-v2 get",
            "faq-question-entry-v2 delete",
            "faq-question-entry-v2 update",
            "faq-question-entry-v2 query",
            "faq-question-entry-v2 bulk-delete",
            "faq-question-entry-v2 bulk-update",
            "faq-question-entry-v2 set-labels",
            "faq-question-entry-v2 update-extended-fields",
            "functions-v1 create",
            "functions-v1 get",
            "functions-v1 update",
            "functions-v1 delete",
            "functions-v1 query",
            "functions-v1 bulk-update-tags",
            "functions-v1 bulk-update-tags-by-filter",
            "function-types get",
            "function-types query",
            "function-templates get",
            "function-templates query",
            "function-productions create",
            "function-productions update",
            "function-productions delete",
            "builderless-productions create",
            "builderless-productions get",
            "builderless-productions update",
            "function-methods create",
            "function-methods delete",
            "function-methods query",
            "function-activations upsert",
            "function-activations delete",
            "function-spi-configurations create",
            "function-spi-configurations get",
            "function-spi-configurations update",
            "function-spi-configurations delete",
            "function-spi-configurations query",
            "function-spi-configurations validate",
            "billable-items create",
            "billable-items get",
            "billable-items update",
            "billable-items delete",
            "billable-items query",
            "billable-items search",
            "billable-items bulk-create",
            "billable-items bulk-delete",
            "billable-items bulk-update",
            "billable-items bulk-update-tags",
            "billable-items bulk-update-tags-by-filter",
            "payment-links create",
            "payment-links get",
            "payment-links delete",
            "payment-links query",
            "payment-links search",
            "payment-links activate",
            "payment-links deactivate",
            "payment-links initiate-payment",
            "payment-links send",
            "payment-links set-note",
            "payment-links update-extended-fields",
            "payment-links bulk-update-tags",
            "payment-links bulk-update-tags-by-filter",
            "payment-link-payments query",
            "payment-link-payments search",
            "payment-link-payments issue-receipt",
            "receipts create",
            "receipts get",
            "receipts query",
            "receipts get-latest-number",
            "receipts regenerate-document",
            "receipts send-email",
            "receipts update-extended-fields",
            "receipt-presets create",
            "receipt-presets get",
            "receipt-presets update",
            "receipt-presets delete",
            "receipt-presets list",
            "receipt-presets get-default",
            "receipt-presets set-default",
            "receipt-presets update-extended-fields",
            "receipts-settings get",
            "receipts-settings update",
            "payment-link-settings get",
            "payment-link-settings update",
            "headless-oauth-apps create",
            "headless-oauth-apps get",
            "headless-oauth-apps update",
            "headless-oauth-apps query",
            "headless-authentication login-v2",
            "headless-authentication retrieve-tokens",
            "headless-authentication register-v2",
            "headless-authentication change-password",
            "headless-authentication logout",
            "headless-authentication sign-on",
            "headless-recovery send-recovery-email",
            "headless-redirects create-redirect-session",
            "headless-sitemap list-pages",
            "headless-verification verify-during-authentication",
            "site-urls get-editor-urls",
            "site-urls list-published-site-urls",
            "domains check-availability",
            "domains suggest",
            "domain-dns get-zone",
            "domain-dns preview-zone",
            "domain-dns create-zone",
            "domain-dns update-zone",
            "domain-dns delete-zone",
            "dns-propagation get",
            "connected-domains list",
            "connected-domains get",
            "connected-domains get-setup-info",
            "connected-domains create",
            "connected-domains delete",
            "projects create-project",
            "resellers get",
            "resellers query",
            "resellers create-package",
            "resellers adjust-product-instance",
            "resellers assign-product-instance",
            "resellers unassign-product-instance",
            "resellers update-package-external-id",
            "resellers cancel-package",
            "resellers cancel-product-instance",
            "site-actions bulk-delete",
            "site-actions duplicate",
            "site-actions publish",
            "site-folders query",
            "site-folders get-folder-by-site",
            "site-folders create",
            "site-folders update",
            "site-folders delete",
            "site-folders move-folders",
            "site-folders move-sites",
            "data-items get",
            "data-items query",
            "data-items query-referenced",
            "data-items count",
            "data-items aggregate",
            "data-items aggregate-pipeline",
            "data-items distinct",
            "data-items search",
            "data-items is-referenced",
            "data-items insert-reference",
            "data-items remove-reference",
            "data-items replace-references",
            "data-items insert",
            "data-items save",
            "data-items truncate",
            "data-items bulk-insert",
            "data-items bulk-patch",
            "data-items bulk-remove",
            "data-items bulk-save",
            "data-items bulk-update",
            "data-items bulk-insert-references",
            "data-items bulk-remove-references",
            "data-items update",
            "data-items patch",
            "data-items remove",
            "data-collections list",
            "data-collections get",
            "data-collections create",
            "data-collections update",
            "data-collections patch",
            "data-collections delete",
            "data-collections create-field",
            "data-collections update-field",
            "data-collections patch-field",
            "data-collections delete-field",
            "data-collections add-plugin",
            "data-collections delete-plugin",
        ]

    @staticmethod
    def _collect_parser_command_paths() -> list[str]:
        parser = build_parser()
        paths: list[str] = []

        def walk(p: argparse.ArgumentParser, prefix: str) -> None:
            for action in p._actions:
                if not isinstance(action, argparse._SubParsersAction):
                    continue
                for name, choice in action.choices.items():
                    command_path = f"{prefix} {name}".strip()
                    has_children = any(
                        isinstance(child_action, argparse._SubParsersAction) for child_action in choice._actions
                    )
                    if has_children:
                        walk(choice, command_path)
                    else:
                        paths.append(command_path)

        walk(parser, "")
        return paths

    def test_skill_wrapper_path_exists_and_slug_matches(self) -> None:
        root = Path(__file__).resolve().parents[1]
        docs_wrappers = root / "docs" / "skills_wrappers.md"
        readme = root / "README.md"

        skill_text = self._skill_text(root)
        docs_text = docs_wrappers.read_text(encoding="utf-8")
        readme_text = readme.read_text(encoding="utf-8")

        self.assertIn("name: wix", skill_text)
        self.assertIn("Install slug: `wix`", readme_text)
        self.assertIn("Source wrapper: `skills/wix/SKILL.md`", docs_text)
        self.assertIn("Public mirror wrapper: `SKILL.md`", docs_text)
        self.assertIn("wix-safe-agent-cli", skill_text)

    def test_wrapper_and_command_reference_cover_the_same_shipped_surface(self) -> None:
        root = Path(__file__).resolve().parents[1]
        skill_text = self._skill_text(root)
        docs_wrappers_text = (root / "docs" / "skills_wrappers.md").read_text(encoding="utf-8")
        command_reference_text = (root / "docs" / "command_reference.md").read_text(encoding="utf-8")
        parser_paths = set(self._collect_parser_command_paths())

        missing = [cmd for cmd in self._expected_command_names() if cmd not in skill_text]
        if missing:
            self.fail("Wrapper missing required shipped command names: " + ", ".join(missing))

        missing_from_reference = [cmd for cmd in self._expected_command_names() if cmd not in command_reference_text]
        if missing_from_reference:
            self.fail("Command reference missing shipped command names: " + ", ".join(missing_from_reference))

        for cmd in self._expected_command_names():
            self.assertIn(cmd, parser_paths)

        expected_parser_paths = set(self._expected_command_names())
        unexpected_parser_paths = sorted(set(parser_paths) - expected_parser_paths)
        if unexpected_parser_paths:
            self.fail("Parser exposes unexpected shipped commands: " + ", ".join(unexpected_parser_paths))

        for banned in ["jobs run", "demo read", "demo write"]:
            self.assertNotIn(banned, skill_text, msg=f"Shipped command still present in wrapper: {banned}")
            self.assertNotIn(banned, docs_wrappers_text, msg=f"Wrapper docs still mention removed command: {banned}")
            self.assertNotIn(
                banned, command_reference_text, msg=f"Command reference still includes removed command: {banned}"
            )

        self.assertIn("runs list", docs_wrappers_text)
        self.assertIn("runs show", docs_wrappers_text)
        self.assertIn("auth token request", docs_wrappers_text)
        self.assertIn("auth token refresh", docs_wrappers_text)
        self.assertIn("accounts get", docs_wrappers_text)
        self.assertIn("accounts list-child-accounts", docs_wrappers_text)
        self.assertIn("domain-dns get-zone", docs_wrappers_text)
        self.assertIn("domain-dns preview-zone", docs_wrappers_text)
        self.assertIn("domain-dns create-zone", docs_wrappers_text)
        self.assertIn("domain-dns update-zone", docs_wrappers_text)
        self.assertIn("domain-dns delete-zone", docs_wrappers_text)
        self.assertIn("dns-propagation get", docs_wrappers_text)
        self.assertIn("site-search search", docs_wrappers_text)
        self.assertIn("analytics-semantic-models list|get|query", docs_wrappers_text)
        self.assertIn("async-jobs get|list-items", docs_wrappers_text)
        self.assertIn("branches get-default|get|query", docs_wrappers_text)
        self.assertIn("locations list|query|get|create|update|archive|set-default", docs_wrappers_text)
        self.assertIn("tags list|get|create|update|delete", docs_wrappers_text)
        self.assertIn("app-instance get", docs_wrappers_text)
        self.assertIn("bi-event send", docs_wrappers_text)
        self.assertIn("embedded-scripts get", docs_wrappers_text)
        self.assertIn("embedded-scripts embed", docs_wrappers_text)
        self.assertIn("custom-embeds list|get|create|update|delete", docs_wrappers_text)
        self.assertIn("secrets list|get-value|create|patch|delete", docs_wrappers_text)
        self.assertIn(
            "sender-emails list|get|create|delete|get-or-create|send-verification-code|verify",
            docs_wrappers_text,
        )
        self.assertIn(
            "sender-details list|get|create|update|delete|get-default|mark-default",
            docs_wrappers_text,
        )
        self.assertIn("sending-domains get|query|authenticate", docs_wrappers_text)
        self.assertIn(
            "marketing-consent get|query|get-by-identifier|create|update|delete|upsert|bulk-upsert|remove",
            docs_wrappers_text,
        )
        self.assertIn(
            "referral-program get|get-premium-features|get-ai-social-media-posts-suggestions|activate|pause|generate-ai-social-media-posts-suggestions|update",
            docs_wrappers_text,
        )
        self.assertIn("referral-rewards get|query", docs_wrappers_text)
        self.assertIn("referring-customers get|query|get-by-referral-code|generate-for-contact|delete", docs_wrappers_text)
        self.assertIn("referred-friends get|query|get-by-contact-id|create|update|delete", docs_wrappers_text)
        self.assertIn("referral-tracker get|query|get-statistics", docs_wrappers_text)
        self.assertIn(
            "email-campaigns list|get|get-audience|list-statistics|list-recipients|pause-scheduling|reschedule|send-test|publish|reuse|delete|identify-sender-address",
            docs_wrappers_text,
        )
        self.assertIn(
            "donation-campaigns get|get-metrics|query|create|update|bulk-create|bulk-update|bulk-update-tags|bulk-update-tags-by-filter",
            docs_wrappers_text,
        )
        self.assertIn(
            "benefit-items get|list|query|count|create|update|delete|bulk-create|bulk-delete|bulk-update|bulk-delete-by-filter",
            docs_wrappers_text,
        )
        self.assertIn("balances get|list|query|change|revert-change", docs_wrappers_text)
        self.assertIn(
            "coupons get|query|create|update|delete|bulk-create|bulk-delete",
            docs_wrappers_text,
        )
        self.assertIn(
            "pricing-plans get|query|search|count|create|update|delete|bulk-update",
            docs_wrappers_text,
        )
        self.assertIn("orders search|get|create|update|cancel|bulk-update", docs_wrappers_text)
        self.assertIn(
            "bookings-time-slots-v2 list-availability|get-availability|list-event|get-event|list-multi-service|get-multi-service",
            docs_wrappers_text,
        )
        self.assertIn("Bookings Time Slots V2", docs_wrappers_text)
        self.assertIn(
            "bookings-services-v2 get|query|search|count|create|update|delete|bulk-create|bulk-update|bulk-update-by-filter|bulk-delete|bulk-delete-by-filter|query-policies|query-locations|query-categories|set-service-locations|enable-pricing-plans|disable-pricing-plans|set-custom-slug|validate-slug|clone|create-add-on-group|delete-add-on-group|list-add-on-groups-by-service-id|set-add-ons-for-group|update-add-on-group",
            docs_wrappers_text,
        )
        self.assertIn("Bookings Services V2", docs_wrappers_text)
        self.assertIn(
            "bookings-resources-v2 get|query|search|count|create|update|delete|bulk-create|bulk-update|bulk-delete",
            docs_wrappers_text,
        )
        self.assertIn("Bookings Resources V2", docs_wrappers_text)
        self.assertIn(
            "bookings-resource-types-v2 get|query|count|create|update|delete",
            docs_wrappers_text,
        )
        self.assertIn("Bookings Resource Types V2", docs_wrappers_text)
        self.assertIn(
            "bookings-policies get|query|count|strictest|create|update|delete|set-default",
            docs_wrappers_text,
        )
        self.assertIn("Booking Policies", docs_wrappers_text)
        self.assertIn("bookings-policy-snapshots list", docs_wrappers_text)
        self.assertIn("bookings-attendance get|query|count|set|bulk-set|delete|bulk-delete", docs_wrappers_text)
        self.assertIn("bookings-waitlist list|register|leave|book", docs_wrappers_text)
        self.assertIn("calendar-schedules-v3 get|query|create|update|cancel", docs_wrappers_text)
        self.assertIn("calendar-schedule-time-frames-v3 get|list", docs_wrappers_text)
        self.assertIn("calendar-events-v3 create|get|update|query|list|bulk-create|bulk-update|bulk-cancel|cancel|list-by-contact|list-by-member|restore-defaults|split-recurring", docs_wrappers_text)
        self.assertIn("calendar-events-v3 get|query|list|list-by-contact|list-by-member", docs_wrappers_text)
        self.assertIn("calendar-events-v3 cancel", docs_wrappers_text)
        self.assertIn("calendar-events-v3 bulk-update", docs_wrappers_text)
        self.assertIn("calendar-event-views-v3 get", docs_wrappers_text)
        self.assertIn(
            "bookings-external-calendars-v2 list-providers|connect-by-credentials|connect-by-oauth|list-connections|get-connection|update-sync-config|list-calendars|list-events|disconnect",
            docs_wrappers_text,
        )
        self.assertIn("bookings-service-options-v1 get|get-by-service-id|query|create|update|delete|clone", docs_wrappers_text)
        self.assertIn("Booking Policy Snapshots", docs_wrappers_text)
        self.assertIn("Bookings Attendance", docs_wrappers_text)
        self.assertIn("Bookings Waitlist", docs_wrappers_text)
        self.assertIn("Calendar Schedules V3", docs_wrappers_text)
        self.assertIn("Bookings External Calendar V2", docs_wrappers_text)
        self.assertIn("Bookings Service Options and Variants", docs_wrappers_text)
        self.assertIn("course-specific Bookings flow is not a separate official REST family", docs_wrappers_text)
        self.assertIn("bookedEntity.item.schedule.serviceId", docs_wrappers_text)
        self.assertIn("booking.bookedEntity.schedule.scheduleId", docs_wrappers_text)
        self.assertIn(
            "stores-products-v3 get|get-by-slug|get-all-products-category|query|search|count|create|update",
            docs_wrappers_text,
        )
        self.assertIn("read-only-variants-v3 query|search", docs_wrappers_text)
        self.assertIn("brands-v3 get|query", docs_wrappers_text)
        self.assertIn(
            "ribbons-v3 get|query|create|update|delete|bulk-create|bulk-delete|bulk-update|get-or-create|bulk-get-or-create",
            docs_wrappers_text,
        )
        self.assertIn(
            "stores-info-sections-v3 get|query|create|update|delete|bulk-create|bulk-delete|bulk-update|get-or-create|bulk-get-or-create",
            docs_wrappers_text,
        )
        self.assertIn(
            "customizations-v3 get|query|create|update|delete|bulk-create|bulk-update|add-choices|bulk-add-choices|remove-choices|set-choices",
            docs_wrappers_text,
        )
        self.assertIn(
            "stores-inventory-items-v3 get|query|search|create|update|delete",
            docs_wrappers_text,
        )
        self.assertIn("stores-locations-v3 get|query", docs_wrappers_text)
        self.assertIn("catalog-versioning get", docs_wrappers_text)
        self.assertIn(
            "order-billing get-order-refundability|calculate-refund|authorize-charge-with-saved-payment-method|capture-authorized-payments|void-authorized-payments|generate-receipts|redeem-gift-card|refund-payments",
            docs_wrappers_text,
        )
        self.assertIn("payments transactions-list", docs_wrappers_text)
        self.assertIn("gift-cards create|get|query|search|count|disable|send-email", docs_wrappers_text)
        self.assertIn("campaign-validation validate-link|validate-html-links", docs_wrappers_text)
        self.assertIn(
            "interactive-form-sessions create|create-streamed|send-message|send-message-streamed|generate-summary",
            docs_wrappers_text,
        )
        self.assertIn("intake-forms query|create-customer-submission-link|archive|unarchive|update-expiration-period|delete", docs_wrappers_text)
        self.assertIn("intake-form-submissions query|search|count-by-intake-form-ids|list-data-by-contacts|cancel|extend|exempt|delete", docs_wrappers_text)
        self.assertIn("community-groups list|get|get-by-slug|query|create|update|delete", docs_wrappers_text)
        self.assertIn("community-group-rules list|create-or-replace", docs_wrappers_text)
        self.assertIn("community-group-requests list|query|approve|reject", docs_wrappers_text)
        self.assertIn("community-group-members list|list-memberships|query|query-memberships|add|remove", docs_wrappers_text)
        self.assertIn("community-group-roles assign|unassign", docs_wrappers_text)
        self.assertIn("community-join-requests list|query|approve|reject", docs_wrappers_text)
        self.assertIn("community-membership-questions list|list-answers|create-or-replace", docs_wrappers_text)
        self.assertIn(
            "community-comments create|get|update|delete|moderate-draft-content|query|mark|unmark|hide|publish|count|list-by-resource|get-thread|bulk-publish|bulk-hide|bulk-delete|bulk-moderate-draft-content|bulk-move-by-filter",
            docs_wrappers_text,
        )
        self.assertIn("community-reports get|query|count-by-reason-types|create|update|upsert|delete|bulk-delete-by-filter", docs_wrappers_text)
        self.assertIn(
            "community-reviews get|query|count|create|update|delete|bulk-create|bulk-delete|remove-reply|set-reply|update-moderation-status|bulk-update-moderation-status",
            docs_wrappers_text,
        )
        self.assertIn(
            "community-review-requests create|get|delete|query|count|bulk-cancel-by-filter",
            docs_wrappers_text,
        )
        self.assertIn(
            "community-moderation-rules create|get|update|delete|query|check-content",
            docs_wrappers_text,
        )
        self.assertIn("inbox-conversations get|get-or-create", docs_wrappers_text)
        self.assertIn("inbox-messages list|send", docs_wrappers_text)
        self.assertIn(
            "loyalty-program get|premium-features|update|activate|pause|enable-points-expiration|disable-points-expiration",
            docs_wrappers_text,
        )
        self.assertIn(
            "loyalty-earning-rules list|get|create|update|delete|bulk-create|create-custom|delete-automation",
            docs_wrappers_text,
        )
        self.assertIn(
            "loyalty-tiers list|get|create|update|delete|bulk-create|get-program|create-program-settings|get-program-settings|update-program-settings",
            docs_wrappers_text,
        )
        self.assertIn(
            "loyalty-accounts list|get|query|search|count|get-program-totals|get-current-member-account|get-by-secondary-id|create|adjust-points|bulk-adjust-points|earn-points",
            docs_wrappers_text,
        )
        self.assertIn("loyalty-transactions get|query", docs_wrappers_text)
        self.assertIn("loyalty-social-media list|create", docs_wrappers_text)
        self.assertIn(
            "loyalty-imports get|query|create-file-url|create|execute|get-error-file-download-url",
            docs_wrappers_text,
        )
        self.assertIn("loyalty-rewards list|get|query|create|bulk-create|update|delete", docs_wrappers_text)
        self.assertIn("loyalty-checkout-discounts query|apply", docs_wrappers_text)
        self.assertIn(
            "loyalty-coupons get|query|get-current-member|redeem-current-member|redeem|delete",
            docs_wrappers_text,
        )
        self.assertIn("email-subscriptions query|upsert|bulk-upsert|generate-unsubscribe-link", docs_wrappers_text)
        self.assertIn("events-settings get|update", docs_wrappers_text)
        self.assertIn("portfolio-settings get|update", docs_wrappers_text)
        self.assertIn("portfolio-collections create|get|update|delete|query|list", docs_wrappers_text)
        self.assertIn("portfolio-projects create|get|update|delete|query|list|bulk-update", docs_wrappers_text)
        self.assertIn(
            "portfolio-project-items create|get|update|delete|list|bulk-create|bulk-update|bulk-delete|duplicate",
            docs_wrappers_text,
        )
        self.assertIn(
            "suppliers-hub-products get|query|search|query-categories|create|update|delete|bulk-create|bulk-update|bulk-delete|bulk-add-to-store|bulk-update-tags|bulk-update-tags-by-filter",
            docs_wrappers_text,
        )
        self.assertIn(
            "suppliers-hub-suppliers get|query|create|update|delete|bulk-create|bulk-update|bulk-delete|bulk-update-tags|bulk-update-tags-by-filter",
            docs_wrappers_text,
        )
        self.assertIn("suppliers-hub-marketplace-provider-submissions submit-generated-mockups", docs_wrappers_text)
        self.assertIn("bi-event send", command_reference_text)
        self.assertIn("embedded-scripts get", command_reference_text)
        self.assertIn("embedded-scripts embed", command_reference_text)
        self.assertIn("custom-embeds list", command_reference_text)
        self.assertIn("custom-embeds get", command_reference_text)
        self.assertIn("custom-embeds create", command_reference_text)
        self.assertIn("custom-embeds update", command_reference_text)
        self.assertIn("custom-embeds delete", command_reference_text)
        self.assertIn("secrets list", command_reference_text)
        self.assertIn("secrets get-value", command_reference_text)
        self.assertIn("secrets create", command_reference_text)
        self.assertIn("secrets patch", command_reference_text)
        self.assertIn("secrets delete", command_reference_text)
        self.assertIn("sender-emails list", command_reference_text)
        self.assertIn("sender-emails get", command_reference_text)
        self.assertIn("sender-emails create", command_reference_text)
        self.assertIn("sender-emails delete", command_reference_text)
        self.assertIn("sender-emails get-or-create", command_reference_text)
        self.assertIn("sender-emails send-verification-code", command_reference_text)
        self.assertIn("sender-emails verify", command_reference_text)
        self.assertIn("sender-details list", command_reference_text)
        self.assertIn("sender-details get", command_reference_text)
        self.assertIn("sender-details create", command_reference_text)
        self.assertIn("sender-details update", command_reference_text)
        self.assertIn("sender-details delete", command_reference_text)
        self.assertIn("sender-details get-default", command_reference_text)
        self.assertIn("sender-details mark-default", command_reference_text)
        self.assertIn("sending-domains get", command_reference_text)
        self.assertIn("sending-domains query", command_reference_text)
        self.assertIn("sending-domains authenticate", command_reference_text)
        self.assertIn("marketing-consent get", command_reference_text)
        self.assertIn("marketing-consent query", command_reference_text)
        self.assertIn("marketing-consent get-by-identifier", command_reference_text)
        self.assertIn("marketing-consent create", command_reference_text)
        self.assertIn("marketing-consent update", command_reference_text)
        self.assertIn("marketing-consent delete", command_reference_text)
        self.assertIn("marketing-consent upsert", command_reference_text)
        self.assertIn("marketing-consent bulk-upsert", command_reference_text)
        self.assertIn("marketing-consent remove", command_reference_text)
        self.assertIn("referral-program get", command_reference_text)
        self.assertIn("referral-program get-premium-features", command_reference_text)
        self.assertIn("referral-program get-ai-social-media-posts-suggestions", command_reference_text)
        self.assertIn("referral-program activate", command_reference_text)
        self.assertIn("referral-program pause", command_reference_text)
        self.assertIn("referral-program generate-ai-social-media-posts-suggestions", command_reference_text)
        self.assertIn("referral-program update", command_reference_text)
        self.assertIn("referral-rewards get", command_reference_text)
        self.assertIn("referral-rewards query", command_reference_text)
        self.assertIn("referring-customers get", command_reference_text)
        self.assertIn("referring-customers query", command_reference_text)
        self.assertIn("referring-customers get-by-referral-code", command_reference_text)
        self.assertIn("referring-customers generate-for-contact", command_reference_text)
        self.assertIn("referring-customers delete", command_reference_text)
        self.assertIn("referred-friends get", command_reference_text)
        self.assertIn("referred-friends query", command_reference_text)
        self.assertIn("referred-friends get-by-contact-id", command_reference_text)
        self.assertIn("referred-friends create", command_reference_text)
        self.assertIn("referred-friends update", command_reference_text)
        self.assertIn("referred-friends delete", command_reference_text)
        self.assertIn("referral-tracker get", command_reference_text)
        self.assertIn("referral-tracker query", command_reference_text)
        self.assertIn("referral-tracker get-statistics", command_reference_text)
        self.assertIn("email-campaigns list", command_reference_text)
        self.assertIn("email-campaigns get", command_reference_text)
        self.assertIn("email-campaigns get-audience", command_reference_text)
        self.assertIn("email-campaigns list-statistics", command_reference_text)
        self.assertIn("email-campaigns list-recipients", command_reference_text)
        self.assertIn("email-campaigns pause-scheduling", command_reference_text)
        self.assertIn("email-campaigns reschedule", command_reference_text)
        self.assertIn("email-campaigns send-test", command_reference_text)
        self.assertIn("email-campaigns publish", command_reference_text)
        self.assertIn("email-campaigns reuse", command_reference_text)
        self.assertIn("email-campaigns delete", command_reference_text)
        self.assertIn("email-campaigns identify-sender-address", command_reference_text)
        self.assertIn("donation-campaigns get", command_reference_text)
        self.assertIn("donation-campaigns get-metrics", command_reference_text)
        self.assertIn("donation-campaigns query", command_reference_text)
        self.assertIn("donation-campaigns create", command_reference_text)
        self.assertIn("donation-campaigns update", command_reference_text)
        self.assertIn("donation-campaigns bulk-create", command_reference_text)
        self.assertIn("donation-campaigns bulk-update", command_reference_text)
        self.assertIn("donation-campaigns bulk-update-tags", command_reference_text)
        self.assertIn("donation-campaigns bulk-update-tags-by-filter", command_reference_text)
        self.assertIn("benefit-items get", command_reference_text)
        self.assertIn("benefit-items list", command_reference_text)
        self.assertIn("benefit-items query", command_reference_text)
        self.assertIn("benefit-items count", command_reference_text)
        self.assertIn("benefit-items create", command_reference_text)
        self.assertIn("benefit-items update", command_reference_text)
        self.assertIn("benefit-items delete", command_reference_text)
        self.assertIn("benefit-items bulk-create", command_reference_text)
        self.assertIn("benefit-items bulk-delete", command_reference_text)
        self.assertIn("benefit-items bulk-update", command_reference_text)
        self.assertIn("benefit-items bulk-delete-by-filter", command_reference_text)
        self.assertIn("balances get", command_reference_text)
        self.assertIn("balances list", command_reference_text)
        self.assertIn("balances query", command_reference_text)
        self.assertIn("balances change", command_reference_text)
        self.assertIn("balances revert-change", command_reference_text)
        self.assertIn("coupons get", command_reference_text)
        self.assertIn("coupons query", command_reference_text)
        self.assertIn("coupons create", command_reference_text)
        self.assertIn("coupons update", command_reference_text)
        self.assertIn("coupons delete", command_reference_text)
        self.assertIn("coupons bulk-create", command_reference_text)
        self.assertIn("coupons bulk-delete", command_reference_text)
        self.assertIn("pricing-plans get", command_reference_text)
        self.assertIn("pricing-plans query", command_reference_text)
        self.assertIn("pricing-plans search", command_reference_text)
        self.assertIn("pricing-plans count", command_reference_text)
        self.assertIn("pricing-plans create", command_reference_text)
        self.assertIn("pricing-plans update", command_reference_text)
        self.assertIn("pricing-plans delete", command_reference_text)
        self.assertIn("pricing-plans bulk-update", command_reference_text)
        self.assertIn("orders search", command_reference_text)
        self.assertIn("orders get", command_reference_text)
        self.assertIn("orders create", command_reference_text)
        self.assertIn("orders update", command_reference_text)
        self.assertIn("orders cancel", command_reference_text)
        self.assertIn("orders bulk-update", command_reference_text)
        self.assertIn("stores-products-v3 get", command_reference_text)
        self.assertIn("stores-products-v3 get-by-slug", command_reference_text)
        self.assertIn("stores-products-v3 get-all-products-category", command_reference_text)
        self.assertIn("stores-products-v3 query", command_reference_text)
        self.assertIn("stores-products-v3 search", command_reference_text)
        self.assertIn("stores-products-v3 count", command_reference_text)
        self.assertIn("stores-products-v3 create", command_reference_text)
        self.assertIn("stores-products-v3 update", command_reference_text)
        self.assertIn("read-only-variants-v3 query", command_reference_text)
        self.assertIn("read-only-variants-v3 search", command_reference_text)
        self.assertIn("brands-v3 get", command_reference_text)
        self.assertIn("brands-v3 query", command_reference_text)
        self.assertIn("brands-v3 create", command_reference_text)
        self.assertIn("brands-v3 update", command_reference_text)
        self.assertIn("brands-v3 delete", command_reference_text)
        self.assertIn("brands-v3 bulk-create", command_reference_text)
        self.assertIn("brands-v3 bulk-delete", command_reference_text)
        self.assertIn("brands-v3 bulk-update", command_reference_text)
        self.assertIn("brands-v3 get-or-create", command_reference_text)
        self.assertIn("brands-v3 bulk-get-or-create", command_reference_text)
        self.assertIn("ribbons-v3 get", command_reference_text)
        self.assertIn("ribbons-v3 query", command_reference_text)
        self.assertIn("ribbons-v3 create", command_reference_text)
        self.assertIn("ribbons-v3 update", command_reference_text)
        self.assertIn("ribbons-v3 delete", command_reference_text)
        self.assertIn("ribbons-v3 bulk-create", command_reference_text)
        self.assertIn("ribbons-v3 bulk-delete", command_reference_text)
        self.assertIn("ribbons-v3 bulk-update", command_reference_text)
        self.assertIn("ribbons-v3 get-or-create", command_reference_text)
        self.assertIn("ribbons-v3 bulk-get-or-create", command_reference_text)
        self.assertIn("stores-info-sections-v3 get", command_reference_text)
        self.assertIn("stores-info-sections-v3 query", command_reference_text)
        self.assertIn("stores-info-sections-v3 create", command_reference_text)
        self.assertIn("stores-info-sections-v3 update", command_reference_text)
        self.assertIn("stores-info-sections-v3 delete", command_reference_text)
        self.assertIn("stores-info-sections-v3 bulk-create", command_reference_text)
        self.assertIn("stores-info-sections-v3 bulk-delete", command_reference_text)
        self.assertIn("stores-info-sections-v3 bulk-update", command_reference_text)
        self.assertIn("stores-info-sections-v3 get-or-create", command_reference_text)
        self.assertIn("stores-info-sections-v3 bulk-get-or-create", command_reference_text)
        self.assertIn("customizations-v3 get", command_reference_text)
        self.assertIn("customizations-v3 query", command_reference_text)
        self.assertIn("customizations-v3 create", command_reference_text)
        self.assertIn("customizations-v3 update", command_reference_text)
        self.assertIn("customizations-v3 delete", command_reference_text)
        self.assertIn("customizations-v3 bulk-create", command_reference_text)
        self.assertIn("customizations-v3 bulk-update", command_reference_text)
        self.assertIn("customizations-v3 add-choices", command_reference_text)
        self.assertIn("customizations-v3 bulk-add-choices", command_reference_text)
        self.assertIn("customizations-v3 remove-choices", command_reference_text)
        self.assertIn("customizations-v3 set-choices", command_reference_text)
        self.assertIn("stores-inventory-items-v3 get", command_reference_text)
        self.assertIn("stores-inventory-items-v3 query", command_reference_text)
        self.assertIn("stores-inventory-items-v3 search", command_reference_text)
        self.assertIn("stores-inventory-items-v3 create", command_reference_text)
        self.assertIn("stores-inventory-items-v3 update", command_reference_text)
        self.assertIn("stores-inventory-items-v3 delete", command_reference_text)
        self.assertIn("stores-locations-v3 get", command_reference_text)
        self.assertIn("stores-locations-v3 query", command_reference_text)
        self.assertIn("catalog-versioning get", command_reference_text)
        self.assertIn("bookings-time-slots-v2 list-availability", command_reference_text)
        self.assertIn("bookings-time-slots-v2 get-availability", command_reference_text)
        self.assertIn("bookings-time-slots-v2 list-event", command_reference_text)
        self.assertIn("bookings-time-slots-v2 get-event", command_reference_text)
        self.assertIn("bookings-time-slots-v2 list-multi-service", command_reference_text)
        self.assertIn("bookings-time-slots-v2 get-multi-service", command_reference_text)
        self.assertIn("bookings-reader-v2 query-extended-bookings", docs_wrappers_text)
        self.assertIn("bookings-reader-v2 count-extended-bookings", docs_wrappers_text)
        self.assertIn("bookings-reader-v2 query-extended-bookings", command_reference_text)
        self.assertIn("bookings-reader-v2 count-extended-bookings", command_reference_text)
        self.assertIn("bookings-services-v2 get", command_reference_text)
        self.assertIn("bookings-services-v2 create", command_reference_text)
        self.assertIn("bookings-services-v2 set-service-locations", command_reference_text)
        self.assertIn("bookings-services-v2 list-add-on-groups-by-service-id", command_reference_text)
        self.assertIn("bookings-resources-v2 get", command_reference_text)
        self.assertIn("bookings-resources-v2 bulk-delete", command_reference_text)
        self.assertIn("bookings-resource-types-v2 get", command_reference_text)
        self.assertIn("bookings-resource-types-v2 delete", command_reference_text)
        self.assertIn("order-billing get-order-refundability", command_reference_text)
        self.assertIn("order-billing calculate-refund", command_reference_text)
        self.assertIn("order-billing authorize-charge-with-saved-payment-method", command_reference_text)
        self.assertIn("order-billing capture-authorized-payments", command_reference_text)
        self.assertIn("order-billing void-authorized-payments", command_reference_text)
        self.assertIn("order-billing generate-receipts", command_reference_text)
        self.assertIn("order-billing redeem-gift-card", command_reference_text)
        self.assertIn("order-billing refund-payments", command_reference_text)
        self.assertIn("payments transactions-list", command_reference_text)
        self.assertIn("gift-cards create", command_reference_text)
        self.assertIn("gift-cards get", command_reference_text)
        self.assertIn("gift-cards query", command_reference_text)
        self.assertIn("gift-cards search", command_reference_text)
        self.assertIn("gift-cards count", command_reference_text)
        self.assertIn("gift-cards disable", command_reference_text)
        self.assertIn("gift-cards send-email", command_reference_text)
        self.assertIn("campaign-validation validate-link", command_reference_text)
        self.assertIn("campaign-validation validate-html-links", command_reference_text)
        self.assertIn("events-settings get", command_reference_text)
        self.assertIn("events-settings update", command_reference_text)
        self.assertIn("portfolio-settings get", command_reference_text)
        self.assertIn("portfolio-settings update", command_reference_text)
        self.assertIn("portfolio-collections create", command_reference_text)
        self.assertIn("portfolio-collections update", command_reference_text)
        self.assertIn("portfolio-collections delete", command_reference_text)
        self.assertIn("portfolio-projects create", command_reference_text)
        self.assertIn("portfolio-projects bulk-update", command_reference_text)
        self.assertIn("portfolio-projects delete", command_reference_text)
        self.assertIn("portfolio-project-items create", command_reference_text)
        self.assertIn("portfolio-project-items bulk-delete", command_reference_text)
        self.assertIn("portfolio-project-items duplicate", command_reference_text)
        self.assertIn("suppliers-hub-products create", command_reference_text)
        self.assertIn("suppliers-hub-products bulk-add-to-store", command_reference_text)
        self.assertIn("suppliers-hub-products bulk-update-tags-by-filter", command_reference_text)
        self.assertIn("suppliers-hub-suppliers create", command_reference_text)
        self.assertIn("suppliers-hub-suppliers bulk-update", command_reference_text)
        self.assertIn("suppliers-hub-suppliers bulk-update-tags-by-filter", command_reference_text)
        self.assertIn("suppliers-hub-marketplace-provider-submissions submit-generated-mockups", command_reference_text)
        self.assertIn("events-v3 create", command_reference_text)
        self.assertIn("events-v3 bulk-cancel-by-filter", command_reference_text)
        self.assertIn("events-v3 publish-draft", command_reference_text)
        self.assertIn("events-v3 list-by-category", docs_wrappers_text)
        self.assertIn("events-v3 bulk-delete-by-filter", skill_text)
        self.assertIn("calendar-events-v3 create", command_reference_text)
        self.assertIn("calendar-events-v3 split-recurring", command_reference_text)
        self.assertIn("list-by-contact|list-by-member", docs_wrappers_text)
        self.assertIn("calendar-events-v3 bulk-cancel", skill_text)
        self.assertIn("calendar-event-views-v3 get", command_reference_text)
        self.assertIn("calendar-event-views-v3 get", skill_text)
        self.assertIn("calendar-participations-v3 create", command_reference_text)
        self.assertIn("calendar-participations-v3 delete", command_reference_text)
        self.assertIn("calendar-participations-v3 create|get|update|delete|query", docs_wrappers_text)
        self.assertIn("calendar-participations-v3 get|query", docs_wrappers_text)
        self.assertIn("calendar-participations-v3 delete", docs_wrappers_text)
        self.assertIn("calendar-participations-v3 create", skill_text)
        self.assertIn("Wix Bookings-managed participation details", skill_text)
        self.assertIn("There is no `calendar-skills` command", command_reference_text)
        self.assertIn("Calendar Skills / default business hours is docs-only", docs_wrappers_text)
        self.assertIn("Calendar Skills / default business hours is docs-only", skill_text)
        self.assertIn("4e0579a5-491e-4e70-a872-d097eed6e520", command_reference_text)
        self.assertNotIn("calendar-skills get", command_reference_text)
        self.assertIn("There is no `captcha authorize` command", command_reference_text)
        self.assertIn("Captcha is gated and non-callable", docs_wrappers_text)
        self.assertIn("Captcha is gated and non-callable", skill_text)
        self.assertIn("/captcharator/api/v1/authorize", skill_text)
        self.assertNotIn("captcha authorize --", command_reference_text)
        self.assertIn("cookie-consent-policy update-cookie-banner-settings", command_reference_text)
        self.assertIn("cookie-consent-policy bulk-update-consent-config-tags-by-filter", command_reference_text)
        self.assertIn("cookie-consent-policy get-cookie-banner-settings|update-cookie-banner-settings", docs_wrappers_text)
        self.assertIn("cookie-consent-policy delete-consent-config", skill_text)
        self.assertIn("bulk-update-consent-configs` as Developer Preview", command_reference_text)
        self.assertIn("dashboard-favorite-list create", command_reference_text)
        self.assertIn("dashboard-favorite-list delete-favorite", command_reference_text)
        self.assertIn("dashboard-favorite-list create|update|delete|add-favorite|delete-favorite|get", docs_wrappers_text)
        self.assertIn("dashboard-favorite-list delete", skill_text)
        self.assertIn("faq-category-v2 create", command_reference_text)
        self.assertIn("faq-question-entry-v2 bulk-update", command_reference_text)
        self.assertIn("faq-category-v2 create|get|update|delete|query|list|update-extended-fields", docs_wrappers_text)
        self.assertIn("faq-question-entry-v2 bulk-delete", skill_text)
        self.assertIn("functions-v1 bulk-update-tags-by-filter", command_reference_text)
        self.assertIn("functions-v1 create|get|update|delete|query|bulk-update-tags|bulk-update-tags-by-filter", docs_wrappers_text)
        self.assertIn("functions-v1 delete", skill_text)
        self.assertIn("function-types query", command_reference_text)
        self.assertIn("function-types get|query", docs_wrappers_text)
        self.assertIn("function-types query", skill_text)
        self.assertIn("favoriteList.revision", command_reference_text)
        self.assertIn("events-ticket-definitions-v3 create", command_reference_text)
        self.assertIn("events-ticket-definitions-v3 bulk-delete-by-filter", command_reference_text)
        self.assertIn("events-ticket-definitions-v3 change-currency", docs_wrappers_text)
        self.assertIn("events-ticket-definitions-v3 reorder", skill_text)
        self.assertIn("events-categories create", command_reference_text)
        self.assertIn("events-categories bulk-assign-events", command_reference_text)
        self.assertIn("events-categories unassign-events", docs_wrappers_text)
        self.assertIn("events-categories reorder-events", skill_text)
        self.assertIn("events-schedule-items get", command_reference_text)
        self.assertIn("events-schedule-items delete", command_reference_text)
        self.assertIn("events-schedule-items publish-draft", docs_wrappers_text)
        self.assertIn("events-schedule-items reschedule-draft", skill_text)
        self.assertIn("events-policies-v2 create", command_reference_text)
        self.assertIn("events-policies-v2 delete", command_reference_text)
        self.assertIn("events-policies-v2 reorder", docs_wrappers_text)
        self.assertIn("events-policies-v2 update", skill_text)
        self.assertIn("events-staff-members create", command_reference_text)
        self.assertIn("events-staff-members delete", command_reference_text)
        self.assertIn("events-staff-members query", docs_wrappers_text)
        self.assertIn("events-staff-members update", skill_text)
        self.assertIn("events-guests query", command_reference_text)
        self.assertIn("events-guests query", docs_wrappers_text)
        self.assertIn("events-guests query", skill_text)
        self.assertIn("events-rsvps-v2 create", command_reference_text)
        self.assertIn("events-rsvps-v2 bulk-delete-by-filter", command_reference_text)
        self.assertIn("events-rsvps-v2 list-summary", docs_wrappers_text)
        self.assertIn("events-rsvps-v2 cancel-check-in", skill_text)
        self.assertIn("events-ticket-reservations create", command_reference_text)
        self.assertIn("events-ticket-reservations bulk-update-tags-by-filter", command_reference_text)
        self.assertIn("events-ticket-reservations get", docs_wrappers_text)
        self.assertIn("events-ticket-reservations cancel", skill_text)
        self.assertIn("events-tickets get", command_reference_text)
        self.assertIn("events-tickets bulk-update", command_reference_text)
        self.assertIn("events-tickets check-in", docs_wrappers_text)
        self.assertIn("events-tickets delete-check-in", skill_text)
        self.assertIn("events-orders list", command_reference_text)
        self.assertIn("events-orders checkout", command_reference_text)
        self.assertIn("events-orders query-available-tickets", docs_wrappers_text)
        self.assertIn("events-orders confirm", skill_text)
        self.assertIn("events-forms get-form", command_reference_text)
        self.assertIn("events-forms delete-control", command_reference_text)
        self.assertIn("events-forms add-control", docs_wrappers_text)
        self.assertIn("events-forms publish-draft", skill_text)
        self.assertIn("restaurants-menus list", command_reference_text)
        self.assertIn("restaurants-menus delete", command_reference_text)
        self.assertIn("restaurants-menus create", docs_wrappers_text)
        self.assertIn("restaurants-menus bulk-update", skill_text)
        self.assertIn("restaurants-sections list", command_reference_text)
        self.assertIn("restaurants-sections bulk-delete", command_reference_text)
        self.assertIn("restaurants-sections create", docs_wrappers_text)
        self.assertIn("restaurants-sections bulk-update", skill_text)
        self.assertIn("restaurants-items search", command_reference_text)
        self.assertIn("restaurants-items bulk-delete", command_reference_text)
        self.assertIn("restaurants-items create", docs_wrappers_text)
        self.assertIn("restaurants-items bulk-update", skill_text)
        self.assertIn("restaurants-item-labels query", command_reference_text)
        self.assertIn("restaurants-item-labels delete", docs_wrappers_text)
        self.assertIn("restaurants-item-labels update", skill_text)
        self.assertIn("restaurants-item-variants count", command_reference_text)
        self.assertIn("restaurants-item-variants bulk-delete", docs_wrappers_text)
        self.assertIn("restaurants-item-variants bulk-update", skill_text)
        self.assertIn("restaurants-item-modifiers count", command_reference_text)
        self.assertIn("restaurants-item-modifiers bulk-delete", docs_wrappers_text)
        self.assertIn("restaurants-item-modifiers bulk-update", skill_text)
        self.assertIn("restaurants-item-modifier-groups count", command_reference_text)
        self.assertIn("restaurants-item-modifier-groups delete", docs_wrappers_text)
        self.assertIn("restaurants-item-modifier-groups bulk-update", skill_text)
        self.assertIn("restaurants-online-order-operation-groups query", command_reference_text)
        self.assertIn("restaurants-online-order-operation-groups bulk-delete", docs_wrappers_text)
        self.assertIn("restaurants-online-order-operation-groups bulk-update-tags-by-filter", skill_text)
        self.assertIn("restaurants-online-order-operations available-dates-in-range", command_reference_text)
        self.assertIn("restaurants-online-order-operations delete", docs_wrappers_text)
        self.assertIn("restaurants-online-order-operations bulk-update-tags-by-filter", skill_text)
        self.assertIn("restaurants-online-order-menu-ordering-settings list-menus-availability-status", command_reference_text)
        self.assertIn("restaurants-online-order-menu-ordering-settings bulk-update-tags-by-filter", docs_wrappers_text)
        self.assertIn("restaurants-online-order-menu-ordering-settings upsert-by-menu-id", skill_text)
        self.assertIn("restaurants-online-order-fulfillment-methods list-available-for-address", command_reference_text)
        self.assertIn("restaurants-online-order-fulfillment-methods bulk-update-tags-by-filter", docs_wrappers_text)
        self.assertIn("restaurants-online-order-fulfillment-methods get-combined-availability", skill_text)
        self.assertIn("restaurants-online-order-availability-exceptions bulk-update", command_reference_text)
        self.assertIn("restaurants-online-order-availability-exceptions bulk-update-tags-by-filter", docs_wrappers_text)
        self.assertIn("restaurants-online-order-availability-exceptions delete", skill_text)
        self.assertIn("restaurants-online-order-service-fees calculate", command_reference_text)
        self.assertIn("restaurants-online-order-service-fees bulk-delete", docs_wrappers_text)
        self.assertIn("restaurants-online-order-service-fees bulk-update-tags-by-filter", skill_text)
        self.assertIn("restaurants-online-order-notification-recipients bulk-update", command_reference_text)
        self.assertIn("restaurants-online-order-notification-recipients bulk-delete", docs_wrappers_text)
        self.assertIn("restaurants-online-order-notification-recipients bulk-update-tags-by-filter", skill_text)
        self.assertIn("restaurants-reservations create-held", command_reference_text)
        self.assertIn("restaurants-reservations cancel", docs_wrappers_text)
        self.assertIn("restaurants-reservations reserve", skill_text)
        self.assertIn("restaurants-reservation-locations update", command_reference_text)
        self.assertIn("restaurants-reservation-locations get", docs_wrappers_text)
        self.assertIn("restaurants-reservation-locations list", skill_text)
        self.assertIn("restaurants-reservation-time-slots get-scheduled", command_reference_text)
        self.assertIn("restaurants-reservation-time-slots check", docs_wrappers_text)
        self.assertIn("restaurants-reservation-time-slots get", skill_text)
        self.assertIn("restaurants-reservation-experiences get-by-slug", command_reference_text)
        self.assertIn("restaurants-reservation-experiences bulk-update-tags-by-filter", docs_wrappers_text)
        self.assertIn("restaurants-reservation-experiences update", skill_text)
        self.assertIn("blog-posts-stats get-by-slug", command_reference_text)
        self.assertIn("blog-posts-stats get-total", docs_wrappers_text)
        self.assertIn("blog-posts-stats query-count", skill_text)
        self.assertIn("blog-draft-posts bulk-delete", command_reference_text)
        self.assertIn("blog-draft-posts remove-from-trash-bin", docs_wrappers_text)
        self.assertIn("blog-draft-posts restore-from-trash-bin", skill_text)
        self.assertIn("blog-categories get-by-slug", command_reference_text)
        self.assertIn("blog-categories delete", docs_wrappers_text)
        self.assertIn("blog-categories query", skill_text)
        self.assertIn("blog-tags get-by-label", command_reference_text)
        self.assertIn("blog-tags delete", docs_wrappers_text)
        self.assertIn("blog-tags get-by-slug", skill_text)
        self.assertIn("blog-likes delete-by-fqdn-entity-id", command_reference_text)
        self.assertIn("blog-likes delete", docs_wrappers_text)
        self.assertIn("blog-likes query", skill_text)
        self.assertIn("Disabled Wix Forum", command_reference_text)
        self.assertIn("Forum is intentionally disabled", docs_wrappers_text)
        self.assertIn("Forum is intentionally disabled", skill_text)
        self.assertNotIn("forum-categories get", command_reference_text)
        self.assertNotIn("forum-posts get", command_reference_text)
        self.assertIn("There is no `media-skills` command", command_reference_text)
        self.assertIn("Wix Skills / Media skills is docs-only", docs_wrappers_text)
        self.assertIn("Wix Skills / Media skills is docs-only", skill_text)
        self.assertIn("There is no `sites-skills` command", command_reference_text)
        self.assertIn("Account Level Sites Skills is docs-only", docs_wrappers_text)
        self.assertIn("Account Level Sites Skills is docs-only", skill_text)
        self.assertNotIn("sites-skills query", command_reference_text)
        self.assertNotIn("sites-skills create", command_reference_text)
        self.assertIn("resellers create-package", command_reference_text)
        self.assertIn("resellers cancel-product-instance", command_reference_text)
        self.assertIn("`resellers` covers the official Account Level Resellers", docs_wrappers_text)
        self.assertIn("`resellers` covers the official Account Level Resellers", skill_text)
        self.assertIn("multilingual-locale-settings set-mode", command_reference_text)
        self.assertIn("`multilingual-locale-settings` covers the official Wix Multilingual", docs_wrappers_text)
        self.assertIn("`multilingual-locale-settings` covers the official Wix Multilingual", skill_text)
        self.assertIn("multilingual-locales create-new-primary", command_reference_text)
        self.assertIn("`multilingual-locales` covers the official Wix Multilingual", docs_wrappers_text)
        self.assertIn("`multilingual-locales` covers the official Wix Multilingual", skill_text)
        self.assertIn("multilingual-translation-schemas get-by-key", command_reference_text)
        self.assertIn("`multilingual-translation-schemas` covers the official Wix Multilingual", docs_wrappers_text)
        self.assertIn("`multilingual-translation-schemas` covers the official Wix Multilingual", skill_text)
        self.assertIn("multilingual-translation-contents bulk-update-by-key", command_reference_text)
        self.assertIn("`multilingual-translation-contents` covers the official Wix Multilingual", docs_wrappers_text)
        self.assertIn("`multilingual-translation-contents` covers the official Wix Multilingual", skill_text)
        self.assertIn("multilingual-translation-published-contents query", command_reference_text)
        self.assertIn("`multilingual-translation-published-contents` covers the official Wix Multilingual", docs_wrappers_text)
        self.assertIn("`multilingual-translation-published-contents` covers the official Wix Multilingual", skill_text)
        self.assertIn("multilingual-machine-translation bulk-translate", command_reference_text)
        self.assertIn("`multilingual-machine-translation` covers the official Wix Multilingual", docs_wrappers_text)
        self.assertIn("`multilingual-machine-translation` covers the official Wix Multilingual", skill_text)
        self.assertIn("multilingual-machine-translation-credit-data check-sufficient", command_reference_text)
        self.assertIn("`multilingual-machine-translation-credit-data` covers the official Wix Multilingual", docs_wrappers_text)
        self.assertIn("`multilingual-machine-translation-credit-data` covers the official Wix Multilingual", skill_text)
        self.assertIn("online-programs-programs bulk-update", command_reference_text)
        self.assertIn("`online-programs-programs` covers the official Wix Online Programs", docs_wrappers_text)
        self.assertIn("`online-programs-programs` covers the official Wix Online Programs", skill_text)
        self.assertIn("online-programs-instructor-v2 change-program-instructors", command_reference_text)
        self.assertIn("`online-programs-instructor-v2` covers the official Wix Online Programs", docs_wrappers_text)
        self.assertIn("`online-programs-instructor-v2` covers the official Wix Online Programs", skill_text)
        self.assertIn("b2b-site-transfer transfer", command_reference_text)
        self.assertIn("`b2b-site-transfer` covers the official Wix B2B Site Management", docs_wrappers_text)
        self.assertIn("`b2b-site-transfer` covers the official Wix B2B Site Management", skill_text)
        self.assertIn("partner-profiles find-public-by-slug", command_reference_text)
        self.assertIn("`partner-profiles` covers the official Developer Preview Wix Partner Profile", docs_wrappers_text)
        self.assertIn("`partner-profiles` covers the official Developer Preview Wix Partner Profile", skill_text)
        self.assertIn("viewer-seo-tags resolve-static", command_reference_text)
        self.assertIn("`viewer-cache` and `viewer-seo-tags` cover the official Wix Viewer", docs_wrappers_text)
        self.assertIn("`viewer-cache` and `viewer-seo-tags` cover the official Wix Viewer", skill_text)
        self.assertIn("There is no `wix-safe-agent-cli graphql` command", command_reference_text)
        self.assertIn("GraphQL is docs-only/non-callable", docs_wrappers_text)
        self.assertIn("GraphQL is docs-only/non-callable", skill_text)
        self.assertIn("There is no generic async job runner command", command_reference_text)
        self.assertIn("Generic async job runner is docs-only/non-callable", docs_wrappers_text)
        self.assertIn("Generic async job runner is docs-only/non-callable", skill_text)
        self.assertIn("There is no generic `http-functions call` command", command_reference_text)
        self.assertIn("HTTP Functions is site-defined and non-callable", docs_wrappers_text)
        self.assertIn("HTTP Functions is site-defined and non-callable", skill_text)
        self.assertIn("rich-content-ricos convert-from", command_reference_text)
        self.assertIn("rich-content-ricos validate", command_reference_text)
        self.assertIn("rich-content-ricos validate", skill_text)
        self.assertIn("pro-gallery create-gallery", command_reference_text)
        self.assertIn("pro-gallery bulk-delete-gallery-items", command_reference_text)
        self.assertIn("pro-gallery bulk-delete-gallery-items", skill_text)
        self.assertIn("Developer Preview", command_reference_text)
        self.assertIn("Manage Events", command_reference_text)
        self.assertIn("market-listing search", docs_wrappers_text)
        self.assertIn("editor-deep-link create", docs_wrappers_text)
        self.assertIn("editor-deep-link create", command_reference_text)
        self.assertIn("site-plugins get-placement-status", docs_wrappers_text)
        self.assertIn("app-permissions list", docs_wrappers_text)
        self.assertIn("app-permissions create", docs_wrappers_text)
        self.assertIn("app-permissions delete", docs_wrappers_text)
        self.assertIn("contact-labels query", docs_wrappers_text)
        self.assertIn("contacts list|get|query|list-facets|query-facets|get-bulk-job|preview-merge|create|update|delete|merge|label|unlabel|bulk-delete|bulk-update|bulk-label-unlabel", docs_wrappers_text)
        self.assertIn("contacts bulk-label-unlabel", docs_wrappers_text)
        self.assertIn("contact-labels list", docs_wrappers_text)
        self.assertIn("contact-labels find-or-create", docs_wrappers_text)
        self.assertIn("contact-labels get", docs_wrappers_text)
        self.assertIn("contact-labels update", docs_wrappers_text)
        self.assertIn("contact-labels delete", docs_wrappers_text)
        self.assertIn("contact-notes get", docs_wrappers_text)
        self.assertIn("contact-notes query", docs_wrappers_text)
        self.assertIn("contact-notes create", docs_wrappers_text)
        self.assertIn("contact-notes update", docs_wrappers_text)
        self.assertIn("contact-notes delete", docs_wrappers_text)
        self.assertIn("contact-attachments get", docs_wrappers_text)
        self.assertIn("contact-attachments list", docs_wrappers_text)
        self.assertIn("contact-attachments generate-upload-url", docs_wrappers_text)
        self.assertIn("contact-attachments delete", docs_wrappers_text)
        self.assertIn("data-permissions get", docs_wrappers_text)
        self.assertIn("data-permissions get-my", docs_wrappers_text)
        self.assertIn("data-permissions update", docs_wrappers_text)
        self.assertIn("data-permissions add-special", docs_wrappers_text)
        self.assertIn("data-permissions update-special", docs_wrappers_text)
        self.assertIn("data-permissions remove-special", docs_wrappers_text)
        self.assertIn(
            "data-permissions get|get-my|update|add-special|update-special|remove-special",
            docs_wrappers_text,
        )
        self.assertIn(
            "data-sharing list-policies|get-policy|list-shared-collections|create-policy|update-policy|delete-policy|connect|disconnect",
            docs_wrappers_text,
        )
        self.assertIn("Wix app collections are reference-only", docs_wrappers_text)
        self.assertIn("data-collections list|get", docs_wrappers_text)
        self.assertIn("data-items get|query|search", docs_wrappers_text)
        self.assertIn("data-indexes list|create|drop", docs_wrappers_text)
        self.assertIn(
            "data-folders get|create|update|delete|create-collection-reference|get-collection-references|delete-collection-reference",
            docs_wrappers_text,
        )
        self.assertIn(
            "data-extension-schemas list|create|update|delete-user-defined-fields",
            docs_wrappers_text,
        )
        self.assertIn(
            "form-submissions get-submission|query-submissions-by-namespace|count-submissions|get-media-upload-url|create-submission|update-submission|delete-submission|confirm-submission|bulk-mark-submissions-as-seen",
            docs_wrappers_text,
        )
        self.assertIn("app-permissions list|create|delete", docs_wrappers_text)
        self.assertIn("app-instance get", command_reference_text)
        self.assertIn("market-listing search", command_reference_text)
        self.assertIn("site-plugins get-placement-status", command_reference_text)
        self.assertIn("auth token request", command_reference_text)
        self.assertIn("auth token refresh", command_reference_text)
        self.assertIn("site-search search", command_reference_text)
        self.assertIn("analytics-semantic-models list", command_reference_text)
        self.assertIn("analytics-semantic-models get", command_reference_text)
        self.assertIn("analytics-semantic-models query", command_reference_text)
        self.assertIn("analytics-sessions get-list-job-result", command_reference_text)
        self.assertIn("analytics-sessions list-async", command_reference_text)
        self.assertIn("analytics-sessions mark-recordings-deleted", command_reference_text)
        self.assertIn("analytics-sessions mark-session-recorded", command_reference_text)
        self.assertIn("automation-storage-items create", command_reference_text)
        self.assertIn("automation-storage-items bulk-update-tags-by-filter", command_reference_text)
        self.assertIn("automations-v2 validate", command_reference_text)
        self.assertIn("automations-v2 delete", command_reference_text)
        self.assertIn("async-jobs get", command_reference_text)
        self.assertIn("async-jobs list-items", command_reference_text)
        self.assertIn("branches get-default", command_reference_text)
        self.assertIn("branches get", command_reference_text)
        self.assertIn("branches query", command_reference_text)
        self.assertIn("app-permissions list", command_reference_text)
        self.assertIn("app-permissions create", command_reference_text)
        self.assertIn("app-permissions delete", command_reference_text)
        self.assertIn("contact-labels query", command_reference_text)
        self.assertIn("contacts list-facets", command_reference_text)
        self.assertIn("contacts query-facets", command_reference_text)
        self.assertIn("contacts get-bulk-job", command_reference_text)
        self.assertIn("contacts preview-merge", command_reference_text)
        self.assertIn("contacts bulk-label-unlabel", command_reference_text)
        self.assertIn("contact-labels list", command_reference_text)
        self.assertIn("contact-labels find-or-create", command_reference_text)
        self.assertIn("contact-labels get", command_reference_text)
        self.assertIn("contact-labels update", command_reference_text)
        self.assertIn("contact-labels delete", command_reference_text)
        self.assertIn("contact-notes get", command_reference_text)
        self.assertIn("contact-notes query", command_reference_text)
        self.assertIn("contact-notes create", command_reference_text)
        self.assertIn("contact-notes update", command_reference_text)
        self.assertIn("contact-notes delete", command_reference_text)
        self.assertIn("contact-attachments get", command_reference_text)
        self.assertIn("contact-attachments list", command_reference_text)
        self.assertIn("contact-attachments generate-upload-url", command_reference_text)
        self.assertIn("contact-attachments delete", command_reference_text)
        self.assertIn("data-permissions get", command_reference_text)
        self.assertIn("data-permissions get-my", command_reference_text)
        self.assertIn("data-permissions update", command_reference_text)
        self.assertIn("data-permissions add-special", command_reference_text)
        self.assertIn("data-permissions update-special", command_reference_text)
        self.assertIn("data-permissions remove-special", command_reference_text)
        self.assertIn("data-sharing list-policies", command_reference_text)
        self.assertIn("data-sharing get-policy", command_reference_text)
        self.assertIn("data-sharing list-shared-collections", command_reference_text)
        self.assertIn("data-sharing create-policy", command_reference_text)
        self.assertIn("data-sharing update-policy", command_reference_text)
        self.assertIn("data-sharing delete-policy", command_reference_text)
        self.assertIn("data-sharing connect", command_reference_text)
        self.assertIn("data-sharing disconnect", command_reference_text)
        self.assertIn("Read CMS Wix app collections", command_reference_text)
        self.assertIn("Stores/Products", command_reference_text)
        self.assertIn("Bookings/Services", command_reference_text)
        self.assertIn("data-indexes list", command_reference_text)
        self.assertIn("data-indexes create", command_reference_text)
        self.assertIn("data-indexes drop", command_reference_text)
        self.assertIn("data-folders get", command_reference_text)
        self.assertIn("data-folders create", command_reference_text)
        self.assertIn("data-folders update", command_reference_text)
        self.assertIn("data-folders delete", command_reference_text)
        self.assertIn("data-folders create-collection-reference", command_reference_text)
        self.assertIn("data-folders get-collection-references", command_reference_text)
        self.assertIn("data-folders delete-collection-reference", command_reference_text)
        self.assertIn("data-extension-schemas list", command_reference_text)
        self.assertIn("data-extension-schemas create", command_reference_text)
        self.assertIn("data-extension-schemas update", command_reference_text)
        self.assertIn("data-extension-schemas delete-user-defined-fields", command_reference_text)
        self.assertIn("notifications notify", command_reference_text)
        self.assertIn("notifications notify", docs_wrappers_text)
        self.assertIn("form-submissions get-submission", command_reference_text)
        self.assertIn("form-submissions query-submissions-by-namespace", command_reference_text)
        self.assertIn("form-submissions count-submissions", command_reference_text)
        self.assertIn("form-submissions get-media-upload-url", command_reference_text)
        self.assertIn("form-submissions create-submission", command_reference_text)
        self.assertIn("form-submissions update-submission", command_reference_text)
        self.assertIn("form-submissions delete-submission", command_reference_text)
        self.assertIn("form-submissions confirm-submission", command_reference_text)
        self.assertIn("form-submissions bulk-mark-submissions-as-seen", command_reference_text)
        self.assertIn("function-templates get", command_reference_text)
        self.assertIn("function-templates query", command_reference_text)
        self.assertIn("function-templates get|query", docs_wrappers_text)
        self.assertIn("function-templates query", skill_text)
        self.assertIn("function-productions create", command_reference_text)
        self.assertIn("function-productions delete", command_reference_text)
        self.assertIn("function-productions create|update|delete", docs_wrappers_text)
        self.assertIn("function-productions delete", skill_text)
        self.assertIn("builderless-productions create", command_reference_text)
        self.assertIn("builderless-productions get", command_reference_text)
        self.assertIn("builderless-productions create|get|update", docs_wrappers_text)
        self.assertIn("builderless-productions update", skill_text)
        self.assertIn("function-methods create", command_reference_text)
        self.assertIn("function-methods query", command_reference_text)
        self.assertIn("function-methods create|delete|query", docs_wrappers_text)
        self.assertIn("function-methods delete", skill_text)
        self.assertIn("function-activations upsert", command_reference_text)
        self.assertIn("function-activations delete", command_reference_text)
        self.assertIn("function-activations upsert|delete", docs_wrappers_text)
        self.assertIn("function-activations delete", skill_text)
        self.assertIn("function-spi-configurations create", command_reference_text)
        self.assertIn("function-spi-configurations validate", command_reference_text)
        self.assertIn("function-spi-configurations create|get|update|delete|query|validate", docs_wrappers_text)
        self.assertIn("function-spi-configurations update", skill_text)
        self.assertIn("site-properties get|update-business-contact|update-business-profile|update-business-schedule|update-consent-policy", docs_wrappers_text)
        self.assertIn("site-urls get-editor-urls|list-published-site-urls", docs_wrappers_text)
        self.assertIn("skills/wix/SKILL.md", docs_wrappers_text)
        self.assertIn("contacts list|get|query", docs_wrappers_text)
        self.assertIn(
            "files list|get|batch-get|search|query|list-deleted|update|bulk-delete|bulk-restore|generate-upload-url|generate-resumable-upload-url|import|generate-download-url",
            docs_wrappers_text,
        )
        self.assertIn(
            "media-folders list|get|search|query|list-deleted|create|update|bulk-delete|bulk-restore|generate-download-url",
            docs_wrappers_text,
        )
        self.assertIn("rich-content-ricos convert-from|convert-to|validate", docs_wrappers_text)
        self.assertIn(
            "pro-gallery list-galleries|get-gallery|create-gallery|update-gallery|delete-gallery|list-gallery-items|get-gallery-item|create-gallery-item|update-gallery-item|delete-gallery-item|bulk-delete-gallery-items",
            docs_wrappers_text,
        )
        self.assertNotIn("media-skills ", docs_wrappers_text)
        self.assertIn(
            "data-items get|query|count|aggregate|aggregate-pipeline|distinct|search|query-referenced|is-referenced",
            docs_wrappers_text,
        )
        self.assertIn(
            "data-items insert|save|truncate|bulk-insert|bulk-patch|bulk-remove|bulk-save|bulk-update|bulk-insert-references|bulk-remove-references|update|patch|remove",
            docs_wrappers_text,
        )
        self.assertIn("analytics-data get", docs_wrappers_text)
        self.assertIn("analytics-sessions get-list-job-result", docs_wrappers_text)
        self.assertIn("analytics-semantic-models list", docs_wrappers_text)
        self.assertIn(
            "automation-storage-items create|get|query|bulk-update-tags|bulk-update-tags-by-filter|update-counter-by|update-value",
            docs_wrappers_text,
        )
        self.assertIn("automations-v2 create|get|update|delete|query|validate", docs_wrappers_text)
        self.assertIn("branches get-default", docs_wrappers_text)
        self.assertIn("--plan-out", skill_text)
        self.assertIn("--plan-in", skill_text)
        self.assertIn("--apply --yes", skill_text)
        self.assertIn("--receipt-out", skill_text)
        self.assertIn("domain-dns", skill_text)

    def test_front_door_boundary_docs_use_frozen_boundary_terms(self) -> None:
        root = Path(__file__).resolve().parents[1]
        boundary_files = [
            root / "README.md",
            root / "docs" / "references.md",
            root / "docs" / "api_coverage.md",
            root / "docs" / "command_reference.md",
            root / "docs" / "onboarding.md",
            root / "docs" / "proof.md",
            root / "docs" / "skills_wrappers.md",
            root / "docs" / "authentication.md",
            root / "CHANGELOG.md",
            self._skill_path(root),
        ]
        banned_phrases = [
            "this slice",
            "planned to implemented",
            "not shipped yet",
            "not shipped here",
            "outside this shipped slice",
            "outside the shipped surface",
            "outside the shipped contributors surface",
            "outside this shipped surface",
            "not shipped in this slice",
            "current source-ready scope",
        ]

        for path in boundary_files:
            text = path.read_text(encoding="utf-8").lower()
            for phrase in banned_phrases:
                self.assertNotIn(
                    phrase,
                    text,
                    msg=f"{path.name} includes forbidden slice-boundary phrase: {phrase}",
                )

    def test_authentication_boundary_terms_are_normalized(self) -> None:
        root = Path(__file__).resolve().parents[1]
        auth_text = (root / "docs" / "authentication.md").read_text(encoding="utf-8").lower()

        banned_boundary_phrases = [
            "this slice",
            "not shipped in this tool",
        ]

        for phrase in banned_boundary_phrases:
            self.assertNotIn(
                phrase,
                auth_text,
                msg=f"authentication.md still has legacy boundary wording: {phrase}",
            )

    def test_restaurants_remaining_coverage_is_split_into_exact_rows(self) -> None:
        root = Path(__file__).resolve().parents[1]
        coverage_text = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")

        self.assertNotIn("Restaurants: remaining subfamilies", coverage_text)
        for label in [
            "Restaurants: Item Labels",
            "Restaurants: Item Variants",
            "Restaurants: Item Modifiers",
            "Restaurants: Item Modifier Groups",
            "Restaurants Online Orders: Operation Groups",
            "Restaurants Online Orders: Operations",
            "Restaurants Online Orders: Menu Ordering Settings",
            "Restaurants Online Orders: Fulfillment Methods",
            "Restaurants Online Orders: Availability Exceptions",
            "Restaurants Online Orders: Service Fees",
            "Restaurants Online Orders: Notification Recipients",
            "Restaurants Reservations: Reservations",
            "Restaurants Reservations: Reservation Locations",
            "Restaurants Reservations: Time Slots",
            "Restaurants Reservations: Experiences",
        ]:
            with self.subTest(label=label):
                self.assertIn(label, coverage_text)

    def test_get_paid_coverage_is_split_into_exact_rows(self) -> None:
        root = Path(__file__).resolve().parents[1]
        coverage_text = (root / "docs" / "api_coverage.md").read_text(encoding="utf-8")
        command_reference_text = (root / "docs" / "command_reference.md").read_text(encoding="utf-8")
        wrappers_text = (root / "docs" / "skills_wrappers.md").read_text(encoding="utf-8")
        skill_text = self._skill_text(root)

        self.assertNotIn("| Get Paid | not-yet-implemented | n/a |", coverage_text)
        self.assertNotIn("| Headless | not-yet-implemented | n/a |", coverage_text)
        for label in [
            "Get Paid: Billable Items",
            "Get Paid: Bulk Downloads",
            "Get Paid: Payment Links",
            "Get Paid: Payment Link Payments",
            "Get Paid: Payment Link Settings",
            "Get Paid: Receipts",
            "Get Paid: Receipt Presets",
            "Get Paid: Receipts Settings",
            "Headless: OAuth Apps",
            "Headless: Authentication",
            "Headless: Recovery",
            "Headless: Redirects",
            "Headless: Sitemap",
            "Headless: Verification",
        ]:
            with self.subTest(label=label):
                self.assertIn(label, coverage_text)
        self.assertIn("payment-link-settings get", command_reference_text)
        self.assertIn("payment-link-settings update", wrappers_text)
        self.assertIn("payment-link-settings update", skill_text)
        self.assertIn("payment-links create", command_reference_text)
        self.assertIn("payment-links create|get|delete", wrappers_text)
        self.assertIn("bulk-update-tags-by-filter", wrappers_text)
        self.assertIn("payment-links initiate-payment", skill_text)
        self.assertIn("payment-link-payments issue-receipt", command_reference_text)
        self.assertIn("payment-link-payments query|search|issue-receipt", wrappers_text)
        self.assertIn("payment-link-payments issue-receipt", skill_text)
        self.assertIn("receipts create", command_reference_text)
        self.assertIn("receipts create|get|query|get-latest-number", wrappers_text)
        self.assertIn("receipts send-email", skill_text)
        self.assertIn("receipt-presets create", command_reference_text)
        self.assertIn("receipt-presets create|get|update|delete", wrappers_text)
        self.assertIn("receipt-presets set-default", skill_text)
        self.assertIn("receipts-settings get", command_reference_text)
        self.assertIn("receipts-settings get|update", wrappers_text)
        self.assertIn("receipts-settings update", skill_text)
        self.assertIn("headless-oauth-apps create", command_reference_text)
        self.assertIn("headless-oauth-apps create|get|update|query", wrappers_text)
        self.assertIn("headless-oauth-apps update", skill_text)
        self.assertIn("headless-authentication login-v2", command_reference_text)
        self.assertIn("headless-authentication login-v2|retrieve-tokens", wrappers_text)
        self.assertIn("headless-authentication sign-on", skill_text)
        self.assertIn("headless-recovery send-recovery-email", command_reference_text)
        self.assertIn("headless-recovery send-recovery-email", wrappers_text)
        self.assertIn("Headless Recovery API", skill_text)
        self.assertIn("headless-redirects create-redirect-session", command_reference_text)
        self.assertIn("headless-redirects create-redirect-session", wrappers_text)
        self.assertIn("Headless Redirects API", skill_text)
        self.assertIn("headless-sitemap list-pages", command_reference_text)
        self.assertIn("headless-sitemap list-pages", wrappers_text)
        self.assertIn("Headless Sitemap API", skill_text)
        self.assertIn("headless-verification verify-during-authentication", command_reference_text)
        self.assertIn("headless-verification verify-during-authentication", wrappers_text)
        self.assertIn("Headless Verification API", skill_text)
        self.assertIn("billable-items get", command_reference_text)
        self.assertIn("bulk-update-tags-by-filter", wrappers_text)
        self.assertIn("bulk-update-tags-by-filter", skill_text)

    def test_finish_line_matrices_and_proof_anchors_exist(self) -> None:
        root = Path(__file__).resolve().parents[1]
        auth_text = (root / "docs" / "authentication.md").read_text(encoding="utf-8")
        onboarding_text = (root / "docs" / "onboarding.md").read_text(encoding="utf-8")
        wrappers_text = (root / "docs" / "skills_wrappers.md").read_text(encoding="utf-8")
        skill_text = self._skill_text(root)
        proof_text = (root / "docs" / "proof.md").read_text(encoding="utf-8")
        changelog_text = (root / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("## Auth family matrix", auth_text)
        self.assertIn("## Auth family matrix", onboarding_text)
        self.assertIn("## Flag contract matrix", wrappers_text)
        self.assertIn("## Flag contract matrix", skill_text)
        self.assertIn("## Evidence anchors", proof_text)
        self.assertIn("## Shipped family proof map", proof_text)
        self.assertIn("## Live-unverified by design", proof_text)
        self.assertIn("## [0.1.0] - 2026-06-22", changelog_text)
        self.assertIn("site-actions bulk-delete", wrappers_text)
        self.assertIn("--ack-irreversible", wrappers_text)
        self.assertIn("contributors change-role", skill_text)
        self.assertIn("2026-06-24-marketing-email-setup-contract-run", proof_text)
