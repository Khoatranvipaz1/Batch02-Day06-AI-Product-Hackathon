# AI Chatbot Project

Khung dự án gồm React frontend và Python FastAPI backend để nhóm bắt đầu code chatbot.

## Cấu trúc

```text
codebase/
  backend/
    app/
      main.py
      config.py
      routers/chat.py
    requirements.txt
    .env.example
  frontend/
    src/
      App.tsx
      api.ts
      main.tsx
      styles.css
    package.json
    .env.example
  package.json
  .env.example
```

## Setup backend Python

```bash
cd codebase/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Backend chạy mặc định tại `http://localhost:8000`.

Nếu máy Windows dùng Python Launcher, có thể thay `python` bằng `py`.

## Setup frontend React

```bash
cd codebase/frontend
npm install
copy .env.example .env
npm run dev
```

Frontend chạy mặc định tại `http://localhost:5173`.

Nếu PowerShell báo chặn `npm.ps1`, dùng `npm.cmd install` và `npm.cmd run dev`, hoặc chạy bằng terminal CMD/Git Bash.

## Chạy cả frontend và backend từ thư mục `codebase`

Phần này là tuỳ chọn nếu nhóm muốn chạy hai service bằng một lệnh.

```bash
cd codebase
npm install
npm run dev
```

## Ghi chú môi trường

- Không commit file `.env`.
- API key chỉ để ở backend `.env`, không để trong frontend.
- Endpoint mẫu hiện tại là `POST /api/chat`; phần gọi model thật sẽ được code trong `backend/app/routers/chat.py`.
