# 🚀 Quick Fix for PowerShell - Installation Issues

## Problems Identified

1. ✅ **FIXED**: `rrule>=0.10.1` package doesn't exist (removed from requirements.txt)
2. ⚠️ **ISSUE**: Virtual environment not activated
3. ⚠️ **ISSUE**: Dependencies not installed in virtual environment

## 🔧 Quick Fix (Copy and Paste)

### Step 1: Open PowerShell in Backend Directory

```powershell
cd D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend
```

### Step 2: Create/Activate Virtual Environment

```powershell
# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Set execution policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify activation - you should see (venv) in your prompt
Write-Host "Virtual environment path: $env:VIRTUAL_ENV" -ForegroundColor Cyan
```

### Step 3: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This may take 5-10 minutes, be patient!
```

### Step 4: Verify Installation

```powershell
# Test if modules are installed
python -c "import flask; print('✅ Flask installed')"
python -c "import flask_jwt_extended; print('✅ Flask-JWT-Extended installed')"
python -c "import dotenv; print('✅ python-dotenv installed')"
python -c "import psycopg2; print('✅ psycopg2 installed')"
```

## 📋 Complete Command Block (Copy All at Once)

Copy this entire block and paste into PowerShell:

```powershell
# Navigate to backend
cd D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend

# Create venv if not exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Verify activation
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not activated. Please run: .\venv\Scripts\Activate.ps1" -ForegroundColor Red
    exit
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies (this may take 5-10 minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
python -c "import flask, flask_jwt_extended, dotenv, psycopg2; print('✅ All modules installed successfully!')"

Write-Host "🎉 Installation complete!" -ForegroundColor Green
```

## ✅ What to Look For

### After Activation, You Should See:
```
(venv) PS D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend>
```

The `(venv)` at the beginning means the virtual environment is active.

### After Installation, You Should See:
```
✅ All modules installed successfully!
```

## 🐛 If You Still Get Errors

### Error: "Execution Policy Error"

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\venv\Scripts\Activate.ps1
```

### Error: "ModuleNotFoundError" After Installation

**Make sure virtual environment is activated:**
```powershell
# Check if venv is active
echo $env:VIRTUAL_ENV

# Should show something like:
# D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend\venv

# If empty, activate it:
.\venv\Scripts\Activate.ps1
```

### Error: "pip is not recognized"

```powershell
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Error: "Failed building wheel"

Install Visual Studio Build Tools:
- Download: https://visualstudio.microsoft.com/downloads/
- Install "Desktop development with C++" workload

Or install pre-built packages:
```powershell
pip install --only-binary :all: -r requirements.txt
```

## 🎯 After Successful Installation

1. **Create .env file:**
   ```powershell
   copy .env.example .env
   notepad .env
   ```

2. **Initialize database:**
   ```powershell
   python database/init_db.py
   ```

3. **Create admin user:**
   ```powershell
   python scripts/create_admin.py
   ```

4. **Start server:**
   ```powershell
   python app.py
   ```

## 📝 Important Notes

- **Always activate virtual environment** before running Python scripts
- **You'll see `(venv)` in your prompt** when it's active
- **If you close PowerShell, activate it again** when you reopen
- **Never install packages globally** - always use virtual environment

## 🔍 Verify Everything is Working

```powershell
# 1. Check virtual environment is active
echo $env:VIRTUAL_ENV

# 2. Check Python path
where python
# Should show: ...\backend\venv\Scripts\python.exe

# 3. Check installed packages
pip list

# 4. Test imports
python -c "import flask; import flask_jwt_extended; import dotenv; print('✅ All OK')"

# 5. Try running the app
python app.py
```

## 🆘 Still Having Issues?

1. **Check Python version:**
   ```powershell
   python --version
   # Should be 3.8 or higher
   ```

2. **Check if venv folder exists:**
   ```powershell
   Test-Path venv
   # Should return True
   ```

3. **Try fresh installation:**
   ```powershell
   # Remove old venv
   Remove-Item -Recurse -Force venv
   
   # Create new venv
   python -m venv venv
   
   # Activate
   .\venv\Scripts\Activate.ps1
   
   # Install
   pip install -r requirements.txt
   ```

## ✅ Success Checklist

- [ ] Virtual environment created (`venv` folder exists)
- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] Python points to venv (`where python` shows venv path)
- [ ] Dependencies installed (`pip list` shows packages)
- [ ] Modules can be imported (no ModuleNotFoundError)
- [ ] App can start (`python app.py` works)

---

**🎉 Once all checks pass, you're ready to go!**



