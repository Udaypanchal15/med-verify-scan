import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Navigation } from '@/components/Navigation';
import { getAuthHeader } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Search, Package, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function AdminMedicineManagement() {
  const [sellers, setSellers] = useState([]);
  const [expandedSeller, setExpandedSeller] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const { toast } = useToast();

  useEffect(() => {
    loadSellerMedicines();
  }, []);

  const loadSellerMedicines = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/sellers/medicines`, {
        headers: getAuthHeader(),
      });

      if (response.ok) {
        const data = await response.json();
        setSellers(data.data || []);
      } else if (response.status === 404) {
        // Endpoint might not exist yet, fetch sellers and their medicines separately
        await loadSellersMedicinesSeparately();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load seller medicines",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadSellersMedicinesSeparately = async () => {
    try {
      const sellersResponse = await fetch(`${API_BASE_URL}/admin/sellers`, {
        headers: getAuthHeader(),
      });

      if (sellersResponse.ok) {
        const sellersData = await sellersResponse.json();
        const sellersWithMedicines = await Promise.all(
          (sellersData.data || []).map(async (seller) => {
            try {
              // Get medicines for this seller (would need a seller-specific endpoint)
              return {
                ...seller,
                medicines: [],
              };
            } catch (error) {
              return { ...seller, medicines: [] };
            }
          })
        );
        setSellers(sellersWithMedicines);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load sellers",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleSellerExpand = (sellerId) => {
    setExpandedSeller(expandedSeller === sellerId ? null : sellerId);
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

  const getSellerStatus = (status) => {
    const statusMap = {
      pending: 'bg-amber-100 text-amber-800',
      viewed: 'bg-blue-100 text-blue-800',
      verifying: 'bg-purple-100 text-purple-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      changes_required: 'bg-orange-100 text-orange-800',
    };
    return statusMap[status] || 'bg-gray-100 text-gray-800';
  };

  // Filter sellers based on search
  const filteredSellers = sellers.filter(seller =>
    seller.company_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    seller.license_number?.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Medicine Database</h1>
            <p className="text-muted-foreground mt-2">View medicines from all approved sellers</p>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Approved Sellers</p>
                  <p className="text-2xl font-bold">
                    {sellers.filter(s => s.status === 'approved').length}
                  </p>
                </div>
                <Package className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Total Sellers</p>
                  <p className="text-2xl font-bold">{sellers.length}</p>
                </div>
                <Package className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-muted-foreground text-sm">Total Medicines</p>
                  <p className="text-2xl font-bold">
                    {sellers.reduce((acc, seller) => acc + (seller.medicines?.length || 0), 0)}
                  </p>
                </div>
                <Package className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by company name or license number..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Sellers and Their Medicines */}
        {filteredSellers.length > 0 ? (
          <div className="space-y-4">
            {filteredSellers.map((seller) => (
              <Card key={seller.id}>
                <div
                  className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => toggleSellerExpand(seller.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold">{seller.company_name}</h3>
                          <p className="text-sm text-muted-foreground">License: {seller.license_number}</p>
                          <div className="flex gap-2 mt-2">
                            <Badge className={getSellerStatus(seller.status)}>
                              {seller.status?.replace('_', ' ').toUpperCase()}
                            </Badge>
                            {seller.medicines && seller.medicines.length > 0 && (
                              <Badge variant="secondary">
                                {seller.medicines.length} Medicines
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="ml-4">
                      {expandedSeller === seller.id ? (
                        <ChevronUp className="h-5 w-5 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>
                  </div>
                </div>

                {/* Medicines List - Expanded */}
                {expandedSeller === seller.id && (
                  <div className="border-t bg-gray-50 p-6">
                    {seller.medicines && seller.medicines.length > 0 ? (
                      <div className="space-y-3">
                        {seller.medicines.map((medicine) => (
                          <div
                            key={medicine.id}
                            className="bg-white p-4 rounded-lg border border-gray-200"
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1">
                                <h4 className="font-semibold">{medicine.name}</h4>
                                <p className="text-sm text-muted-foreground">Batch: {medicine.batch_no}</p>
                                <div className="flex gap-2 mt-2">
                                  {medicine.strength && <Badge variant="outline">{medicine.strength}</Badge>}
                                  {medicine.dosage && <Badge variant="outline">{medicine.dosage}</Badge>}
                                  {medicine.category && <Badge variant="outline">{medicine.category}</Badge>}
                                </div>
                              </div>
                              <div className="text-right space-y-2">
                                <div className={`p-2 rounded ${getStockColor(medicine.stock_quantity || 0)}`}>
                                  <p className="text-xs">Stock: {medicine.stock_quantity || 0}</p>
                                </div>
                                <Badge className={getDeliveryColor(medicine.delivery_status)}>
                                  {medicine.delivery_status === 'in_stock' ? 'In Stock' :
                                   medicine.delivery_status === 'pending' ? 'Pending' :
                                   medicine.delivery_status === 'delivered' ? 'Delivered' : 'Discontinued'}
                                </Badge>
                              </div>
                            </div>
                            <div className="flex gap-4 mt-3 text-xs text-muted-foreground">
                              <span>Mfg: {new Date(medicine.mfg_date).toLocaleDateString()}</span>
                              <span>Exp: {new Date(medicine.expiry_date).toLocaleDateString()}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          No medicines added by this seller yet
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                )}
              </Card>
            ))}
          </div>
        ) : (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {searchQuery ? "No sellers found matching your search" : "No sellers registered yet"}
            </AlertDescription>
          </Alert>
        )}
      </main>
    </div>
  );
}
