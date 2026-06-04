# Huong dan chay project sau khi clone moi

## Yeu cau

- Node.js 20+
- Python 3.11+

## 1. Clone project

```powershell
git clone <repo-url>
cd Batch02-Day06-AI-Product-Hackathon
```

## 2. Chay backend

Mo terminal thu nhat:

```powershell
cd codebase/backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Backend chay tai:

```text
http://localhost:8000
```

Kiem tra backend:

```text
http://localhost:8000/health
```

API danh sach mon an:

```text
http://localhost:8000/api/menu-items
```

## 3. Chay frontend

Mo terminal thu hai:

```powershell
cd codebase/frontend
npm install
copy .env.example .env
npm run dev
```

Frontend chay tai:

```text
http://localhost:5173
```

## Chay ca backend va frontend bang mot lenh

Neu muon chay ca hai service cung luc:

```powershell
cd codebase
npm install
npm run dev
```

Lenh nay se chay:

```text
Backend:  http://localhost:8000
Frontend: http://localhost:5173
```

## Ghi chu Windows

Neu PowerShell chan `npm.ps1`, dung:

```powershell
npm.cmd install
npm.cmd run dev
```

Neu may dung Python Launcher, co the thay `python` bang `py`.
