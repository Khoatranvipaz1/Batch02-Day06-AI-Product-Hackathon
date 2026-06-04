from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import quote, quote_plus, urlparse

import httpx


MOCK_DATA_DIR = (
    Path(__file__).resolve().parents[3]
    / "mock_data"
    / "shopee_food_db_hcm_q1"
)
MENU_ITEMS_CSV = MOCK_DATA_DIR / "menu_items.csv"
WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"
MOCK_IMAGE_HOSTS = {"cdn.mock.local"}
CURATED_WIKIMEDIA_FILES = [
    {
        "keywords": ("cơm tấm",),
        "file_name": "Com-Tam-2008.jpg",
        "title": "File:Com-Tam-2008.jpg",
    },
    {
        "keywords": ("bún bò", "bún huế"),
        "file_name": "Bún bò Huế (6927379094).jpg",
        "title": "File:Bún bò Huế (6927379094).jpg",
    },
]
CANONICAL_FOOD_KEYWORDS = [
    (("cơm tấm",), "Cơm tấm"),
    (("bún bò", "bún huế"), "Bún bò Huế"),
    (("gà rán",), "Korean fried chicken"),
    (("tokbokki",), "Tteokbokki"),
    (("bánh mì",), "Bánh mì Vietnamese sandwich"),
    (("phở",), "Phở Vietnamese noodle soup"),
    (("bún thịt nướng", "bún nem", "bún bò xào"), "Vietnamese vermicelli bowl"),
    (("gỏi cuốn",), "Gỏi cuốn"),
    (("pizza",), "Pizza"),
    (("mì ý",), "Spaghetti bolognese"),
    (("sushi",), "Sushi"),
    (("donburi", "gyudon"), "Gyudon"),
    (("miso soup",), "Miso soup"),
    (("lẩu thái",), "Thai hot pot"),
    (("lẩu",), "Hot pot"),
    (("cơm chay", "gỏi cuốn chay", "nấm kho"), "Vegetarian Vietnamese food"),
    (("há cảo",), "Har gow"),
    (("xíu mại",), "Siu mai"),
    (("bánh bao",), "Steamed bun"),
    (("mì hoành thánh", "hoành thánh"), "Wonton noodles"),
    (("burger",), "Burger"),
    (("cơm gà hải nam",), "Hainanese chicken rice"),
    (("cơm gà",), "Chicken rice"),
    (("bún đậu",), "Bún đậu mắm tôm"),
    (("trà sữa",), "Bubble tea"),
    (("cháo",), "Vietnamese congee"),
    (("súp cua",), "Crab soup"),
    (("cơm niêu",), "Vietnamese clay pot rice"),
    (("bánh canh",), "Bánh canh"),
    (("pad thai",), "Pad Thai"),
    (("tom yum",), "Tom yum"),
    (("mì trộn",), "Mixed noodles"),
    (("xôi",), "Vietnamese sticky rice"),
    (("bún riêu",), "Bún riêu"),
    (("kebab", "falafel", "hummus"), "Middle Eastern food"),
    (("ốc", "nghêu", "sò điệp", "ghẹ"), "Vietnamese seafood"),
    (("croissant",), "Croissant"),
    (("sandwich",), "Sandwich"),
    (("pancake",), "Pancake"),
    (("mì quảng",), "Mì Quảng"),
    (("taco",), "Taco"),
    (("burrito",), "Burrito"),
    (("nachos",), "Nachos"),
    (("cơm thịt kho",), "Thịt kho"),
    (("ramen",), "Ramen"),
    (("gyoza",), "Gyoza"),
    (("bún chả",), "Bún chả"),
    (("bibimbap",), "Bibimbap"),
    (("cà ri",), "Curry"),
    (("naan",), "Naan"),
    (("salad",), "Salad"),
    (("bò né",), "Bò né"),
    (("hủ tiếu",), "Hủ tiếu"),
    (("bánh xèo",), "Bánh xèo"),
    (("bánh khọt",), "Bánh khọt"),
    (("tiramisu",), "Tiramisu"),
    (("cheesecake",), "Cheesecake"),
    (("macaron",), "Macaron"),
    (("muffin",), "Muffin"),
    (("bún cá",), "Fish noodle soup"),
]

_image_cache: dict[str, dict[str, str | None]] = {}


def read_menu_items() -> list[dict[str, str]]:
    with MENU_ITEMS_CSV.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def find_menu_items(
    query: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, str]]:
    items = read_menu_items()
    if not query:
        return items[offset : offset + limit]

    normalized_query = normalize_text(query)
    matches = [
        item
        for item in items
        if normalized_query in normalize_text(item["name"])
    ]
    return matches[offset : offset + limit]


