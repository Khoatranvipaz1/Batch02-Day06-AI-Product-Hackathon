import unittest

from .pipeline import _apply_history_exclusions


class PipelineHistoryTests(unittest.TestCase):
    def test_alternative_request_excludes_previous_recommendations(self):
        task = {
            "intent": "recommend_items",
            "task_type": "recommend_items",
            "entities": {},
            "filters": {"is_available": 1, "shop_status": "open"},
        }

        _apply_history_exclusions(
            task,
            "Món khác đi, tôi không ưng",
            [
                {"role": "user", "content": "Gợi ý món dưới 50k"},
                {
                    "role": "assistant",
                    "content": "Mình gợi ý Cookie chocolate.",
                    "recommendation_item_ids": ["item_041_005", "item_018_004"],
                },
            ],
        )

        self.assertEqual(
            task["entities"]["exclude_item_ids"],
            ["item_041_005", "item_018_004"],
        )
