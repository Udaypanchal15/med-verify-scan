# QR Code Download Implementation Guide

## 📥 Overview

After generating a QR code, sellers can now download it in two formats:
1. **PNG Image** - For immediate use or email sharing
2. **PDF** - For printing and packaging

---

## 🔧 Backend Implementation

### New Endpoints Added

#### 1. Download QR as PNG Image
```
GET /seller/qr/<qr_id>/download
```

**Purpose:** Download QR code as a PNG image file

**Response:** Binary PNG file with filename format: `QR_{medicine_name}_{batch_no}_{qr_id_short}.png`

**Example:**
```bash
curl -X GET http://localhost:5000/seller/qr/550e8400-e29b-41d4-a716-446655440000/download \
  -H "Authorization: Bearer {access_token}" \
  -o medicine_qr.png
```

#### 2. Download QR as PDF
```
GET /seller/qr/<qr_id>/download-pdf
```

**Purpose:** Download QR code as a printable PDF document

**Features:**
- Includes medicine details
- Company name
- QR code image (3x3 inches)
- Generated timestamp
- QR ID reference
- Formatted for standard letter size (8.5" x 11")

**Response:** PDF file with filename format: `QR_{medicine_name}_{batch_no}_{qr_id_short}.pdf`

**Example:**
```bash
curl -X GET http://localhost:5000/seller/qr/550e8400-e29b-41d4-a716-446655440000/download-pdf \
  -H "Authorization: Bearer {access_token}" \
  -o medicine_qr.pdf
```

---

## 💻 Frontend Implementation

### Step 1: Display QR Code After Generation

```javascript
// In your SellerDashboard or QR generation component
const [generatedQR, setGeneratedQR] = useState(null);

const handleGenerateQR = async (medicineId) => {
  try {
    const response = await fetch('/api/seller/issue-qr', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({
        medicine_id: medicineId,
        batch_details: 'Any batch details'
      })
    });

    const data = await response.json();
    
    if (response.ok) {
      setGeneratedQR(data.data);
      toast.success('QR code generated successfully!');
    } else {
      toast.error(data.error);
    }
  } catch (error) {
    toast.error('Failed to generate QR code');
    console.error(error);
  }
};
```

### Step 2: Display QR Preview with Download Buttons

```jsx
// Display generated QR code
{generatedQR && (
  <Card className="mt-6 p-6">
    <CardHeader>
      <CardTitle>Generated QR Code</CardTitle>
      <CardDescription>
        Medicine: {generatedQR.medicine_name} | Batch: {generatedQR.batch_no}
      </CardDescription>
    </CardHeader>
    
    <CardContent className="space-y-6">
      {/* QR Image Preview */}
      <div className="flex justify-center">
        <div className="border-2 border-dashed border-gray-300 p-4 rounded-lg">
          <img 
            src={generatedQR.qr_image} 
            alt="QR Code"
            className="w-64 h-64"
          />
        </div>
      </div>

      {/* Medicine Details */}
      <div className="bg-gray-50 p-4 rounded-lg space-y-2">
        <p><strong>Medicine ID:</strong> {generatedQR.qr_id}</p>
        <p><strong>Medicine Name:</strong> {generatedQR.medicine_name}</p>
        <p><strong>Batch No:</strong> {generatedQR.batch_no}</p>
        <p><strong>Payload:</strong> {JSON.stringify(generatedQR.payload, null, 2)}</p>
      </div>

      {/* Download Buttons */}
      <div className="grid grid-cols-2 gap-4">
        <Button 
          onClick={() => downloadQRPNG(generatedQR.qr_id)}
          className="flex items-center gap-2"
        >
          <Download className="h-4 w-4" />
          Download as PNG
        </Button>
        
        <Button 
          onClick={() => downloadQRPDF(generatedQR.qr_id)}
          className="flex items-center gap-2"
          variant="outline"
        >
          <FileText className="h-4 w-4" />
          Download as PDF
        </Button>
      </div>

      {/* Copy to Clipboard */}
      <Button 
        onClick={() => copyQRToClipboard(generatedQR.qr_image)}
        className="w-full"
        variant="secondary"
      >
        <Copy className="h-4 w-4 mr-2" />
        Copy QR to Clipboard
      </Button>
    </CardContent>
  </Card>
)}
```

### Step 3: Implement Download Functions

