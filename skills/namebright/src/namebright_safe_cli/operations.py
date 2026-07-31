from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from re import sub as _re_sub


@dataclass(frozen=True)
class FieldSpec:
    api_name: str
    cli_name: str | None
    location: str
    kind: str = "string"
    required: bool = False
    secret: bool = False
    default: int | str | None = None
    positive: bool = False
    choices: tuple[str, ...] = ()
    source: str = "cli"


@dataclass(frozen=True)
class OperationSpec:
    family: str
    method: str
    path: str
    command: str
    fields: tuple[FieldSpec, ...] = ()
    required_acks: tuple[str, ...] = ()
    risk: str = "low"
    no_snapshot: bool = False
    external_message: bool = False
    write_capable: bool = True
    require_nonempty_body: bool = False
    snapshot_commands: tuple[str, ...] = ()
    verify_commands: tuple[str, ...] = ()
    secret_response_fields: tuple[str, ...] = ()



def _cli_field_name(api_name: str) -> str:
    name = _re_sub(r"([a-z0-9])([A-Z])", r"\1-\2", api_name)
    name = _re_sub(r"_", "-", name)
    return name.replace(" ", "-").lower()


def _path_field(name: str, *, required: bool = True, kind: str = "string", source: str = "cli") -> FieldSpec:
    return FieldSpec(
        api_name=name,
        cli_name=None if source != "cli" else _cli_field_name(name),
        location="path",
        kind=kind,
        required=required,
        source=source,
    )


def _path_int_field(name: str, *, required: bool = True) -> FieldSpec:
    return _path_field(name, required=required, kind="int", source="cli")


def _query_field(
    name: str,
    *,
    required: bool = False,
    default: int | str | None = None,
    positive: bool = False,
    kind: str = "string",
    choices: tuple[str, ...] = (),
    source: str = "cli",
) -> FieldSpec:
    return FieldSpec(
        api_name=name,
        cli_name=None if source != "cli" else _cli_field_name(name),
        location="query",
        required=required,
        default=default,
        positive=positive,
        kind=kind,
        choices=choices,
        source=source,
    )


def _body_field(
    name: str,
    *,
    required: bool = False,
    kind: str = "string",
    secret: bool = False,
    positive: bool = False,
    cli_name: str | None = None,
    choices: tuple[str, ...] = (),
    source: str = "cli",
) -> FieldSpec:
    return FieldSpec(
        api_name=name,
        cli_name=_cli_field_name(name) if source == "cli" and cli_name is None else cli_name,
        location="body",
        kind=kind,
        required=required,
        secret=secret,
        positive=positive,
        choices=choices,
        source=source,
    )

def _config_field(
    name: str,
    *,
    required: bool = False,
    kind: str = "string",
    secret: bool = False,
    default: int | str | None = None,
    source: str = "config",
) -> FieldSpec:
    return FieldSpec(
        api_name=name,
        cli_name=None,
        location="body",
        kind=kind,
        required=required,
        secret=secret,
        default=default,
        source=source,
    )


def _cmd_ref(family: str, command: str) -> str:
    return f"{family}:{command}"


def _spec(
    *,
    family: str,
    method: str,
    path: str,
    command: str,
    fields: tuple[FieldSpec, ...] = (),
    required_acks: tuple[str, ...] | list[str] = (),
    risk: str = "low",
    no_snapshot: bool = False,
    external_message: bool = False,
    write_capable: bool | None = None,
    require_nonempty_body: bool | None = None,
    snapshot_commands: tuple[str, ...] | list[str] = (),
    verify_commands: tuple[str, ...] | list[str] = (),
    secret_response_fields: tuple[str, ...] | list[str] = (),
) -> OperationSpec:
    body_present = any(field.location == "body" for field in fields)
    if write_capable is None:
        write_capable = method in {"POST", "PUT", "DELETE"}
    if require_nonempty_body is None:
        require_nonempty_body = bool(body_present)
    return OperationSpec(
        family=family,
        method=method,
        path=path,
        command=command,
        fields=fields,
        required_acks=tuple(required_acks),
        risk=risk,
        no_snapshot=no_snapshot,
        external_message=external_message,
        write_capable=write_capable,
        require_nonempty_body=bool(require_nonempty_body),
        snapshot_commands=tuple(snapshot_commands),
        verify_commands=tuple(verify_commands),
        secret_response_fields=tuple(secret_response_fields),
    )


