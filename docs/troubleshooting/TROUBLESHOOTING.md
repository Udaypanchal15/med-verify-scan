# Troubleshooting Guide

## 🔴 Critical Issues

### "FATAL: Ident authentication failed for user"

**Error Message:**

```
psycopg2.OperationalError: FATAL: Ident authentication failed for user "postgres"
```

**Causes:**

- PostgreSQL not running
- Wrong DATABASE_URL in .env
- PostgreSQL authentication method is ident (not md5)

**Solutions:**

1. **Check PostgreSQL is running:**

   ```bash
   # Windows
   Get-Service postgresql*

   # macOS
   brew services list | grep postgres
   ```

2. **Fix authentication method:**

   ```bash
   # Find postgresql.conf
   # Change: local   all             all                     ident
   # To:     local   all             all                     md5

   # Then restart PostgreSQL
   sudo systemctl restart postgresql  # Linux
   brew services restart postgresql    # macOS
   ```

3. **Verify DATABASE_URL format:**
   ```
   ✅ postgresql://username:password@localhost:5432/med_verify_db
   ❌ psql://... (wrong protocol)
   ❌ postgres://user@localhost/db (missing password)
   ```

---

### "No module named 'flask'" or Import Errors

**Causes:**

- Virtual environment not activated
- Dependencies not installed
- Using system Python instead of venv

**Solutions:**

```bash
# 1. Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 2. Verify venv is active (should show venv in prompt)
(venv) $ python --version

# 3. Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### "CORS error: Cross-Origin Request Blocked"

**Error:**

```
Access to XMLHttpRequest at 'http://localhost:5000/medicines' from origin
'http://localhost:5173' has been blocked by CORS policy
```

**Cause:**

- Frontend URL not in CORS_ORIGINS

**Solution:**

```env
# In backend/.env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173

# Then restart backend
python app.py
```

---

### "Address already in use" / Port Error

**Error:**

```
OSError: [Errno 48] Address already in use
Address already in use: ('127.0.0.1', 5000)
```

**Causes:**

- Flask server already running on port 5000
- Another app using port

**Solutions:**

```bash
# Option 1: Kill existing process
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>

# Option 2: Change port in app.py
# Find: if __name__ == '__main__':
# Change: app.run(port=5001)

# Option 3: For frontend
npm run dev -- --port 5174
```

---

## 🟡 Common Issues

### Medicine Approval Not Working

**Symptom:**

```
Admin approves medicine, but it still shows as "pending" in seller view
```

**Cause:**

- Cache not cleared
- Frontend not refreshing data
- Database transaction not committed

**Solution:**

```python
# 1. Check database directly
psql med_verify_db
SELECT approval_status FROM medicines WHERE id = 'medicine-uuid';

# 2. Clear browser cache
# Ctrl+Shift+Delete (Windows/Linux) or Cmd+Shift+Delete (macOS)

# 3. Restart frontend
# Kill npm dev, restart with: npm run dev
```

---

### QR Code Verification Shows "Counterfeit"

**Symptom:**

```
Scan QR code, get message: "❌ Counterfeit Detected"
```

**Possible Causes:**

1. Medicine not approved by admin yet
2. Seller's keys were revoked
3. QR was tampered with
4. Signature verification failed

**Debugging Steps:**

```python
# Check 1: Is medicine approved?
SELECT approval_status FROM medicines WHERE id = 'medicine-uuid';
# Should be: "approved"

# Check 2: Is seller's key revoked?
SELECT * FROM revoked_keys WHERE seller_id = 'seller-uuid';
# Should be: empty

# Check 3: Is seller approved?
SELECT status FROM sellers WHERE id = 'seller-uuid';
# Should be: "approved"

# Check 4: Verify QR signature manually
# Use: services/qr_signer.py verify_signature()
```

---

### User Can't Login - "Invalid Credentials"

**Error:**

```
{
  "error": "Invalid credentials"
}
```

**Troubleshooting:**

```python
# Check 1: Does user exist?
SELECT email, role FROM users WHERE email = 'user@example.com';

# Check 2: Is user active?
SELECT is_active FROM users WHERE email = 'user@example.com';

# Check 3: Try resetting password (if available)
# Or create new test user

