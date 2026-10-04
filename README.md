# 🎰 Toqi999bigwin - Full-Stack Casino Engine & Simulator

Platform simulasi kasino modern dengan arsitektur **Django REST Framework (Backend & Web HTMX)** dan **Flutter (Mobile App)**, dilengkapi 2 engine permainan utama:
1. **Baccarat (Punto Banco)**: Menggunakan standar 8-deck shoe internasional dengan aturan penarikan kartu ketiga otomatis (*tableau drawing rules*), sistem komisi banker 5%, dan pembayaran tie 8:1.
2. **Cross Chicken (Crash)**: Permainan multiplier real-time yang didukung sistem kriptografi **Provably Fair (HMAC-SHA256)** di mana pemain dapat memverifikasi keaslian hasil secara matematis.

---

## 📁 Struktur Direktori Proyek

```text
Toqi999bigwin/
├── .gitignore
├── README.md
├── Procfile                       # Deployment runner untuk PWS (Gunicorn)
├── requirements.txt               # Root requirements
├── manage.py                      # Root proxy runner
│
├── backend/                       # Project Django Engine
│   ├── manage.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── db.sqlite3                 # SQLite untuk dev (bisa dipindah ke PostgreSQL PWS)
│   │
│   ├── core_project/              # Konfigurasi Utama Django
│   │   ├── __init__.py
│   │   ├── settings.py            # CORS, DRF, WhiteNoise, PWS PostgreSQL settings
│   │   ├── urls.py                # Routing web & REST API
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── accounts/                  # App 1: User & Wallet Management
│   │   ├── models.py              # Wallet ($1,000 complimentary chips), Transaction ledger
│   │   ├── views.py               # Auth & Dashboard Logic (Web/HTMX)
│   │   ├── api_views.py           # Auth API (DRF Token Authentication untuk Flutter)
│   │   ├── serializers.py         # DRF Serializers
│   │   ├── urls.py
│   │   ├── api_urls.py
│   │   └── templates/accounts/    # Template Login, Register, Dashboard
│   │
│   ├── games/                     # App 2: Core Game Engines (Baccarat & Crash)
│   │   ├── models.py              # GameRound, Bet models
│   │   ├── game_logic/            # Murni Logika Matematika & RNG
│   │   │   ├── __init__.py
│   │   │   ├── baccarat.py        # Logic Punto Banco 8-deck & Tableau rules
│   │   │   └── crash.py           # Logic Multiplier curve & HMAC-SHA256 Provably Fair
│   │   ├── views.py               # HTMX Game Controllers (Baccarat deal, Crash bet/cashout)
│   │   ├── api_views.py           # DRF Game APIs
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── api_urls.py
│   │   └── templates/games/       # UI Game Web (Baccarat table, Crash arena, Verifier)
│   │
│   ├── static/                    # Asset Statis Web
│   │   ├── css/style.css          # Desain Luxury Dark Casino Glassmorphism
│   │   ├── js/htmx.min.js         # Library HTMX
│   │   ├── js/baccarat.js         # Interactive Baccarat client
│   │   ├── js/crash.js            # 60fps HTML5 Canvas Cross Chicken client
│   │   └── js/audio.js            # Web Audio API Synthesizer (chips, cards, win sounds)
│   │
│   └── templates/                 # Base layout HTML
│       ├── base.html              # Base layout dengan Live Wallet Badge & Deposit Modal
│       └── index.html             # Landing page
│
└── mobile_app/                    # Project Flutter App
    ├── pubspec.yaml
    ├── lib/
    │   ├── main.dart              # MultiProvider & Dark Theme Setup
    │   ├── models/                # User, Wallet, Bet, Baccarat, Crash Models
    │   ├── services/
    │   │   └── api_service.dart   # HTTP Client ke Django REST Framework
    │   ├── providers/             # State Management (AuthProvider, BaccaratProvider, CrashProvider)
    │   └── screens/               # UI Screens (Login, Register, Dashboard, Baccarat, Crash, History)
    └── assets/
```

---

## 🚀 Panduan Menjalankan Backend (Django)

### 1. Prasyarat
- Python 3.9+ terpasang di komputer Anda.

