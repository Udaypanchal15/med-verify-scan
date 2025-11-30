# Fix Installation Issues

## 🔧 Common Installation Problems and Solutions

### Problem 1: `ERROR: No matching distribution found for rrule>=0.10.1`

**Solution**: The `rrule` package doesn't exist as a separate package. The `rrule` functionality is already included in `python-dateutil`. The requirements.txt has been updated to remove this.

### Problem 2: `ModuleNotFoundError: No module named 'dotenv'` or `ModuleNotFoundError: No module named 'flask'`

**Solution**: You need to:
1. Activate the virtual environment
2. Install dependencies from requirements.txt

## ✅ Step-by-Step Fix

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment (if not already created)

**Windows:**
```powershell
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Verify Virtual Environment is Active

You should see `(venv)` at the beginning of your command prompt:

**Windows:**
```powershell
(venv) PS D:\Mini-project\med-verify-scan-main\med-verify-scan-main\backend>
```

**Linux/Mac:**
```bash
(venv) user@computer:~/backend$
```

### Step 5: Upgrade pip (Recommended)

```bash
python -m pip install --upgrade pip
```

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

This may take 5-10 minutes. Be patient!

### Step 7: Verify Installation

```bash
python -c "import flask; import flask_jwt_extended; import dotenv; print('All modules installed successfully!')"
```

## 🔍 Troubleshooting

### Issue: "pip is not recognized"

**Solution**: 
1. Make sure Python is installed: `python --version`
2. Make sure pip is installed: `python -m pip --version`
3. If not, install pip: `python -m ensurepip --upgrade`

### Issue: "Permission denied" or "Access denied"

**Solution**: 
1. Make sure you're running PowerShell/Command Prompt as Administrator
2. Or use `--user` flag: `pip install -r requirements.txt --user`

### Issue: "Virtual environment not activating"

**Solution**:
1. Check if venv folder exists: `ls venv` (Linux/Mac) or `dir venv` (Windows)
2. If not, create it: `python -m venv venv`
3. Try activating again

### Issue: "ModuleNotFoundError after installation"

**Solution**:
1. Make sure virtual environment is activated (you should see `(venv)` in prompt)
2. Verify you're using the correct Python:
   ```bash
   which python  # Linux/Mac
   where python  # Windows
   ```
   Should point to `venv/Scripts/python` (Windows) or `venv/bin/python` (Linux/Mac)
3. Reinstall dependencies:
   ```bash
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

### Issue: "ERROR: Failed building wheel for..."

**Solution**:
1. Install build tools:
   - Windows: Install Visual Studio Build Tools
   - Linux: `sudo apt-get install build-essential python3-dev`
   - Mac: `xcode-select --install`
2. Try installing again: `pip install -r requirements.txt`

### Issue: "Connection timeout" or "SSL errors"

**Solution**:
1. Use a different index:
   ```bash
   pip install -r requirements.txt -i https://pypi.org/simple
   ```
2. Or increase timeout:
   ```bash
   pip install -r requirements.txt --timeout 1000
   ```

## 🎯 Quick Fix Commands

### For Windows PowerShell:

```powershell
# Navigate to backend
cd backend

# Create venv (if needed)
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# If activation fails, set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; print('Flask installed!')"
```

### For Linux/Mac:

```bash
# Navigate to backend
cd backend

# Create venv (if needed)
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask; print('Flask installed!')"
```

## ✅ Verification Checklist

After installation, verify:

- [ ] Virtual environment is activated (see `(venv)` in prompt)
- [ ] Flask is installed: `python -c "import flask; print(flask.__version__)"`
- [ ] Flask-JWT-Extended is installed: `python -c "import flask_jwt_extended; print('OK')"`
- [ ] python-dotenv is installed: `python -c "import dotenv; print('OK')"`
- [ ] psycopg2 is installed: `python -c "import psycopg2; print('OK')"`
- [ ] All modules can be imported

## 🚀 After Successful Installation

1. **Create .env file:**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

2. **Initialize database:**
   ```bash
   python database/init_db.py
   ```

3. **Create admin user:**
   ```bash
   python scripts/create_admin.py
   ```

4. **Start server:**
   ```bash
   python app.py
   ```

## 📝 Notes

- **Always activate the virtual environment** before running Python scripts
- **Never install packages globally** when working with a virtual environment
- **Keep requirements.txt updated** when adding new packages
- **Use `pip freeze > requirements.txt`** to update requirements after installing new packages

## 🆘 Still Having Issues?

1. Check Python version: `python --version` (should be 3.8+)
2. Check pip version: `pip --version`
3. Verify virtual environment is active
4. Check if you're in the correct directory
5. Try creating a fresh virtual environment:
   ```bash
   rm -rf venv  # Linux/Mac
   rmdir /s venv  # Windows
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\Activate.ps1  # Windows
   pip install -r requirements.txt
   ```

---

**If you're still having issues, make sure:**
1. ✅ Virtual environment is activated
2. ✅ You're in the `backend` directory
3. ✅ Python 3.8+ is installed
4. ✅ requirements.txt is updated (rrule removed)



