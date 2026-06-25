from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EndpointSpec:
    family: str
    name: str
    command: tuple[str, ...]
    method: str
    path: str
    safety: str
    source: str


DATA_EXPORT: tuple[EndpointSpec, ...] = (
    EndpointSpec("data-export", "create-export-job", ("data-export", "create-job"), "POST", "/v1/exports", "plan_apply", "Data Export endpoint reference"),
    EndpointSpec("data-export", "list-export-jobs", ("data-export", "list-jobs"), "GET", "/v1/exports", "read", "Data Export endpoint reference"),
    EndpointSpec("data-export", "list-successful-runs", ("data-export", "list-successful-runs"), "GET", "/v1/exports/successful-runs", "read", "Data Export endpoint reference"),
    EndpointSpec("data-export", "get-export-job", ("data-export", "get-job"), "GET", "/v1/exports/{jobId}", "read", "Data Export endpoint reference"),
    EndpointSpec("data-export", "list-job-runs", ("data-export", "list-runs"), "GET", "/v1/exports/{jobId}/runs", "read", "Data Export endpoint reference"),
    EndpointSpec("data-export", "get-job-run", ("data-export", "get-run"), "GET", "/v1/exports/{jobId}/runs/{runId}", "read", "Data Export endpoint reference"),
    EndpointSpec("data-export", "list-exportable-fields", ("data-export", "exportable-fields"), "GET", "/v1/exportable-fields", "read", "Data Export endpoint reference"),
    EndpointSpec("data-export", "list-custom-vars", ("data-export", "custom-vars"), "GET", "/v1/custom-vars", "read", "Data Export endpoint reference"),
    EndpointSpec("data-export", "list-dynamic-var-keys", ("data-export", "dynamic-var-keys"), "GET", "/v1/dynamic-var-keys", "read", "Data Export endpoint reference"),
)

METRICS_OBJECTS: tuple[EndpointSpec, ...] = (
    EndpointSpec("metrics", "segments", ("metrics", "segments"), "GET", "/v1/segments", "read", "Metrics object endpoints"),
    EndpointSpec("metrics", "goals", ("metrics", "goals"), "GET", "/v1/goals", "read", "Metrics object endpoints"),
    EndpointSpec("metrics", "mappings", ("metrics", "mappings"), "GET", "/v1/mappings", "read", "Metrics object endpoints"),
    EndpointSpec("metrics", "mapping", ("metrics", "mapping"), "GET", "/v1/mappings/{mappingId}", "read", "Metrics object endpoints"),
    EndpointSpec("metrics", "page-groups", ("metrics", "page-groups"), "GET", "/v1/mappings/{mappingId}/page-groups", "read", "Metrics object endpoints"),
    EndpointSpec("metrics", "page-group", ("metrics", "page-group"), "GET", "/v1/page-groups/{pageGroupId}", "read", "Metrics object endpoints"),
    EndpointSpec("metrics", "zonings", ("metrics", "zonings"), "GET", "/v1/page-groups/{pageGroupId}/zonings", "read", "Metrics object endpoints"),
    EndpointSpec("metrics", "zones", ("metrics", "zones"), "GET", "/v1/zonings/{zoningId}/zones", "read", "Metrics object endpoints"),
)

SITE_METRICS = ("site", "bounce-rate", "cart-average", "conversions", "conversion-rate", "pageview-average", "revenue", "session-time-average", "visits")
PAGE_GROUP_METRICS = ("page-group", "activity-rate", "bounce-rate", "conversion-rate", "exit-rate", "fold-height", "interaction-time", "landing-rate", "loading-time", "page-height", "scroll-rate", "elapsed-time", "unique-visits", "views", "views-visits", "visits", "web-vitals")
ZONE_WEB_METRICS = ("zone", "attractiveness-rate", "click-rate", "click-recurrence", "conversion-rate-per-click", "conversion-rate-per-hover", "engagement-rate", "exposure-rate", "exposure-time", "hesitation", "hover-rate", "hover-time", "number-of-clicks", "revenue", "revenue-per-click", "time-before-first-click")
ZONE_APP_METRICS = ("zone", "conversion-rate-per-tap", "revenue", "revenue-per-tap", "swipe-rate", "swipe-recurrence", "tap-rate", "tap-recurrence", "time-before-first-tap")