```javascript
// Download QR as PNG
const downloadQRPNG = async (qrId) => {
  try {
    const response = await fetch(`/api/seller/qr/${qrId}/download`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    });

    if (!response.ok) {
      toast.error('Failed to download QR code');
      return;
    }

    // Get filename from response header
    const contentDisposition = response.headers.get('content-disposition');
    let filename = 'qr_code.png';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/download_name="(.+)"/);
      if (filenameMatch) filename = filenameMatch[1];
    }

    // Create blob and download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    toast.success('QR code downloaded!');
  } catch (error) {
    toast.error('Download failed');
    console.error(error);
  }
};

// Download QR as PDF
const downloadQRPDF = async (qrId) => {
  try {
    const response = await fetch(`/api/seller/qr/${qrId}/download-pdf`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    });

    if (!response.ok) {
      toast.error('Failed to download PDF');
      return;
    }

    // Get filename from response header
    const contentDisposition = response.headers.get('content-disposition');
    let filename = 'qr_code.pdf';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/download_name="(.+)"/);
      if (filenameMatch) filename = filenameMatch[1];
    }

    // Create blob and download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    toast.success('PDF downloaded!');
  } catch (error) {
    toast.error('Download failed');
    console.error(error);
  }
};

// Copy QR image to clipboard
const copyQRToClipboard = async (qrImageBase64) => {
  try {
    // Convert base64 to blob
    const response = await fetch(qrImageBase64);
    const blob = await response.blob();
    
    // Copy to clipboard
    await navigator.clipboard.write([
      new ClipboardItem({ 'image/png': blob })
    ]);
    
    toast.success('QR code copied to clipboard!');
  } catch (error) {
    toast.error('Failed to copy QR code');
    console.error(error);
  }
};
```

---

## 📋 Complete Workflow

### For Sellers:

1. **Login to Dashboard**
   ```
   POST /api/auth/login
   ```

2. **Create/View Medicine**
   ```
   POST /api/seller/medicine
   GET /api/seller/medicine
   ```

3. **Generate QR Code**
   ```
   POST /api/seller/issue-qr
   Response includes: qr_id, qr_image (base64), payload
   ```

4. **View QR Preview**
   - Display base64 image on screen
   - See medicine details

5. **Download QR**
   ```
   Option A: GET /api/seller/qr/{qr_id}/download (PNG)
   Option B: GET /api/seller/qr/{qr_id}/download-pdf (PDF)
   ```

6. **Use Downloaded QR**
   - Print PNG as sticker
   - Print PDF for labeling
   - Email to vendors
   - Share digitally

---

## 🛠️ Installation Requirements

### For PNG Download:
```bash
pip install qrcode[pil]
```

### For PDF Download:
```bash
pip install reportlab
```

### Update requirements.txt:
```
qrcode[pil]==7.4.2
reportlab==4.0.7
```

---

## 🔐 Security Considerations

1. **Authentication**: Both endpoints require `@seller_required` decorator
2. **Authorization**: Verifies seller owns the medicine before download
3. **Rate Limiting**: Apply rate limits to prevent abuse
4. **File Naming**: Safe filenames with UUID short prefix

---

## 📱 API Response Examples

### PNG Download Response:
```
Status: 200 OK
Content-Type: image/png
Content-Disposition: attachment; download_name="QR_Aspirin_B001_550e8400.png"
Body: [Binary PNG image data]
```

### PDF Download Response:
```
Status: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; download_name="QR_Aspirin_B001_550e8400.pdf"
Body: [Binary PDF file data]
```

---

## 💡 Use Cases

### 1. Print for Packaging
Seller downloads PNG → Prints as label → Applies to medicine boxes

### 2. Email to Retailers
Seller generates QR → Downloads PNG → Emails to retail partners

### 3. Bulk Distribution
Seller generates multiple QRs → Downloads all PDFs → Prints in batch

### 4. Digital Sharing
Seller shares QR image via messaging apps

### 5. Quality Control
Seller scans own QR code to verify → Tests distribution system

---

## 🚀 Next Steps

1. Install required libraries:
   ```bash
   pip install qrcode[pil] reportlab
   ```

2. Update requirements.txt

3. Test endpoints with curl:
   ```bash
   curl -X GET http://localhost:5000/seller/qr/{qr_id}/download \
     -H "Authorization: Bearer {token}" \
     -o qr.png
   ```

4. Implement frontend buttons in SellerDashboard

5. Add to git and commit:
   ```bash
   git add backend/routes/seller_routes.py
   git commit -m "Add: QR code download functionality (PNG and PDF)"
   git push origin main
   ```

---

## ❓ Troubleshooting

### qrcode library not installed
```
Error: ImportError: No module named 'qrcode'
Fix: pip install qrcode[pil]
```

### reportlab library not installed
```
Error: ImportError: No module named 'reportlab'
Fix: pip install reportlab
```

### QR code not found
```
Error: QR code not found (404)
Fix: Verify qr_id is correct and QR was successfully created
```

### Unauthorized access
```
Error: Unauthorized (403)
Fix: Verify seller owns the medicine associated with the QR
```

---

## 📊 File Naming Convention

Generated files follow this pattern:
```
QR_{MEDICINE_NAME}_{BATCH_NO}_{QR_ID_SHORT}.{ext}

Example:
QR_Aspirin_500mg_B001_550e8400.png
QR_Aspirin_500mg_B001_550e8400.pdf
```

---

**Implementation Date:** December 2025  
**Status:** Ready for Integration
