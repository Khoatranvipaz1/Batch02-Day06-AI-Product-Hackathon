# Prompt Eval - ShopeeFood AI Chatbot

Muc tieu cua eval nay la chung minh luong AI khong chi tra loi tu do, ma di qua dung pipeline:

1. Hieu cau hoi nguoi dung bang prompt NLU.
2. Tao `food_task.v1` co intent, filters, entities, ranking.
3. Lay mon tu mock data.
4. Sinh cau tra loi cuoi bang tieng Viet, chi dua tren retrieved data.

## Prompt dang duoc eval

- NLU parser prompt: `codebase/chatbot_parser/openai_parser.py` -> `SYSTEM_PROMPT`
- Final answer prompt: `codebase/food_chatbot/answerer.py` -> `FINAL_ANSWER_SYSTEM_PROMPT`

## Eval prompt cho nguoi cham/demo

Hay kiem tra chatbot voi cac input sau. Voi moi input, chatbot dat neu:

- Tra loi bang tieng Viet, ngan gon, dung ngu canh dat mon an.
- Khong bia mon/gia/quan ngoai mock data.
- Parsed task dung intent chinh, filter gia/thoi gian/do cay/di ung/nhom nguoi.
- Co goi y mon khi yeu cau ro; hoi lai khi cau hoi mo hoac khong lien quan do an.

| ID | Input | Ky vong |
| --- | --- | --- |
| budget_fast_lunch | `Goi y mon an trua duoi 50k giao nhanh o Quan 1` | Nhan ra budget + an trua + giao nhanh; gia <= 50k; co goi y mon. |
| specific_dish_allergen | `Toi muon an Banh khot Vung Tau, khong hai san, tam 60k` | Nhan ra ten mon, tranh hai san, gia tam 60k; neu khong khop tuyet doi thi bao gan dung. |
| healthy_low_oil | `Minh dang an healthy, it dau mo, co mon nao nhe bung khong?` | Nhan ra healthy/it dau mo; goi y mon phu hop. |
| spicy_dinner | `Toi nay muon an mon cay cay, rating tot` | Nhan ra an toi + cay; set do cay toi thieu; uu tien rating. |
| group_vegetarian | `Dat mon chay cho nhom 3 nguoi, uu tien combo` | Nhan ra mon chay, nhom 3 nguoi, combo/phan nhieu nguoi; neu mock data khong co mon khop thi hoi nguoi dung noi dieu kien. |
| clarify_noise | `Hom nay thoi tiet the nao?` | Khong query mon an; hoi lai nhu cau dat mon. |

## Cach chay nhanh

Offline, khong can API key:

```bash
cd codebase
..\.venv\Scripts\python.exe evals\run_eval.py
```

Neu chay tu thu muc goc repo:

```bash
.\.venv\Scripts\python.exe -c "import runpy, sys; sys.argv=['run_eval.py']; runpy.run_path('codebase/evals/run_eval.py', run_name='__main__')"
```

Chay voi AI that sau khi set `OPENAI_API_KEY` trong `codebase/backend/.env` hoac environment:

```bash
.\.venv\Scripts\python.exe -c "import runpy, sys; sys.argv=['run_eval.py','--parse-mode','api','--answer-mode','api']; runpy.run_path('codebase/evals/run_eval.py', run_name='__main__')"
```

Ket qua pass/fail chi ra case nao sai, sai o field nao: intent, filter, entity, recommendation count, hoac noi dung answer.
