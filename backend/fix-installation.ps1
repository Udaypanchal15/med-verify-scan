# PowerShell script to fix installation issues
# Run this script from the backend directory

Write-Host "🔧 Fixing Installation Issues..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔄 Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Activation failed. Trying to set execution policy..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    & ".\venv\Scripts\Activate.ps1"
}

# Verify activation
if ($env:VIRTUAL_ENV -eq $null) {
    Write-Host "❌ Virtual environment not activated. Please run manually:" -ForegroundColor Red
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green

# Upgrade pip
Write-Host "🔄 Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install dependencies
Write-Host "🔄 Installing dependencies from requirements.txt..." -ForegroundColor Cyan
Write-Host "   This may take 5-10 minutes. Please wait..." -ForegroundColor Yellow

pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host "   Try installing individually:" -ForegroundColor Yellow
    Write-Host "   pip install flask flask-cors flask-jwt-extended python-dotenv" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green

# Verify installation
Write-Host "🔍 Verifying installation..." -ForegroundColor Cyan

$modules = @("flask", "flask_cors", "flask_jwt_extended", "dotenv", "psycopg2", "bcrypt")
$allInstalled = $true

foreach ($module in $modules) {
    python -c "import $module; print('✅ $module')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ $module not installed" -ForegroundColor Red
        $allInstalled = $false
    }
}

if ($allInstalled) {
    Write-Host "✅ All modules installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Installation complete!" -ForegroundColor Green
    Write-Host "   Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Create .env file: cp .env.example .env" -ForegroundColor Yellow
    Write-Host "   2. Edit .env with your configurations" -ForegroundColor Yellow
    Write-Host "   3. Initialize database: python database/init_db.py" -ForegroundColor Yellow
    Write-Host "   4. Create admin user: python scripts/create_admin.py" -ForegroundColor Yellow
    Write-Host "   5. Start server: python app.py" -ForegroundColor Yellow
} else {
    Write-Host "❌ Some modules are missing. Please check the errors above." -ForegroundColor Red
    exit 1
}



