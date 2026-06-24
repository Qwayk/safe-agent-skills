# API coverage

AWS coverage shows exactly what the shipped commands can do from the pinned Boto3/Botocore package. AWS has many services, many versions, and many account-specific features, so this page tells you which AWS service models this skill ships with and whether a command is part of the tested package or outside the current boundary.

The boundary is the Boto3/Botocore 1.43.36 package shipped with the CLI. Botocore is the AWS SDK data layer that names services, operations, input shapes, paginators, waiters, and endpoints. The tool turns those packaged models into named commands and does not claim AWS surfaces outside that pinned package. If an endpoint or workflow is not listed here, do not assume the skill supports it.

A good first coverage check is: compare the service and operation you want against the inventory summary here, then check the exact command syntax before asking for a plan.

## Boundary

- Packaged Boto3/Botocore 1.43.36 data only
- No `~/.aws/models` lookup
- No `AWS_DATA_PATH` lookup
- Date: 2026-06-24

## Inventory summary

- Services: 428
- Operations: 18727
- Paginator services: 343 / 428
- Paginators: 3186
- Waiter services: 68 / 428
- Waiters: 367
- Endpoints model version: 3
- Partitions: 8
- Generated named commands: 18727
- Services with multiple service-model versions: 10
- Full per-operation inventory: `docs/_generated/aws_botocore_inventory.json`

## Generated per-operation evidence

The generated JSON ledger records every operation with `operation_name`, generated command name, status, mode, risk categories, and acknowledgement requirements.

| Status | Operations |
|---|---:|
| `generated_named_command` | 18727 |

## Safety and risk coverage

These counts come from the same generated ledger. They do not replace human review; they prove that every pinned operation received a conservative safety class.

| Mode | Operations |
|---|---:|
| `high_no_snapshot` | 473 |
| `irreversible` | 2394 |
| `read` | 7984 |
| `remote_write` | 5892 |
| `unknown_mutating` | 1984 |

| Risk category | Operations |
|---|---:|
| `data_movement` | 907 |
| `irreversible` | 2394 |
| `messaging` | 580 |
| `no_snapshot` | 10743 |
| `public_exposure` | 1741 |
| `secret` | 522 |
| `security_identity` | 2940 |
| `spend_quota` | 2850 |
| `unknown_mutating` | 1984 |

## Services with multiple service-model versions

| Service | Available apiVersions | Selected apiVersion |
|---|---|---|
| appmesh | 2018-10-01, 2019-01-25 | 2019-01-25 |
| clouddirectory | 2016-05-10, 2017-01-11 | 2017-01-11 |
| cloudfront | 2014-05-31, 2014-10-21, 2014-11-06, 2015-04-17, 2015-07-27, 2015-09-17, 2016-01-13, 2016-01-28, 2016-08-01, 2016-08-20, 2016-09-07, 2016-09-29, 2016-11-25, 2017-03-25, 2017-10-30, 2018-06-18, 2018-11-05, 2019-03-26, 2020-05-31 | 2020-05-31 |
| cloudsearch | 2011-02-01, 2013-01-01 | 2013-01-01 |
| ec2 | 2014-09-01, 2014-10-01, 2015-03-01, 2015-04-15, 2015-10-01, 2016-04-01, 2016-09-15, 2016-11-15 | 2016-11-15 |
| elasticache | 2014-09-30, 2015-02-02 | 2015-02-02 |
| events | 2014-02-03, 2015-10-07 | 2015-10-07 |
| inspector | 2015-08-18, 2016-02-16 | 2016-02-16 |
| lambda | 2014-11-11, 2015-03-31 | 2015-03-31 |
| rds | 2014-09-01, 2014-10-31 | 2014-10-31 |

## Service inventory

This table keeps the human coverage page readable. The generated JSON file records every operation name under its service row.

