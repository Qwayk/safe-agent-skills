from __future__ import annotations

from typing import Any

from ..errors import ValidationError


def _non_empty(value: object, *, flag_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValidationError(f"Missing {flag_name}")
    return text


def _one_letter(value: object) -> str:
    text = _non_empty(value, flag_name="--letter")
    if len(text) != 1 or not text.isalpha():
        raise ValidationError("--letter must be exactly one alphabetic character")
    return text.lower()


def _meal_id(value: object) -> str:
    text = _non_empty(value, flag_name="--meal-id")
    if not text.isdigit():
        raise ValidationError("--meal-id must be numeric")
    return text


def _request_json(ctx: dict[str, Any], endpoint: str, *, params: dict[str, str] | None = None) -> dict[str, Any]:
    cfg = ctx["cfg"]
    response = ctx["http"].request("GET", f"{cfg.api_root}/{endpoint}", params=params)
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("API response was not a JSON object")
    return payload


def _collection(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    raw = payload.get(key)
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise RuntimeError(f"Expected `{key}` to be a list")
    clean: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            clean.append(item)
    return clean


def _emit(ctx: dict[str, Any], *, event: str, payload: dict[str, Any]) -> int:
    ctx["audit"].write(event, payload)
    ctx["out"].emit(payload)
    return 0


def fetch_categories(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    payload = _request_json(ctx, "categories.php")
    return _collection(payload, "categories")


def cmd_categories(args, ctx) -> int:
    _ = args
    categories = fetch_categories(ctx)
    return _emit(
        ctx,
        event="categories.list",
        payload={
            "ok": True,
            "command": "categories",
            "request": {},
            "count": len(categories),
            "categories": categories,
        },
    )


def _meals_result(
    ctx: dict[str, Any],
    *,
    command: str,
    endpoint: str,
    request_data: dict[str, str],
    params: dict[str, str] | None = None,
) -> int:
    payload = _request_json(ctx, endpoint, params=params)
    meals = _collection(payload, "meals")
    return _emit(
        ctx,
        event=command,
        payload={
            "ok": True,
            "command": command,
            "request": request_data,
            "count": len(meals),
            "found": bool(meals),
            "meals": meals,
        },
    )


def _items_result(
    ctx: dict[str, Any],
    *,
    command: str,
    list_key: str,
    item_kind: str,
) -> int:
    payload = _request_json(ctx, "list.php", params={list_key: "list"})
    items = _collection(payload, "meals")
    return _emit(
        ctx,
        event=command,
        payload={
            "ok": True,
            "command": command,
            "request": {},
            "item_kind": item_kind,
            "count": len(items),
            "items": items,
        },
    )


def cmd_random(args, ctx) -> int:
    _ = args
    return _meals_result(ctx, command="random", endpoint="random.php", request_data={})


def cmd_search_name(args, ctx) -> int:
    name = _non_empty(getattr(args, "name", ""), flag_name="--name")
    return _meals_result(
        ctx,
        command="search.name",
        endpoint="search.php",
        request_data={"name": name},
        params={"s": name},
    )


def cmd_search_first_letter(args, ctx) -> int:
    letter = _one_letter(getattr(args, "letter", ""))
    return _meals_result(
        ctx,
        command="search.first_letter",
        endpoint="search.php",
        request_data={"letter": letter},
        params={"f": letter},
    )


def cmd_lookup_id(args, ctx) -> int:
    meal_id = _meal_id(getattr(args, "meal_id", ""))
    return _meals_result(
        ctx,
        command="lookup.id",
        endpoint="lookup.php",
        request_data={"meal_id": meal_id},
        params={"i": meal_id},
    )


def cmd_list_categories(args, ctx) -> int:
    _ = args
    return _items_result(ctx, command="list.categories", list_key="c", item_kind="category")


def cmd_list_areas(args, ctx) -> int:
    _ = args
    return _items_result(ctx, command="list.areas", list_key="a", item_kind="area")


def cmd_list_ingredients(args, ctx) -> int:
    _ = args
    return _items_result(ctx, command="list.ingredients", list_key="i", item_kind="ingredient")


def cmd_filter_ingredient(args, ctx) -> int:
    ingredient = _non_empty(getattr(args, "ingredient", ""), flag_name="--ingredient")
    return _meals_result(
        ctx,
        command="filter.ingredient",
        endpoint="filter.php",
        request_data={"ingredient": ingredient},
        params={"i": ingredient},
    )


def cmd_filter_category(args, ctx) -> int:
    category = _non_empty(getattr(args, "category", ""), flag_name="--category")
    return _meals_result(
        ctx,
        command="filter.category",
        endpoint="filter.php",
        request_data={"category": category},
        params={"c": category},
    )


def cmd_filter_area(args, ctx) -> int:
    area = _non_empty(getattr(args, "area", ""), flag_name="--area")
    return _meals_result(
        ctx,
        command="filter.area",
        endpoint="filter.php",
        request_data={"area": area},
        params={"a": area},
    )
