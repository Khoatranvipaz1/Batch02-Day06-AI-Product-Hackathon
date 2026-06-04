# Chatbot parser

Bước đầu của chatbot ShopeeFood demo: đổi câu hỏi tiếng Việt của người dùng thành task JSON có thể dùng để query mock database.

## Chạy thử

```powershell
python -m codebase.chatbot_parser "Gợi ý món dưới 50k gần tôi"
```

Nếu không truyền câu hỏi, CLI sẽ chạy vài ví dụ demo:

```powershell
python -m codebase.chatbot_parser
```

## Output chính

```json
{
  "version": "food_task.v1",
  "task_type": "recommend_items",
  "intent": "recommend_items",
  "primary_intent": "budget_meal",
  "sub_intents": ["budget_meal"],
  "entities": {
    "include_tags": ["rẻ"]
  },
  "filters": {
    "is_available": 1,
    "shop_status": "open",
    "max_effective_price": 50000
  },
  "ranking": {
    "recommendation_score": "desc",
    "item_rating": "desc",
    "effective_price": "asc"
  },
  "limit": 10
}
```

## Field dùng cho bước tiếp theo

- `filters`: điều kiện query, ví dụ `max_effective_price`, `min_spicy_level`, `max_avg_delivery_time_min`, `exclude_allergens`.
- `entities`: keyword/tag/cuisine/tên món người dùng nhắc đến.
- `ranking`: thứ tự ưu tiên khi sort kết quả.
- `needs_clarification`: `true` khi câu hỏi quá mơ hồ và chatbot nên hỏi lại.

Parser hiện chạy offline bằng rule + vocab trong CSV: `tags.csv`, `cuisines.csv`, `allergens.csv`, `menu_items.csv`. Sau này có thể thêm LLM fallback trước khi query DB.
