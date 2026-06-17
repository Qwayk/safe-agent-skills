from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WebsocketControlCommand:
    official_command: str
    cli_command: str
    ship_status: str
    notes: str


@dataclass(frozen=True)
class WebsocketEvent:
    event: str
    additional_payload: str


@dataclass(frozen=True)
class WebsocketTopic:
    topic: str
    event_count: int
    events: tuple[WebsocketEvent, ...]
    cli_command: str
    ship_status: str
    notes: str


@dataclass(frozen=True)
class WebsocketInventory:
    source_url: str
    audited_utc: str
    stream_url: str
    control_command_count: int
    topic_count: int
    event_count: int
    notes: tuple[str, ...]
    control_commands: tuple[WebsocketControlCommand, ...]
    topics: tuple[WebsocketTopic, ...]


def _vendor_dir() -> Path:
    return Path(__file__).resolve().parent / "_vendor"


def _load_raw_inventory() -> dict:
    path = _vendor_dir() / "websocket_inventory.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError(f"Unexpected websocket inventory payload in {path}")
    return raw


def load_websocket_inventory() -> WebsocketInventory:
    raw = _load_raw_inventory()
    control_commands = tuple(
        WebsocketControlCommand(
            official_command=str(item["official_command"]),
            cli_command=str(item["cli_command"]),
            ship_status=str(item["ship_status"]),
            notes=str(item.get("notes") or ""),
        )
        for item in raw["control_commands"]
    )
    topics = tuple(
        WebsocketTopic(
            topic=str(item["topic"]),
            event_count=int(item["event_count"]),
            events=tuple(
                WebsocketEvent(
                    event=str(event["event"]),
                    additional_payload=str(event.get("additional_payload") or ""),
                )
                for event in item["events"]
            ),
            cli_command=str(item["cli_command"]),
            ship_status=str(item["ship_status"]),
            notes=str(item.get("notes") or ""),
        )
        for item in raw["topics"]
    )
    return WebsocketInventory(
        source_url=str(raw["source_url"]),
        audited_utc=str(raw["audited_utc"]),
        stream_url=str(raw["stream_url"]),
        control_command_count=int(raw["control_command_count"]),
        topic_count=int(raw["topic_count"]),
        event_count=int(raw["event_count"]),
        notes=tuple(str(note) for note in raw["notes"]),
        control_commands=control_commands,
        topics=topics,
    )


def official_control_commands() -> tuple[str, ...]:
    return tuple(command.official_command for command in load_websocket_inventory().control_commands)


def topic_names() -> tuple[str, ...]:
    return tuple(topic.topic for topic in load_websocket_inventory().topics)