# Check 4: Check if password hash is corrupted
UPDATE users SET password_hash = bcrypt_hash('newpass123') WHERE email = 'user@example.com';
```

---

### AI Assistant Not Working

**Symptom:**

```
Error: "OpenAI API key not found or invalid"
```

**Cause:**

- OPENAI_API_KEY not set in .env
- API key expired or invalid

**Solution:**

```bash
# 1. Check if key is set
echo $OPENAI_API_KEY  # macOS/Linux
echo %OPENAI_API_KEY%  # Windows

# 2. Add key to .env
OPENAI_API_KEY=sk-your-actual-key-here

# 3. Restart backend
python app.py

# 4. Test API key
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

---

### Frontend Shows Blank Page

**Causes:**

- JavaScript error in console
- Backend not running
- Network request failed

**Debugging:**

```javascript
// 1. Open browser DevTools: F12 or Cmd+Option+I

// 2. Check Console for errors
// Should see: "Connected to backend" or similar

// 3. Check Network tab
// POST /auth/login should return 200

// 4. Check if backend is running
curl http://localhost:5000/
# Should return: {"message": "Medicine Scanner Backend Running ✅"}
```

---

### Seller Can't Generate QR Code

**Symptom:**

```
Button disabled or error: "Please generate keys first"
```

**Causes:**

1. Seller not approved yet (KYC pending)
2. Keys not generated
3. Medicine not approved

**Checklist:**

```
☑️ Seller registered with role "seller"
☑️ Admin approved seller (status = "approved")
☑️ Seller generated ECDSA keys
☑️ Seller added medicine
☑️ Admin approved medicine (approval_status = "approved")
☑️ Now seller can generate QR
```

---

### Database Schema Mismatch

**Error:**

```
psycopg2.ProgrammingError: column "approval_status" does not exist
```

**Cause:**

- Database schema outdated
- Never ran schema.sql

**Solution:**

```bash
# Drop and recreate database (CAUTION: DATA LOSS)
psql
DROP DATABASE med_verify_db;
CREATE DATABASE med_verify_db;
\q

# Run schema
psql med_verify_db < backend/database/schema.sql

# Or use Python script
python backend/database/init_db.py
```

---

### Token Expired - "Unauthorized"

**Error:**

```
{
  "error": "Authorization required",
  "message": "Token has expired"
}
```

**Cause:**

- Access token expired (default 1 hour)
- Browser cache not updated

**Solution:**

```javascript
// Frontend automatically refreshes token
// If error persists:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Login again
3. Token will be valid for 1 hour
```

---

## 📋 Debugging Checklist

### Before reporting a bug:

- [ ] Backend running? `python app.py`
- [ ] Frontend running? `npm run dev`
- [ ] Database running? `psql med_verify_db`
- [ ] Virtual environment activated? `(venv) $`
- [ ] .env file exists with correct values?
- [ ] No typos in DATABASE_URL or API endpoints?
- [ ] Cache cleared in browser?
- [ ] Tried restarting services?
- [ ] Check browser DevTools console for errors
- [ ] Check Flask console for error messages
- [ ] Verified with curl: `curl http://localhost:5000/`

---

## Getting Help

### Check These Files First

1. **Error Details**: `/backend/logs/app.log`
2. **Database Schema**: `/backend/database/schema.sql`
3. **API Docs**: `/docs/api/ENDPOINTS.md`
4. **Features**: `/docs/features/FEATURES.md`
5. **Analysis**: `/ISSUES_ANALYSIS.md`

### Report a Bug

Include:

1. **Step to reproduce** (exact steps)
2. **Expected behavior**
3. **Actual behavior**
4. **Error message** (full stack trace)
5. **Environment** (OS, Python version, Node version)
6. **Logs** (relevant sections from app.log)

---

## Performance Optimization

### If system is slow:

```sql
-- Check for missing indexes
SELECT * FROM pg_stat_user_indexes;

-- Add indexes if needed
CREATE INDEX idx_medicines_approval_status ON medicines(approval_status);
CREATE INDEX idx_users_email ON users(email);

-- Vacuum database
VACUUM ANALYZE;

-- Check query plans
EXPLAIN SELECT * FROM medicines WHERE approval_status = 'approved';
```

---

## Production Deployment

See `/docs/setup/DEPLOYMENT.md` for production-specific issues.