def is_mock_image_url(image_url: str | None) -> bool:
    if not image_url:
        return True

    return urlparse(image_url).hostname in MOCK_IMAGE_HOSTS


async def get_menu_item_images(
    query: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    items = find_menu_items(query=query, limit=limit, offset=offset)

    async with httpx.AsyncClient(timeout=8.0) as client:
        results = []
        for item in items:
            image = await resolve_food_image(
                item_name=item["name"],
                existing_image_url=item.get("image_url"),
                client=client,
            )
            results.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "shop_id": item["shop_id"],
                    "base_price": int(item["base_price"]),
                    "sale_price": int(item["sale_price"]) if item["sale_price"] else None,
                    "image_url": image["image_url"],
                    "image_source": image["image_source"],
                    "image_title": image["image_title"],
                }
            )

    return results


async def resolve_food_image(
    item_name: str,
    existing_image_url: str | None,
    client: httpx.AsyncClient,
) -> dict[str, str | None]:
    if existing_image_url and not is_mock_image_url(existing_image_url):
        return {
            "image_url": existing_image_url,
            "image_source": "menu_items.csv",
            "image_title": None,
        }

    cache_key = normalize_text(item_name)
    if cache_key in _image_cache:
        return _image_cache[cache_key]

    image = get_curated_image(item_name)
    if image is None:
        image = await search_wikimedia_image(item_name=item_name, client=client)
    if image is None:
        image = {
            "image_url": build_keyword_food_image_url(item_name),
            "image_source": "keyword_food_image",
            "image_title": None,
        }

    _image_cache[cache_key] = image
    return image


def get_curated_image(item_name: str) -> dict[str, str | None] | None:
    normalized_name = normalize_text(item_name)
    for image in CURATED_WIKIMEDIA_FILES:
        if any(keyword in normalized_name for keyword in image["keywords"]):
            return {
                "image_url": build_wikimedia_file_url(image["file_name"]),
                "image_source": "wikimedia_commons_curated",
                "image_title": image["title"],
            }

    return None


async def search_wikimedia_image(
    item_name: str,
    client: httpx.AsyncClient,
) -> dict[str, str | None] | None:
    search_terms = build_food_search_terms(item_name)

    for search_term in search_terms:
        try:
            response = await client.get(
                WIKIMEDIA_API_URL,
                params={
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrsearch": search_term,
                    "gsrnamespace": "6",
                    "gsrlimit": "5",
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "iiurlwidth": "640",
                },
            )
            response.raise_for_status()
        except httpx.HTTPError:
            continue

        pages = response.json().get("query", {}).get("pages", {})
        for page in pages.values():
            image_info = page.get("imageinfo", [])
            if not image_info:
                continue

            first_image = image_info[0]
            image_url = first_image.get("thumburl") or first_image.get("url")
            if image_url:
                return {
                    "image_url": image_url,
                    "image_source": "wikimedia_commons",
                    "image_title": page.get("title"),
                }

    return None


def build_food_search_terms(item_name: str) -> list[str]:
    canonical_name = get_canonical_food_name(item_name)
    terms = [
        f"{canonical_name} food",
        f"{canonical_name} Vietnamese food",
        f"{item_name} food",
    ]
    return list(dict.fromkeys(terms))


def get_canonical_food_name(item_name: str) -> str:
    normalized_name = normalize_text(item_name)
    for keywords, canonical_name in CANONICAL_FOOD_KEYWORDS:
        if any(keyword in normalized_name for keyword in keywords):
            return canonical_name

    return strip_menu_modifiers(item_name)


def strip_menu_modifiers(item_name: str) -> str:
    removable_terms = [
        "đặc biệt",
        "size m",
        "size l",
        "cấp độ 1",
        "cấp độ 2",
        "cấp độ 3",
        "cấp độ 4",
        "cấp độ 5",
        "thêm",
        "combo",
        "2 người",
        "mini",
        "lớn",
    ]
    simplified_name = item_name
    for term in removable_terms:
        simplified_name = simplified_name.replace(term, "")
        simplified_name = simplified_name.replace(term.title(), "")

    return " ".join(simplified_name.split())


def build_placeholder_url(item_name: str) -> str:
    return f"https://placehold.co/640x480/f8f4ed/3b3028?text={quote_plus(item_name)}"


def build_keyword_food_image_url(item_name: str) -> str:
    canonical_name = get_canonical_food_name(item_name)
    ascii_name = strip_accents(canonical_name).lower()
    tags = [tag for tag in re.split(r"[^a-z0-9]+", ascii_name) if tag]
    keyword = ",".join(tags[:4] + ["food"])
    return f"https://loremflickr.com/640/480/{quote(keyword)}"


def build_wikimedia_file_url(file_name: str) -> str:
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(file_name)}?width=640"


def strip_accents(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())
