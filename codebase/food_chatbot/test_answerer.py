import json
import unittest
from unittest.mock import patch

from .answerer import build_template_answer, generate_final_answer_with_gpt


class AnswererTests(unittest.TestCase):
    def test_template_answer_uses_retrieved_items(self):
        answer = build_template_answer(
            "Gợi ý món dưới 50k",
            {"intent": "recommend_items", "filters": {"max_effective_price": 50000}},
            {
                "items": [
                    {
                        "item_name": "Súp cua",
                        "effective_price": 33000,
                        "shop_name": "Cháo Sườn Chú Tư",
                        "item_rating": 4.8,
                        "avg_delivery_time_min": 18,
                        "match_reasons": ["giá 33,000đ <= 50,000đ"],
                    }
                ]
            },
        )

        self.assertIn("Súp cua", answer)
        self.assertIn("33,000đ", answer)

    @patch("codebase.food_chatbot.answerer._post_json")
    def test_final_answer_calls_openai_with_retrieved_data(self, post_json):
        post_json.return_value = {
            "choices": [{"message": {"content": "Bạn nên chọn Súp cua."}}]
        }

        answer = generate_final_answer_with_gpt(
            "Gợi ý món dưới 50k",
            {"intent": "recommend_items", "filters": {"max_effective_price": 50000}},
            {"items": [{"item_name": "Súp cua", "effective_price": 33000}]},
            api_key="test-key",
        )

        payload = post_json.call_args.args[1]
        user_payload = json.loads(payload["messages"][1]["content"])
        self.assertEqual(payload["model"], "gpt-4o-mini")
        self.assertEqual(answer, "Bạn nên chọn Súp cua.")
        self.assertEqual(user_payload["retrieved_data"]["items"][0]["item_name"], "Súp cua")
