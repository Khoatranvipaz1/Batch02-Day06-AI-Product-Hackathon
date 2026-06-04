# CSV Retrieve Tools

These tools support the ShopeeFood thin spec by retrieving menu/shop evidence from CSV files. The main data source is:

```text
codebase/mock_data/shopee_food_db_hcm_q1/v_recommendation_items.csv
```

## `retrieve_csv_rows`

Generic CSV retrieval for debugging or quick lookup.

Use this when the assistant needs to inspect rows from any CSV file.

Input:

```json
{
  "csv_path": "../mock_data/shopee_food_db_hcm_q1/v_recommendation_items.csv",
  "query": "com tam",
  "columns": ["item_name", "effective_price", "shop_name"],
  "limit": 10
}
```

Output:

```json
{
  "source": ".../v_recommendation_items.csv",
  "total_rows": 264,
  "matched_rows": 10,
  "rows": []
}
```

## `retrieve_food_options`

ShopeeFood-aware retrieval for the prototype's top-3 recommendation flow.

Use this when the user asks for food under a budget, non-spicy food, fast delivery, or correction after a bad suggestion.

Input:

```json
{
  "query": "an trua",
  "budget": 60000,
  "max_delivery_time_min": 30,
  "avoid_spicy": true,
  "only_open": true,
  "only_available": true,
  "limit": 3
}
```

Output:

```json
{
  "recommendations": [
    {
      "item_name": "Sup cua",
      "shop_name": "Chao Suon Chu Tu",
      "effective_price": 33000,
      "delivery_fee": 13000,
      "total_price": 46000,
      "spicy_level": 0,
      "delivery_time_min": 18,
      "reason": "tong gia 46000 <= ngan sach 60000; giao trong 18 phut; khong cay; rating quan 4.8"
    }
  ],
  "needs_clarification": false
}
```

## Spec coverage

- Happy path: returns top 3 options under budget, non-spicy, and fast delivery.
- Low-confidence path: if query is vague, call with default constraints or ask for preference if results are too broad.
- Failure path: filters out spicy, over-budget, closed, unavailable, or slow-delivery options.
- Correction path: rerun with updated constraints such as `avoid_spicy=true` or a lower `budget`.

## Notes

- `total_price` is calculated as `effective_price + estimated_delivery_fee`.
- `avoid_spicy=true` rejects any row with `spicy_level > 0`.
- If no recommendation matches, the tool returns `needs_clarification=true` and a Vietnamese clarification question.
