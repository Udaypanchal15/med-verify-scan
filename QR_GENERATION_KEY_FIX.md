# QR Code Generation - Security Keys Fix

## Issue Fixed

**Problem:** QR code generation was returning `400 Bad Request` error with message "Private key not found"

**Root Cause:** Sellers need to generate ECDSA cryptographic key pairs before they can issue signed QR codes for their medicines. The system requires a private key file to exist before creating QR codes.

---

## What Are Security Keys?

The MediVerify system uses **ECDSA (Elliptic Curve Digital Signature Algorithm)** cryptography to sign QR codes:

- **Private Key**: Stored securely on the server, used by sellers to sign QR codes
- **Public Key**: Stored in database, used by anyone to verify QR code authenticity
- **Signed QR Codes**: Contain medicine information + cryptographic signature
- **Verification**: Users can verify QR codes are genuine and haven't been tampered with

---

## Changes Made

### Backend: `backend/routes/seller_routes.py`

**Line 239: Added CORS Support**
```python
@seller_bp.route('/generate-keys', methods=['POST', 'OPTIONS'])  # Added OPTIONS
```

**Lines 246, 249, 262, 279, 282: Added Content-Type Headers**
```python
return jsonify({"error": "Seller not found"}), 404, {'Content-Type': 'application/json'}
return jsonify({"error": "Seller must be approved before generating keys"}), 403, {'Content-Type': 'application/json'}
return jsonify({"error": "Failed to generate keys"}), 500, {'Content-Type': 'application/json'}
return jsonify({...}), 200, {'Content-Type': 'application/json'}
return jsonify({"error": str(e)}), 500, {'Content-Type': 'application/json'}
```

### Frontend: `src/pages/SellerDashboard.jsx`

**Line 14: Added Key Icon Import**
```javascript
import { Plus, Search, QrCode, CheckCircle2, Clock, AlertCircle, Building2, User, Package, Mail, Phone, MapPin, BarChart3, TrendingUp, Edit, Key } from 'lucide-react';
```

**Lines 33-34: Added State Variables**
```javascript
const [generatingKeys, setGeneratingKeys] = useState(false);
const [hasKeys, setHasKeys] = useState(false);
```

**Lines 78-80: Check for Existing Keys on Load**
```javascript
if (statusData.data && statusData.data.public_key) {
  setHasKeys(true);
}
```

**Lines 270-301: Added Key Generation Handler**
```javascript
const handleGenerateKeys = async () => {
  setGeneratingKeys(true);
  try {
    const response = await fetch(`${API_BASE_URL}/seller/generate-keys`, {
      method: 'POST',
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Failed to generate keys');
    }

    const data = await response.json();
    toast({
      title: "Success",
      description: "Security keys generated successfully. You can now generate QR codes.",
    });
    setHasKeys(true);
  } catch (error) {
    toast({
      title: "Error",
      description: error.message,
      variant: "destructive",
    });
  } finally {
    setGeneratingKeys(false);
  }
};
```

**Lines 451-468: Added UI Alert with Generate Keys Button**
```javascript
{seller.status === 'approved' && !hasKeys && (
  <Alert className="md:col-span-2 border-blue-200 bg-blue-50">
    <Key className="h-4 w-4 text-blue-600" />
    <AlertDescription className="text-sm text-blue-700 ml-2 flex items-center justify-between">
      <div>
        <strong>Security Keys Required:</strong> Generate your cryptographic keys to enable QR code generation for your medicines.
      </div>
      <Button
        onClick={handleGenerateKeys}
        disabled={generatingKeys}
        className="ml-4 bg-blue-600 hover:bg-blue-700"
        size="sm"
      >
        {generatingKeys ? 'Generating...' : 'Generate Keys'}
      </Button>
    </AlertDescription>
  </Alert>
)}
```

---

## How It Works Now

### First-Time Workflow (New Approved Seller):

1. **Login as approved seller**
   - Navigate to Seller Dashboard

2. **See "Security Keys Required" Alert**
   - Blue alert appears in Seller Profile card
   - Message: "Generate your cryptographic keys to enable QR code generation"

3. **Click "Generate Keys" Button**
   - Button shows "Generating..." during processing
   - Backend creates ECDSA key pair:
     - Private key saved to: `backend/keys/seller_{id}_private_key.pem`
     - Public key saved to: `backend/keys/seller_{id}_public_key.pem`
     - Public key stored in database `sellers.public_key` column

4. **Success Toast Appears**
   - Message: "Security keys generated successfully. You can now generate QR codes."
   - Alert disappears from dashboard

5. **Generate QR Codes**
   - Go to "My Medicines" tab
   - Click "Generate QR" on any approved medicine
   - QR code will be created successfully with cryptographic signature

### Returning Seller Workflow (Already Has Keys):

1. **Login**
   - Dashboard loads seller data
   - System checks if `seller.public_key` exists
   - If exists, sets `hasKeys = true`

2. **No Alert Shown**
   - "Generate Keys" alert does not appear
   - Seller can immediately generate QR codes

---

## Testing Instructions

### Step 1: Restart Backend

**CRITICAL:** Backend must be restarted for changes to take effect!

