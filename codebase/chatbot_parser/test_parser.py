import unittest

from .parser import parse_user_query


class ChatbotParserTests(unittest.TestCase):
    def test_budget_under_50k(self):
        task = parse_user_query("Gợi ý món dưới 50k gần tôi")

        self.assertEqual(task["intent"], "recommend_items")
        self.assertEqual(task["primary_intent"], "budget_meal")
        self.assertEqual(task["filters"]["max_effective_price"], 50000)
        self.assertEqual(task["filters"]["is_available"], 1)
        self.assertEqual(task["filters"]["shop_status"], "open")

    def test_specific_dish_and_allergen(self):
        task = parse_user_query("Tôi muốn ăn bánh khọt Vũng Tàu, không hải sản, tầm 60k")

        self.assertIn("Bánh khọt Vũng Tàu", task["entities"]["dish_keywords"])
        self.assertIn("hải sản", task["entities"]["exclude_allergens"])
        self.assertEqual(task["filters"]["max_effective_price"], 60000)

    def test_spicy_fast_dinner(self):
        task = parse_user_query("Có món nào cay cay ăn tối giao nhanh không?")

        self.assertEqual(task["filters"]["min_spicy_level"], 3)
        self.assertEqual(task["filters"]["max_avg_delivery_time_min"], 20)
        self.assertIn("ăn tối", task["entities"]["include_tags"])
        self.assertEqual(next(iter(task["ranking"])), "avg_delivery_time_min")

    def test_50k_does_not_negate_following_tag(self):
        task = parse_user_query("Gợi ý món dưới 50k giao nhanh")

        self.assertIn("giao nhanh", task["entities"]["include_tags"])
        self.assertNotIn("exclude_tags", task["entities"])

    def test_group_vegetarian(self):
        task = parse_user_query("Tôi ăn chay, đặt cho nhóm 3 người")

        self.assertEqual(task["primary_intent"], "group_order")
        self.assertEqual(task["entities"]["party_size"], 3)
        self.assertIn("chay", [tag.casefold() for tag in task["entities"]["include_tags"]])


if __name__ == "__main__":
    unittest.main()