def _metric_specs() -> tuple[EndpointSpec, ...]:
    specs: list[EndpointSpec] = []
    for metric in SITE_METRICS:
        suffix = "" if metric == "site" else f"/{metric}"
        command = ("metrics", "site", "all") if metric == "site" else ("metrics", "site", metric)
        specs.append(EndpointSpec("metrics", f"site-{metric}", command, "GET", f"/v1/metrics/site{suffix}", "read", "Metrics site endpoints"))
    for metric in PAGE_GROUP_METRICS:
        suffix = "" if metric == "page-group" else f"/{metric}"
        command = ("metrics", "page-group-metric", "all") if metric == "page-group" else ("metrics", "page-group-metric", metric)
        specs.append(EndpointSpec("metrics", f"page-group-{metric}", command, "GET", f"/v1/metrics/page-group/{{pageGroupId}}{suffix}", "read", "Metrics page group endpoints"))
    for metric in ZONE_WEB_METRICS:
        suffix = "" if metric == "zone" else f"/{metric}"
        command = ("metrics", "zone-web", "all") if metric == "zone" else ("metrics", "zone-web", metric)
        specs.append(EndpointSpec("metrics", f"zone-web-{metric}", command, "GET", f"/v1/metrics/zone/{{zoneId}}{suffix}", "read", "Metrics zone web endpoints"))
    for metric in ZONE_APP_METRICS:
        suffix = "" if metric == "zone" else f"/{metric}"
        command = ("metrics", "zone-app", "all") if metric == "zone" else ("metrics", "zone-app", metric)
        specs.append(EndpointSpec("metrics", f"zone-app-{metric}", command, "GET", f"/v1/metrics/zone/{{zoneId}}{suffix}", "read", "Metrics zone apps endpoints"))
    return tuple(specs)


METRICS: tuple[EndpointSpec, ...] = METRICS_OBJECTS + _metric_specs()

ENRICHMENT: tuple[EndpointSpec, ...] = (
    EndpointSpec("enrichment", "send-enrichments", ("enrichment", "send-batch"), "POST", "/v1/enrichments", "plan_apply_ack_no_snapshot", "Enrichment batch endpoint"),
)

SPEED_ANALYSIS: tuple[EndpointSpec, ...] = (
    EndpointSpec("speed-analysis", "analysis-report", ("speed-analysis", "analysis-report"), "POST", "/v1/speed-analysis/analysis/report", "post_read", "Speed Analysis analysis endpoints"),
    EndpointSpec("speed-analysis", "analysis-har", ("speed-analysis", "analysis-har"), "POST", "/v1/speed-analysis/analysis/har", "post_read", "Speed Analysis analysis endpoints"),
    EndpointSpec("speed-analysis", "monitoring-list", ("speed-analysis", "monitoring-list"), "POST", "/v1/speed-analysis/monitoring/list", "post_read", "Speed Analysis monitoring endpoints"),
    EndpointSpec("speed-analysis", "monitoring-last-report", ("speed-analysis", "monitoring-last-report"), "POST", "/v1/speed-analysis/monitoring/last-report", "post_read", "Speed Analysis monitoring endpoints"),
    EndpointSpec("speed-analysis", "monitoring-reports", ("speed-analysis", "monitoring-reports"), "POST", "/v1/speed-analysis/monitoring/reports", "post_read", "Speed Analysis monitoring endpoints"),
    EndpointSpec("speed-analysis", "scenario-list", ("speed-analysis", "scenario-list"), "POST", "/v1/speed-analysis/scenario/list", "post_read", "Speed Analysis scenario endpoints"),
    EndpointSpec("speed-analysis", "scenario-report", ("speed-analysis", "scenario-report"), "POST", "/v1/speed-analysis/scenario/report", "post_read", "Speed Analysis scenario endpoints"),
    EndpointSpec("speed-analysis", "scenario-reports", ("speed-analysis", "scenario-reports"), "POST", "/v1/speed-analysis/scenario/reports", "post_read", "Speed Analysis scenario endpoints"),
    EndpointSpec("speed-analysis", "scenario-step-report", ("speed-analysis", "scenario-step-report"), "POST", "/v1/speed-analysis/scenario/step/report", "post_read", "Speed Analysis scenario endpoints"),
    EndpointSpec("speed-analysis", "scenario-report-har", ("speed-analysis", "scenario-report-har"), "POST", "/v1/speed-analysis/scenario/report/har", "post_read", "Speed Analysis scenario endpoints"),
    EndpointSpec("speed-analysis", "event-list", ("speed-analysis", "event-list"), "POST", "/v1/speed-analysis/event/list", "post_read", "Speed Analysis event endpoints"),
    EndpointSpec("speed-analysis", "event-create", ("speed-analysis", "event-create"), "POST", "/v1/speed-analysis/event/create", "plan_apply_no_snapshot", "Speed Analysis event endpoints"),
    EndpointSpec("speed-analysis", "event-delete", ("speed-analysis", "event-delete"), "POST", "/v1/speed-analysis/event/delete", "plan_apply_ack_irreversible", "Speed Analysis event endpoints"),
)

ALL_ENDPOINTS: tuple[EndpointSpec, ...] = DATA_EXPORT + METRICS + ENRICHMENT + SPEED_ANALYSIS


def find_spec(command: tuple[str, ...]) -> EndpointSpec:
    for spec in ALL_ENDPOINTS:
        if spec.command == command:
            return spec
    raise KeyError(command)
