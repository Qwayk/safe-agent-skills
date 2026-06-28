# API coverage

Azure coverage shows exactly what the shipped commands can do from the pinned official Azure REST API spec snapshot. If an endpoint or workflow is not listed here, do not assume the skill supports it. A good first coverage check is: ask the agent to name the service command, operation name, plane, lifecycle, and whether the operation is read, sensitive read, or write before it prepares a request. The coverage boundary is Azure REST API specs only; Microsoft Graph, Microsoft 365, Microsoft Ads, Azure DevOps, GitHub, and other separate Microsoft products are outside this skill.

## Source summary

- Source repository: `https://github.com/Azure/azure-rest-api-specs`
- Pinned commit: `ada8601c3b75c15f06f21e50f9368d9476229305`
- Generated at: `2026-06-28T08:19:50Z`
- Services: `340`
- Source spec files: `15332`
- Operation candidates across versions: `214231`
- Selected generated operations: `26337`
- Management-plane operations: `20673`
- Data-plane operations: `5664`
- Stable operations: `19049`
- Preview operations: `7288`
- Read operations: `12904`
- Sensitive read operations with default value redaction: `411`
- Write operations: `13433`

## Boundary

- Included: official Azure REST API specs under `resource-manager` and `data-plane` stable or preview folders.
- Excluded: examples, shared common types, repo plumbing, sample/test specs such as Contoso WidgetManager and Widget demo specs, Microsoft Graph, Microsoft 365, Microsoft Ads, Azure DevOps, GitHub, and other separate Microsoft products.
- Preview APIs are included only because they are official Azure specs; the lifecycle column keeps that visible.
- Secret/token/key/password/credential-like reads stay implemented but are marked `sensitive_read` in `docs/official_inventory.json`; their response values are redacted by default.

## Generated command coverage

