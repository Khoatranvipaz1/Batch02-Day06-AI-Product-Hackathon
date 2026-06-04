import json
import unittest
from unittest.mock import patch

from .openai_parser import OpenAIParserError, _sanitize_api_error, parse_user_query_with_gpt


def _sample_model_task():
    return {
        "version": "food_task.v1",
        "source_text": "ignored",
        "task_type": "recommend_items",
        "intent": "recommend_items",
        "primary_intent": "budget_meal",
        "sub_intents": ["budget_meal"],
        "entities": {
            "include_tags": [],
            "exclude_tags": [],
            "include_cuisines": [],
            "dish_keywords": [],
            "exclude_allergens": [],
            "exclude_item_ids": [],
            "party_size": None,
        },
        "filters": {
            "is_available": 1,
            "shop_status": "open",
            "max_effective_price": 50000,
            "min_effective_price": None,
            "max_estimated_delivery_fee": None,
            "min_spicy_level": None,
            "max_spicy_level": None,
            "max_calories_estimate": None,
            "max_avg_delivery_time_min": None,
            "min_portion_people": None,
            "requires_discount": None,
        },
        "ranking": {
            "recommendation_score": "desc",
            "item_rating": "desc",
            "effective_price": "asc",
            "avg_delivery_time_min": "none",
            "item_sold_count": "none",
            "shop_rating": "none",
            "calories_estimate": "none",
        },
        "limit": 10,
        "confidence": 0.9,
        "needs_clarification": False,
        "clarifying_questions": [],
    }


class OpenAIParserTests(unittest.TestCase):
    def test_missing_api_key_raises(self):
        with self.assertRaises(OpenAIParserError):
            parse_user_query_with_gpt("Gợi ý món dưới 50k", api_key="")

    @patch("codebase.chatbot_parser.openai_parser._post_json")
    def test_api_payload_uses_gpt_4o_mini_and_json_schema(self, post_json):
        post_json.return_value = {
            "choices": [
                {"message": {"content": json.dumps(_sample_model_task(), ensure_ascii=False)}}
            ]
        }

        task = parse_user_query_with_gpt("Gợi ý món dưới 50k", api_key="test-key")

        payload = post_json.call_args.args[1]
        self.assertEqual(payload["model"], "gpt-4o-mini")
        self.assertEqual(payload["response_format"]["type"], "json_schema")
        self.assertTrue(payload["response_format"]["json_schema"]["strict"])
        self.assertEqual(task["filters"]["max_effective_price"], 50000)
        self.assertNotIn("min_effective_price", task["filters"])
        self.assertEqual(task["ranking"]["effective_price"], "asc")
        self.assertNotIn("avg_delivery_time_min", task["ranking"])
        self.assertEqual(task["parser"], "openai_chat_completions_json_schema")

    @patch("codebase.chatbot_parser.openai_parser._post_json")
    def test_api_payload_includes_conversation_history(self, post_json):
        post_json.return_value = {
            "choices": [
                {"message": {"content": json.dumps(_sample_model_task(), ensure_ascii=False)}}
            ]
        }

        parse_user_query_with_gpt(
            "Món khác đi",
            api_key="test-key",
            conversation_history=[
                {
                    "role": "assistant",
                    "content": "Mình gợi ý Súp cua.",
                    "recommendation_item_ids": ["item_018_004"],
                }
            ],
        )

        payload = post_json.call_args.args[1]
        user_payload = json.loads(payload["messages"][1]["content"])
        self.assertEqual(
            user_payload["conversation_history"][0]["recommendation_item_ids"],
            ["item_018_004"],
        )

    def test_api_error_sanitizes_key_like_strings(self):
        body = "Incorrect API key provided: sk-proj-********************************abcD."

        self.assertNotIn("abcD", _sanitize_api_error(body))
        self.assertIn("sk-***", _sanitize_api_error(body))


if __name__ == "__main__":
    unittest.main()
