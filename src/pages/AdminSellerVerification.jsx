import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Navigation } from '@/components/Navigation';
import { getAuthHeader, getUserRole } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { CheckCircle2, XCircle, Clock, FileText, User, Building2, AlertCircle } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function AdminSellerVerification() {
  const [sellers, setSellers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeller, setSelectedSeller] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [remarks, setRemarks] = useState('');
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();
  const { toast} = useToast();

  useEffect(() => {
    const role = getUserRole();
    if (role !== 'admin') {
      navigate('/');
      return;
    }
    
    fetchSellers();
  }, [navigate]);

  const fetchSellers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/sellers`, {
        headers: getAuthHeader(),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch sellers');
      }

      const data = await response.json();
      setSellers(data.data || []);
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

  const handleMarkViewed = async (sellerId) => {
    setProcessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/sellers/${sellerId}/mark-viewed`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to mark as viewed');
      }

      toast({
        title: "Success",
        description: "Seller marked as viewed",
      });

      fetchSellers();
      // Update selected seller
      const updatedData = await response.json();
      if (updatedData.seller_updated) {
        setSelectedSeller(updatedData.seller_updated);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleSetVerifying = async (sellerId) => {
    setProcessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/sellers/${sellerId}/set-verifying`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to set verifying status');
      }

      toast({
        title: "Success",
        description: "Seller marked as verifying",
      });

      fetchSellers();
      // Update selected seller
      const updatedData = await response.json();
      if (updatedData.seller_updated) {
        setSelectedSeller(updatedData.seller_updated);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleApproveSeller = async (sellerId) => {
    setProcessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/sellers/${sellerId}/approve`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to approve seller');
      }

      toast({
        title: "Success",
        description: "Seller approved successfully",
      });

      setSelectedSeller(null);
      fetchSellers();
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleRejectSeller = async (sellerId) => {
    if (!rejectReason.trim()) {
      toast({
        title: "Error",
        description: "Please provide a rejection reason",
        variant: "destructive",
      });
      return;
    }

    setProcessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/sellers/${sellerId}/reject`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason: rejectReason }),
      });

      if (!response.ok) {
        throw new Error('Failed to reject seller');
      }

      toast({
        title: "Success",
        description: "Seller rejected successfully",
      });

      setSelectedSeller(null);
      setRejectReason('');
      fetchSellers();
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleRequestChanges = async (sellerId) => {
    if (!remarks.trim()) {
      toast({
        title: "Error",
        description: "Please provide remarks for the required changes",
        variant: "destructive",
      });
      return;
    }

    setProcessing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/sellers/${sellerId}/request-changes`, {
        method: 'POST',
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ remarks: remarks }),
      });

      if (!response.ok) {
        throw new Error('Failed to request changes');
      }

      toast({
        title: "Success",
        description: "Changes requested - seller will be notified",
      });

      setSelectedSeller(null);
      setRemarks('');
      fetchSellers();
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setProcessing(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-amber-100 text-amber-800"><Clock className="h-3 w-3 mr-1" /> Pending</Badge>;
      case 'viewed':
        return <Badge className="bg-blue-100 text-blue-800"><CheckCircle2 className="h-3 w-3 mr-1" /> Viewed</Badge>;
      case 'verifying':
        return <Badge className="bg-purple-100 text-purple-800"><Clock className="h-3 w-3 mr-1" /> Verifying</Badge>;
      case 'approved':
        return <Badge className="bg-green-100 text-green-800"><CheckCircle2 className="h-3 w-3 mr-1" /> Approved</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800"><XCircle className="h-3 w-3 mr-1" /> Rejected</Badge>;
      case 'changes_required':
        return <Badge className="bg-orange-100 text-orange-800"><AlertCircle className="h-3 w-3 mr-1" /> Changes Required</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const pendingSellers = sellers.filter(s => ['pending', 'viewed', 'verifying', 'changes_required'].includes(s.status));
  const approvedSellers = sellers.filter(s => s.status === 'approved');
  const rejectedSellers = sellers.filter(s => s.status === 'rejected');

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

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-6xl mx-auto p-4 pt-20">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Seller Verification</h1>
          <p className="text-muted-foreground">Review and approve seller KYC applications</p>
        </div>

        <Tabs defaultValue="pending" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="pending">
              Pending ({pendingSellers.length})
            </TabsTrigger>
            <TabsTrigger value="approved">
              Approved ({approvedSellers.length})
            </TabsTrigger>
            <TabsTrigger value="rejected">
              Rejected ({rejectedSellers.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="pending" className="mt-6 space-y-4">
            {pendingSellers.length === 0 ? (
              <Card>
                <CardContent className="pt-6 text-center text-muted-foreground">
                  No pending seller applications
                </CardContent>
              </Card>
            ) : (
              pendingSellers.map(seller => (
                <Card key={seller.id} className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => setSelectedSeller(seller)}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Building2 className="h-5 w-5" />
                          <CardTitle>{seller.company_name}</CardTitle>
                        </div>
                        <CardDescription>{seller.email}</CardDescription>
                      </div>
                      {getStatusBadge(seller.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">License Number</p>
                        <p className="font-medium">{seller.license_number}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">License Type</p>
                        <p className="font-medium">{seller.license_type || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">GSTIN</p>
                        <p className="font-medium">{seller.gstin || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Submitted</p>
                        <p className="font-medium">{new Date(seller.submission_date).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          <TabsContent value="approved" className="mt-6 space-y-4">
            {approvedSellers.length === 0 ? (
              <Card>
                <CardContent className="pt-6 text-center text-muted-foreground">
                  No approved sellers
                </CardContent>
              </Card>
            ) : (
              approvedSellers.map(seller => (
                <Card key={seller.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Building2 className="h-5 w-5" />
                          <CardTitle>{seller.company_name}</CardTitle>
                        </div>
                        <CardDescription>{seller.email}</CardDescription>
                      </div>
                      {getStatusBadge(seller.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">License Number</p>
                        <p className="font-medium">{seller.license_number}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Approved Date</p>
                        <p className="font-medium">{new Date(seller.approved_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          <TabsContent value="rejected" className="mt-6 space-y-4">
            {rejectedSellers.length === 0 ? (
              <Card>
                <CardContent className="pt-6 text-center text-muted-foreground">
                  No rejected sellers
                </CardContent>
              </Card>
            ) : (
              rejectedSellers.map(seller => (
                <Card key={seller.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Building2 className="h-5 w-5" />
                          <CardTitle>{seller.company_name}</CardTitle>
                        </div>
                        <CardDescription>{seller.email}</CardDescription>
                      </div>
                      {getStatusBadge(seller.status)}
                    </div>
                  </CardHeader>
                </Card>
              ))
            )}
          </TabsContent>
        </Tabs>

        {/* Detailed View Modal */}
        {selectedSeller && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Building2 className="h-5 w-5" />
                      {selectedSeller.company_name}
                    </CardTitle>
                    <CardDescription>KYC Application Details</CardDescription>
                  </div>
                  <Button 
                    variant="ghost"
                    onClick={() => setSelectedSeller(null)}
                  >
                    ✕
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Company Information */}
                <div className="space-y-4 border-b pb-4">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Building2 className="h-4 w-4" />
                    Company Information
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Company Name</p>
                      <p className="font-medium">{selectedSeller.company_name}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Email</p>
                      <p className="font-medium">{selectedSeller.email}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">License Number</p>
                      <p className="font-medium">{selectedSeller.license_number}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">License Type</p>
                      <p className="font-medium">{selectedSeller.license_type || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">License Expiry</p>
                      <p className="font-medium">{selectedSeller.license_expiry || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">GSTIN</p>
                      <p className="font-medium">{selectedSeller.gstin || 'N/A'}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-muted-foreground">Address</p>
                      <p className="font-medium">{selectedSeller.address || 'N/A'}</p>
                    </div>
                    {selectedSeller.company_website && (
                      <div className="col-span-2">
                        <p className="text-muted-foreground">Website</p>
                        <p className="font-medium">
                          <a href={selectedSeller.company_website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                            {selectedSeller.company_website}
                          </a>
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Authorized Person */}
                <div className="space-y-4 border-b pb-4">
                  <h3 className="font-semibold flex items-center gap-2">
                    <User className="h-4 w-4" />
                    Authorized Person
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Name</p>
                      <p className="font-medium">{selectedSeller.authorized_person || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Contact</p>
                      <p className="font-medium">{selectedSeller.authorized_person_contact || 'N/A'}</p>
                    </div>
                  </div>
                </div>

                {/* Documents */}
                {selectedSeller.documents && (
                  <div className="space-y-4 border-b pb-4">
                    <h3 className="font-semibold flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Uploaded Documents
                    </h3>
                    <Alert className="border-blue-200 bg-blue-50">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription className="text-sm">
                        Documents list: {typeof selectedSeller.documents === 'string' 
                          ? selectedSeller.documents 
                          : 'Verification documents provided'}
                      </AlertDescription>
                    </Alert>
                  </div>
                )}

                {/* Status and Actions */}
                {['pending', 'viewed', 'verifying', 'changes_required'].includes(selectedSeller.status) && (
                  <div className="space-y-4 border-t pt-4">
                    <h3 className="font-semibold">Verification Actions</h3>

                    <Alert className="border-blue-200 bg-blue-50 mb-4">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription className="text-sm ml-2">
                        <strong>Current Status:</strong> {selectedSeller.status.replace('_', ' ').toUpperCase()}
                        <br />
                        {selectedSeller.status === 'changes_required'
                          ? 'Seller has been notified to make changes. Review again once they resubmit.'
                          : 'Update the verification stage as you review the application.'}
                      </AlertDescription>
                    </Alert>

                    <div className="space-y-3">
                      {/* Stage Buttons */}
                      {selectedSeller.status === 'pending' && (
                        <Button
                          onClick={() => handleMarkViewed(selectedSeller.id)}
                          className="w-full bg-blue-600 hover:bg-blue-700"
                          disabled={processing}
                        >
                          <CheckCircle2 className="h-4 w-4 mr-2" />
                          {processing ? 'Processing...' : 'Mark as Viewed'}
                        </Button>
                      )}

                      {(selectedSeller.status === 'pending' || selectedSeller.status === 'viewed') && (
                        <Button
                          onClick={() => handleSetVerifying(selectedSeller.id)}
                          className="w-full bg-purple-600 hover:bg-purple-700"
                          disabled={processing}
                        >
                          <Clock className="h-4 w-4 mr-2" />
                          {processing ? 'Processing...' : 'Start Verification Process'}
                        </Button>
                      )}

                      {/* Approve Button */}
                      <Button
                        onClick={() => handleApproveSeller(selectedSeller.id)}
                        className="w-full bg-green-600 hover:bg-green-700"
                        disabled={processing}
                      >
                        <CheckCircle2 className="h-4 w-4 mr-2" />
                        {processing ? 'Processing...' : 'Approve Seller'}
                      </Button>

                      {/* Request Changes Section */}
                      <div className="space-y-2 pt-4 border-t">
                        <label className="text-sm font-medium">Request Changes (Remarks)</label>
                        <Textarea
                          placeholder="Provide detailed remarks about what needs to be corrected or updated..."
                          value={remarks}
                          onChange={(e) => setRemarks(e.target.value)}
                          className="h-24"
                        />
                        <Button
                          onClick={() => handleRequestChanges(selectedSeller.id)}
                          className="w-full bg-orange-600 hover:bg-orange-700"
                          disabled={processing}
                        >
                          <AlertCircle className="h-4 w-4 mr-2" />
                          {processing ? 'Processing...' : 'Request Changes'}
                        </Button>
                      </div>

                      {/* Reject Section */}
                      <div className="space-y-2 pt-4 border-t">
                        <label className="text-sm font-medium">Rejection Reason</label>
                        <Textarea
                          placeholder="Provide reason for rejection..."
                          value={rejectReason}
                          onChange={(e) => setRejectReason(e.target.value)}
                          className="h-24"
                        />
                        <Button
                          onClick={() => handleRejectSeller(selectedSeller.id)}
                          variant="destructive"
                          className="w-full"
                          disabled={processing}
                        >
                          <XCircle className="h-4 w-4 mr-2" />
                          {processing ? 'Processing...' : 'Reject Seller'}
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