| Service | apiVersion | Operations | Paginators | Waiters |
|---|---|---:|---:|---:|
| accessanalyzer | 2019-11-01 | 39 | 11 | 0 |
| account | 2021-02-01 | 15 | 1 | 0 |
| acm | 2015-12-08 | 17 | 2 | 1 |
| acm-pca | 2017-08-22 | 23 | 3 | 3 |
| aiops | 2018-05-10 | 11 | 1 | 0 |
| amp | 2020-08-01 | 44 | 4 | 6 |
| amplify | 2017-07-25 | 37 | 4 | 0 |
| amplifybackend | 2020-08-11 | 31 | 1 | 0 |
| amplifyuibuilder | 2021-08-11 | 28 | 7 | 0 |
| apigateway | 2015-07-09 | 124 | 18 | 0 |
| apigatewaymanagementapi | 2018-11-29 | 3 | 0 | 0 |
| apigatewayv2 | 2018-11-29 | 103 | 15 | 0 |
| appconfig | 2019-10-09 | 45 | 8 | 2 |
| appconfigdata | 2021-11-11 | 2 | 0 | 0 |
| appfabric | 2023-05-19 | 26 | 4 | 0 |
| appflow | 2020-08-23 | 25 | 0 | 0 |
| appintegrations | 2020-07-29 | 23 | 6 | 0 |
| application-autoscaling | 2016-02-06 | 14 | 4 | 0 |
| application-insights | 2018-11-25 | 33 | 0 | 0 |
| application-signals | 2024-04-15 | 30 | 10 | 0 |
| applicationcostprofiler | 2020-09-10 | 6 | 1 | 0 |
| appmesh | 2019-01-25 | 38 | 8 | 0 |
| apprunner | 2020-05-15 | 37 | 0 | 0 |
| appstream | 2016-12-01 | 89 | 10 | 2 |
| appsync | 2017-07-25 | 74 | 12 | 0 |
| arc-region-switch | 2022-07-26 | 21 | 8 | 2 |
| arc-zonal-shift | 2022-10-30 | 15 | 3 | 0 |
| artifact | 2018-05-10 | 8 | 3 | 0 |
| athena | 2017-05-18 | 70 | 7 | 0 |
| auditmanager | 2017-07-25 | 62 | 0 | 0 |
| autoscaling | 2011-01-01 | 66 | 11 | 0 |
| autoscaling-plans | 2018-01-06 | 6 | 2 | 0 |
| b2bi | 2022-06-23 | 30 | 4 | 1 |
| backup | 2018-11-15 | 109 | 22 | 0 |
| backup-gateway | 2021-01-01 | 25 | 3 | 0 |
| backupsearch | 2018-05-10 | 12 | 4 | 0 |
| batch | 2016-08-10 | 45 | 10 | 0 |
| bcm-dashboards | 2025-08-18 | 15 | 2 | 0 |
| bcm-data-exports | 2023-11-26 | 12 | 3 | 0 |
| bcm-pricing-calculator | 2024-06-19 | 36 | 10 | 0 |
| bcm-recommended-actions | 2024-11-14 | 1 | 1 | 0 |
| bedrock | 2023-04-20 | 108 | 19 | 0 |
| bedrock-agent | 2023-06-05 | 75 | 14 | 0 |
| bedrock-agent-runtime | 2023-07-26 | 33 | 8 | 0 |
| bedrock-agentcore | 2024-02-28 | 65 | 11 | 0 |
| bedrock-agentcore-control | 2023-06-05 | 153 | 35 | 6 |
| bedrock-data-automation | 2023-07-26 | 27 | 5 | 0 |
| bedrock-data-automation-runtime | 2024-06-13 | 6 | 0 | 0 |
| bedrock-runtime | 2023-09-30 | 11 | 1 | 0 |
| billing | 2023-09-07 | 12 | 2 | 0 |
| billingconductor | 2021-07-30 | 32 | 10 | 0 |
| braket | 2019-09-01 | 17 | 4 | 0 |
| budgets | 2016-10-20 | 26 | 8 | 0 |
| ce | 2017-10-25 | 47 | 13 | 0 |
| chatbot | 2017-10-11 | 34 | 9 | 0 |
| chime | 2018-05-01 | 62 | 2 | 0 |
| chime-sdk-identity | 2021-04-20 | 30 | 0 | 0 |
| chime-sdk-media-pipelines | 2021-07-15 | 31 | 0 | 0 |
| chime-sdk-meetings | 2021-07-15 | 16 | 0 | 0 |
| chime-sdk-messaging | 2021-05-15 | 51 | 0 | 0 |
| chime-sdk-voice | 2022-08-03 | 96 | 2 | 0 |
| cleanrooms | 2022-02-17 | 88 | 20 | 0 |
| cleanroomsml | 2023-09-06 | 59 | 16 | 0 |
| cloud9 | 2017-09-23 | 13 | 2 | 0 |
| cloudcontrol | 2021-09-30 | 8 | 2 | 1 |
| clouddirectory | 2017-01-11 | 66 | 19 | 0 |
| cloudformation | 2010-05-15 | 90 | 21 | 10 |
| cloudfront | 2020-05-31 | 167 | 17 | 4 |
| cloudfront-keyvaluestore | 2022-07-26 | 6 | 1 | 0 |
| cloudhsm | 2014-05-30 | 20 | 3 | 0 |
| cloudhsmv2 | 2017-04-28 | 18 | 3 | 0 |
| cloudsearch | 2013-01-01 | 26 | 0 | 0 |
| cloudsearchdomain | 2013-01-01 | 3 | 0 | 0 |
| cloudtrail | 2013-11-01 | 60 | 7 | 0 |
| cloudtrail-data | 2021-08-11 | 1 | 0 | 0 |
| cloudwatch | 2010-08-01 | 49 | 7 | 3 |
| codeartifact | 2018-09-22 | 48 | 10 | 0 |
| codebuild | 2016-10-06 | 59 | 15 | 0 |
| codecatalyst | 2022-09-28 | 38 | 10 | 0 |
| codecommit | 2015-04-13 | 79 | 7 | 0 |
| codeconnections | 2023-12-01 | 27 | 0 | 0 |
| codedeploy | 2014-10-06 | 47 | 9 | 1 |
| codeguru-reviewer | 2019-09-19 | 14 | 1 | 2 |
| codeguru-security | 2018-05-10 | 13 | 3 | 0 |
| codeguruprofiler | 2019-07-18 | 23 | 1 | 0 |
| codepipeline | 2015-07-09 | 44 | 8 | 0 |
| codestar-connections | 2019-12-01 | 27 | 0 | 0 |
| codestar-notifications | 2019-10-15 | 13 | 3 | 0 |
| cognito-identity | 2014-06-30 | 23 | 1 | 0 |
| cognito-idp | 2016-04-18 | 126 | 9 | 0 |
| cognito-sync | 2014-06-30 | 17 | 0 | 0 |
| comprehend | 2017-11-27 | 85 | 10 | 0 |
| comprehendmedical | 2018-10-30 | 26 | 0 | 0 |
| compute-optimizer | 2019-11-01 | 28 | 5 | 0 |
| compute-optimizer-automation | 2025-09-22 | 23 | 9 | 0 |
| config | 2014-11-12 | 97 | 33 | 0 |
| connect | 2017-08-08 | 372 | 81 | 0 |
| connect-contact-lens | 2020-08-21 | 1 | 0 | 0 |
| connectcampaigns | 2021-01-30 | 22 | 1 | 0 |
| connectcampaignsv2 | 2024-04-23 | 37 | 2 | 0 |
| connectcases | 2022-10-03 | 43 | 4 | 0 |
| connecthealth | 2025-01-29 | 16 | 2 | 0 |
| connectparticipant | 2018-09-07 | 11 | 0 | 0 |
| controlcatalog | 2018-05-10 | 6 | 5 | 0 |
| controltower | 2018-05-10 | 28 | 6 | 0 |
| cost-optimization-hub | 2022-07-26 | 8 | 4 | 0 |
| cur | 2017-01-06 | 7 | 1 | 0 |
| customer-profiles | 2020-08-15 | 107 | 13 | 0 |
| databrew | 2017-07-25 | 44 | 8 | 0 |
| dataexchange | 2017-07-25 | 37 | 7 | 0 |
| datapipeline | 2012-10-29 | 19 | 3 | 0 |
| datasync | 2018-11-09 | 53 | 5 | 0 |
| datazone | 2018-05-10 | 189 | 40 | 0 |
| dax | 2017-04-19 | 21 | 7 | 0 |
| deadline | 2023-10-12 | 126 | 30 | 10 |
| detective | 2018-10-26 | 29 | 0 | 0 |
| devicefarm | 2015-06-23 | 77 | 20 | 0 |
| devops-agent | 2026-01-01 | 62 | 12 | 0 |
| devops-guru | 2020-12-01 | 31 | 14 | 0 |
| directconnect | 2012-10-25 | 63 | 3 | 0 |
| discovery | 2015-11-01 | 28 | 7 | 0 |
| dlm | 2018-01-12 | 8 | 0 | 0 |
| dms | 2016-01-01 | 119 | 16 | 17 |
| docdb | 2014-10-31 | 55 | 13 | 2 |
| docdb-elastic | 2022-11-28 | 19 | 3 | 0 |
| drs | 2020-02-26 | 50 | 11 | 0 |
| ds | 2015-04-16 | 80 | 15 | 1 |
| ds-data | 2023-05-31 | 17 | 6 | 0 |
| dsql | 2018-05-10 | 16 | 2 | 4 |
| dynamodb | 2012-08-10 | 57 | 5 | 6 |
| dynamodbstreams | 2012-08-10 | 4 | 0 | 0 |
| ebs | 2019-11-02 | 6 | 0 | 0 |
| ec2 | 2016-11-15 | 769 | 171 | 43 |
| ec2-instance-connect | 2018-04-02 | 2 | 0 | 0 |
| ecr | 2015-09-21 | 58 | 7 | 2 |
| ecr-public | 2020-10-30 | 23 | 4 | 0 |
| ecs | 2014-11-13 | 77 | 9 | 9 |
| efs | 2015-02-01 | 31 | 5 | 0 |
| eks | 2017-11-01 | 64 | 15 | 8 |
| eks-auth | 2023-11-26 | 1 | 0 | 0 |
| elasticache | 2015-02-02 | 75 | 19 | 4 |
| elasticbeanstalk | 2010-12-01 | 47 | 5 | 3 |
| elb | 2012-06-01 | 29 | 2 | 3 |
| elbv2 | 2015-12-01 | 51 | 10 | 5 |
| elementalinference | 2018-11-14 | 16 | 2 | 1 |
| emr | 2009-03-31 | 65 | 11 | 3 |
| emr-containers | 2020-10-01 | 23 | 5 | 0 |
| emr-serverless | 2021-07-13 | 22 | 4 | 0 |
| entityresolution | 2018-05-10 | 38 | 7 | 0 |
| es | 2015-01-01 | 51 | 5 | 0 |
| events | 2015-10-07 | 57 | 3 | 0 |
| evs | 2023-07-27 | 22 | 5 | 0 |
| finspace | 2021-03-12 | 50 | 1 | 0 |
| finspace-data | 2020-07-13 | 31 | 5 | 0 |
| firehose | 2015-08-04 | 12 | 0 | 0 |
| fis | 2020-12-01 | 26 | 6 | 0 |
| fms | 2018-01-01 | 42 | 8 | 0 |
| forecast | 2018-06-26 | 63 | 14 | 0 |
| forecastquery | 2018-06-26 | 2 | 0 | 0 |
| frauddetector | 2019-11-15 | 73 | 0 | 0 |
| freetier | 2023-09-07 | 5 | 2 | 0 |
| fsx | 2018-03-01 | 48 | 7 | 0 |
| gamelift | 2015-10-01 | 120 | 26 | 0 |
| gameliftstreams | 2018-05-10 | 24 | 4 | 5 |
| geo-maps | 2020-11-19 | 5 | 0 | 0 |
| geo-places | 2020-11-19 | 7 | 0 | 0 |
| geo-routes | 2020-11-19 | 5 | 0 | 0 |
| glacier | 2012-06-01 | 33 | 4 | 2 |
| globalaccelerator | 2018-08-08 | 56 | 11 | 0 |
| glue | 2017-03-31 | 295 | 36 | 0 |
| grafana | 2020-08-18 | 25 | 5 | 0 |
| greengrass | 2017-06-07 | 92 | 19 | 0 |
| greengrassv2 | 2020-11-30 | 29 | 7 | 0 |
| groundstation | 2019-05-23 | 40 | 10 | 2 |
| guardduty | 2017-11-28 | 90 | 14 | 0 |
| health | 2016-08-04 | 14 | 7 | 0 |
| healthlake | 2017-07-01 | 14 | 0 | 4 |
| iam | 2010-05-08 | 176 | 34 | 4 |
| identitystore | 2020-06-15 | 19 | 4 | 0 |
| imagebuilder | 2019-12-02 | 77 | 21 | 0 |
| importexport | 2010-06-01 | 6 | 1 | 0 |
| inspector | 2016-02-16 | 37 | 9 | 0 |
| inspector-scan | 2023-08-08 | 1 | 0 | 0 |
| inspector2 | 2020-06-08 | 75 | 16 | 0 |
| interconnect | 2022-07-26 | 13 | 3 | 2 |
| internetmonitor | 2021-06-03 | 16 | 3 | 0 |
| invoicing | 2024-12-01 | 17 | 3 | 0 |
| iot | 2015-05-28 | 272 | 64 | 0 |
| iot-data | 2015-05-28 | 11 | 2 | 0 |
| iot-jobs-data | 2017-09-29 | 5 | 0 | 0 |
| iot-managed-integrations | 2025-03-03 | 83 | 17 | 0 |
| iotdeviceadvisor | 2020-09-18 | 14 | 0 | 0 |
| iotevents | 2018-07-27 | 26 | 0 | 0 |
| iotevents-data | 2018-10-23 | 12 | 0 | 0 |
| iotfleetwise | 2021-06-17 | 57 | 14 | 0 |
| iotsecuretunneling | 2018-10-05 | 8 | 0 | 0 |
| iotsitewise | 2019-12-02 | 104 | 27 | 6 |
| iotthingsgraph | 2018-09-06 | 35 | 10 | 0 |
| iottwinmaker | 2021-11-29 | 40 | 0 | 0 |
| iotwireless | 2020-11-22 | 112 | 0 | 0 |
| ivs | 2020-07-14 | 41 | 6 | 0 |
| ivs-realtime | 2020-07-14 | 39 | 3 | 0 |
| ivschat | 2020-07-14 | 17 | 0 | 0 |
| kafka | 2018-11-14 | 59 | 14 | 0 |
| kafkaconnect | 2021-09-14 | 18 | 4 | 0 |
| kendra | 2019-02-03 | 66 | 0 | 0 |
| kendra-ranking | 2022-10-19 | 9 | 0 | 0 |
| keyspaces | 2022-02-10 | 19 | 4 | 0 |
| keyspacesstreams | 2024-09-09 | 4 | 2 | 0 |
| kinesis | 2013-12-02 | 39 | 4 | 2 |
| kinesis-video-archived-media | 2017-09-30 | 6 | 2 | 0 |
| kinesis-video-media | 2017-09-30 | 1 | 0 | 0 |
| kinesis-video-signaling | 2019-12-04 | 2 | 0 | 0 |
| kinesis-video-webrtc-storage | 2018-05-10 | 2 | 0 | 0 |
| kinesisanalytics | 2015-08-14 | 20 | 0 | 0 |
| kinesisanalyticsv2 | 2018-05-23 | 33 | 4 | 0 |
| kinesisvideo | 2017-09-30 | 32 | 4 | 0 |
| kms | 2014-11-01 | 54 | 8 | 0 |
| lakeformation | 2017-03-31 | 61 | 6 | 0 |
| lambda | 2015-03-31 | 85 | 16 | 6 |
| lambda-core | 2026-04-30 | 5 | 1 | 0 |
| lambda-microvms | 2025-09-09 | 24 | 6 | 0 |
| launch-wizard | 2018-05-10 | 15 | 5 | 0 |
| lex-models | 2017-04-19 | 42 | 10 | 0 |
| lex-runtime | 2016-11-28 | 5 | 0 | 0 |
| lexv2-models | 2020-08-07 | 107 | 2 | 8 |
| lexv2-runtime | 2020-08-07 | 6 | 0 | 0 |
| license-manager | 2018-08-01 | 62 | 5 | 0 |
| license-manager-linux-subscriptions | 2018-05-10 | 11 | 3 | 0 |
| license-manager-user-subscriptions | 2018-05-10 | 17 | 5 | 0 |
| lightsail | 2016-11-28 | 161 | 20 | 0 |
| location | 2020-11-19 | 64 | 12 | 1 |
| logs | 2014-03-28 | 116 | 20 | 0 |
| lookoutequipment | 2020-12-15 | 49 | 0 | 0 |
| m2 | 2021-04-28 | 37 | 10 | 0 |
| machinelearning | 2014-12-12 | 28 | 4 | 4 |
| macie2 | 2020-01-01 | 81 | 17 | 1 |
| mailmanager | 2023-10-17 | 60 | 12 | 0 |
| managedblockchain | 2018-09-24 | 27 | 1 | 0 |
| managedblockchain-query | 2023-05-04 | 9 | 5 | 0 |
| marketplace-agreement | 2020-03-01 | 25 | 8 | 0 |
| marketplace-catalog | 2018-09-17 | 13 | 2 | 0 |
| marketplace-deployment | 2023-01-25 | 4 | 0 | 0 |
| marketplace-discovery | 2026-02-05 | 9 | 5 | 0 |
| marketplace-entitlement | 2017-01-11 | 1 | 1 | 0 |
| marketplace-reporting | 2018-05-10 | 1 | 0 | 0 |
| marketplacecommerceanalytics | 2015-07-01 | 2 | 0 | 0 |
| mediaconnect | 2018-11-14 | 82 | 10 | 11 |
| mediaconvert | 2017-08-29 | 34 | 7 | 0 |
| medialive | 2017-10-14 | 123 | 23 | 22 |
| mediapackage | 2017-10-12 | 19 | 3 | 0 |
| mediapackage-vod | 2018-11-07 | 17 | 3 | 0 |
| mediapackagev2 | 2022-12-25 | 30 | 4 | 1 |
| mediastore | 2017-09-01 | 21 | 1 | 0 |
| mediastore-data | 2017-09-01 | 5 | 1 | 0 |
| mediatailor | 2018-04-23 | 48 | 9 | 0 |
| medical-imaging | 2023-07-19 | 18 | 4 | 0 |
| memorydb | 2021-01-01 | 45 | 13 | 0 |
| meteringmarketplace | 2016-01-14 | 4 | 0 | 0 |
| mgh | 2017-05-31 | 21 | 7 | 0 |
| mgn | 2020-02-26 | 95 | 29 | 0 |
| migration-hub-refactor-spaces | 2021-10-26 | 24 | 5 | 0 |
| migrationhub-config | 2019-06-30 | 4 | 0 | 0 |
| migrationhuborchestrator | 2021-08-28 | 31 | 7 | 0 |
| migrationhubstrategy | 2020-02-19 | 22 | 6 | 0 |
| mpa | 2022-07-26 | 22 | 6 | 0 |
| mq | 2017-11-27 | 25 | 2 | 0 |
| mturk | 2017-01-17 | 39 | 9 | 0 |
| mwaa | 2020-07-01 | 12 | 1 | 0 |
| mwaa-serverless | 2024-07-26 | 15 | 4 | 0 |
| neptune | 2014-10-31 | 70 | 16 | 2 |
| neptune-graph | 2023-11-29 | 34 | 5 | 11 |
| neptunedata | 2023-08-01 | 43 | 0 | 0 |
| network-firewall | 2020-11-12 | 79 | 13 | 0 |
| networkflowmonitor | 2023-04-19 | 25 | 5 | 0 |
| networkmanager | 2019-07-05 | 95 | 24 | 0 |
| networkmonitor | 2023-08-01 | 12 | 1 | 0 |
| notifications | 2018-05-10 | 39 | 11 | 0 |
| notificationscontacts | 2018-05-10 | 9 | 1 | 0 |
| nova-act | 2025-08-22 | 16 | 4 | 0 |
| oam | 2022-06-10 | 15 | 3 | 0 |
| observabilityadmin | 2018-05-10 | 40 | 7 | 0 |
| odb | 2024-08-20 | 66 | 17 | 0 |
| omics | 2022-11-28 | 107 | 25 | 18 |
| opensearch | 2021-01-01 | 92 | 1 | 0 |
| opensearchserverless | 2021-11-01 | 46 | 0 | 0 |
| organizations | 2016-11-28 | 63 | 18 | 0 |
| osis | 2022-01-01 | 22 | 2 | 0 |
| outposts | 2019-12-03 | 43 | 13 | 0 |
| panorama | 2019-07-24 | 34 | 0 | 0 |
| partnercentral-account | 2025-04-04 | 29 | 3 | 0 |
| partnercentral-benefits | 2018-05-10 | 17 | 3 | 0 |
| partnercentral-channel | 2024-03-18 | 17 | 3 | 0 |
| partnercentral-selling | 2022-07-26 | 45 | 12 | 0 |
| payment-cryptography | 2021-09-14 | 32 | 3 | 0 |
| payment-cryptography-data | 2022-02-03 | 15 | 0 | 0 |
| pca-connector-ad | 2018-05-10 | 25 | 5 | 0 |
| pca-connector-scep | 2018-05-10 | 12 | 2 | 0 |
| pcs | 2023-02-10 | 19 | 3 | 0 |
| personalize | 2018-05-22 | 71 | 16 | 0 |
| personalize-events | 2018-03-22 | 5 | 0 | 0 |
| personalize-runtime | 2018-05-22 | 3 | 0 | 0 |
| pi | 2018-02-27 | 14 | 1 | 0 |
| pinpoint | 2016-12-01 | 122 | 0 | 0 |
| pinpoint-email | 2018-07-26 | 42 | 5 | 0 |
| pinpoint-sms-voice | 2018-09-05 | 8 | 0 | 0 |
| pinpoint-sms-voice-v2 | 2022-03-31 | 106 | 27 | 0 |
| pipes | 2015-10-07 | 10 | 1 | 0 |
| polly | 2016-06-10 | 10 | 3 | 0 |
| pricing | 2017-10-15 | 5 | 4 | 0 |
| proton | 2020-07-20 | 87 | 21 | 10 |
| qapps | 2023-11-27 | 35 | 2 | 0 |
| qbusiness | 2023-11-27 | 83 | 20 | 0 |
| qconnect | 2020-10-19 | 94 | 23 | 0 |
| quicksight | 2018-04-01 | 267 | 42 | 0 |
| ram | 2018-01-04 | 35 | 7 | 0 |
| rbin | 2021-06-15 | 10 | 1 | 0 |
| rds | 2014-10-31 | 164 | 42 | 11 |
| rds-data | 2018-08-01 | 6 | 0 | 0 |
| redshift | 2012-12-01 | 141 | 37 | 4 |
| redshift-data | 2019-12-20 | 11 | 7 | 0 |
| redshift-serverless | 2021-04-21 | 65 | 14 | 0 |
| rekognition | 2016-06-27 | 75 | 9 | 2 |
| repostspace | 2022-05-13 | 19 | 2 | 4 |
| resiliencehub | 2020-04-30 | 63 | 3 | 0 |
| resiliencehubv2 | 2026-02-17 | 51 | 15 | 4 |
| resource-explorer-2 | 2022-07-28 | 32 | 11 | 0 |
| resource-groups | 2017-11-27 | 23 | 5 | 0 |
| resourcegroupstaggingapi | 2017-01-26 | 9 | 5 | 0 |
| rolesanywhere | 2018-05-10 | 30 | 4 | 0 |
| route53 | 2013-04-01 | 71 | 8 | 1 |
| route53-recovery-cluster | 2019-12-02 | 4 | 1 | 0 |
| route53-recovery-control-config | 2020-11-02 | 25 | 5 | 6 |
| route53-recovery-readiness | 2019-12-02 | 32 | 10 | 0 |
| route53domains | 2014-05-15 | 34 | 4 | 0 |
| route53globalresolver | 2022-09-27 | 47 | 9 | 0 |
| route53profiles | 2018-05-10 | 16 | 3 | 0 |
| route53resolver | 2018-04-01 | 72 | 17 | 0 |
| rtbfabric | 2023-05-15 | 36 | 5 | 15 |
| rum | 2018-05-10 | 20 | 4 | 0 |
| s3 | 2006-03-01 | 116 | 8 | 4 |
| s3control | 2018-08-20 | 97 | 3 | 0 |
| s3files | 2025-05-05 | 21 | 4 | 0 |
| s3outposts | 2017-07-25 | 5 | 3 | 0 |
| s3tables | 2018-05-10 | 49 | 3 | 0 |
| s3vectors | 2025-07-15 | 19 | 4 | 0 |
| sagemaker | 2017-07-24 | 403 | 89 | 13 |
| sagemaker-a2i-runtime | 2019-11-07 | 5 | 1 | 0 |
| sagemaker-edge | 2020-09-23 | 3 | 0 | 0 |
| sagemaker-featurestore-runtime | 2020-07-01 | 4 | 0 | 0 |
| sagemaker-geospatial | 2020-05-27 | 19 | 3 | 0 |
| sagemaker-metrics | 2022-09-30 | 2 | 0 | 0 |
| sagemaker-runtime | 2017-05-13 | 3 | 0 | 0 |
| sagemakerjobruntime | 2026-02-01 | 4 | 0 | 0 |
| savingsplans | 2019-06-28 | 10 | 0 | 0 |
| scheduler | 2021-06-30 | 12 | 2 | 0 |
| schemas | 2019-12-02 | 31 | 5 | 1 |
| sdb | 2009-04-15 | 10 | 2 | 0 |
| secretsmanager | 2017-10-17 | 23 | 1 | 0 |
| security-ir | 2018-05-10 | 24 | 5 | 0 |
| securityagent | 2025-09-06 | 92 | 22 | 0 |
| securityhub | 2018-10-26 | 109 | 24 | 0 |
| securitylake | 2018-05-10 | 31 | 4 | 0 |
| serverlessrepo | 2017-09-08 | 14 | 3 | 0 |
| service-quotas | 2019-06-24 | 26 | 6 | 0 |
| servicecatalog | 2015-12-10 | 90 | 16 | 0 |
| servicecatalog-appregistry | 2020-06-24 | 24 | 5 | 0 |
| servicediscovery | 2017-03-14 | 30 | 4 | 0 |
| ses | 2010-12-01 | 71 | 5 | 1 |
| sesv2 | 2019-09-27 | 111 | 5 | 0 |
| shield | 2016-06-02 | 36 | 2 | 0 |
| signer | 2017-08-25 | 19 | 3 | 1 |
| signer-data | 2017-08-25 | 1 | 0 | 0 |
| signin | 2023-01-01 | 8 | 1 | 0 |
| simpledbv2 | 2025-09-26 | 3 | 1 | 1 |
| simspaceweaver | 2022-10-28 | 16 | 0 | 0 |
| sms-voice | 2018-09-05 | 8 | 0 | 0 |
| snow-device-management | 2021-08-04 | 13 | 4 | 0 |
| snowball | 2016-06-30 | 27 | 6 | 0 |
| sns | 2010-03-31 | 42 | 8 | 0 |
| socialmessaging | 2024-01-01 | 31 | 5 | 0 |
| sqs | 2012-11-05 | 23 | 2 | 0 |
| ssm | 2014-11-06 | 146 | 50 | 1 |
| ssm-contacts | 2021-05-03 | 39 | 11 | 0 |
| ssm-guiconnect | 2021-05-01 | 3 | 0 | 0 |
| ssm-incidents | 2018-05-10 | 31 | 7 | 2 |
| ssm-quicksetup | 2018-05-10 | 14 | 2 | 0 |
| ssm-sap | 2018-05-10 | 27 | 9 | 0 |
| sso | 2019-06-10 | 4 | 2 | 0 |
| sso-admin | 2020-07-20 | 79 | 21 | 0 |
| sso-oidc | 2019-06-10 | 4 | 0 | 0 |
| stepfunctions | 2016-11-23 | 37 | 5 | 0 |
| storagegateway | 2013-06-30 | 96 | 12 | 0 |
| sts | 2011-06-15 | 11 | 0 | 0 |
| supplychain | 2024-01-01 | 30 | 6 | 0 |
| support | 2013-04-15 | 16 | 2 | 0 |
| support-app | 2021-08-20 | 10 | 0 | 0 |
| sustainability | 2018-05-10 | 2 | 2 | 0 |
| swf | 2012-01-25 | 39 | 7 | 0 |
| synthetics | 2017-10-11 | 22 | 0 | 0 |
| taxsettings | 2018-05-10 | 16 | 3 | 0 |
| textract | 2018-06-27 | 25 | 2 | 0 |
| timestream-influxdb | 2023-01-27 | 19 | 4 | 0 |
| timestream-query | 2018-11-01 | 15 | 3 | 0 |
| timestream-write | 2018-11-01 | 19 | 0 | 0 |
| tnb | 2008-10-21 | 33 | 5 | 0 |
| transcribe | 2017-10-26 | 43 | 0 | 7 |
| transfer | 2018-11-05 | 71 | 13 | 2 |
| translate | 2017-07-01 | 19 | 1 | 0 |
| trustedadvisor | 2022-09-15 | 11 | 6 | 0 |
| uxc | 2024-07-01 | 3 | 1 | 0 |
| verifiedpermissions | 2021-12-01 | 34 | 5 | 0 |
| voice-id | 2021-09-27 | 29 | 6 | 0 |
| vpc-lattice | 2022-11-30 | 73 | 15 | 0 |
| waf | 2015-08-24 | 77 | 16 | 0 |
| waf-regional | 2016-11-28 | 81 | 0 | 0 |
| wafv2 | 2019-07-29 | 59 | 0 | 0 |
| wellarchitected | 2020-03-31 | 72 | 0 | 0 |
| wickr | 2024-02-01 | 44 | 8 | 0 |
| wisdom | 2020-10-19 | 41 | 10 | 0 |
| workdocs | 2016-05-01 | 44 | 10 | 0 |
| workmail | 2017-10-01 | 92 | 10 | 0 |
| workmailmessageflow | 2019-05-01 | 2 | 0 | 0 |
| workspaces | 2015-04-08 | 91 | 9 | 0 |
| workspaces-instances | 2022-07-26 | 13 | 3 | 0 |
| workspaces-thin-client | 2023-08-22 | 16 | 3 | 0 |
| workspaces-web | 2020-07-08 | 75 | 3 | 0 |
| xray | 2016-04-12 | 38 | 10 | 0 |