| Service command | Plane | Lifecycles | Operations | Status | Notes |
| --- | --- | --- | ---: | --- | --- |
| `addons-management` | management | preview | 6 | implemented | Generated named operations from pinned official specs. |
| `adhybridhealthservice-management` | management | stable | 77 | implemented | Generated named operations from pinned official specs. |
| `advisor-management` | management | preview, stable | 39 | implemented | Generated named operations from pinned official specs. |
| `agricultureplatform-management` | management | preview | 8 | implemented | Generated named operations from pinned official specs. |
| `agrifood-data-plane` | data_plane | preview | 314 | implemented | Generated named operations from pinned official specs. |
| `agrifood-management` | management | preview | 57 | implemented | Generated named operations from pinned official specs. |
| `ai-data-plane` | data_plane | preview, stable | 457 | implemented | Generated named operations from pinned official specs. |
| `ai-foundry-data-plane` | data_plane | preview | 121 | implemented | Generated named operations from pinned official specs. |
| `alertsmanagement-management` | management | preview, stable | 73 | implemented | Generated named operations from pinned official specs. |
| `analysisservices-management` | management | preview, stable | 16 | implemented | Generated named operations from pinned official specs. |
| `apicenter-data-plane` | data_plane | preview | 14 | implemented | Generated named operations from pinned official specs. |
| `apicenter-management` | management | preview, stable | 54 | implemented | Generated named operations from pinned official specs. |
| `apimanagement-data-plane` | data_plane | preview | 141 | implemented | Generated named operations from pinned official specs. |
| `apimanagement-management` | management | preview, stable | 859 | implemented | Generated named operations from pinned official specs. |
| `app-management` | management | preview, stable | 251 | implemented | Generated named operations from pinned official specs. |
| `appcomplianceautomation-management` | management | preview, stable | 36 | implemented | Generated named operations from pinned official specs. |
| `appconfiguration-data-plane` | data_plane | preview, stable | 21 | implemented | Generated named operations from pinned official specs. |
| `appconfiguration-management` | management | preview, stable | 36 | implemented | Generated named operations from pinned official specs. |
| `applicationinsights-data-plane` | data_plane | preview | 23 | implemented | Generated named operations from pinned official specs. |
| `applicationinsights-management` | management | preview, stable | 99 | implemented | Generated named operations from pinned official specs. |
| `applink-management` | management | preview | 14 | implemented | Generated named operations from pinned official specs. |
| `appplatform-management` | management | preview, stable | 183 | implemented | Generated named operations from pinned official specs. |
| `artifactsigning-data-plane` | data_plane | stable | 5 | implemented | Generated named operations from pinned official specs. |
| `attestation-data-plane` | data_plane | preview, stable | 22 | implemented | Generated named operations from pinned official specs. |
| `attestation-management` | management | preview, stable | 14 | implemented | Generated named operations from pinned official specs. |
| `authorization-management` | management | preview, stable | 150 | implemented | Generated named operations from pinned official specs. |
| `automanage-management` | management | preview, stable | 50 | implemented | Generated named operations from pinned official specs. |
| `automation-management` | management | preview, stable | 197 | implemented | Generated named operations from pinned official specs. |
| `azsadmin-management` | management | preview, stable | 280 | implemented | Generated named operations from pinned official specs. |
| `azure-kusto-management` | management | preview, stable | 89 | implemented | Generated named operations from pinned official specs. |
| `azureactivedirectory-management` | management | preview, stable | 24 | implemented | Generated named operations from pinned official specs. |
| `azurearcdata-management` | management | preview, stable | 74 | implemented | Generated named operations from pinned official specs. |
| `azuredata-management` | management | preview | 11 | implemented | Generated named operations from pinned official specs. |
| `azuredatatransfer-management` | management | preview, stable | 46 | implemented | Generated named operations from pinned official specs. |
| `azuredependencymap-management` | management | preview | 17 | implemented | Generated named operations from pinned official specs. |
| `azurefleet-management` | management | preview, stable | 9 | implemented | Generated named operations from pinned official specs. |
| `azureintegrationspaces-management` | management | preview | 34 | implemented | Generated named operations from pinned official specs. |
| `azurelargeinstance-management` | management | preview, stable | 16 | implemented | Generated named operations from pinned official specs. |
| `azureresiliencemanagement-management` | management | preview | 91 | implemented | Generated named operations from pinned official specs. |
| `azurestack-management` | management | preview, stable | 30 | implemented | Generated named operations from pinned official specs. |
| `azurestackhci-management` | management | preview, stable | 329 | implemented | Generated named operations from pinned official specs. |
| `baremetalinfrastructure-management` | management | preview, stable | 17 | implemented | Generated named operations from pinned official specs. |
| `batch-data-plane` | data_plane | stable | 163 | implemented | Generated named operations from pinned official specs. |
| `batch-management` | management | stable | 57 | implemented | Generated named operations from pinned official specs. |
| `billing-management` | management | preview, stable | 346 | implemented | Generated named operations from pinned official specs. |
| `billingbenefits-management` | management | preview, stable | 67 | implemented | Generated named operations from pinned official specs. |
| `blueprint-management` | management | preview | 40 | implemented | Generated named operations from pinned official specs. |
| `botservice-management` | management | preview, stable | 46 | implemented | Generated named operations from pinned official specs. |
| `carbon-management` | management | stable | 3 | implemented | Generated named operations from pinned official specs. |
| `cdn-management` | management | preview, stable | 193 | implemented | Generated named operations from pinned official specs. |
| `certificateregistration-management` | management | stable | 23 | implemented | Generated named operations from pinned official specs. |
| `chaos-management` | management | preview, stable | 72 | implemented | Generated named operations from pinned official specs. |
| `cloudhealth-management` | management | preview | 33 | implemented | Generated named operations from pinned official specs. |
| `cloudshell-management` | management | stable | 16 | implemented | Generated named operations from pinned official specs. |
| `codesigning-management` | management | preview, stable | 14 | implemented | Generated named operations from pinned official specs. |
| `cognitiveservices-data-plane` | data_plane | preview, stable | 1306 | implemented | Generated named operations from pinned official specs. |
| `cognitiveservices-management` | management | preview, stable | 191 | implemented | Generated named operations from pinned official specs. |
| `commerce-management` | management | preview | 2 | implemented | Generated named operations from pinned official specs. |
| `communication-data-plane` | data_plane | preview, stable | 291 | implemented | Generated named operations from pinned official specs. |
| `communication-management` | management | preview, stable | 52 | implemented | Generated named operations from pinned official specs. |
| `communitytraining-management` | management | stable | 7 | implemented | Generated named operations from pinned official specs. |
| `compute-management` | management | preview, stable | 386 | implemented | Generated named operations from pinned official specs. |
| `computebulkactions-management` | management | preview | 16 | implemented | Generated named operations from pinned official specs. |
| `computelimit-management` | management | stable | 24 | implemented | Generated named operations from pinned official specs. |
| `computeschedule-management` | management | preview, stable | 34 | implemented | Generated named operations from pinned official specs. |
| `confidentialledger-data-plane` | data_plane | preview, stable | 52 | implemented | Generated named operations from pinned official specs. |
| `confidentialledger-management` | management | preview, stable | 21 | implemented | Generated named operations from pinned official specs. |
| `confluent-management` | management | preview, stable | 51 | implemented | Generated named operations from pinned official specs. |
| `connectedcache-management` | management | preview | 43 | implemented | Generated named operations from pinned official specs. |
| `connectedvmware-management` | management | preview, stable | 98 | implemented | Generated named operations from pinned official specs. |
| `consumption-management` | management | preview, stable | 113 | implemented | Generated named operations from pinned official specs. |
| `containerinstance-management` | management | preview, stable | 61 | implemented | Generated named operations from pinned official specs. |
| `containerregistry-data-plane` | data_plane | preview, stable | 48 | implemented | Generated named operations from pinned official specs. |
| `containerregistry-management` | management | preview, stable | 107 | implemented | Generated named operations from pinned official specs. |
| `containerservice-management` | management | preview, stable | 223 | implemented | Generated named operations from pinned official specs. |
| `containerstorage-management` | management | preview | 16 | implemented | Generated named operations from pinned official specs. |
| `cosmos-db-data-plane` | data_plane | stable | 9 | implemented | Generated named operations from pinned official specs. |
| `cosmos-db-management` | management | preview, stable | 384 | implemented | Generated named operations from pinned official specs. |
| `cost-management-management` | management | preview, stable | 207 | implemented | Generated named operations from pinned official specs. |
| `cpim-management` | management | preview, stable | 22 | implemented | Generated named operations from pinned official specs. |
| `customer-insights-management` | management | stable | 66 | implemented | Generated named operations from pinned official specs. |
| `customerlockbox-management` | management | preview | 7 | implemented | Generated named operations from pinned official specs. |
| `customproviders-management` | management | preview | 11 | implemented | Generated named operations from pinned official specs. |
| `dashboard-management` | management | preview, stable | 36 | implemented | Generated named operations from pinned official specs. |
| `databasefleetmanager-management` | management | preview | 32 | implemented | Generated named operations from pinned official specs. |
| `databasewatcher-management` | management | preview, stable | 24 | implemented | Generated named operations from pinned official specs. |
| `databox-management` | management | preview, stable | 19 | implemented | Generated named operations from pinned official specs. |
| `databoxedge-management` | management | preview, stable | 85 | implemented | Generated named operations from pinned official specs. |
| `databricks-management` | management | preview, stable | 24 | implemented | Generated named operations from pinned official specs. |
| `datacatalog-management` | management | stable | 6 | implemented | Generated named operations from pinned official specs. |
| `datadog-management` | management | preview, stable | 36 | implemented | Generated named operations from pinned official specs. |
| `datafactory-management` | management | preview, stable | 109 | implemented | Generated named operations from pinned official specs. |
| `datalake-analytics-data-plane` | data_plane | preview, stable | 67 | implemented | Generated named operations from pinned official specs. |
| `datalake-analytics-management` | management | preview, stable | 49 | implemented | Generated named operations from pinned official specs. |
| `datalake-store-data-plane` | data_plane | preview, stable | 6 | implemented | Generated named operations from pinned official specs. |
| `datalake-store-management` | management | preview, stable | 37 | implemented | Generated named operations from pinned official specs. |
| `datamigration-management` | management | preview, stable | 83 | implemented | Generated named operations from pinned official specs. |
| `dataprotection-management` | management | preview, stable | 81 | implemented | Generated named operations from pinned official specs. |
| `datashare-management` | management | preview, stable | 53 | implemented | Generated named operations from pinned official specs. |
| `dell-management` | management | preview, stable | 7 | implemented | Generated named operations from pinned official specs. |
| `desktopvirtualization-management` | management | preview, stable | 108 | implemented | Generated named operations from pinned official specs. |
| `devcenter-data-plane` | data_plane | preview, stable | 91 | implemented | Generated named operations from pinned official specs. |
| `devcenter-management` | management | preview, stable | 149 | implemented | Generated named operations from pinned official specs. |
| `developerhub-management` | management | preview, stable | 28 | implemented | Generated named operations from pinned official specs. |
| `deviceprovisioningservices-data-plane` | data_plane | preview, stable | 19 | implemented | Generated named operations from pinned official specs. |
| `deviceprovisioningservices-management` | management | preview, stable | 27 | implemented | Generated named operations from pinned official specs. |
| `deviceregistry-management` | management | preview, stable | 84 | implemented | Generated named operations from pinned official specs. |
| `deviceupdate-data-plane` | data_plane | preview, stable | 126 | implemented | Generated named operations from pinned official specs. |
| `deviceupdate-management` | management | preview, stable | 27 | implemented | Generated named operations from pinned official specs. |
| `devspaces-management` | management | stable | 9 | implemented | Generated named operations from pinned official specs. |
| `devtestlabs-management` | management | preview, stable | 190 | implemented | Generated named operations from pinned official specs. |
| `digitaltwins-data-plane` | data_plane | preview, stable | 32 | implemented | Generated named operations from pinned official specs. |
| `digitaltwins-management` | management | preview, stable | 22 | implemented | Generated named operations from pinned official specs. |
| `discovery-data-plane` | data_plane | preview | 39 | implemented | Generated named operations from pinned official specs. |
| `discovery-management` | management | preview, stable | 63 | implemented | Generated named operations from pinned official specs. |
| `dnc-management` | management | preview, stable | 19 | implemented | Generated named operations from pinned official specs. |
| `dns-management` | management | preview, stable | 28 | implemented | Generated named operations from pinned official specs. |
| `dnsresolver-management` | management | preview, stable | 58 | implemented | Generated named operations from pinned official specs. |
| `domainregistration-management` | management | stable | 20 | implemented | Generated named operations from pinned official specs. |
| `domainservices-management` | management | preview, stable | 19 | implemented | Generated named operations from pinned official specs. |
| `durabletask-management` | management | preview, stable | 28 | implemented | Generated named operations from pinned official specs. |
| `dynatrace-management` | management | preview, stable | 34 | implemented | Generated named operations from pinned official specs. |
| `edge-management` | management | preview, stable | 211 | implemented | Generated named operations from pinned official specs. |
| `edgemarketplace-management` | management | preview, stable | 9 | implemented | Generated named operations from pinned official specs. |
| `edgeorder-management` | management | preview, stable | 42 | implemented | Generated named operations from pinned official specs. |
| `edgeorderpartner-management` | management | preview | 4 | implemented | Generated named operations from pinned official specs. |
| `edgezones-management` | management | preview | 5 | implemented | Generated named operations from pinned official specs. |
| `education-management` | management | preview | 21 | implemented | Generated named operations from pinned official specs. |
| `elastic-management` | management | preview, stable | 45 | implemented | Generated named operations from pinned official specs. |
| `elasticsan-management` | management | preview, stable | 31 | implemented | Generated named operations from pinned official specs. |
| `engagementfabric-management` | management | preview | 16 | implemented | Generated named operations from pinned official specs. |
| `eventgrid-data-plane` | data_plane | stable | 6 | implemented | Generated named operations from pinned official specs. |
| `eventgrid-management` | management | preview, stable | 187 | implemented | Generated named operations from pinned official specs. |
| `eventhub-management` | management | preview, stable | 94 | implemented | Generated named operations from pinned official specs. |
| `ews-management` | management | preview | 13 | implemented | Generated named operations from pinned official specs. |
| `extendedlocation-management` | management | preview, stable | 14 | implemented | Generated named operations from pinned official specs. |
| `fabric-management` | management | preview, stable | 13 | implemented | Generated named operations from pinned official specs. |
| `fileshares-management` | management | preview, stable | 22 | implemented | Generated named operations from pinned official specs. |
| `fist-management` | management | preview, stable | 47 | implemented | Generated named operations from pinned official specs. |
| `fluidrelay-management` | management | preview, stable | 26 | implemented | Generated named operations from pinned official specs. |
| `frontdoor-management` | management | preview, stable | 46 | implemented | Generated named operations from pinned official specs. |
| `guestconfiguration-management` | management | preview, stable | 27 | implemented | Generated named operations from pinned official specs. |
| `hanaonazure-management` | management | preview | 19 | implemented | Generated named operations from pinned official specs. |
| `hardwaresecuritymodules-management` | management | preview, stable | 25 | implemented | Generated named operations from pinned official specs. |
| `hdinsight-data-plane` | data_plane | preview | 26 | implemented | Generated named operations from pinned official specs. |
| `hdinsight-management` | management | preview, stable | 66 | implemented | Generated named operations from pinned official specs. |
| `healthbot-management` | management | preview, stable | 15 | implemented | Generated named operations from pinned official specs. |
| `healthcareapis-management` | management | preview, stable | 51 | implemented | Generated named operations from pinned official specs. |
| `healthdataaiservices-data-plane` | data_plane | preview, stable | 7 | implemented | Generated named operations from pinned official specs. |
| `healthdataaiservices-management` | management | stable | 12 | implemented | Generated named operations from pinned official specs. |
| `help-management` | management | preview, stable | 22 | implemented | Generated named operations from pinned official specs. |
| `horizondb-management` | management | preview | 32 | implemented | Generated named operations from pinned official specs. |
| `hybridaks-management` | management | preview, stable | 61 | implemented | Generated named operations from pinned official specs. |
| `hybridcloud-management` | management | preview | 14 | implemented | Generated named operations from pinned official specs. |
| `hybridcompute-management` | management | preview, stable | 90 | implemented | Generated named operations from pinned official specs. |
| `hybridconnectivity-management` | management | preview, stable | 33 | implemented | Generated named operations from pinned official specs. |
| `hybridkubernetes-management` | management | preview, stable | 16 | implemented | Generated named operations from pinned official specs. |
| `hybridnetwork-management` | management | preview, stable | 114 | implemented | Generated named operations from pinned official specs. |
| `imagebuilder-management` | management | preview, stable | 24 | implemented | Generated named operations from pinned official specs. |
| `imds-data-plane` | data_plane | stable | 5 | implemented | Generated named operations from pinned official specs. |
| `impact-management` | management | preview | 17 | implemented | Generated named operations from pinned official specs. |
| `informatica-management` | management | preview, stable | 17 | implemented | Generated named operations from pinned official specs. |
| `intune-management` | management | preview | 33 | implemented | Generated named operations from pinned official specs. |
| `iotcentral-data-plane` | data_plane | preview, stable | 131 | implemented | Generated named operations from pinned official specs. |
| `iotcentral-management` | management | preview, stable | 16 | implemented | Generated named operations from pinned official specs. |
| `iothub-management` | management | preview, stable | 38 | implemented | Generated named operations from pinned official specs. |
| `iotoperations-management` | management | preview, stable | 67 | implemented | Generated named operations from pinned official specs. |
| `iotoperationsdataprocessor-management` | management | preview | 17 | implemented | Generated named operations from pinned official specs. |
| `iotoperationsmq-management` | management | preview | 62 | implemented | Generated named operations from pinned official specs. |
| `iotoperationsorchestrator-management` | management | preview | 19 | implemented | Generated named operations from pinned official specs. |
| `iotspaces-management` | management | preview | 0 | implemented | Generated named operations from pinned official specs. |
| `keyvault-data-plane` | data_plane | preview, stable | 115 | implemented | Generated named operations from pinned official specs. |
| `keyvault-management` | management | preview, stable | 50 | implemented | Generated named operations from pinned official specs. |
| `kubernetesconfiguration-management` | management | preview, stable | 48 | implemented | Generated named operations from pinned official specs. |
| `kubernetesruntime-management` | management | preview, stable | 18 | implemented | Generated named operations from pinned official specs. |
| `labservices-management` | management | preview, stable | 96 | implemented | Generated named operations from pinned official specs. |
| `liftrarize-management` | management | preview, stable | 7 | implemented | Generated named operations from pinned official specs. |
| `liftrastronomer-management` | management | preview, stable | 7 | implemented | Generated named operations from pinned official specs. |
| `liftrcommvault-management` | management | preview | 35 | implemented | Generated named operations from pinned official specs. |
| `liftrhyperexecute-management` | management | preview, stable | 7 | implemented | Generated named operations from pinned official specs. |
| `liftrmongodb-management` | management | preview, stable | 17 | implemented | Generated named operations from pinned official specs. |
| `liftrpinecone-management` | management | preview | 7 | implemented | Generated named operations from pinned official specs. |
| `liftrqumulo-management` | management | preview, stable | 7 | implemented | Generated named operations from pinned official specs. |
| `liftrweightsandbiases-management` | management | preview, stable | 7 | implemented | Generated named operations from pinned official specs. |
| `loadtestservice-data-plane` | data_plane | preview, stable | 62 | implemented | Generated named operations from pinned official specs. |
| `loadtestservice-management` | management | preview, stable | 34 | implemented | Generated named operations from pinned official specs. |
| `logic-management` | management | preview, stable | 161 | implemented | Generated named operations from pinned official specs. |
| `machinelearning-management` | management | preview, stable | 29 | implemented | Generated named operations from pinned official specs. |
| `machinelearningservices-data-plane` | data_plane | preview, stable | 250 | implemented | Generated named operations from pinned official specs. |
| `machinelearningservices-management` | management | preview, stable | 368 | implemented | Generated named operations from pinned official specs. |
| `maintenance-management` | management | preview, stable | 55 | implemented | Generated named operations from pinned official specs. |
| `managednetwork-management` | management | preview | 19 | implemented | Generated named operations from pinned official specs. |
| `managednetworkfabric-management` | management | preview, stable | 249 | implemented | Generated named operations from pinned official specs. |
| `managedoperations-management` | management | preview | 6 | implemented | Generated named operations from pinned official specs. |
| `managedservices-management` | management | preview, stable | 14 | implemented | Generated named operations from pinned official specs. |
| `management-management` | management | preview, stable | 25 | implemented | Generated named operations from pinned official specs. |
| `managementpartner-management` | management | preview | 6 | implemented | Generated named operations from pinned official specs. |
| `manufacturingplatform-management` | management | stable | 8 | implemented | Generated named operations from pinned official specs. |
| `maps-data-plane` | data_plane | preview, stable | 108 | implemented | Generated named operations from pinned official specs. |
| `maps-management` | management | preview, stable | 33 | implemented | Generated named operations from pinned official specs. |
| `mariadb-management` | management | preview, stable | 60 | implemented | Generated named operations from pinned official specs. |
| `marketplace-management` | management | stable | 53 | implemented | Generated named operations from pinned official specs. |
| `marketplacecatalog-data-plane` | data_plane | preview, stable | 18 | implemented | Generated named operations from pinned official specs. |
| `marketplacecatalog-management` | management | preview, stable | 23 | implemented | Generated named operations from pinned official specs. |
| `marketplacenotifications-management` | management | stable | 3 | implemented | Generated named operations from pinned official specs. |
| `marketplaceordering-management` | management | stable | 7 | implemented | Generated named operations from pinned official specs. |
| `migrate-management` | management | preview, stable | 650 | implemented | Generated named operations from pinned official specs. |
| `migrateprojects-management` | management | preview | 23 | implemented | Generated named operations from pinned official specs. |
| `mission-management` | management | preview | 73 | implemented | Generated named operations from pinned official specs. |
| `mongocluster-management` | management | preview, stable | 24 | implemented | Generated named operations from pinned official specs. |
| `monitor-data-plane` | data_plane | preview, stable | 12 | implemented | Generated named operations from pinned official specs. |
| `monitor-management` | management | preview, stable | 181 | implemented | Generated named operations from pinned official specs. |
| `monitoringservice-management` | management | preview, stable | 68 | implemented | Generated named operations from pinned official specs. |
| `msi-management` | management | preview, stable | 14 | implemented | Generated named operations from pinned official specs. |
| `mysql-management` | management | preview, stable | 164 | implemented | Generated named operations from pinned official specs. |
| `mysqldiscovery-management` | management | preview | 17 | implemented | Generated named operations from pinned official specs. |
| `napster-management` | management | preview | 10 | implemented | Generated named operations from pinned official specs. |
| `netapp-management` | management | preview, stable | 200 | implemented | Generated named operations from pinned official specs. |
| `network-management` | management | preview, stable | 911 | implemented | Generated named operations from pinned official specs. |
| `networkcloud-management` | management | preview, stable | 144 | implemented | Generated named operations from pinned official specs. |
| `networkfunction-management` | management | preview, stable | 12 | implemented | Generated named operations from pinned official specs. |
| `newrelic-management` | management | preview, stable | 36 | implemented | Generated named operations from pinned official specs. |
| `nginx-management` | management | preview, stable | 28 | implemented | Generated named operations from pinned official specs. |
| `notificationhubs-management` | management | preview, stable | 55 | implemented | Generated named operations from pinned official specs. |
| `oep-management` | management | preview | 11 | implemented | Generated named operations from pinned official specs. |
| `offazurespringboot-management` | management | preview | 24 | implemented | Generated named operations from pinned official specs. |
| `onlineexperimentation-data-plane` | data_plane | preview | 5 | implemented | Generated named operations from pinned official specs. |
| `onlineexperimentation-management` | management | preview | 13 | implemented | Generated named operations from pinned official specs. |
| `operationalinsights-management` | management | preview, stable | 160 | implemented | Generated named operations from pinned official specs. |
| `operationsmanagement-management` | management | preview | 15 | implemented | Generated named operations from pinned official specs. |
| `oracle-management` | management | preview, stable | 110 | implemented | Generated named operations from pinned official specs. |
| `orbital-data-plane` | data_plane | preview, stable | 179 | implemented | Generated named operations from pinned official specs. |
| `orbital-management` | management | preview, stable | 42 | implemented | Generated named operations from pinned official specs. |
| `orbitalplanetarycomputer-management` | management | preview, stable | 6 | implemented | Generated named operations from pinned official specs. |
| `paloaltonetworks-management` | management | preview, stable | 104 | implemented | Generated named operations from pinned official specs. |
| `peering-management` | management | preview, stable | 49 | implemented | Generated named operations from pinned official specs. |
| `playwrighttesting-data-plane` | data_plane | preview, stable | 11 | implemented | Generated named operations from pinned official specs. |
| `playwrighttesting-management` | management | preview, stable | 17 | implemented | Generated named operations from pinned official specs. |
| `policyinsights-management` | management | preview, stable | 80 | implemented | Generated named operations from pinned official specs. |
| `portal-management` | management | preview, stable | 12 | implemented | Generated named operations from pinned official specs. |
| `portalservices-management` | management | preview, stable | 7 | implemented | Generated named operations from pinned official specs. |
| `postgresql-management` | management | preview, stable | 224 | implemented | Generated named operations from pinned official specs. |
| `postgresqlhsc-management` | management | preview, stable | 59 | implemented | Generated named operations from pinned official specs. |
| `powerbidedicated-management` | management | stable | 18 | implemented | Generated named operations from pinned official specs. |
| `powerbiembedded-management` | management | stable | 12 | implemented | Generated named operations from pinned official specs. |
| `powerbiprivatelinks-management` | management | stable | 14 | implemented | Generated named operations from pinned official specs. |
| `privatedns-management` | management | stable | 18 | implemented | Generated named operations from pinned official specs. |
| `professionalservice-management` | management | preview | 8 | implemented | Generated named operations from pinned official specs. |
| `programenrollment-management` | management | preview | 7 | implemented | Generated named operations from pinned official specs. |
| `programmableconnectivity-data-plane` | data_plane | preview | 5 | implemented | Generated named operations from pinned official specs. |
| `programmableconnectivity-management` | management | preview | 15 | implemented | Generated named operations from pinned official specs. |
| `providerhub-management` | management | preview, stable | 60 | implemented | Generated named operations from pinned official specs. |
| `purestorage-management` | management | preview, stable | 50 | implemented | Generated named operations from pinned official specs. |
| `purview-data-plane` | data_plane | preview, stable | 405 | implemented | Generated named operations from pinned official specs. |
| `purview-management` | management | preview, stable | 28 | implemented | Generated named operations from pinned official specs. |
| `purviewdatagovernace-data-plane` | data_plane | preview | 60 | implemented | Generated named operations from pinned official specs. |
| `purviewdatagovernance-data-plane` | data_plane | preview | 122 | implemented | Generated named operations from pinned official specs. |
| `purviewpolicy-management` | management | preview | 2 | implemented | Generated named operations from pinned official specs. |
| `quantum-data-plane` | data_plane | preview | 31 | implemented | Generated named operations from pinned official specs. |
| `quantum-management` | management | preview | 13 | implemented | Generated named operations from pinned official specs. |
| `quota-management` | management | preview, stable | 53 | implemented | Generated named operations from pinned official specs. |
| `recommendationsservice-management` | management | preview, stable | 20 | implemented | Generated named operations from pinned official specs. |
| `recoveryservices-management` | management | preview, stable | 28 | implemented | Generated named operations from pinned official specs. |
| `recoveryservicesbackup-management` | management | preview, stable | 165 | implemented | Generated named operations from pinned official specs. |
| `recoveryservicesdatareplication-management` | management | preview, stable | 67 | implemented | Generated named operations from pinned official specs. |
| `recoveryservicessiterecovery-management` | management | stable | 282 | implemented | Generated named operations from pinned official specs. |
| `redhatopenshift-management` | management | preview, stable | 34 | implemented | Generated named operations from pinned official specs. |
| `redis-management` | management | preview, stable | 80 | implemented | Generated named operations from pinned official specs. |
| `redisenterprise-management` | management | preview, stable | 39 | implemented | Generated named operations from pinned official specs. |
| `relationships-management` | management | preview | 7 | implemented | Generated named operations from pinned official specs. |
| `relay-management` | management | preview, stable | 81 | implemented | Generated named operations from pinned official specs. |
| `reservations-management` | management | preview, stable | 30 | implemented | Generated named operations from pinned official specs. |
| `resourceconnector-management` | management | preview, stable | 12 | implemented | Generated named operations from pinned official specs. |
| `resourcehealth-management` | management | preview, stable | 28 | implemented | Generated named operations from pinned official specs. |
| `resourcemover-management` | management | preview, stable | 19 | implemented | Generated named operations from pinned official specs. |
| `resources-management` | management | preview, stable | 380 | implemented | Generated named operations from pinned official specs. |
| `riskiq-data-plane` | data_plane | preview | 88 | implemented | Generated named operations from pinned official specs. |
| `riskiq-management` | management | preview | 13 | implemented | Generated named operations from pinned official specs. |
| `saas-management` | management | preview | 19 | implemented | Generated named operations from pinned official specs. |
| `scheduler-management` | management | preview, stable | 15 | implemented | Generated named operations from pinned official specs. |
| `schemaregistry-data-plane` | data_plane | stable | 6 | implemented | Generated named operations from pinned official specs. |
| `scom-management` | management | preview | 21 | implemented | Generated named operations from pinned official specs. |
| `scvmm-management` | management | preview, stable | 95 | implemented | Generated named operations from pinned official specs. |
| `search-data-plane` | data_plane | preview, stable | 80 | implemented | Generated named operations from pinned official specs. |
| `search-management` | management | preview, stable | 35 | implemented | Generated named operations from pinned official specs. |
| `security-management` | management | preview, stable | 281 | implemented | Generated named operations from pinned official specs. |
| `securityandcompliance-management` | management | stable | 50 | implemented | Generated named operations from pinned official specs. |
| `securityinsights-data-plane` | data_plane | preview | 2 | implemented | Generated named operations from pinned official specs. |
| `securityinsights-management` | management | preview, stable | 301 | implemented | Generated named operations from pinned official specs. |
| `serialconsole-management` | management | stable | 10 | implemented | Generated named operations from pinned official specs. |
| `service-map-management` | management | preview | 25 | implemented | Generated named operations from pinned official specs. |
| `servicebus-data-plane` | data_plane | stable | 13 | implemented | Generated named operations from pinned official specs. |
| `servicebus-management` | management | preview, stable | 101 | implemented | Generated named operations from pinned official specs. |
| `servicefabric-data-plane` | data_plane | stable | 257 | implemented | Generated named operations from pinned official specs. |
| `servicefabric-management` | management | preview, stable | 56 | implemented | Generated named operations from pinned official specs. |
| `servicefabricmanagedclusters-management` | management | preview, stable | 88 | implemented | Generated named operations from pinned official specs. |
| `servicefabricmesh-management` | management | preview | 50 | implemented | Generated named operations from pinned official specs. |
| `servicelinker-management` | management | preview, stable | 40 | implemented | Generated named operations from pinned official specs. |
| `servicenetworking-management` | management | preview, stable | 22 | implemented | Generated named operations from pinned official specs. |
| `signalr-management` | management | preview, stable | 48 | implemented | Generated named operations from pinned official specs. |
| `softwareplan-management` | management | preview, stable | 8 | implemented | Generated named operations from pinned official specs. |
| `solutions-management` | management | preview, stable | 28 | implemented | Generated named operations from pinned official specs. |
| `sovereign-management` | management | preview | 20 | implemented | Generated named operations from pinned official specs. |
| `sphere-management` | management | stable | 45 | implemented | Generated named operations from pinned official specs. |
| `splitio-management` | management | preview | 8 | implemented | Generated named operations from pinned official specs. |
| `sql-management` | management | preview, stable | 602 | implemented | Generated named operations from pinned official specs. |
| `sqlvirtualmachine-management` | management | preview, stable | 22 | implemented | Generated named operations from pinned official specs. |
| `standbypool-management` | management | preview, stable | 19 | implemented | Generated named operations from pinned official specs. |
| `storage-data-plane` | data_plane | preview, stable | 33 | implemented | Generated named operations from pinned official specs. |
| `storage-management` | management | preview, stable | 144 | implemented | Generated named operations from pinned official specs. |
| `storageactions-management` | management | stable | 11 | implemented | Generated named operations from pinned official specs. |
| `storagecache-management` | management | preview, stable | 88 | implemented | Generated named operations from pinned official specs. |
| `storagediscovery-management` | management | preview, stable | 12 | implemented | Generated named operations from pinned official specs. |
| `storageimportexport-management` | management | preview, stable | 10 | implemented | Generated named operations from pinned official specs. |
| `storagemover-management` | management | preview, stable | 35 | implemented | Generated named operations from pinned official specs. |
| `storagepool-management` | management | preview, stable | 18 | implemented | Generated named operations from pinned official specs. |
| `storagesync-management` | management | preview, stable | 47 | implemented | Generated named operations from pinned official specs. |
| `streamanalytics-management` | management | preview, stable | 50 | implemented | Generated named operations from pinned official specs. |
| `subscription-management` | management | preview, stable | 40 | implemented | Generated named operations from pinned official specs. |
| `support-management` | management | preview, stable | 50 | implemented | Generated named operations from pinned official specs. |
| `synapse-data-plane` | data_plane | preview, stable | 183 | implemented | Generated named operations from pinned official specs. |
| `synapse-management` | management | preview, stable | 265 | implemented | Generated named operations from pinned official specs. |
| `syntex-management` | management | preview | 7 | implemented | Generated named operations from pinned official specs. |
| `terraform-management` | management | preview | 2 | implemented | Generated named operations from pinned official specs. |
| `testbase-management` | management | preview | 93 | implemented | Generated named operations from pinned official specs. |
| `timeseriesinsights-data-plane` | data_plane | stable | 13 | implemented | Generated named operations from pinned official specs. |
| `timeseriesinsights-management` | management | preview, stable | 27 | implemented | Generated named operations from pinned official specs. |
| `trafficmanager-management` | management | preview, stable | 22 | implemented | Generated named operations from pinned official specs. |
| `translation-data-plane` | data_plane | preview, stable | 15 | implemented | Generated named operations from pinned official specs. |
| `verifiedid-management` | management | preview | 7 | implemented | Generated named operations from pinned official specs. |
| `vi-management` | management | preview, stable | 20 | implemented | Generated named operations from pinned official specs. |
| `vmware-management` | management | preview, stable | 126 | implemented | Generated named operations from pinned official specs. |
| `vmwarecloudsimple-management` | management | stable | 34 | implemented | Generated named operations from pinned official specs. |
| `web-management` | management | preview, stable | 1075 | implemented | Generated named operations from pinned official specs. |
| `webpubsub-data-plane` | data_plane | preview, stable | 49 | implemented | Generated named operations from pinned official specs. |
| `webpubsub-management` | management | preview, stable | 44 | implemented | Generated named operations from pinned official specs. |
| `windowsesu-management` | management | preview | 7 | implemented | Generated named operations from pinned official specs. |
| `windowsiot-management` | management | preview, stable | 8 | implemented | Generated named operations from pinned official specs. |
| `workloadmonitor-management` | management | preview | 17 | implemented | Generated named operations from pinned official specs. |
| `workloads-management` | management | preview, stable | 135 | implemented | Generated named operations from pinned official specs. |

## Operation-level detail

Operation-level detail lives in `docs/official_inventory.json` so the full ledger stays machine-readable and does not turn this page into a giant table.
