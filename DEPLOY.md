# Deploy MedVault to Render

Render hosts the **Flask app**. You still need a **cloud MySQL** database (Render does not include MySQL on the free plan).

After setup, your live URL will look like:

**`https://medvault-hospital.onrender.com`**

(exact name depends on what you choose in Render)

---

## Step 1 — Push code to GitHub

1. Create a new repo on [GitHub](https://github.com/new) (e.g. `hospital-medvault`).
2. In PowerShell, from your project folder:

```powershell
cd "C:\Users\Sai Supritha K S\Desktop\HOSPITAL"
git init
git add .
git commit -m "Prepare MedVault for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub details.

---

## Step 2 — Free cloud MySQL

Use a free remote MySQL host (pick one):

| Service | Sign up |
|--------|---------|
| **FreeSQLDatabase** | https://www.freesqldatabase.com |
| **RemoteMySQL** | https://remotemysql.com |

1. Create a database (note **host**, **port**, **username**, **password**, **database name**).
2. Open their **phpMyAdmin** (or SQL console).
3. Run **`setup.sql`** (full file).
4. Run **`alter.sql`** (adds login columns for doctors/patients).

Keep those credentials — you will paste them into Render.

---

## Step 3 — Create Render Web Service

1. Go to [https://render.com](https://render.com) and sign up / log in.
2. Click **New +** → **Blueprint** (or **Web Service** if you prefer manual).
3. Connect your **GitHub** account and select your repo.
4. If using **Blueprint**, Render reads `render.yaml` automatically.
5. If using **Web Service** manually:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

---

## Step 4 — Environment variables (Render Dashboard)

In your service → **Environment** → add:

| Key | Value |
|-----|--------|
| `SECRET_KEY` | Long random string (Render can generate one) |
| `FLASK_DEBUG` | `false` |
| `MYSQL_HOST` | From your MySQL provider |
| `MYSQL_PORT` | Usually `3306` |
| `MYSQL_USER` | From your MySQL provider |
| `MYSQL_PASSWORD` | From your MySQL provider |
| `MYSQL_DATABASE` | e.g. `hospital_db` or provider DB name |
| `MYSQL_SSL` | `false` (set `true` only if provider requires SSL) |

Click **Save Changes** → **Manual Deploy** (or wait for auto deploy).

---

## Step 5 — Your deployed link

When deploy status is **Live**, open:

**https://&lt;your-service-name&gt;.onrender.com**

Example: `https://medvault-hospital.onrender.com`

### Demo logins (after `alter.sql` is imported)

| Role | Login | Password |
|------|--------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `LIC-CARD-001` | `doctor123` |
| Patient | `arjun@email.com` | `patient123` |

---

## Troubleshooting

| Problem | Fix |
|--------|-----|
| **Deploy failed** | Check Render **Logs** tab for Python/pip errors |
| **502 / app crashes** | Wrong `MYSQL_*` env vars or DB not reachable |
| **Can't login** | Run `alter.sql` on cloud DB; confirm tables have `password` columns |
| **Slow first load** | Free Render spins down after ~15 min idle — first request wakes it (~30–60s) |

---

## Local vs production

| | Local | Render |
|--|--------|--------|
| URL | http://127.0.0.1:5000 | https://your-app.onrender.com |
| DB | Local MySQL | Cloud MySQL env vars |
| Run | `python app.py` | Automatic via gunicorn |

Do **not** commit `.env` or real passwords to GitHub.