OPERATIONS: tuple[OperationSpec, ...] = (
    # 1
    _spec(
        family="auth",
        method="POST",
        path="token",
        command="auth token",
        write_capable=False,
        risk="low",
        fields=(
            _config_field("grant_type", required=True, default="client_credentials"),
            _config_field("client_id", required=True, source="config"),
            _config_field("client_secret", required=True, source="config", secret=True),
        ),
        secret_response_fields=("access_token",),
        snapshot_commands=(),
        verify_commands=(),
    ),
    # 2
    _spec(
        family="purchase",
        method="GET",
        path="purchase/availability/{domain}",
        command="purchase availability",
        fields=(_path_field("domain"),),
        snapshot_commands=(_cmd_ref("purchase", "purchase availability"),),
        verify_commands=(_cmd_ref("purchase", "purchase availability"),),
    ),
    # 3
    _spec(
        family="purchase",
        method="POST",
        path="purchase/register",
        command="purchase register",
        required_acks=("ack_spend",),
        risk="high",
        fields=(
            _body_field("DomainName", required=True),
            _body_field("Years", required=True, kind="int", positive=True),
            _body_field("CategoryId", required=False, kind="int"),
            _body_field("CategoryName"),
        ),
        snapshot_commands=(
            _cmd_ref("account", "account show"),
            _cmd_ref("purchase", "purchase availability"),
        ),
        verify_commands=(_cmd_ref("account", "account show"), _cmd_ref("domains", "domains get")),
    ),
    # 4
    _spec(
        family="purchase",
        method="POST",
        path="purchase/renew",
        command="purchase renew",
        required_acks=("ack_spend",),
        risk="high",
        fields=(
            _body_field("DomainName", required=True),
            _body_field("Years", required=True, kind="int", positive=True),
            _body_field("CategoryId", required=False, kind="int"),
            _body_field("CategoryName"),
        ),
        snapshot_commands=(
            _cmd_ref("purchase", "purchase availability"),
            _cmd_ref("domains", "domains get"),
            _cmd_ref("account", "account show"),
        ),
        verify_commands=(_cmd_ref("account", "account show"), _cmd_ref("domains", "domains get")),
    ),
    # 5
    _spec(
        family="account",
        method="GET",
        path="account",
        command="account show",
        risk="low",
        secret_response_fields=("AccountBalance",),
        verify_commands=(_cmd_ref("account", "account show"),),
    ),
    # 6
    _spec(
        family="domains",
        method="GET",
        path="account/domains?page={page}&domainsPerPage={domainsPerPage}",
        command="domains list",
        risk="low",
        fields=(
            _query_field("page", default=1, positive=True),
            _query_field("domainsPerPage", default=50, positive=True),
        ),
        secret_response_fields=("AuthCode",),
        verify_commands=(_cmd_ref("domains", "domains list"),),
    ),
    # 7
    _spec(
        family="domains",
        method="GET",
        path="account/domains/{domain}",
        command="domains get",
        risk="low",
        fields=(_path_field("domain"),),
        secret_response_fields=("AuthCode",),
    ),
    # 8
    _spec(
        family="domains",
        method="PUT",
        path="account/domains/{domain}?optOutOfLock={optOutOfLock}",
        command="domains update",
        required_acks=("ack_high_risk",),
        risk="high",
        external_message=False,
        fields=(
            _path_field("domain"),
            _query_field("optOutOfLock", kind="bool"),
            _body_field("Locked", kind="bool"),
            _body_field("AutoRenew", kind="bool"),
            _body_field("WhoIsPrivacy", kind="bool"),
        ),
        secret_response_fields=("AuthCode",),
        snapshot_commands=(_cmd_ref("domains", "domains get"),),
        verify_commands=(_cmd_ref("domains", "domains get"),),
    ),
    # 9
    _spec(
        family="contacts",
        method="GET",
        path="account/domains/{domain}/contacts/administrative",
        command="contacts get-administrative",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 10
    _spec(
        family="contacts",
        method="GET",
        path="account/domains/{domain}/contacts/all",
        command="contacts get-all",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 11
    _spec(
        family="contacts",
        method="GET",
        path="account/domains/{domain}/contacts/registrant",
        command="contacts get-registrant",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 12
    _spec(
        family="contacts",
        method="GET",
        path="account/domains/{domain}/contacts/technical",
        command="contacts get-technical",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 13
    _spec(
        family="contacts",
        method="PUT",
        path="account/domains/{domain}/contacts/administrative",
        command="contacts update-administrative",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("FirstName"),
            _body_field("LastName"),
            _body_field("Organization"),
            _body_field("Department"),
            _body_field("Email"),
            _body_field("Address1"),
            _body_field("Address2"),
            _body_field("City"),
            _body_field("Region"),
            _body_field("Country"),
            _body_field("PostalCode"),
            _body_field("PhoneCountry", kind="int"),
            _body_field("Phone"),
            _body_field("FaxCountry", kind="int"),
            _body_field("Fax"),
        ),
        snapshot_commands=(_cmd_ref("contacts", "contacts get-administrative"),),
        verify_commands=(
            _cmd_ref("contacts", "contacts get-administrative"),
            _cmd_ref("contacts", "contacts get-all"),
        ),
    ),
    # 14
    _spec(
        family="contacts",
        method="PUT",
        path="account/domains/{domain}/contacts/all",
        command="contacts update-all",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("FirstName"),
            _body_field("LastName"),
            _body_field("Organization"),
            _body_field("Department"),
            _body_field("Email"),
            _body_field("Address1"),
            _body_field("Address2"),
            _body_field("City"),
            _body_field("Region"),
            _body_field("Country"),
            _body_field("PostalCode"),
            _body_field("PhoneCountry", kind="int"),
            _body_field("Phone"),
            _body_field("FaxCountry", kind="int"),
            _body_field("Fax"),
        ),
        snapshot_commands=(
            _cmd_ref("contacts", "contacts get-all"),
            _cmd_ref("contacts", "contacts get-administrative"),
            _cmd_ref("contacts", "contacts get-registrant"),
            _cmd_ref("contacts", "contacts get-technical"),
        ),
        verify_commands=(
            _cmd_ref("contacts", "contacts get-all"),
        ),
    ),
    # 15
    _spec(
        family="contacts",
        method="PUT",
        path="account/domains/{domain}/contacts/registrant?optOutOfLock={optOutOfLock}",
        command="contacts update-registrant",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _query_field("optOutOfLock", kind="bool"),
            _body_field("FirstName"),
            _body_field("LastName"),
            _body_field("Organization"),
            _body_field("Department"),
            _body_field("Email"),
            _body_field("Address1"),
            _body_field("Address2"),
            _body_field("City"),
            _body_field("Region"),
            _body_field("Country"),
            _body_field("PostalCode"),
            _body_field("PhoneCountry", kind="int"),
            _body_field("Phone"),
            _body_field("FaxCountry", kind="int"),
            _body_field("Fax"),
        ),
        snapshot_commands=(
            _cmd_ref("contacts", "contacts get-registrant"),
            _cmd_ref("contacts", "contacts get-all"),
        ),
        verify_commands=(
            _cmd_ref("contacts", "contacts get-registrant"),
        ),
    ),
    # 16
    _spec(
        family="contacts",
        method="PUT",
        path="account/domains/{domain}/contacts/technical",
        command="contacts update-technical",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("FirstName"),
            _body_field("LastName"),
            _body_field("Organization"),
            _body_field("Department"),
            _body_field("Email"),
            _body_field("Address1"),
            _body_field("Address2"),
            _body_field("City"),
            _body_field("Region"),
            _body_field("Country"),
            _body_field("PostalCode"),
            _body_field("PhoneCountry", kind="int"),
            _body_field("Phone"),
            _body_field("FaxCountry", kind="int"),
            _body_field("Fax"),
        ),
        snapshot_commands=(
            _cmd_ref("contacts", "contacts get-technical"),
            _cmd_ref("contacts", "contacts get-all"),
        ),
        verify_commands=(
            _cmd_ref("contacts", "contacts get-technical"),
        ),
    ),
    # 17
    _spec(
        family="nameservers",
        method="GET",
        path="account/domains/{domain}/nameservers",
        command="nameservers list",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 18
    _spec(
        family="nameservers",
        method="GET",
        path="account/domains/{domain}/nameservers/{nameServer}",
        command="nameservers get",
        risk="low",
        fields=(
            _path_field("domain"),
            _path_field("nameServer"),
        ),
    ),
    # 19
    _spec(
        family="nameservers",
        method="PUT",
        path="account/domains/{domain}/nameservers/{nameServer}",
        command="nameservers add",
        required_acks=("ack_high_risk",),
        risk="high",
        require_nonempty_body=False,
        fields=(
            _path_field("domain"),
            _path_field("nameServer"),
        ),
        snapshot_commands=(
            _cmd_ref("nameservers", "nameservers list"),
        ),
        verify_commands=(
            _cmd_ref("nameservers", "nameservers get"),
            _cmd_ref("nameservers", "nameservers list"),
        ),
    ),
    # 20
    _spec(
        family="nameservers",
        method="DELETE",
        path="account/domains/{domain}/nameservers",
        command="nameservers delete-all",
        required_acks=("ack_high_risk", "ack_destructive"),
        risk="high",
        fields=(_path_field("domain"),),
        snapshot_commands=(
            _cmd_ref("nameservers", "nameservers list"),
        ),
        verify_commands=(
            _cmd_ref("nameservers", "nameservers list"),
        ),
    ),
    # 21
    _spec(
        family="nameservers",
        method="DELETE",
        path="account/domains/{domain}/nameservers/{nameServer}",
        command="nameservers delete",
        required_acks=("ack_high_risk", "ack_destructive"),
        risk="high",
        fields=(
            _path_field("domain"),
            _path_field("nameServer"),
        ),
        snapshot_commands=(
            _cmd_ref("nameservers", "nameservers list"),
            _cmd_ref("nameservers", "nameservers get"),
        ),
        verify_commands=(
            _cmd_ref("nameservers", "nameservers list"),
        ),
    ),
    # 22
    _spec(
        family="host-records",
        method="GET",
        path="account/domains/{domain}/hostrecords/all",
        command="host-records list-all",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 23
    _spec(
        family="host-records",
        method="GET",
        path="account/domains/{domain}/hostrecords/a",
        command="host-records list-a",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 24
    _spec(
        family="host-records",
        method="GET",
        path="account/domains/{domain}/hostrecords/aaaa",
        command="host-records list-aaaa",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 25
    _spec(
        family="host-records",
        method="GET",
        path="account/domains/{domain}/hostrecords/cname",
        command="host-records list-cname",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 26
    _spec(
        family="host-records",
        method="GET",
        path="account/domains/{domain}/hostrecords/mx",
        command="host-records list-mx",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 27
    _spec(
        family="host-records",
        method="GET",
        path="account/domains/{domain}/hostrecords/srv",
        command="host-records list-srv",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 28
    _spec(
        family="host-records",
        method="GET",
        path="account/domains/{domain}/hostrecords/txt",
        command="host-records list-txt",
        risk="low",
        fields=(_path_field("domain"),),
    ),
    # 29
    _spec(
        family="host-records",
        method="POST",
        path="account/domains/{domain}/hostrecords/a",
        command="host-records create-a",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("Subdomain"),
            _body_field("IPV4Address"),
            _body_field("RecordId", kind="int", required=False, positive=True),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-a"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-a"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
    ),
    # 30
    _spec(
        family="host-records",
        method="POST",
        path="account/domains/{domain}/hostrecords/aaaa",
        command="host-records create-aaaa",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("Subdomain"),
            _body_field("IPV6Address"),
            _body_field("RecordId", kind="int", required=False, positive=True),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-aaaa"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-aaaa"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
    ),
    # 31
    _spec(
        family="host-records",
        method="POST",
        path="account/domains/{domain}/hostrecords/cname",
        command="host-records create-cname",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("Subdomain"),
            _body_field("RedirectDomain"),
            _body_field("RecordId", kind="int", required=False, positive=True),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-cname"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-cname"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
    ),
    # 32
    _spec(
        family="host-records",
        method="POST",
        path="account/domains/{domain}/hostrecords/mx",
        command="host-records create-mx",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("Subdomain"),
            _body_field("MailServer"),
            _body_field("Priority", kind="int", required=False, positive=True),
            _body_field("RecordId", kind="int", required=False, positive=True),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-mx"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-mx"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
    ),
    # 33
    _spec(
        family="host-records",
        method="POST",
        path="account/domains/{domain}/hostrecords/srv",
        command="host-records create-srv",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("Service"),
            _body_field("Protocol"),
            _body_field("Priority", kind="int", required=False, positive=True),
            _body_field("Weight", kind="int", required=False, positive=True),
            _body_field("Port", kind="int", required=False, positive=True),
            _body_field("Target"),
            _body_field("RecordId", kind="int", required=False, positive=True),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-srv"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-srv"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
    ),
    # 34
    _spec(
        family="host-records",
        method="POST",
        path="account/domains/{domain}/hostrecords/txt",
        command="host-records create-txt",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _path_field("domain"),
            _body_field("Subdomain"),
            _body_field("TextRecord"),
            _body_field("RecordId", kind="int", required=False, positive=True),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-txt"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-txt"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
    ),
    # 35
    _spec(
        family="host-records",
        method="DELETE",
        path="account/domains/{domain}/hostrecords/a/{id}",
        command="host-records delete-a",
        required_acks=("ack_high_risk", "ack_destructive"),
        risk="high",
        fields=(
            _path_field("domain"),
            _path_int_field("id"),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-a"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-a"),
        ),
    ),
    # 36
    _spec(
        family="host-records",
        method="DELETE",
        path="account/domains/{domain}/hostrecords/aaaa/{id}",
        command="host-records delete-aaaa",
        required_acks=("ack_high_risk", "ack_destructive"),
        risk="high",
        fields=(
            _path_field("domain"),
            _path_int_field("id"),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-aaaa"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-aaaa"),
        ),
    ),
    # 37
    _spec(
        family="host-records",
        method="DELETE",
        path="account/domains/{domain}/hostrecords/cname/{id}",
        command="host-records delete-cname",
        required_acks=("ack_high_risk", "ack_destructive"),
        risk="high",
        fields=(
            _path_field("domain"),
            _path_int_field("id"),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-cname"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-cname"),
        ),
    ),
    # 38
    _spec(
        family="host-records",
        method="DELETE",
        path="account/domains/{domain}/hostrecords/mx/{id}",
        command="host-records delete-mx",
        required_acks=("ack_high_risk", "ack_destructive"),
        risk="high",
        fields=(
            _path_field("domain"),
            _path_int_field("id"),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-mx"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-mx"),
        ),
    ),
    # 39
    _spec(
        family="host-records",
        method="DELETE",
        path="account/domains/{domain}/hostrecords/srv/{id}",
        command="host-records delete-srv",
        required_acks=("ack_high_risk", "ack_destructive"),
        risk="high",
        fields=(
            _path_field("domain"),
            _path_int_field("id"),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-srv"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-srv"),
        ),
    ),
    # 40
    _spec(
        family="host-records",
        method="DELETE",
        path="account/domains/{domain}/hostrecords/txt/{id}",
        command="host-records delete-txt",
        required_acks=("ack_high_risk", "ack_destructive"),
        risk="high",
        fields=(
            _path_field("domain"),
            _path_int_field("id"),
        ),
        snapshot_commands=(
            _cmd_ref("host-records", "host-records list-txt"),
            _cmd_ref("host-records", "host-records list-all"),
        ),
        verify_commands=(
            _cmd_ref("host-records", "host-records list-txt"),
        ),
    ),
    # 41
    _spec(
        family="inbound-push",
        method="GET",
        path="account/inboundpush/Completed?page={page}&domainsPerPage={domainsPerPage}",
        command="inbound-push list-completed",
        fields=(
            _query_field("page", default=1, positive=True),
            _query_field("domainsPerPage", default=50, positive=True),
        ),
    ),
    # 42
    _spec(
        family="inbound-push",
        method="GET",
        path="account/inboundpush/Pending?page={page}&domainsPerPage={domainsPerPage}",
        command="inbound-push list-pending",
        fields=(
            _query_field("page", default=1, positive=True),
            _query_field("domainsPerPage", default=50, positive=True),
        ),
    ),
    # 43
    _spec(
        family="inbound-push",
        method="PUT",
        path="account/inboundpush/Accept?domain={domain}",
        command="inbound-push accept-query",
        required_acks=("ack_ownership", "ack_no_snapshot", "ack_irreversible"),
        risk="high",
        no_snapshot=True,
        fields=(_query_field("domain", required=True),),
        snapshot_commands=(
            _cmd_ref("domains", "domains get"),
            _cmd_ref("inbound-push", "inbound-push list-pending"),
        ),
        verify_commands=(
            _cmd_ref("domains", "domains get"),
            _cmd_ref("inbound-push", "inbound-push list-completed"),
            _cmd_ref("inbound-push", "inbound-push list-pending"),
        ),
    ),
    # 44
    _spec(
        family="inbound-push",
        method="PUT",
        path="account/inboundpush/{domain}/Accept",
        command="inbound-push accept-path",
        required_acks=("ack_ownership", "ack_no_snapshot", "ack_irreversible"),
        risk="high",
        no_snapshot=True,
        fields=(_path_field("domain"),),
        snapshot_commands=(
            _cmd_ref("domains", "domains get"),
            _cmd_ref("inbound-push", "inbound-push list-pending"),
        ),
        verify_commands=(
            _cmd_ref("domains", "domains get"),
            _cmd_ref("inbound-push", "inbound-push list-completed"),
            _cmd_ref("inbound-push", "inbound-push list-pending"),
        ),
    ),
    # 45
    _spec(
        family="inbound-push",
        method="DELETE",
        path="account/inboundpush/Decline?domain={domain}",
        command="inbound-push decline-query",
        required_acks=("ack_destructive", "ack_high_risk"),
        risk="high",
        fields=(_query_field("domain", required=True),),
        snapshot_commands=(
            _cmd_ref("inbound-push", "inbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
        verify_commands=(
            _cmd_ref("inbound-push", "inbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
    ),
    # 46
    _spec(
        family="inbound-push",
        method="DELETE",
        path="account/inboundpush/{domain}/Decline",
        command="inbound-push decline-path",
        required_acks=("ack_destructive", "ack_high_risk"),
        risk="high",
        fields=(_path_field("domain"),),
        snapshot_commands=(
            _cmd_ref("inbound-push", "inbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
        verify_commands=(
            _cmd_ref("inbound-push", "inbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
    ),
    # 47
    _spec(
        family="outbound-push",
        method="GET",
        path="account/outboundpush/Completed?page={page}&domainsPerPage={domainsPerPage}",
        command="outbound-push list-completed",
        fields=(
            _query_field("page", default=1, positive=True),
            _query_field("domainsPerPage", default=50, positive=True),
        ),
    ),
    # 48
    _spec(
        family="outbound-push",
        method="GET",
        path="account/outboundpush/Pending?page={page}&domainsPerPage={domainsPerPage}",
        command="outbound-push list-pending",
        fields=(
            _query_field("page", default=1, positive=True),
            _query_field("domainsPerPage", default=50, positive=True),
        ),
    ),
    # 49
    _spec(
        family="outbound-push",
        method="POST",
        path="account/outboundpush/ForcePush?domain={domain}",
        command="outbound-push force-query",
        required_acks=(
            "ack_high_risk",
            "ack_ownership",
            "ack_no_snapshot",
            "ack_irreversible",
            "ack_account_creation",
            "ack_external_message",
        ),
        risk="high",
        no_snapshot=True,
        external_message=True,
        fields=(
            _query_field("domain", required=True),
            _body_field("FirstName"),
            _body_field("LastName"),
            _body_field("Organization"),
            _body_field("Department"),
            _body_field("Email", required=True),
            _body_field("Address1"),
            _body_field("Address2"),
            _body_field("City"),
            _body_field("Region"),
            _body_field("Country"),
            _body_field("PostalCode"),
            _body_field("PhoneCountry", kind="int"),
            _body_field("Phone"),
            _body_field("FaxCountry", kind="int"),
            _body_field("Fax"),
        ),
        snapshot_commands=(
            _cmd_ref("domains", "domains get"),
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("outbound-push", "outbound-push list-completed"),
        ),
        verify_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("outbound-push", "outbound-push list-completed"),
            _cmd_ref("domains", "domains get"),
        ),
    ),
    # 50
    _spec(
        family="outbound-push",
        method="POST",
        path="account/outboundpush/{domain}/ForcePush",
        command="outbound-push force-path",
        required_acks=(
            "ack_high_risk",
            "ack_ownership",
            "ack_no_snapshot",
            "ack_irreversible",
            "ack_account_creation",
            "ack_external_message",
        ),
        risk="high",
        no_snapshot=True,
        external_message=True,
        fields=(
            _path_field("domain"),
            _body_field("FirstName"),
            _body_field("LastName"),
            _body_field("Organization"),
            _body_field("Department"),
            _body_field("Email", required=True),
            _body_field("Address1"),
            _body_field("Address2"),
            _body_field("City"),
            _body_field("Region"),
            _body_field("Country"),
            _body_field("PostalCode"),
            _body_field("PhoneCountry", kind="int"),
            _body_field("Phone"),
            _body_field("FaxCountry", kind="int"),
            _body_field("Fax"),
        ),
        snapshot_commands=(
            _cmd_ref("domains", "domains get"),
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("outbound-push", "outbound-push list-completed"),
        ),
        verify_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("outbound-push", "outbound-push list-completed"),
            _cmd_ref("domains", "domains get"),
        ),
    ),
    # 51
    _spec(
        family="outbound-push",
        method="POST",
        path="account/outboundpush/Initiate?domain={domain}&emailAddress={emailAddress}&optOutOfLock={optOutOfLock}",
        command="outbound-push initiate-query",
        required_acks=(
            "ack_high_risk",
            "ack_ownership",
            "ack_no_snapshot",
            "ack_irreversible",
            "ack_external_message",
        ),
        risk="high",
        no_snapshot=True,
        external_message=True,
        fields=(
            _query_field("domain", required=True),
            _query_field("emailAddress", required=True),
            _query_field("optOutOfLock", kind="bool"),
        ),
        snapshot_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
        verify_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
    ),
    # 52
    _spec(
        family="outbound-push",
        method="POST",
        path="account/outboundpush/{domain}/Initiate?emailAddress={emailAddress}&optOutOfLock={optOutOfLock}",
        command="outbound-push initiate-path",
        required_acks=(
            "ack_high_risk",
            "ack_ownership",
            "ack_no_snapshot",
            "ack_irreversible",
            "ack_external_message",
        ),
        risk="high",
        no_snapshot=True,
        external_message=True,
        fields=(
            _path_field("domain"),
            _query_field("emailAddress", required=True),
            _query_field("optOutOfLock", kind="bool"),
        ),
        snapshot_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
        verify_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
    ),
    # 53
    _spec(
        family="outbound-push",
        method="DELETE",
        path="account/outboundpush/Cancel?domain={domain}",
        command="outbound-push cancel-query",
        required_acks=("ack_destructive", "ack_high_risk"),
        risk="high",
        fields=(_query_field("domain", required=True),),
        snapshot_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
        verify_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
    ),
    # 54
    _spec(
        family="outbound-push",
        method="DELETE",
        path="account/outboundpush/{domain}/Cancel",
        command="outbound-push cancel-path",
        required_acks=("ack_destructive", "ack_high_risk"),
        risk="high",
        fields=(_path_field("domain"),),
        snapshot_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
        verify_commands=(
            _cmd_ref("outbound-push", "outbound-push list-pending"),
            _cmd_ref("domains", "domains get"),
        ),
    ),
    # 55
    _spec(
        family="whois-accuracy",
        method="GET",
        path="account/domains/{domain}/whoisaccuracy",
        command="whois-accuracy get",
        fields=(_path_field("domain"),),
    ),
    # 56
    _spec(
        family="contact-verification",
        method="GET",
        path="account/domains/{domain}/contactverifications",
        command="contact-verification list",
        fields=(_path_field("domain"),),
    ),
    # 57
    _spec(
        family="contact-verification",
        method="POST",
        path="account/contactverification/SendEmail",
        command="contact-verification send-email",
        required_acks=("ack_high_risk", "ack_external_message"),
        risk="high",
        external_message=True,
        fields=(_body_field("Email", required=True),),
        snapshot_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
        ),
        verify_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
        ),
    ),
    # 58
    _spec(
        family="contact-verification",
        method="POST",
        path="account/contactverification/SendPhoneNumber",
        command="contact-verification send-phone",
        required_acks=("ack_high_risk", "ack_external_message"),
        risk="high",
        external_message=True,
        fields=(
            _body_field(
                "PhoneNumberVerificationMethod",
                required=True,
                kind="choice",
                choices=("Sms", "Voice"),
            ),
            _body_field("PhoneNumber", required=True),
        ),
        snapshot_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
        ),
        verify_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
        ),
    ),
    # 59
    _spec(
        family="contact-verification",
        method="POST",
        path="account/contactverification/VerifyContact",
        command="contact-verification verify-contact",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _body_field(
                "LinkAuthCode",
                kind="secret_file",
                required=True,
                secret=True,
                cli_name="link-auth-code-file",
            ),
            _body_field("IpAddress", required=True),
        ),
        snapshot_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
            _cmd_ref("contacts", "contacts get-all"),
        ),
        verify_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
        ),
    ),
    # 60
    _spec(
        family="contact-verification",
        method="POST",
        path="account/contactverification/VerifyEmail",
        command="contact-verification verify-email",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _body_field("Email", required=True),
            _body_field(
                "VerificationCode",
                kind="secret_file",
                required=True,
                secret=True,
                cli_name="verification-code-file",
            ),
            _body_field("IpAddress", required=True),
        ),
        snapshot_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
            _cmd_ref("contacts", "contacts get-registrant"),
        ),
        verify_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
        ),
    ),
    # 61
    _spec(
        family="contact-verification",
        method="POST",
        path="account/contactverification/VerifyPhoneNumber",
        command="contact-verification verify-phone",
        required_acks=("ack_high_risk",),
        risk="high",
        fields=(
            _body_field("PhoneNumber", required=True),
            _body_field(
                "VerificationCode",
                kind="secret_file",
                required=True,
                secret=True,
                cli_name="verification-code-file",
            ),
            _body_field("IpAddress", required=True),
        ),
        snapshot_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
            _cmd_ref("contacts", "contacts get-technical"),
        ),
        verify_commands=(
            _cmd_ref("contact-verification", "contact-verification list"),
        ),
    ),
)


_OPERATION_INDEX = {(entry.family, entry.command): entry for entry in OPERATIONS}


def get_operation(family: str, command: str) -> OperationSpec | None:
    return _OPERATION_INDEX.get((family, command))


def method_counts() -> dict[str, int]:
    return dict(Counter(op.method for op in OPERATIONS))


def family_counts() -> dict[str, int]:
    return dict(Counter(op.family for op in OPERATIONS))


__all__ = [
    "FieldSpec",
    "OperationSpec",
    "OPERATIONS",
    "get_operation",
    "family_counts",
    "method_counts",
]
