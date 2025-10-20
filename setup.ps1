# Quick Start Script for Backend Setup
# Run this in PowerShell from the backend directory

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "RAG Chatbot Backend - Quick Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Step 2: Create Virtual Environment
Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}
else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Step 3: Activate Virtual Environment
Write-Host "[3/6] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Step 4: Install Dependencies
Write-Host "[4/6] Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Step 5: Check .env file
Write-Host "[5/6] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
    $envContent = Get-Content .env -Raw
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "✓ OpenAI API key configured" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ WARNING: OpenAI API key not set in .env file!" -ForegroundColor Red
        Write-Host "  Please edit .env and add your OpenAI API key" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠ .env file not found, using defaults" -ForegroundColor Yellow
}

# Step 6: Initialize Database
Write-Host "[6/6] Initializing database..." -ForegroundColor Yellow
python manage.py makemigrations --noinput 2>&1 | Out-Null
python manage.py migrate --noinput 2>&1 | Out-Null
Write-Host "✓ Database initialized" -ForegroundColor Green

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Make sure Redis is running:" -ForegroundColor White
Write-Host "   redis-server" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Celery worker (in new terminal):" -ForegroundColor White
Write-Host "   celery -A config worker --loglevel=info --pool=solo" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start Django server:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host ""
