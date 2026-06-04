import unittest

from .retriever import retrieve_items_for_task


class RetrieverTests(unittest.TestCase):
    def test_budget_filter_returns_items_under_price(self):
        task = {
            "intent": "recommend_items",
            "task_type": "recommend_items",
            "entities": {},
            "filters": {
                "is_available": 1,
                "shop_status": "open",
                "max_effective_price": 50000,
            },
            "ranking": {"effective_price": "asc"},
            "limit": 5,
        }

        result = retrieve_items_for_task(task)

        self.assertGreater(len(result["items"]), 0)
        self.assertTrue(all(item["effective_price"] <= 50000 for item in result["items"]))
        self.assertTrue(all(item["shop_status"] == "open" for item in result["items"]))

    def test_specific_dish_keyword_can_retrieve_item(self):
        task = {
            "intent": "recommend_items",
            "task_type": "search_or_recommend_items",
            "entities": {"dish_keywords": ["Bánh khọt Vũng Tàu"]},
            "filters": {"is_available": 1, "shop_status": "open"},
            "ranking": {"recommendation_score": "desc"},
            "limit": 5,
        }

        result = retrieve_items_for_task(task)

        self.assertTrue(any(item["item_name"] == "Bánh khọt Vũng Tàu" for item in result["items"]))

    def test_exclude_allergen_filters_matching_items(self):
        task = {
            "intent": "recommend_items",
            "task_type": "recommend_items",
            "entities": {"exclude_allergens": ["hải sản"]},
            "filters": {"is_available": 1, "shop_status": "open"},
            "ranking": {"recommendation_score": "desc"},
            "limit": 20,
        }

        result = retrieve_items_for_task(task)

        self.assertGreater(len(result["items"]), 0)
        for item in result["items"]:
            haystack = " ".join([item["item_name"], item["description"], *item["tags"], *item["allergens"]])
            self.assertNotIn("hải sản", haystack.casefold())

    def test_fallback_keeps_price_before_relaxing_price(self):
        task = {
            "intent": "recommend_items",
            "task_type": "recommend_items",
            "entities": {"include_tags": ["giao nhanh"]},
            "filters": {
                "is_available": 1,
                "shop_status": "open",
                "max_effective_price": 50000,
                "max_avg_delivery_time_min": 20,
            },
            "ranking": {
                "avg_delivery_time_min": "asc",
                "recommendation_score": "desc",
            },
            "limit": 5,
        }

        result = retrieve_items_for_task(task)

        self.assertEqual(result["items"], [])
        self.assertGreater(len(result["fallback_items"]), 0)
        self.assertTrue(
            all(item["effective_price"] <= 50000 for item in result["fallback_items"])
        )
