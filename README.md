# Web Application - Spotify Explorer

## Disclaimer

There is a chance for Spotify API to change their API setup (e.g., different endpoint name).
If something does not load within the app, it is likely because of that — check API endpoints first.

---

## 🚀 Running the Project

You can run the project using **Docker Compose** (recommended) or set it up manually using **Python virtual environments**.

---

### 🐳 Docker Compose (recommended)

This is the easiest way to run the app for **both development** and **production**.

---

#### 📦 1. Clone the repository

```bash
git clone https://github.com/your-org/web-application.git
cd web-application
```

---

#### 🔑 2. Define environment variables

Navigate to the Django project root:

```bash
cd WebProject
cp ../.env.example .env
```

Edit `WebProject/.env` with your credentials:

```
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret
SECRET_KEY=your-secret
DEBUG=True
DOMAIN=localhost
```

---

#### 🏃 3. Start the app

From the **repo root**:

```bash
docker-compose up --build
```

* Visit [http://localhost:8000](http://localhost:8000).

---

#### 🔄 Common Docker commands (example only)

Run Django management commands inside the container:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

---

### 🐍 Python Virtual Environment (manual setup)

This is the **legacy setup** for running the app without Docker.

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

#### 🏃 4. Run the app

Navigate to the Django project root:

```bash
cd WebProject
```

Set up your `.env` file:

```bash
cp ../.env.example .env
```

Run the server:

```bash
python manage.py runserver
```

---

## 📝 Notes

* Make sure you have Python 3.12+ installed.
* For Docker Compose, you need Docker Desktop (Windows/Mac) or Docker Engine (Linux).