```bash
cd backend
# Press Ctrl+C to stop
python app.py
```

Expected output:
```
* Running on http://localhost:5000
* Debug mode: on
```

### Step 2: Test as New Approved Seller

1. **Login with approved seller account**
   - If you don't have one, create new seller and get admin to approve

2. **Check Seller Profile Card**
   - Should see blue alert: "Security Keys Required"
   - Button visible: "Generate Keys"

3. **Click "Generate Keys"**
   - Button changes to "Generating..."
   - Wait 2-3 seconds

4. **Verify Success**
   - ✅ Toast notification: "Security keys generated successfully"
   - ✅ Alert disappears from dashboard
   - ✅ Check backend terminal: no errors
   - ✅ Check `backend/keys/` folder:
     - File exists: `seller_{id}_private_key.pem`
     - File exists: `seller_{id}_public_key.pem`

5. **Test QR Generation**
   - Go to "My Medicines" tab
   - Find an approved medicine
   - Click "Generate QR"
   - Enter optional batch details
   - Click "Generate QR" in modal
   - ✅ Success toast: "QR code generated successfully"
   - ✅ No 400 error

### Step 3: Test as Returning Seller

1. **Refresh page** or **logout and login again**
   - Dashboard loads

2. **Verify Alert Doesn't Appear**
   - ✅ No "Generate Keys" alert in Seller Profile
   - ✅ System detected existing keys

3. **Generate QR Immediately**
   - Should work without generating keys again

---

## Error Scenarios

### Error 1: "Seller must be approved before generating keys"

**Cause:** Seller status is not 'approved'

**Solution:**
- Admin must approve seller in Admin panel
- Check seller status in database: `SELECT status FROM sellers WHERE id = ?`
- Status should be 'approved', not 'pending', 'viewed', 'verifying', etc.

### Error 2: "Failed to generate keys"

**Cause:** File system permission issue or `backend/keys/` folder error

**Solution:**
1. Check backend terminal for detailed error
2. Verify `backend/keys/` folder exists and is writable
3. On Windows, check folder permissions
4. Try creating folder manually: `mkdir backend/keys`

### Error 3: Keys generated but QR still returns 400

**Cause:** Private key file was deleted or moved

**Solution:**
1. Check `backend/keys/seller_{id}_private_key.pem` exists
2. If missing, click "Generate Keys" again
3. Check backend terminal for file path errors

### Error 4: Generate Keys button not appearing

**Cause:** Seller not approved or already has keys

**Solution:**
- Check `seller.status` is 'approved'
- Check database: `SELECT public_key FROM sellers WHERE id = ?`
- If `public_key` column has data, keys already exist
- Alert only shows when: `status === 'approved' && !hasKeys`

---

## Security Notes

### Private Key Security

**IMPORTANT:** The private key file is stored on the server and should NEVER be shared or exposed:

- **File Location:** `backend/keys/seller_{id}_private_key.pem`
- **Permissions:** Only readable by backend application
- **Backup:** Should be backed up securely
- **Loss:** If lost, seller must generate new keys (invalidates old QR codes)

### Key Rotation

If a seller's private key is compromised:

1. Admin should revoke seller status
2. Delete old key files
3. Update `sellers.public_key` to NULL in database
4. Seller re-generates new keys
5. Old QR codes will fail verification (good security feature)

---

## API Endpoint Reference

### POST `/seller/generate-keys`

**Authentication:** Requires seller JWT token

**Request Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:** None (empty)

**Success Response (200):**
```json
{
  "message": "Keys generated successfully",
  "data": {
    "seller_id": "123",
    "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
    "private_key_path": "backend/keys/seller_123_private_key.pem",
    "warning": "Keep private key secure and never share it"
  }
}
```

**Error Responses:**

**403 - Not Approved:**
```json
{
  "error": "Seller must be approved before generating keys"
}
```

**404 - Seller Not Found:**
```json
{
  "error": "Seller not found"
}
```

**500 - Generation Failed:**
```json
{
  "error": "Failed to generate keys"
}
```

---

## Files Modified

### Backend
- ✅ `backend/routes/seller_routes.py` (Lines 239-282)
  - Added OPTIONS method
  - Added Content-Type headers

### Frontend
- ✅ `src/pages/SellerDashboard.jsx` (Lines 14, 33-34, 78-80, 270-301, 451-468)
  - Added Key icon import
  - Added state management
  - Added key generation handler
  - Added UI alert with button
  - Auto-detect existing keys on load

---

## Summary

✅ **Root Cause Fixed:** Added UI and workflow for sellers to generate cryptographic keys

✅ **Backend Fixed:** Added CORS support and Content-Type headers to `/generate-keys` endpoint

✅ **Frontend Fixed:** Added alert, button, and automatic key detection

✅ **User Experience:** Clear instructions and one-click key generation

✅ **Security:** Private keys stored securely on server, public keys in database

✅ **QR Generation:** Now works seamlessly after one-time key generation

---

## What's Next?

After generating keys, sellers can:

1. ✅ Generate QR codes for approved medicines
2. ✅ Add batch details to QR codes
3. ✅ Track QR code generation history
4. ✅ Verify their medicines are genuine

**No more 400 errors!** 🎉