## Exceptions ledger

This ledger keeps the model boundary honest. It does not claim official AWS surfaces outside packaged Botocore until they are researched and added explicitly.

| Bucket | Official source bucket | Status | Note |
|---|---|---|---|
| console-only-api | AWS service API reference or AWS console/help documentation | outside_coverage_not_claimed | Official AWS surfaces outside packaged Botocore were not claimed as covered in this source build. |
| modeled-but-conditional | AWS service API reference and packaged botocore service model | covered_by_generated_command_when_access_allows | The operation has a generated named command, but AWS may still refuse it based on region, account state, permissions, resource type, or gated service access. |
| multi-version-service-model | botocore/data/<service>/<apiVersion>/service-2.json | selected_latest_packaged_api_version | When Botocore ships multiple service-model apiVersions, the generated inventory records the selected latest packaged version. |
| support-metadata | botocore paginators, waiters, endpoint, retry, and sdk-extras models | accounted_as_metadata | Paginator, waiter, endpoint, retry, and SDK metadata are counted separately because they are not standalone AWS operations. |
| legacy-or-separate-guide | Official AWS legacy appendix, separate service guide, or migration page | outside_coverage_not_claimed_until_researched | Legacy or separately documented official surfaces outside packaged Botocore need a targeted official-doc review before any full-AWS claim includes them. |
