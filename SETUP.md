# Backend Setup and Installation Guide

## Quick Start

This guide will help you set up the backend development environment step by step.

### Step 1: Create Virtual Environment

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```powershell
# Copy example env file
copy .env.example .env

# Edit .env file with your settings:
# - Add your OpenAI API key
# - Configure database URL (or use SQLite default)
# - Set Redis URLs
```

### Step 4: Initialize Database

```powershell
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

### Step 5: Download NLTK Data (for text processing)

```powershell
# Open Python shell
python manage.py shell

# In Python shell, run:
import nltk
nltk.download('punkt')
nltk.download('stopwords')
exit()
```

### Step 6: Start Services

You'll need 3 separate terminal windows:

**Terminal 1 - Redis Server:**

```powershell
# Install Redis on Windows: https://github.com/microsoftarchive/redis/releases
# Or use WSL/Docker
redis-server
```

**Terminal 2 - Celery Worker:**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
celery -A config worker --loglevel=info --pool=solo
```

**Terminal 3 - Django Server:**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

### Step 7: Test the Setup

Open your browser and navigate to:

- **API Root:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/

## Troubleshooting

### Django Import Errors

If you see import errors in VS Code, make sure:

1. You've activated the virtual environment
2. Python interpreter is set to `backend\venv\Scripts\python.exe`

### Redis Connection Issues

- Windows: Download from https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis:latest`
- Or use WSL: `wsl sudo service redis-server start`

### PostgreSQL Setup (Optional)

If using PostgreSQL instead of SQLite:

```powershell
# Install PostgreSQL
# Create database
createdb rag_chatbot_db

# Update .env
DATABASE_URL=postgresql://username:password@localhost:5432/rag_chatbot_db
```

### Celery on Windows

Celery 5.x has issues with Windows. Use `--pool=solo` flag:

```powershell
celery -A config worker --loglevel=info --pool=solo
```

## Next Steps

1. Upload a PDF via the API
2. Query the RAG system
3. Test voice functionality
4. Explore the admin panel

## Development Commands

```powershell
# Run tests
pytest

# Format code
black .

# Check code style
flake8 .

# Create new migration
python manage.py makemigrations

# View SQL for migration
python manage.py sqlmigrate app_name migration_number

# Open Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic
```
