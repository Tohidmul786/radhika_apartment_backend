# Radhika Apartment — Maintenance Backend
### Django 4.2 + PostgreSQL REST API

Society: Radhika Apartment Co-op Housing Society (Niyojit)
Address: New Ganesh Nagar, Hazimalang Road, Adiwali, Kalyan (East) - 421306

---

## 🏗️ Apartment Structure (39 Flats Total)

| Wing | Floor   | Rooms | Flat Numbers   |
|------|---------|-------|----------------|
| B    | Ground  | 4     | B-001 to B-004 |
| B    | First   | 6     | B-101 to B-106 |
| B    | Second  | 6     | B-201 to B-206 |
| B    | Third   | 6     | B-301 to B-306 |
| A    | Ground  | 2     | A-001 to A-002 |
| A    | First   | 5     | A-101 to A-105 |
| A    | Second  | 5     | A-201 to A-205 |
| A    | Third   | 5     | A-301 to A-305 |
| **Total** |    | **39**|                |

Monthly Maintenance: ₹400 per flat
Total Outstanding (March 2026): ₹56,800

---

## ⚡ LOCAL Setup (PostgreSQL)

### 1. Install PostgreSQL
Download from `https://www.postgresql.org/download/` and install.
During install, set a password for the `postgres` user — remember it!

### 2. Create database
Open **pgAdmin** or **psql** and run:
```sql
CREATE DATABASE apartment_db;
```

### 3. Install Python packages
```bash
pip install -r requirements.txt
```

### 4. Configure .env
```bash
cp .env.example .env
```
Edit `.env`:
```
DB_NAME=apartment_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Migrate + Seed
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

### 6. Run
```bash
python manage.py runserver
```

---

## 🚀 DEPLOY to Render (PostgreSQL included)

### Step 1 — Push code to GitHub
Create a GitHub repo and push this `apartment_backend` folder.

### Step 2 — Create PostgreSQL Database on Render
1. Go to `https://render.com` → **New** → **PostgreSQL**
2. Name it `radhika-db`
3. Click **Create Database**
4. Wait until status is **Available**
5. Copy the **Internal Database URL** (starts with `postgres://...`)

### Step 3 — Create Web Service
1. Click **New** → **Web Service**
2. Connect your GitHub repo
3. Settings:

| Field | Value |
|-------|-------|
| Build Command | `./build.sh` |
| Start Command | `gunicorn core.wsgi:application` |

### Step 4 — Environment Variables
Add these in Render dashboard:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | (generate random string) |
| `DEBUG` | `False` |
| `DATABASE_URL` | (paste Internal Database URL from Step 2) |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com,https://*.vercel.app` |

### Step 5 — Deploy
Click **Create Web Service**. Render will:
- Install requirements
- Run migrations
- Seed 39 flats
- Start server with gunicorn

You'll get a URL like:
```
https://radhika-apartment-api.onrender.com
```

### Step 6 — Verify
```
https://radhika-apartment-api.onrender.com/api/flats/
https://radhika-apartment-api.onrender.com/admin/
```
Login: `admin / admin123`

---

## 🔐 Authentication

```
POST /api/auth/login/
Body: { "username": "admin", "password": "admin123" }
```
Use returned `access` token as:
```
Authorization: Bearer <access_token>
```

---

## 📡 Key API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/flats/` | List flats (filter: wing, floor, status, search) |
| GET | `/api/flats/{id}/` | Flat detail |
| POST | `/api/payments/` | Record payment |
| GET | `/api/dashboard/` | Stats |
| GET | `/api/reports/pdf/` | PDF report |
| GET | `/api/reports/excel/` | Excel report |
| GET | `/api/reports/receipt/{flat_number}/` | Individual receipt PDF |

---

## 📁 Project Structure
```
apartment_backend/
├── core/
│   ├── settings.py      # PostgreSQL + Whitenoise + CORS
│   └── urls.py
├── apartment_maintenance/
│   ├── models.py
│   ├── serializers.py
│   ├── admin.py
│   ├── urls.py
│   └── views/
├── Procfile              # gunicorn start command
├── build.sh              # Render build script
├── runtime.txt           # Python version
├── requirements.txt
├── .env.example
└── manage.py
```
