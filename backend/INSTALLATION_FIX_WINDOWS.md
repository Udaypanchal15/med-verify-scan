# 🔧 Fix Installation Issues - Windows PowerShell

## Quick Fix for Windows

### Problem 1: `ERROR: No matching distribution found for rrule>=0.10.1`

**Fixed!** ✅ The `rrule` package has been removed from requirements.txt (it's part of python-dateutil).

### Problem 2: `ModuleNotFoundError: No module named 'dotenv'` or `'flask'`

**Solution:** You need to activate the virtual environment and install dependencies.

## 🚀 Quick Fix (Automatic)

### Option 1: Use the Fix Script (Recommended)

1. Open PowerShell in the `backend` directory
2. Run the fix script:
   ```powershell
   .\fix-installation.ps1
   ```

If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\fix-installation.ps1
```

## 🔧 Manual Fix (Step by Step)

### Step 1: Open PowerShell in Backend Directory

```powershell
cd D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend
```

### Step 2: Create Virtual Environment (if not exists)

```powershell
python -m venv venv
```

### Step 3: Set Execution Policy (if needed)

If you get an execution policy error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

**You should see `(venv)` at the beginning of your prompt:**

```
(venv) PS D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend>
```

### Step 5: Verify You're in Virtual Environment

```powershell
python --version
where python
```

**Should show:**

```
Python 3.x.x
D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend\venv\Scripts\python.exe
```

### Step 6: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 7: Install Dependencies

```powershell
pip install -r requirements.txt
```

**This will take 5-10 minutes. Be patient!**

### Step 8: Verify Installation

```powershell
python -c "import flask; import flask_jwt_extended; import dotenv; print('✅ All modules installed!')"
```

## ✅ Verification Checklist

After installation, verify:

- [ ] Virtual environment is activated (see `(venv)` in prompt)
- [ ] Flask is installed: `python -c "import flask; print(flask.__version__)"`
- [ ] Flask-JWT-Extended is installed: `python -c "import flask_jwt_extended; print('OK')"`
- [ ] python-dotenv is installed: `python -c "import dotenv; print('OK')"`
- [ ] psycopg2 is installed: `python -c "import psycopg2; print('OK')"`

## 🐛 Common Issues and Solutions

### Issue 1: "Execution Policy Error"

**Error:**

```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:

```powershell
.\venv\Scripts\Activate.ps1
```

### Issue 2: "ModuleNotFoundError" After Installation

**Cause:** Virtual environment is not activated or using wrong Python.

**Solution:**

1. Make sure virtual environment is activated (see `(venv)` in prompt)
2. Verify Python path:
   ```powershell
   where python
   ```
   Should point to `venv\Scripts\python.exe`
3. If not, activate virtual environment again:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

### Issue 3: "pip is not recognized"

**Solution:**

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Issue 4: "Failed building wheel"

**Solution:**

1. Install Visual Studio Build Tools:
   - Download from: https://visualstudio.microsoft.com/downloads/
   - Install "Desktop development with C++" workload
2. Or install pre-built wheels:
   ```powershell
   pip install --only-binary :all: -r requirements.txt
   ```

### Issue 5: "Connection timeout"

**Solution:**

```powershell
pip install -r requirements.txt --timeout 1000
```

Or use a different index:

```powershell
pip install -r requirements.txt -i https://pypi.org/simple
```

## 🎯 Complete Installation Command Sequence

Copy and paste this entire block into PowerShell:

```powershell
# Navigate to backend directory
cd D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend

# Create virtual environment (if not exists)
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Set execution policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify activation
python --version
where python

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; import flask_jwt_extended; import dotenv; print('✅ All modules installed!')"
```

## 🚀 After Successful Installation

1. **Create .env file:**

   ```powershell
   copy .env.example .env
   # Edit .env with your configurations (use Notepad or any text editor)
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

- **Always activate the virtual environment** before running Python scripts
- **Never install packages globally** when working with a virtual environment
- **Keep the virtual environment activated** while working on the project
- **If you close PowerShell, you need to activate the virtual environment again**

## ✅ Success Indicators

You know installation is successful when:

1. ✅ You see `(venv)` at the beginning of your PowerShell prompt
2. ✅ `python -c "import flask"` works without errors
3. ✅ `pip list` shows all required packages
4. ✅ `python app.py` starts the server without import errors

## 🆘 Still Having Issues?

1. **Check Python version:**

   ```powershell
   python --version
   ```

   Should be 3.8 or higher.

2. **Check if virtual environment is activated:**

   ```powershell
   echo $env:VIRTUAL_ENV
   ```

   Should show the path to venv directory.

3. **Verify you're using the correct Python:**

   ```powershell
   where python
   ```

   Should point to `venv\Scripts\python.exe`.

4. **Try creating a fresh virtual environment:**
   ```powershell
   Remove-Item -Recurse -Force venv
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

## 🎉 Next Steps

Once installation is complete:

1. Read `FIX_INSTALLATION_ISSUES.md` for more troubleshooting
2. Follow `FINAL_SETUP_INSTRUCTIONS.md` for complete setup
3. Start developing!

---

**If you're still having issues, make sure:**

- ✅ Python 3.8+ is installed
- ✅ Virtual environment is created
- ✅ Virtual environment is activated
- ✅ You're in the `backend` directory
- ✅ requirements.txt is updated (rrule removed)