### 2. Setup Virtual Environment & Install Dependensi
Buka terminal di root direktori `Toqi999bigwin/`:

```bash
# Buat virtual environment
python3 -m venv .venv

# Aktifkan virtual environment
# Di macOS / Linux:
source .venv/bin/activate
# Di Windows:
# .venv\Scripts\activate

# Install dependensi backend
pip install -r backend/requirements.txt
```

### 3. Migrasi Database & Buat Superuser
```bash
python manage.py makemigrations accounts games
python manage.py migrate
python manage.py createsuperuser  # Opsional untuk akses Django Admin
```

### 4. Menjalankan Unit Tests
Semua engine logika Baccarat, Crash, Provably Fair, dan sistem Wallet telah dilengkapi unit test:
```bash
python manage.py test accounts games
```

### 5. Jalankan Web Server
```bash
python manage.py runserver
```
Buka browser di: `http://127.0.0.1:8000/`

---

## 📱 Panduan Menjalankan Mobile App (Flutter)

### 1. Masuk ke Direktori Flutter
```bash
cd mobile_app
```

### 2. Install Dependensi
```bash
flutter pub get
```

### 3. Konfigurasi Endpoint Backend
Secara *default*, `lib/services/api_service.dart` menggunakan `http://10.0.2.2:8000` (untuk Android Emulator).
- Jika menggunakan **iOS Simulator** atau **Chrome Web**: Ubah `baseUrl` ke `http://127.0.0.1:8000`.
- Jika mengakses server **PWS production**: Ubah `baseUrl` ke `https://muhammad-syarifudin51-toqi999bigwin.pws.cs.ui.ac.id`.

### 4. Jalankan Aplikasi
```bash
flutter run
```

---

## 🌐 Panduan Deployment ke PWS (Pacil Web Service)

Sesuai kredensial dan konfigurasi di PWS:
- **Project Name:** `toqi999bigwin`
- **Username:** `muhammad.syarifudin51`
- **Remote URL:** `https://pws.cs.ui.ac.id/muhammad.syarifudin51/toqi999bigwin`

### Langkah-langkah Push ke PWS:
1. Daftarkan remote PWS ke repositori Git lokal:
   ```bash
   git remote add pws https://pws.cs.ui.ac.id/muhammad.syarifudin51/toqi999bigwin
   ```
2. Pastikan branch utama bernama `master`:
   ```bash
   git branch -M master
   ```
3. Push kode ke PWS:
   ```bash
   git push pws master
   ```
   *Masukkan Username dan Password PWS saat diminta oleh terminal.*

4. Jalankan migrasi di terminal container PWS:
   ```bash
   python manage.py migrate
   ```

---

## 🎲 Dokumentasi API REST (DRF)

| Method | Endpoint | Deskripsi |
|---|---|---|
| `POST` | `/api/accounts/register/` | Pendaftaran user baru (+ free 1,000 chips) |
| `POST` | `/api/accounts/login/` | Autentikasi user & mengembalikan Auth Token |
| `GET` | `/api/accounts/profile/` | Mengambil data user & saldo wallet aktif |
| `POST` | `/api/accounts/deposit/` | Isi ulang chips virtual |
| `POST` | `/api/games/baccarat/play/` | Pasang taruhan Baccarat & terima hasil kartu |
| `POST` | `/api/games/crash/init-round/` | Inisialisasi round provably fair Cross Chicken |
| `POST` | `/api/games/crash/bet/` | Pasang taruhan Cross Chicken |
| `POST` | `/api/games/crash/cashout/` | Cash out taruhan pada multiplier berjalan |
| `POST` | `/api/games/crash/finish/` | Finalisasi round setelah crash |
| `GET` | `/api/games/history/` | Riwayat transaksi dan taruhan user |
| `POST` | `/api/games/verify/` | Verifikasi independen provably fair hash |

---

## ⚖️ Disclaimer
Aplikasi ini dibuat murni untuk keperluan akademis dan pembelajaran pengembangan perangkat lunak (Course Pemrograman Berbasis Platform). Seluruh chips dan saldo adalah virtual dan tidak melibatkan uang riil.
