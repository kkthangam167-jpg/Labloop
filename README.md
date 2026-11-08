# LabLoop – Smart Laboratory Management Platform

LabLoop is a full-stack, enterprise-grade laboratory equipment scheduling, attendance tracking, and asset management platform designed for academic and institutional research facilities.

---

## 🌟 Key Features

* **Institutional Authentication & Email Verification**:
  - Enforces the student institutional email format: `studentname.ug.YY.DD@francisxavier.ac.in`.
  - Cryptographic 6-digit email OTP verification before student account activation.
  - Role-aware authentication using cryptographically signed JSON Web Tokens (JWT).
* **Role-Based Portals & Dashboards**:
  - **Student Portal**: Equipment catalog search, timeslot reservation, active session QR check-in & check-out, and incident/damage reporting.
  - **Lab In-charge Portal**: Pending booking queue approvals/rejections, physical facility monitoring, equipment calibration status, and maintenance scheduling.
  - **Super Admin Portal**: Campus-wide infrastructure management, academic department oversight, laboratory spaces, and user account status controls.
* **Security & Compliance**:
  - Strict backend-enforced role verification (`@role_required`).
  - Bcrypt password hashing and secure token rotation with database-backed refresh tokens.
  - Complete segregation of privileged administrative portals from public visitor views.
  - Automatic cross-origin resource sharing (CORS) origin protection.

---

## 🏗️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS, React Router v6, React Hook Form, Zod, Lucide Icons, Axios |
| **Backend** | Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Cors, Flask-Limiter, Flask-Mail |
| **Database** | PostgreSQL (Production) / SQLite (Development) |
| **Authentication** | JWT Access & Refresh Tokens, SHA-256 Hashed One-Time Passwords (OTP) |

---

## 📁 Project Directory Structure

```text
web app/
├── .env.example                  # Root environment blueprint
├── .gitignore                    # Global ignore rules (secrets, DBs, node_modules)
├── README.md                     # Project documentation
│
├── frontend/                     # React + Vite Single-Page Application
│   ├── .env.example              # Frontend environment reference
│   ├── index.html                # Application root HTML
│   ├── package.json              # NPM dependencies & scripts
│   ├── vite.config.js            # Vite configuration with API reverse proxy
│   └── src/
│       ├── api/                  # Axios HTTP client & domain API endpoints
│       ├── components/           # Reusable UI controls & layout wrappers
│       ├── hooks/                # React Query & authentication hooks
│       ├── pages/
│       │   ├── admin/            # Super Admin console
│       │   ├── incharge/         # Lab In-charge operational dashboard
│       │   ├── student/          # Student booking & equipment dashboard
│       │   ├── public/           # Landing page, login, registration, password reset
│       │   └── errors/           # 403 Unauthorized & 404 Not Found pages
│       ├── routes/               # RoleRoute & ProtectedRoute guard wrappers
│       └── store/                # Zustand client-side persistent auth store
│
└── backend/                      # Python Flask REST API
    ├── .env.example              # Backend environment template
    ├── requirements.txt          # Python packages & WSGI servers
    ├── run.py                    # Local development server entry point
    ├── seed.py                   # Initial database seeder script
    ├── migrations/               # Alembic database migration versions
    └── app/
        ├── config.py             # Environment configurations (Dev, Prod, Test)
        ├── extensions.py         # SQLAlchemy, Migrate, JWT, CORS, Limiter, Mail
        ├── models/               # Database ORM models & relationships
        ├── routes/               # Flask Blueprints (Auth, Users, Labs, Bookings, etc.)
        ├── schemas/              # Marshmallow serialization & validation schemas
        └── services/             # Email dispatching & helper utilities
```

---

## 🚀 Local Development Setup

### 1. Prerequisites
- **Node.js** v18+ and **npm**
- **Python** 3.10+ and **pip**

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# (Optional) Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env    # On Windows
# cp .env.example .env    # On Linux/macOS

# Run database migrations
flask --app run.py db upgrade

# (Optional) Seed demo laboratories and accounts
python seed.py

# Start the Flask development server (runs on http://127.0.0.1:5000)
python run.py
```

### 3. Frontend Setup
```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install npm packages
npm install

# Start the Vite development server
npm run dev
```

Open your browser to: **`http://localhost:5173`** (or the port assigned by Vite).

---

## 🔐 Student Institutional Email Specification

All student accounts must follow the approved institutional pattern:
```text
studentname.ug.YY.DD@francisxavier.ac.in
```
* **studentname**: Dynamic lowercase student name (e.g., `priya`, `arun`, `kavin`).
* **ug**: Undergraduate marker.
* **YY**: 2-digit admission year code (e.g., `24`, `25`, `26`, `27`).
* **DD**: 2+ letter academic department code (e.g., `cs`, `ec`, `ai`, `it`, `me`, `ee`).

---

## 📦 Production Deployment

### Frontend Deployment
1. Set the production API URL in `frontend/.env` (or use `/api` if using a reverse proxy):
   ```ini
   VITE_API_BASE_URL=/api
   ```
2. Build the optimized production bundle:
   ```bash
   npm run build
   ```
3. Deploy the resulting `frontend/dist/` directory to **Vercel**, **Netlify**, **Cloudflare Pages**, or serve via **Nginx**.

### Backend Deployment
1. Provide a managed **PostgreSQL** connection string in `DATABASE_URL`.
2. Set strong production secrets for `SECRET_KEY` and `JWT_SECRET_KEY`.
3. Configure outbound institutional SMTP settings (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`).
4. Execute database migrations on the production database:
   ```bash
   flask --app run.py db upgrade
   ```
5. Run using a production WSGI application server (e.g., **Gunicorn**):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
   ```

---

## 🛡️ License & Institutional Notice

This software is developed for institutional resource management. Unauthorized redistribution or modification is subject to institutional guidelines.

