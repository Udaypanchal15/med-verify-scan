import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Navigation } from '@/components/Navigation';
import { getAuthHeader, getCurrentUser } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Search, Plus, Package, TrendingUp, AlertCircle, Trash2, Edit2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function MedicineDatabase() {
  const [medicines, setMedicines] = useState([]);
  const [filteredMedicines, setFilteredMedicines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    name: '',
    batch_no: '',
    mfg_date: '',
    expiry_date: '',
    dosage: '',
    strength: '',
    category: '',
    stock_quantity: 0,
    delivery_status: 'in_stock',
  });

  useEffect(() => {
    loadMedicines();
  }, []);

  useEffect(() => {
    filterMedicines();
  }, [medicines, searchQuery, filterStatus]);

  const loadMedicines = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/seller/medicine`, {
        headers: getAuthHeader(),
      });

      if (response.ok) {
        const data = await response.json();
        setMedicines(data.data || []);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load medicines",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const filterMedicines = () => {
    let filtered = medicines;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(med =>
        med.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        med.batch_no.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(med => med.delivery_status === filterStatus);
    }

    setFilteredMedicines(filtered);
  };

  const handleAddMedicine = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${API_BASE_URL}/seller/medicine`, {
        method: 'POST',
        headers: getAuthHeader(),
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Medicine added successfully",
        });
        setFormData({
          name: '',
          batch_no: '',
          mfg_date: '',
          expiry_date: '',
          dosage: '',
          strength: '',
          category: '',
          stock_quantity: 0,
          delivery_status: 'in_stock',
        });
        setShowAddForm(false);
        loadMedicines();
      } else {
        const error = await response.json();
        toast({
          title: "Error",
          description: error.error || "Failed to add medicine",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const getStockColor = (quantity) => {
    if (quantity === 0) return 'text-red-600 bg-red-50';
    if (quantity < 10) return 'text-amber-600 bg-amber-50';
    return 'text-green-600 bg-green-50';
  };

  const getDeliveryColor = (status) => {
    switch (status) {
      case 'delivered':
        return 'bg-green-100 text-green-800';
      case 'in_stock':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-amber-100 text-amber-800';
      case 'discontinued':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Loading medicines...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="container mx-auto py-8 px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Medicine Inventory</h1>
              <p className="text-muted-foreground mt-2">Manage your medicine stock and delivery status</p>
            </div>
            <Button
              onClick={() => setShowAddForm(!showAddForm)}
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Medicine
            </Button>
          </div>
        </div>

        {/* Add Medicine Form */}
        {showAddForm && (
          <Card className="mb-8 border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle>Add New Medicine</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddMedicine} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Medicine Name</Label>
                    <Input
                      id="name"
                      placeholder="e.g., Aspirin"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="batch_no">Batch Number</Label>
                    <Input
                      id="batch_no"
                      placeholder="e.g., BATCH001"
                      value={formData.batch_no}
                      onChange={(e) => setFormData({ ...formData, batch_no: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="strength">Strength</Label>
                    <Input
                      id="strength"
                      placeholder="e.g., 500mg"
                      value={formData.strength}
                      onChange={(e) => setFormData({ ...formData, strength: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="dosage">Dosage</Label>
                    <Input
                      id="dosage"
                      placeholder="e.g., Tablet"
                      value={formData.dosage}
                      onChange={(e) => setFormData({ ...formData, dosage: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="mfg_date">Manufacturing Date</Label>
                    <Input
                      id="mfg_date"
                      type="date"
                      value={formData.mfg_date}
                      onChange={(e) => setFormData({ ...formData, mfg_date: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="expiry_date">Expiry Date</Label>
                    <Input
                      id="expiry_date"
                      type="date"
                      value={formData.expiry_date}
                      onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="category">Category</Label>
                    <Input
                      id="category"
                      placeholder="e.g., Antibiotic"
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="stock_quantity">Stock Quantity</Label>
                    <Input
                      id="stock_quantity"
                      type="number"
                      min="0"
                      value={formData.stock_quantity}
                      onChange={(e) => setFormData({ ...formData, stock_quantity: parseInt(e.target.value) })}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label htmlFor="delivery_status">Delivery Status</Label>
                    <select
                      id="delivery_status"
                      className="w-full px-3 py-2 border border-input rounded-md bg-background"
                      value={formData.delivery_status}
                      onChange={(e) => setFormData({ ...formData, delivery_status: e.target.value })}
                    >
                      <option value="in_stock">In Stock</option>
                      <option value="pending">Pending Delivery</option>
                      <option value="delivered">Delivered</option>
                      <option value="discontinued">Discontinued</option>
                    </select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button type="submit" className="flex-1">Add Medicine</Button>
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1"
                    onClick={() => setShowAddForm(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Search and Filter */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <Label htmlFor="search" className="mb-2 block">Search Medicine</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    placeholder="Search by name or batch number..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="md:w-48">
                <Label htmlFor="filter" className="mb-2 block">Filter by Status</Label>
                <select
                  id="filter"
                  className="w-full px-3 py-2 border border-input rounded-md bg-background"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option value="all">All Medicines</option>
                  <option value="in_stock">In Stock</option>
                  <option value="pending">Pending Delivery</option>
                  <option value="delivered">Delivered</option>
                  <option value="discontinued">Discontinued</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Total Medicines</p>
                  <p className="text-2xl font-bold">{medicines.length}</p>
                </div>
                <Package className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">In Stock</p>
                  <p className="text-2xl font-bold">
                    {medicines.filter(m => m.delivery_status === 'in_stock').length}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Pending</p>
                  <p className="text-2xl font-bold">
                    {medicines.filter(m => m.delivery_status === 'pending').length}
                  </p>
                </div>
                <AlertCircle className="h-8 w-8 text-amber-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Delivered</p>
                  <p className="text-2xl font-bold">
                    {medicines.filter(m => m.delivery_status === 'delivered').length}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Medicines List */}
        {filteredMedicines.length > 0 ? (
          <div className="space-y-4">
            {filteredMedicines.map((medicine) => (
              <Card key={medicine.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-start gap-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold">{medicine.name}</h3>
                          <p className="text-sm text-muted-foreground">Batch: {medicine.batch_no}</p>
                          <div className="flex flex-wrap gap-2 mt-3">
                            <Badge variant="outline">{medicine.strength || 'N/A'}</Badge>
                            <Badge variant="outline">{medicine.dosage || 'N/A'}</Badge>
                            <Badge variant="outline">{medicine.category || 'N/A'}</Badge>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-3">
                      <div className={`p-2 rounded text-center ${getStockColor(medicine.stock_quantity || 0)}`}>
                        <p className="text-xs text-muted-foreground">Stock</p>
                        <p className="font-bold">{medicine.stock_quantity || 0}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground text-center">Mfg Date</p>
                        <p className="text-sm font-medium text-center">
                          {new Date(medicine.mfg_date).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground text-center">Expiry</p>
                        <p className="text-sm font-medium text-center">
                          {new Date(medicine.expiry_date).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <Badge className={getDeliveryColor(medicine.delivery_status)}>
                          {medicine.delivery_status === 'in_stock' ? 'In Stock' : 
                           medicine.delivery_status === 'pending' ? 'Pending' :
                           medicine.delivery_status === 'delivered' ? 'Delivered' : 'Discontinued'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {searchQuery || filterStatus !== 'all'
                ? "No medicines found matching your filters"
                : "No medicines added yet. Start by adding a new medicine!"}
            </AlertDescription>
          </Alert>
        )}
      </main>
    </div>
  );
}
