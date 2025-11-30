import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Navigation } from '@/components/Navigation';
import { getAuthHeader } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Search, Package, AlertCircle, Building2, CheckCircle2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function AdminMedicineManagement() {
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    loadAllMedicines();
  }, []);

  const loadAllMedicines = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/medicines/all`, {
        headers: getAuthHeader(),
      });

      if (response.ok) {
        const data = await response.json();
        setMedicines(data.data || []);
      } else {
        toast({
          title: "Error",
          description: "Failed to load medicines",
          variant: "destructive",
        });
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

  const getStockBadge = (quantity) => {
    if (quantity === 0) return { label: 'Out of Stock', className: 'bg-red-100 text-red-800' };
    if (quantity < 10) return { label: `Low Stock (${quantity})`, className: 'bg-amber-100 text-amber-800' };
    return { label: `In Stock (${quantity})`, className: 'bg-green-100 text-green-800' };
  };

  const getDeliveryStatusBadge = (status) => {
    const statusMap = {
      in_stock: { label: 'In Stock', className: 'bg-blue-100 text-blue-800' },
      in_transit: { label: 'In Transit', className: 'bg-purple-100 text-purple-800' },
      delivered: { label: 'Delivered', className: 'bg-green-100 text-green-800' },
      out_of_stock: { label: 'Out of Stock', className: 'bg-red-100 text-red-800' },
    };
    return statusMap[status] || { label: status, className: 'bg-gray-100 text-gray-800' };
  };

  const getApprovalStatusBadge = (status) => {
    const statusMap = {
      pending: { label: 'Pending', className: 'bg-amber-100 text-amber-800' },
      approved: { label: 'Approved', className: 'bg-green-100 text-green-800' },
      rejected: { label: 'Rejected', className: 'bg-red-100 text-red-800' },
    };
    return statusMap[status] || { label: status, className: 'bg-gray-100 text-gray-800' };
  };

  // Filter medicines based on search query
  const filteredMedicines = medicines.filter(medicine =>
    medicine.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    medicine.batch_no?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    medicine.category?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    medicine.manufacturer?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    medicine.seller_name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Calculate statistics
  const stats = {
    total: medicines.length,
    approved: medicines.filter(m => m.approval_status === 'approved').length,
    pending: medicines.filter(m => m.approval_status === 'pending').length,
    inStock: medicines.filter(m => m.stock_quantity > 0).length,
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Loading medicine database...</p>
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
          <h1 className="text-3xl font-bold tracking-tight">Medicine Database</h1>
          <p className="text-muted-foreground mt-2">Browse and search all medicines from verified sellers</p>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Total Medicines</p>
                  <p className="text-2xl font-bold">{stats.total}</p>
                </div>
                <Package className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Approved</p>
                  <p className="text-2xl font-bold">{stats.approved}</p>
                </div>
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Pending Approval</p>
                  <p className="text-2xl font-bold">{stats.pending}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-amber-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">In Stock</p>
                  <p className="text-2xl font-bold">{stats.inStock}</p>
                </div>
                <Package className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search Bar */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by medicine name, batch number, category, manufacturer, or seller..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            {searchQuery && (
              <p className="text-sm text-muted-foreground mt-2">
                Found {filteredMedicines.length} medicine{filteredMedicines.length !== 1 ? 's' : ''}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Medicine Cards Grid */}
        {filteredMedicines.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredMedicines.map((medicine) => {
              const stockBadge = getStockBadge(medicine.stock_quantity || 0);
              const deliveryBadge = getDeliveryStatusBadge(medicine.delivery_status);
              const approvalBadge = getApprovalStatusBadge(medicine.approval_status);

              return (
                <Card key={medicine.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{medicine.name}</CardTitle>
                        <CardDescription>Batch: {medicine.batch_no}</CardDescription>
                      </div>
                      <Badge className={approvalBadge.className}>
                        {approvalBadge.label}
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    {/* Seller Information */}
                    {medicine.seller_name && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Building2 className="h-4 w-4" />
                        <span>{medicine.seller_name}</span>
                      </div>
                    )}

                    {/* Medicine Details */}
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-muted-foreground">Strength</p>
                        <p className="font-medium">{medicine.strength || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Dosage</p>
                        <p className="font-medium">{medicine.dosage || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Category</p>
                        <p className="font-medium">{medicine.category || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Manufacturer</p>
                        <p className="font-medium">{medicine.manufacturer || 'N/A'}</p>
                      </div>
                    </div>

                    {/* Dates */}
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-muted-foreground">Mfg Date</p>
                        <p className="font-medium">
                          {medicine.mfg_date ? new Date(medicine.mfg_date).toLocaleDateString() : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Expiry Date</p>
                        <p className="font-medium">
                          {medicine.expiry_date ? new Date(medicine.expiry_date).toLocaleDateString() : 'N/A'}
                        </p>
                      </div>
                    </div>

                    {/* Status Badges */}
                    <div className="flex gap-2 flex-wrap">
                      <Badge className={stockBadge.className}>
                        {stockBadge.label}
                      </Badge>
                      <Badge className={deliveryBadge.className}>
                        {deliveryBadge.label}
                      </Badge>
                    </div>

                    {/* Description */}
                    {medicine.description && (
                      <div className="text-sm">
                        <p className="text-muted-foreground mb-1">Description</p>
                        <p className="text-sm line-clamp-2">{medicine.description}</p>
                      </div>
                    )}

                    {/* Usage */}
                    {medicine.usage && (
                      <div className="text-sm">
                        <p className="text-muted-foreground mb-1">Usage</p>
                        <p className="text-sm line-clamp-2">{medicine.usage}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        ) : (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {searchQuery
                ? "No medicines found matching your search"
                : "No medicines in the database yet"}
            </AlertDescription>
          </Alert>
        )}
      </main>
    </div>
  );
}
