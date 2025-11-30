import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Navigation } from '@/components/Navigation';
import { getAuthHeader, getCurrentUser, getUserRole } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Plus, Search, QrCode, CheckCircle2, Clock, AlertCircle, Building2, User, Package, Mail, Phone, MapPin, BarChart3, TrendingUp, Edit } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function SellerDashboard() {
  const [user, setUser] = useState(null);
  const [seller, setSeller] = useState(null);
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddMedicine, setShowAddMedicine] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMedicine, setSelectedMedicine] = useState(null);
  const [showQRModal, setShowQRModal] = useState(false);
  const [qrBatchDetails, setQRBatchDetails] = useState('');
  const [generatingQR, setGeneratingQR] = useState(false);
  const [editingMedicine, setEditingMedicine] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [updatingMedicine, setUpdatingMedicine] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const [medicineForm, setMedicineForm] = useState({
    name: '',
    batch_no: '',
    mfg_date: '',
    expiry_date: '',
    dosage: '',
    strength: '',
    category: '',
    description: '',
    usage: '',
    stock_quantity: 0,
    delivery_status: 'in_stock',
    manufacturer: '',
  });

  const [submittingMedicine, setSubmittingMedicine] = useState(false);

  useEffect(() => {
    const role = getUserRole();
    if (role !== 'seller') {
      navigate('/');
      return;
    }

    const loadSellerData = async () => {
      try {
        const userData = await getCurrentUser();
        if (userData) {
          setUser(userData);
        }

        // Fetch seller status
        const statusRes = await fetch(`${API_BASE_URL}/seller/status`, {
          headers: getAuthHeader(),
        });

        if (statusRes.ok) {
          const statusData = await statusRes.json();
          setSeller(statusData.data);
        } else if (statusRes.status === 404) {
          // No seller profile yet - user needs to submit KYC application
          setSeller(null);
        }

        // Fetch seller medicines
        const medicinesRes = await fetch(`${API_BASE_URL}/seller/medicine`, {
          headers: getAuthHeader(),
        });

        if (medicinesRes.ok) {
          const medicinesData = await medicinesRes.json();
          setMedicines(medicinesData.data || []);
        }
      } catch (error) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    loadSellerData();
  }, [navigate, toast]);

  const handleAddMedicine = async (e) => {
    e.preventDefault();
    setSubmittingMedicine(true);

    try {
      const response = await fetch(`${API_BASE_URL}/seller/medicine`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(medicineForm),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to add medicine');
      }

      toast({
        title: "Success",
        description: "Medicine added successfully",
      });

      setMedicineForm({
        name: '',
        batch_no: '',
        mfg_date: '',
        expiry_date: '',
        dosage: '',
        strength: '',
        category: '',
        description: '',
        usage: '',
        stock_quantity: 0,
        delivery_status: 'in_stock',
        manufacturer: '',
      });
      setShowAddMedicine(false);

      // Refresh medicines list
      const medicinesRes = await fetch(`${API_BASE_URL}/seller/medicine`, {
        headers: getAuthHeader(),
      });
      if (medicinesRes.ok) {
        const data = await medicinesRes.json();
        setMedicines(data.data || []);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setSubmittingMedicine(false);
    }
  };

  const handleGenerateQR = async () => {
    if (!selectedMedicine) return;

    setGeneratingQR(true);
    try {
      const response = await fetch(`${API_BASE_URL}/seller/issue-qr`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          medicine_id: selectedMedicine.id,
          batch_details: qrBatchDetails,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to generate QR code');
      }

      const data = await response.json();
      
      toast({
        title: "Success",
        description: "QR code generated successfully",
      });

      setShowQRModal(false);
      setQRBatchDetails('');
      setSelectedMedicine(null);
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setGeneratingQR(false);
    }
  };

  const handleEditMedicine = (medicine) => {
    setEditingMedicine(medicine);
    setEditForm({
      name: medicine.name,
      batch_no: medicine.batch_no,
      mfg_date: medicine.mfg_date?.split('T')[0] || '',
      expiry_date: medicine.expiry_date?.split('T')[0] || '',
      dosage: medicine.dosage || '',
      strength: medicine.strength || '',
      category: medicine.category || '',
      description: medicine.description || '',
      usage: medicine.usage || '',
      stock_quantity: medicine.stock_quantity || 0,
      delivery_status: medicine.delivery_status || 'in_stock',
      manufacturer: medicine.manufacturer || '',
    });
    setShowEditModal(true);
  };

  const handleUpdateMedicine = async (e) => {
    e.preventDefault();
    if (!editingMedicine) return;

    setUpdatingMedicine(true);
    try {
      const response = await fetch(`${API_BASE_URL}/seller/medicine/${editingMedicine.id}`, {
        method: 'PUT',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editForm),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to update medicine');
      }

      const data = await response.json();

      // Update medicines list
      setMedicines(medicines.map(m => m.id === editingMedicine.id ? data.medicine : m));

      toast({
        title: "Success",
        description: "Medicine updated successfully",
      });

      setShowEditModal(false);
      setEditingMedicine(null);
      setEditForm({});
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setUpdatingMedicine(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-amber-100 text-amber-800"><Clock className="h-3 w-3 mr-1" /> Pending</Badge>;
      case 'approved':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle2 className="h-3 w-3 mr-1" /> Approved</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800"><AlertCircle className="h-3 w-3 mr-1" /> Rejected</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const filteredMedicines = medicines.filter(med =>
    med.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    med.batch_no.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const approvedMedicines = filteredMedicines.filter(m => m.approval_status === 'approved');

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="flex items-center justify-center pt-20">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  const stats = {
    totalMedicines: medicines.length,
    approvedMedicines: medicines.filter(m => m.approval_status === 'approved').length,
    pendingMedicines: medicines.filter(m => m.approval_status === 'pending').length,
    totalQRCodes: 0, // Would need backend support
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto p-4 pt-20">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold">Seller Dashboard</h1>
          </div>
          <p className="text-muted-foreground">
            Manage your medicines, profile, and business analytics
          </p>
        </div>

        {/* Quick Stats */}
        {seller?.status === 'approved' && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Medicines</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalMedicines}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.approvedMedicines} approved
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Approval</CardTitle>
                <Clock className="h-4 w-4 text-amber-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.pendingMedicines}</div>
                <p className="text-xs text-muted-foreground">
                  Awaiting admin review
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">QR Codes</CardTitle>
                <QrCode className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalQRCodes}</div>
                <p className="text-xs text-muted-foreground">
                  Generated
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Status</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold capitalize">{seller?.status || 'N/A'}</div>
                <p className="text-xs text-muted-foreground">
                  Account status
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Seller Profile Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                <CardTitle>Seller Profile</CardTitle>
              </div>
              {seller && getStatusBadge(seller.status)}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {seller ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Company Name</p>
                  <p className="font-medium">{seller.company_name}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">License Number</p>
                  <p className="font-medium">{seller.license_number}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{seller.email || user?.email}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <p className="font-medium capitalize">{seller.status}</p>
                </div>
                {seller.status === 'pending' && (
                  <Alert className="md:col-span-2 border-amber-200 bg-amber-50">
                    <Clock className="h-4 w-4 text-amber-600" />
                    <AlertDescription className="text-sm text-amber-700 ml-2">
                      Your application is pending admin verification. You can add medicines once approved.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            ) : (
              <Alert className="border-amber-200 bg-amber-50">
                <AlertCircle className="h-4 w-4 text-amber-600" />
                <AlertDescription className="text-sm text-amber-700 ml-2 flex items-center justify-between">
                  <span>You haven't submitted a KYC application yet. Submit your application to get started.</span>
                  <Button 
                    onClick={() => navigate('/seller/apply')}
                    className="ml-4"
                    size="sm"
                  >
                    Submit KYC Application
                  </Button>
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {seller?.status === 'approved' && (
          <>
            {/* Quick Navigation */}
            <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Plus className="h-5 w-5" />
                    Medicine Management
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">Manage your medicines inventory with stock tracking and delivery status</p>
                  <Button 
                    onClick={() => navigate('/seller/medicines')}
                    className="w-full"
                  >
                    Go to Medicine Database
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <QrCode className="h-5 w-5" />
                    Quick Add
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">Quickly add new medicines below or go to full database for advanced features</p>
                  <Button 
                    onClick={() => document.getElementById('add-medicine-tab')?.click()}
                    variant="outline"
                    className="w-full"
                  >
                    Add Here
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Add Medicine and Manage Section */}
            <Tabs defaultValue="medicines" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="medicines">
                  <Search className="h-4 w-4 mr-2" />
                  My Medicines
                </TabsTrigger>
                <TabsTrigger value="add" id="add-medicine-tab">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Medicine
                </TabsTrigger>
                <TabsTrigger value="profile">
                  <User className="h-4 w-4 mr-2" />
                  Business Profile
                </TabsTrigger>
                <TabsTrigger value="analytics">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Analytics
                </TabsTrigger>
              </TabsList>

              {/* My Medicines Tab */}
              <TabsContent value="medicines" className="mt-6 space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Search Your Medicines</CardTitle>
                    <CardDescription>Find and manage your approved medicines</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Input
                      placeholder="Search by name or batch number..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="mb-4"
                    />
                  </CardContent>
                </Card>

                {approvedMedicines.length > 0 ? (
                  <div className="grid gap-4">
                    {approvedMedicines.map((medicine) => (
                      <Card key={medicine.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="text-lg">{medicine.name}</CardTitle>
                              <CardDescription>Batch: {medicine.batch_no}</CardDescription>
                            </div>
                            <Badge className="bg-green-100 text-green-800">
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              Approved
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                            <div>
                              <p className="text-muted-foreground">Strength</p>
                              <p className="font-medium">{medicine.strength || 'N/A'}</p>
                            </div>
                            <div>
                              <p className="text-muted-foreground">Dosage</p>
                              <p className="font-medium">{medicine.dosage || 'N/A'}</p>
                            </div>
                            <div>
                              <p className="text-muted-foreground">Mfg Date</p>
                              <p className="font-medium">{new Date(medicine.mfg_date).toLocaleDateString()}</p>
                            </div>
                            <div>
                              <p className="text-muted-foreground">Expiry Date</p>
                              <p className="font-medium">{new Date(medicine.expiry_date).toLocaleDateString()}</p>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-3 mt-4">
                            <Button
                              variant="outline"
                              onClick={() => handleEditMedicine(medicine)}
                            >
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </Button>
                            <Button
                              onClick={() => {
                                setSelectedMedicine(medicine);
                                setShowQRModal(true);
                              }}
                            >
                              <QrCode className="h-4 w-4 mr-2" />
                              Generate QR
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      No approved medicines found. Add a medicine from the "Add Medicine" tab.
                    </AlertDescription>
                  </Alert>
                )}
              </TabsContent>

              {/* Add Medicine Tab */}
              <TabsContent value="add" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Add New Medicine</CardTitle>
                    <CardDescription>Submit a new medicine for admin approval</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <form onSubmit={handleAddMedicine} className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="name">Medicine Name *</Label>
                          <Input
                            id="name"
                            placeholder="Enter medicine name"
                            value={medicineForm.name}
                            onChange={(e) => setMedicineForm({...medicineForm, name: e.target.value})}
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="batch_no">Batch Number *</Label>
                          <Input
                            id="batch_no"
                            placeholder="Enter batch number"
                            value={medicineForm.batch_no}
                            onChange={(e) => setMedicineForm({...medicineForm, batch_no: e.target.value})}
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="mfg_date">Manufacturing Date *</Label>
                          <Input
                            id="mfg_date"
                            type="date"
                            value={medicineForm.mfg_date}
                            onChange={(e) => setMedicineForm({...medicineForm, mfg_date: e.target.value})}
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="expiry_date">Expiry Date *</Label>
                          <Input
                            id="expiry_date"
                            type="date"
                            value={medicineForm.expiry_date}
                            onChange={(e) => setMedicineForm({...medicineForm, expiry_date: e.target.value})}
                            required
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="dosage">Dosage</Label>
                          <Input
                            id="dosage"
                            placeholder="e.g., 500mg"
                            value={medicineForm.dosage}
                            onChange={(e) => setMedicineForm({...medicineForm, dosage: e.target.value})}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="strength">Strength</Label>
                          <Input
                            id="strength"
                            placeholder="e.g., Standard, Extra"
                            value={medicineForm.strength}
                            onChange={(e) => setMedicineForm({...medicineForm, strength: e.target.value})}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="category">Category</Label>
                          <Input
                            id="category"
                            placeholder="e.g., Tablet, Capsule, Syrup"
                            value={medicineForm.category}
                            onChange={(e) => setMedicineForm({...medicineForm, category: e.target.value})}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="usage">Medical Usage</Label>
                          <Input
                            id="usage"
                            placeholder="e.g., For heart, diabetes, pain relief"
                            value={medicineForm.usage}
                            onChange={(e) => setMedicineForm({...medicineForm, usage: e.target.value})}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="stock_quantity">Stock Quantity</Label>
                          <Input
                            id="stock_quantity"
                            type="number"
                            placeholder="e.g., 1000"
                            value={medicineForm.stock_quantity}
                            onChange={(e) => setMedicineForm({...medicineForm, stock_quantity: parseInt(e.target.value) || 0})}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="delivery_status">Delivery Status</Label>
                          <select
                            id="delivery_status"
                            className="w-full px-3 py-2 border border-input rounded-md bg-background"
                            value={medicineForm.delivery_status}
                            onChange={(e) => setMedicineForm({...medicineForm, delivery_status: e.target.value})}
                          >
                            <option value="in_stock">In Stock</option>
                            <option value="pending">Pending Delivery</option>
                            <option value="delivered">Delivered</option>
                            <option value="discontinued">Discontinued</option>
                          </select>
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="manufacturer">Manufacturer</Label>
                          <Input
                            id="manufacturer"
                            placeholder="Manufacturing company name"
                            value={medicineForm.manufacturer}
                            onChange={(e) => setMedicineForm({...medicineForm, manufacturer: e.target.value})}
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          placeholder="Enter medicine description..."
                          value={medicineForm.description}
                          onChange={(e) => setMedicineForm({...medicineForm, description: e.target.value})}
                          className="h-20"
                        />
                      </div>

                      <div className="flex gap-2">
                        <Button type="submit" disabled={submittingMedicine}>
                          {submittingMedicine ? 'Adding...' : 'Add Medicine'}
                        </Button>
                        <Button type="button" variant="outline" onClick={() => setShowAddMedicine(false)}>
                          Cancel
                        </Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Business Profile Tab */}
              <TabsContent value="profile" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Business Profile</CardTitle>
                    <CardDescription>Your company information and contact details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-4">
                        <div className="flex items-center gap-3">
                          <Building2 className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="text-sm text-muted-foreground">Company Name</p>
                            <p className="font-medium">{seller?.company_name || 'N/A'}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Mail className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="text-sm text-muted-foreground">Email</p>
                            <p className="font-medium">{seller?.email || user?.email || 'N/A'}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <User className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="text-sm text-muted-foreground">Authorized Person</p>
                            <p className="font-medium">{seller?.authorized_person || 'N/A'}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Phone className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="text-sm text-muted-foreground">Contact Number</p>
                            <p className="font-medium">{seller?.authorized_person_contact || 'N/A'}</p>
                          </div>
                        </div>
                      </div>
                      <div className="space-y-4">
                        <div className="flex items-start gap-3">
                          <MapPin className="h-5 w-5 text-muted-foreground mt-1" />
                          <div>
                            <p className="text-sm text-muted-foreground">Address</p>
                            <p className="font-medium">{seller?.address || 'N/A'}</p>
                          </div>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">License Number</p>
                          <p className="font-medium">{seller?.license_number || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">License Type</p>
                          <p className="font-medium">{seller?.license_type || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">GSTIN</p>
                          <p className="font-medium">{seller?.gstin || 'N/A'}</p>
                        </div>
                        {seller?.company_website && (
                          <div>
                            <p className="text-sm text-muted-foreground">Website</p>
                            <a href={seller.company_website} target="_blank" rel="noopener noreferrer" className="font-medium text-blue-600 hover:underline">
                              {seller.company_website}
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Analytics Tab */}
              <TabsContent value="analytics" className="mt-6">
                <div className="grid gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Performance Overview</CardTitle>
                      <CardDescription>Your business metrics and statistics</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Total Medicines Added</span>
                          <strong>{stats.totalMedicines}</strong>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Approved Medicines</span>
                          <strong className="text-green-600">{stats.approvedMedicines}</strong>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Pending Approval</span>
                          <strong className="text-amber-600">{stats.pendingMedicines}</strong>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">QR Codes Generated</span>
                          <strong>{stats.totalQRCodes}</strong>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Alert>
                    <TrendingUp className="h-4 w-4" />
                    <AlertDescription>
                      More analytics features coming soon! Track medicine delivery, scan statistics, stock levels, and more.
                    </AlertDescription>
                  </Alert>
                </div>
              </TabsContent>
            </Tabs>
          </>
        )}

        {/* QR Generation Modal */}
        {showQRModal && selectedMedicine && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <QrCode className="h-5 w-5" />
                  Generate QR Code
                </CardTitle>
                <CardDescription>{selectedMedicine.name} - {selectedMedicine.batch_no}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="batch-details">Batch Details (Optional)</Label>
                  <Textarea
                    id="batch-details"
                    placeholder="Enter additional batch or box details (e.g., Box ID, Serial Number)..."
                    value={qrBatchDetails}
                    onChange={(e) => setQRBatchDetails(e.target.value)}
                    className="h-20"
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={handleGenerateQR}
                    className="flex-1"
                    disabled={generatingQR}
                  >
                    {generatingQR ? 'Generating...' : 'Generate QR'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowQRModal(false);
                      setSelectedMedicine(null);
                      setQRBatchDetails('');
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Edit Medicine Modal */}
        {showEditModal && editingMedicine && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50 overflow-y-auto">
            <Card className="w-full max-w-2xl my-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Edit className="h-5 w-5" />
                  Edit Medicine
                </CardTitle>
                <CardDescription>Update medicine details - {editingMedicine.name}</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleUpdateMedicine} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="edit-name">Medicine Name *</Label>
                      <Input
                        id="edit-name"
                        value={editForm.name}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-batch">Batch Number *</Label>
                      <Input
                        id="edit-batch"
                        value={editForm.batch_no}
                        onChange={(e) => setEditForm({ ...editForm, batch_no: e.target.value })}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-strength">Strength</Label>
                      <Input
                        id="edit-strength"
                        placeholder="e.g., 500mg"
                        value={editForm.strength}
                        onChange={(e) => setEditForm({ ...editForm, strength: e.target.value })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-dosage">Dosage</Label>
                      <Input
                        id="edit-dosage"
                        placeholder="e.g., 1 tablet twice daily"
                        value={editForm.dosage}
                        onChange={(e) => setEditForm({ ...editForm, dosage: e.target.value })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-mfg">Manufacturing Date *</Label>
                      <Input
                        id="edit-mfg"
                        type="date"
                        value={editForm.mfg_date}
                        onChange={(e) => setEditForm({ ...editForm, mfg_date: e.target.value })}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-expiry">Expiry Date *</Label>
                      <Input
                        id="edit-expiry"
                        type="date"
                        value={editForm.expiry_date}
                        onChange={(e) => setEditForm({ ...editForm, expiry_date: e.target.value })}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-category">Category</Label>
                      <Input
                        id="edit-category"
                        placeholder="e.g., Antibiotic, Painkiller"
                        value={editForm.category}
                        onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-manufacturer">Manufacturer</Label>
                      <Input
                        id="edit-manufacturer"
                        placeholder="e.g., Pfizer, GSK"
                        value={editForm.manufacturer}
                        onChange={(e) => setEditForm({ ...editForm, manufacturer: e.target.value })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-stock">Stock Quantity</Label>
                      <Input
                        id="edit-stock"
                        type="number"
                        min="0"
                        value={editForm.stock_quantity}
                        onChange={(e) => setEditForm({ ...editForm, stock_quantity: parseInt(e.target.value) || 0 })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="edit-delivery">Delivery Status</Label>
                      <select
                        id="edit-delivery"
                        value={editForm.delivery_status}
                        onChange={(e) => setEditForm({ ...editForm, delivery_status: e.target.value })}
                        className="w-full border rounded-md px-3 py-2"
                      >
                        <option value="in_stock">In Stock</option>
                        <option value="in_transit">In Transit</option>
                        <option value="delivered">Delivered</option>
                        <option value="out_of_stock">Out of Stock</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="edit-usage">Usage Instructions</Label>
                    <Textarea
                      id="edit-usage"
                      placeholder="How to use this medicine..."
                      value={editForm.usage}
                      onChange={(e) => setEditForm({ ...editForm, usage: e.target.value })}
                      className="h-20"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="edit-description">Description</Label>
                    <Textarea
                      id="edit-description"
                      placeholder="Medicine description and details..."
                      value={editForm.description}
                      onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                      className="h-20"
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button
                      type="submit"
                      className="flex-1"
                      disabled={updatingMedicine}
                    >
                      {updatingMedicine ? 'Updating...' : 'Update Medicine'}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowEditModal(false);
                        setEditingMedicine(null);
                        setEditForm({});
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
