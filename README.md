# Web Application - Spotify Explorer

## Disclaimer

There is a chance for Spotify API to change their API setup (e.g., different endpoint name).
If something does not load within the app, it is likely because of that — check API endpoints first.

---

## 🚀 Running the Project

You can run the project using **Docker Compose** (recommended) or set it up manually using **Python virtual environments**. Both sections can be read standalone, so you don't need to jump back and forth.

---

### 🐳 Docker Compose (recommended)

This is the easiest way to run the app for **both development** and **production**.

---

#### 📦 1. Clone the repository

```bash
git clone https://github.com/nedasadamavicius/spotify-explorer.git
cd spotify-explorer
```

---

#### 🔑 2. Define environment variables

From the same **repository root** directory:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret
SECRET_KEY=your-secret
DEBUG=True
ALLOWED_HOSTS=localhost
STATIC_ROOT=/static
```

For production, set `DEBUG=False`, `ALLOWED_HOSTS=your-domain.com`, and `STATIC_ROOT=/var/www/webapp/static/` - or anywhere you want Django to collect static files to, just make sure you can serve those static files.

---

#### ℹ️ About environment variables

* **SPOTIFY\_CLIENT\_ID / SPOTIFY\_CLIENT\_SECRET**
  Get these from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
  Create an app there to retrieve your credentials.

* **SECRET\_KEY**
  This is required by Django for cryptographic signing.
  Generate a strong secret key with:

  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

  ⚠️ **Keep this key safe and never commit it to version control.**

---

#### 🏃 3. Start the app

From the **repository root**, for development run:

```bash
docker compose -f docker-compose.dev.yml up --build
```

* Visit [http://localhost:8000](http://localhost:8000).

And if production:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

* Then visit the domain you've defined in the `.env` file

---

#### 🔄 Common Docker commands

Run Django management commands inside the container:

```bash
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py migrate --noinput
```

---

### 🐍 Python Virtual Environment (manual setup)

This is the **legacy setup** for running the app without Docker. Works for **both development** and **production**.

---

#### 📦 1. Create a virtual environment

```bash
python -m venv .venv
```

---

#### 🔑 2. Activate the virtual environment

* On **Windows**:

  ```bash
  .venv\Scripts\activate
  ```

* On **Unix/MacOS**:

  ```bash
  source .venv/bin/activate
  ```

---

#### 📥 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

#### 🔑 4. Define environment variables

From the same **repository root** directory:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret
SECRET_KEY=your-secret
DEBUG=True
ALLOWED_HOSTS=localhost
STATIC_ROOT=/static
```

For production, set `DEBUG=False`, `ALLOWED_HOSTS=your-domain.com`, and `STATIC_ROOT=/var/www/webapp/static/` - or anywhere you want Django to collect static files to, just make sure you can serve those static files.

---

#### ℹ️ About environment variables

* **SPOTIFY\_CLIENT\_ID / SPOTIFY\_CLIENT\_SECRET**
  Get these from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
  Create an app there to retrieve your credentials.

* **SECRET\_KEY**
  This is required by Django for cryptographic signing.
  Generate a strong secret key with:

  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

  ⚠️ **Keep this key safe and never commit it to version control.**

---

#### 🏃 5. Start the app

Navigate to the Django project root:

```bash
cd WebProject
```

For development:

```bash
python manage.py runserver 0.0.0.0:8000
```

* Visit [http://localhost:8000](http://localhost:8000).

And if production (recommended to use Gunicorn):

```bash
gunicorn WebProject.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

* Then visit the domain you’ve defined in the `.env` file.

---

#### 🔄 Common management commands

Run Django commands manually:

```bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput
```

#### ⚙️ Start background services (required for both dev and prod)

This app uses **Redis** and **Celery** for background tasks.
If you are not using Docker, you need to set them up manually.

* **Redis**: Django and Celery require a running Redis server.
  Start it on your system (install Redis via your OS package manager). Example:

  ```bash
  # On Debian/Ubuntu:
  sudo apt install redis-server
  sudo systemctl enable redis-server
  sudo systemctl start redis-server
  ```

  Confirm Redis is running:

  ```bash
  redis-cli ping
  # Should return: PONG
  ```

* **Celery Worker**: To process background jobs.
  From the Django project root:

  ```bash
  celery -A WebProject worker --loglevel=info
  ```

* **Celery Beat**: To run periodic tasks.
  From the Django project root:

  ```bash
  celery -A WebProject beat --loglevel=info
  ```

⚠️ To avoid restarting these processes manually on every reboot, configure them with **systemd** or **supervisord**.

---

## 📝 Notes

* Make sure you have Python 3.12+ installed.
* For Docker Compose, you need Docker Desktop (Windows/Mac) or Docker Engine (Linux).
* If you're on a typical Windows environment, you might have to use `docker-compose` instead of `docker compose`, everything else is the same.
