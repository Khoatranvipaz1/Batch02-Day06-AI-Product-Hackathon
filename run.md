# Hướng Dẫn Chạy Project

Tài liệu này dành cho người mới clone project và muốn chạy đầy đủ backend + frontend trên máy local.

## 1. Yêu Cầu

Cài sẵn:

- Node.js 20+
- Python 3.11+
- Git

Kiểm tra nhanh:

```powershell
node -v
npm -v
python --version
```

Nếu Windows PowerShell chặn `npm.ps1`, dùng `npm.cmd` thay cho `npm` trong các lệnh bên dưới.

## 2. Clone Project

```powershell
git clone <repo-url>
cd Batch02-Day06-AI-Product-Hackathon
```

## 3. Tạo File `.env`

Project có 2 file `.env` riêng:

- Backend: `codebase/backend/.env`
- Frontend: `codebase/frontend/.env`

### 3.1. Backend `.env`

Tạo file:

```powershell
cd codebase/backend
copy .env.example .env
```

Mở `codebase/backend/.env` và chỉnh thành dạng sau:

```env
APP_NAME=AI Chatbot Backend
APP_ENV=development
FRONTEND_ORIGIN=http://localhost:5173


OPENAI_API_KEY= your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

```

### 3.2. Frontend `.env`

Tạo file:

```powershell
cd ../frontend
copy .env.example .env
```

Nội dung `codebase/frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Giải thích:

- `VITE_API_BASE_URL`: địa chỉ backend mà frontend sẽ gọi API.
- Khi chạy backend local, giữ `http://localhost:8000`.
- Nếu backend chạy ở máy/server khác, đổi giá trị này sang URL backend đó.

## 4. Chạy Backend

Mở terminal thứ nhất:
Chỉ cần làm 1 lần:

```powershell
cd codebase/backend
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

Những lần sau: 
cd codebase/backend
.\.venv\Scripts\activate
python -m uvicorn app.main:app --reload 
```

Backend chạy tại:

```text
http://localhost:8000
```

Kiểm tra:

```text
http://localhost:8000/health
http://localhost:8000/api/menu-items
```

## 5. Chạy Frontend

Mở terminal thứ hai:
Chỉ cần làm 1 lần:
```powershell
cd codebase/frontend
npm install

Những lần sau:
cd codebase/frontend
npm run dev
```

Nếu PowerShell báo lỗi execution policy, chạy:

```powershell
npm.cmd install
npm.cmd run dev
```

Frontend chạy tại:

```text
http://localhost:5173
```

