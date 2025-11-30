import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { QrCode, Camera, Upload, CheckCircle, XCircle, AlertTriangle, Info, X } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { scanQrData } from "@/lib/api";
import { Html5Qrcode } from "html5-qrcode";

export const QRScanner = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [qrCode, setQrCode] = useState("");
  const [verificationResult, setVerificationResult] = useState(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const scannerRef = useRef(null);
  const fileInputRef = useRef(null);


  // Check if a medicine is expired
  const checkExpiry = (expiryDateStr) => {
    if (!expiryDateStr || expiryDateStr === 'Unknown' || expiryDateStr === 'N/A') {
      return false;
    }
    try {
      const expiry = new Date(expiryDateStr);
      const now = new Date();
      return expiry < now;
    } catch (error) {
      return false;
    }
  };

  // Get alternative medicines based on category or usage
  const getAlternatives = async (medicineName, category) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/medicine/alternatives?name=${encodeURIComponent(medicineName)}&category=${encodeURIComponent(category || '')}`);
      if (response.ok) {
        const data = await response.json();
        return data.data || [];
      }
    } catch (error) {
      console.error('Failed to fetch alternatives:', error);
    }
    // Return mock alternatives if API fails
    return [
      { name: 'Paracetamol 500mg', manufacturer: 'Generic Pharma', category: 'Pain Relief' },
      { name: 'Aspirin 300mg', manufacturer: 'MediCorp', category: 'Pain Relief' },
      { name: 'Ibuprofen 400mg', manufacturer: 'HealthCare Inc', category: 'Anti-inflammatory' }
    ];
  };

  const mockVerifyMedicine = (code) => {
    // Mock verification logic - in real app this would call an API
    const medicines = [
      {
        code: "MED001",
        name: "Paracetamol 500mg",
        manufacturer: "PharmaCorp Ltd.",
        batchNumber: "PCL24001",
        mfgDate: "2024-01-15",
        expDate: "2026-01-15",
        isAuthentic: true,
        isExpired: false,
        status: "verified"
      },
      {
        code: "MED002",
        name: "Ibuprofen 200mg",
        manufacturer: "MediCare Inc.",
        batchNumber: "MC24002",
        mfgDate: "2024-02-20",
        expDate: "2025-08-20",
        isAuthentic: true,
        isExpired: true,
        status: "expired"
      },
      {
        code: "MED003",
        name: "Unknown Medicine",
        manufacturer: "Unknown",
        batchNumber: "Unknown",
        mfgDate: "Unknown",
        expDate: "Unknown",
        isAuthentic: false,
        isExpired: false,
        status: "counterfeit"
      }
    ];

    return medicines.find(med => med.code === code) || medicines[2];
  };

  // Camera scanning functions
  const handleCameraScan = async () => {
    // First, set camera active state to render the modal
    setIsCameraActive(true);
    
    // Wait for the DOM to render the modal element
    setTimeout(async () => {
      try {
        // Request camera permissions
        const html5QrCode = new Html5Qrcode("qr-reader");
        
        await html5QrCode.start(
          { facingMode: "environment" }, // Try back camera first, falls back to front
          {
            fps: 10,
            qrbox: { width: 250, height: 250 }
          },
          (decodedText, decodedResult) => {
            // Success callback - QR code scanned
            handleQrDecoded(decodedText);
            stopCamera(html5QrCode);
          },
          (errorMessage) => {
            // Error callback - ignore scanning errors
          }
        );
        
        scannerRef.current = html5QrCode;
        
        toast({
          title: "Camera Started",
          description: "Point camera at QR code to scan",
        });
        
      } catch (error) {
        console.error("Camera error:", error);
        setIsCameraActive(false);
        toast({
          title: "Camera Error",
          description: "Failed to access camera. Check permissions.",
          variant: "destructive",
        });
      }
    }, 100);
  };

  const stopCamera = (scanner) => {
    if (scanner) {
      scanner.stop().then(() => {
        scanner.clear();
      }).catch((error) => {
        console.error("Stop camera error:", error);
      });
    }
    setIsCameraActive(false);
  };

  const handleCloseCamera = () => {
    if (scannerRef.current) {
      stopCamera(scannerRef.current);
    }
  };

  const handleQrDecoded = async (decodedText) => {
    // Process the decoded QR code
    setQrCode(decodedText);
    await handleScan(decodedText);
  };

  // Image upload functions
  const handleImageSelect = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: "File Too Large",
        description: "Maximum file size is 5MB",
        variant: "destructive",
      });
      return;
    }

    // Check file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: "Invalid File",
        description: "Please select an image file",
        variant: "destructive",
      });
      return;
    }

    setSelectedImage(file);
    handleImageUpload(file);
  };

  const handleImageUpload = async (file) => {
    setIsScanning(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/scan/image`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        toast({
          title: "Scan Failed",
          description: data.error,
          variant: "destructive",
        });
        return;
      }

      // Map API response to verification result
      const isExpired = checkExpiry(data.expiry_date);
      const result = {
        code: data.name || "Unknown",
        name: data.name || "Unknown Medicine",
        manufacturer: data.manufacturer || "Unknown",
        batchNumber: data.batch_number || "N/A",
        mfgDate: data.manufacture_date || "N/A",
        expDate: data.expiry_date || "N/A",
        category: data.category || "N/A",
        isAuthentic: !data.error,
        isExpired: isExpired,
        status: data.error ? "counterfeit" : (isExpired ? "expired" : "verified")
      };

      setVerificationResult(result);

      // If expired, get alternatives
      if (isExpired && result.name !== "Unknown Medicine") {
        const alts = await getAlternatives(result.name, result.category);
        setAlternatives(alts);
      } else {
        setAlternatives([]);
      }

      toast({
        title: isExpired ? "Medicine Expired" : "Upload Successful",
        description: isExpired
          ? `${result.name} has expired. Check alternatives below.`
          : `Medicine scanned: ${result.name}`,
        variant: isExpired ? "destructive" : "default"
      });

    } catch (error) {
      console.error("Upload error:", error);
      toast({
        title: "Upload Failed",
        description: "Failed to process image. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsScanning(false);
      setSelectedImage(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleScan = async (customCode = null) => {
    const codeToScan = customCode || qrCode;
    
    // Check if codeToScan is a string and has content
    if (!codeToScan || typeof codeToScan !== 'string' || !codeToScan.trim()) {
      toast({
        title: "Error",
        description: "Please enter a QR code or medicine ID",
        variant: "destructive",
      });
      return;
    }

    setIsScanning(true);

    try {
      // Try to scan via API first
      const response = await scanQrData(codeToScan);
      
      console.log("API Scan Response:", response);

      // Map API response to verification result format
      const isExpired = checkExpiry(response.expiry_date);
      const result = {
        code: codeToScan,
        name: response.name || "Unknown Medicine",
        manufacturer: response.manufacturer || "Unknown",
        batchNumber: response.batch_number || "N/A",
        mfgDate: response.manufacture_date || "N/A",
        expDate: response.expiry_date || "N/A",
        category: response.category || "N/A",
        isAuthentic: response.name !== "Unknown Medicine",
        isExpired: isExpired,
        status: response.name === "Unknown Medicine" ? "counterfeit" : (isExpired ? "expired" : "verified")
      };

      setVerificationResult(result);

      // If expired, get alternatives
      if (isExpired && result.name !== "Unknown Medicine") {
        const alts = await getAlternatives(result.name, result.category);
        setAlternatives(alts);
      } else {
        setAlternatives([]);
      }

      toast({
        title: "Scan Complete",
        description: isExpired
          ? `Medicine expired. Alternatives suggested below.`
          : `Medicine verification ${result.status}`,
        variant: result.status === "verified" ? "default" : "destructive",
      });
    } catch (error) {
      console.error("Scan error:", error);
      
      // Fallback to mock verification if API fails
      setTimeout(() => {
        const result = mockVerifyMedicine(codeToScan);
        setVerificationResult(result);
        
        toast({
          title: "Scan Complete",
          description: `Medicine verification ${result.status}`,
          variant: result.status === "verified" ? "default" : "destructive",
        });
      }, 1000);
    } finally {
      setIsScanning(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "verified": return "text-success";
      case "expired": return "text-warning";
      case "counterfeit": return "text-destructive";
      default: return "text-muted-foreground";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "verified": return <CheckCircle className="h-6 w-6 text-success" />;
      case "expired": return <AlertTriangle className="h-6 w-6 text-warning" />;
      case "counterfeit": return <XCircle className="h-6 w-6 text-destructive" />;
      default: return <Info className="h-6 w-6 text-muted-foreground" />;
    }
  };

  return (
    <section id="scanner" className="py-20 bg-background">
      <div className="container mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">Medicine Verification Scanner</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Scan QR codes or enter medicine IDs to verify authenticity, check expiry dates, and ensure medicine safety
          </p>
        </div>

        <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Scanner Interface */}
          <Card className="p-8 bg-gradient-to-br from-card to-secondary/20 border-primary/20">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <QrCode className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-2xl font-semibold mb-2">Scan Medicine QR Code</h3>
              <p className="text-muted-foreground">Use camera or enter code manually</p>
            </div>

            <div className="space-y-4">
              <div className="relative">
                <Input
                  value={qrCode}
                  onChange={(e) => setQrCode(e.target.value)}
                  placeholder="Enter QR code or medicine ID (try: MED001, MED002, MED003)"
                  className="text-center text-lg py-6"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  className="py-6"
                  onClick={handleCameraScan}
                  disabled={isCameraActive}
                >
                  <Camera className="mr-2 h-4 w-4" />
                  {isCameraActive ? "Scanning..." : "Use Camera"}
                </Button>
                <Button
                  variant="outline"
                  className="py-6"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isScanning}
                >
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Image
                </Button>
              </div>

              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                style={{ display: 'none' }}
              />

              <Button
                onClick={handleScan}
                disabled={isScanning}
                className="w-full py-6 text-lg bg-gradient-to-r from-primary to-accent hover:shadow-scanner"
              >
                {isScanning ? "Verifying..." : "Verify Medicine"}
              </Button>
            </div>
          </Card>

          {/* Verification Results */}
          <Card className="p-8">
            <h3 className="text-2xl font-semibold mb-6">Verification Result</h3>

            {!verificationResult ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-muted/50 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Info className="h-8 w-8 text-muted-foreground" />
                </div>
                <p className="text-muted-foreground">Enter a medicine code and click verify to see results</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Status Banner */}
                <div className={`flex items-center gap-3 p-4 rounded-lg ${
                  verificationResult.status === "verified" ? "bg-success/10 border border-success/20" :
                  verificationResult.status === "expired" ? "bg-warning/10 border border-warning/20" :
                  "bg-destructive/10 border border-destructive/20"
                }`}>
                  {getStatusIcon(verificationResult.status)}
                  <div>
                    <h4 className={`font-semibold ${getStatusColor(verificationResult.status)}`}>
                      {verificationResult.status === "verified" ? "Medicine Verified" :
                       verificationResult.status === "expired" ? "Medicine Expired" :
                       "Counterfeit Detected"}
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      {verificationResult.status === "verified" ? "This medicine is authentic and safe to use" :
                       verificationResult.status === "expired" ? "This medicine has expired and should not be used" :
                       "This medicine may be counterfeit or unauthorized"}
                    </p>
                  </div>
                </div>

                {/* Medicine Details */}
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Medicine Name</label>
                    <p className="font-semibold">{verificationResult.name}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Manufacturer</label>
                      <p className="font-medium">{verificationResult.manufacturer}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Batch Number</label>
                      <p className="font-medium">{verificationResult.batchNumber}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Mfg Date</label>
                      <p className="font-medium">{verificationResult.mfgDate}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">Exp Date</label>
                      <p className={`font-medium ${verificationResult.isExpired ? 'text-warning' : ''}`}>
                        {verificationResult.expDate}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Alternative Medicines (shown when expired) */}
                {alternatives.length > 0 && verificationResult?.isExpired && (
                  <div className="mt-6 pt-6 border-t">
                    <h4 className="font-semibold mb-3 text-orange-700">
                      ⚠️ Alternative Medicines (This medicine is expired)
                    </h4>
                    <p className="text-sm text-muted-foreground mb-4">
                      Here are some alternative medicines you can use instead:
                    </p>
                    <div className="space-y-3">
                      {alternatives.map((alt, index) => (
                        <div
                          key={index}
                          className="p-3 bg-blue-50 border border-blue-200 rounded-lg hover:shadow-md transition-shadow"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="font-semibold text-blue-900">{alt.name}</p>
                              <p className="text-sm text-blue-700">by {alt.manufacturer}</p>
                              {alt.category && (
                                <p className="text-xs text-blue-600 mt-1">Category: {alt.category}</p>
                              )}
                            </div>
                            <CheckCircle className="h-5 w-5 text-green-600 mt-1" />
                          </div>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground mt-3 italic">
                      💡 Tip: Consult your doctor or pharmacist before switching medicines.
                    </p>
                  </div>
                )}
              </div>
            )}
          </Card>
        </div>

        {/* Camera Scanner Modal */}
        {isCameraActive && (
          <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
            <Card className="w-full max-w-md p-6 relative">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold">Scan QR Code</h3>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleCloseCamera}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              <div id="qr-reader" className="w-full rounded-lg overflow-hidden mb-4" style={{ minHeight: '300px' }}></div>
              
              <p className="text-sm text-muted-foreground text-center">
                Point camera at QR code to scan
              </p>
            </Card>
          </div>
        )}
      </div>
    </section>
  );
};
