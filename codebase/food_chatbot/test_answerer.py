import json
import unittest
from unittest.mock import patch

from .answerer import build_template_answer, generate_final_answer_with_gpt


class AnswererTests(unittest.TestCase):
    def test_template_answer_uses_retrieved_items(self):
        answer = build_template_answer(
            "budget meal under 50k",
            {"intent": "recommend_items", "filters": {"max_effective_price": 50000}},
            {
                "items": [
                    {
                        "item_name": "Sup cua",
                        "effective_price": 33000,
                        "shop_name": "Chao Suon Chu Tu",
                        "item_rating": 4.8,
                        "avg_delivery_time_min": 18,
                        "match_reasons": ["gia 33,000d <= 50,000d"],
                    }
                ]
            },
        )

        self.assertIn("Sup cua", answer)
        self.assertIn("33,000", answer)

    @patch("codebase.food_chatbot.answerer._post_json")
    def test_final_answer_calls_openai_with_retrieved_data(self, post_json):
        post_json.return_value = {
            "choices": [{"message": {"content": "Ban nen chon Sup cua."}}]
        }

        answer = generate_final_answer_with_gpt(
            "budget meal under 50k",
            {"intent": "recommend_items", "filters": {"max_effective_price": 50000}},
            {"items": [{"item_name": "Sup cua", "effective_price": 33000}]},
            api_key="test-key",
            conversation_history=[
                {
                    "role": "assistant",
                    "content": "Previous recommendations",
                    "recommendation_item_ids": ["item_041_005"],
                }
            ],
        )

        payload = post_json.call_args.args[1]
        user_payload = json.loads(payload["messages"][1]["content"])
        self.assertEqual(payload["model"], "gpt-4o-mini")
        self.assertEqual(answer, "Ban nen chon Sup cua.")
        self.assertEqual(user_payload["retrieved_data"]["items"][0]["item_name"], "Sup cua")
        self.assertEqual(
            user_payload["conversation_history"][0]["recommendation_item_ids"],
            ["item_041_005"],
        )
