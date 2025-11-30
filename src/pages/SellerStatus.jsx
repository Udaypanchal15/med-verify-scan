import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Navigation } from '@/components/Navigation';
import { VerticalRoadmap } from '@/components/VerticalRoadmap';
import { getAuthHeader, getCurrentUser, getUserRole } from '@/lib/auth';
import { CheckCircle2, AlertCircle, Clock, RefreshCw, ArrowRight, Building2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const STATUS_BADGE_CONFIG = {
  pending: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
  viewed: { color: 'bg-blue-100 text-blue-800', icon: CheckCircle2 },
  verifying: { color: 'bg-blue-100 text-blue-800', icon: Clock },
  approved: { color: 'bg-green-100 text-green-800', icon: CheckCircle2 },
  rejected: { color: 'bg-red-100 text-red-800', icon: AlertCircle },
  changes_required: { color: 'bg-amber-100 text-amber-800', icon: AlertCircle },
  resubmitted: { color: 'bg-purple-100 text-purple-800', icon: RefreshCw },
};

export default function SellerStatus() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [seller, setSeller] = useState(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());

  // Check user is logged in and is seller
  useEffect(() => {
    const role = getUserRole();
    if (role !== 'seller') {
      navigate('/');
      return;
    }

    loadSellerStatus();

    // Set up auto-polling every 15 seconds
    const pollInterval = setInterval(loadSellerStatus, 15000);

    return () => clearInterval(pollInterval);
  }, [navigate]);

  const loadSellerStatus = async () => {
    try {
      setPolling(true);
      const response = await fetch(`${API_BASE_URL}/seller/status`, {
        headers: getAuthHeader(),
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to load status');
      }

      const data = await response.json();
      setSeller(data.data);
      setLastRefresh(new Date());
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
      setPolling(false);
    }
  };

  const handleGoToDashboard = () => {
    if (seller?.status === 'approved') {
      navigate('/seller/dashboard');
    } else {
      toast({
        title: 'Not Approved',
        description: 'You can access the dashboard after your application is approved.',
        variant: 'destructive',
      });
    }
  };

  const handleReEdit = () => {
    // Navigate to re-edit form with pre-filled data
    navigate('/seller/apply', { state: { editMode: true, seller } });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="flex items-center justify-center pt-20">
          <p className="text-muted-foreground">Loading your application status...</p>
        </div>
      </div>
    );
  }

  if (!seller) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <div className="max-w-4xl mx-auto p-4 pt-20 pb-10">
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <h3 className="font-semibold text-red-800">No Application Found</h3>
              </div>
              <p className="text-sm text-red-700 mb-4">
                You haven't submitted a seller application yet.
              </p>
              <Button onClick={() => navigate('/seller/apply')}>
                Start Application
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const badgeConfig = STATUS_BADGE_CONFIG[seller.status] || STATUS_BADGE_CONFIG.pending;
  const BadgeIcon = badgeConfig.icon;
  const isApproved = seller.status === 'approved';
  const needsChanges = seller.status === 'changes_required';
  const isRejected = seller.status === 'rejected';

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-4xl mx-auto p-4 pt-20 pb-10">
        {/* Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Building2 className="h-6 w-6" />
                <div>
                  <CardTitle className="text-2xl">{seller.company_name}</CardTitle>
                  <CardDescription>{seller.license_number}</CardDescription>
                </div>
              </div>
              <Badge className={badgeConfig.color}>
                <BadgeIcon className="h-3 w-3 mr-1" />
                {seller.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
          </CardHeader>
        </Card>

        {/* Status Timeline */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Application Status</CardTitle>
            <CardDescription>
              Last updated: {lastRefresh.toLocaleTimeString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <VerticalRoadmap
              status={seller.status}
              submittedAt={seller.submitted_at}
              viewedAt={seller.viewed_at}
              verifyingAt={seller.verifying_at}
              approvedAt={seller.approved_at}
              rejectedAt={seller.rejected_at}
              adminRemarks={seller.admin_remarks}
              requiredChanges={seller.required_changes}
            />
          </CardContent>
        </Card>

        {/* Application Details */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Application Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Company Email</p>
                <p className="font-medium">{seller.email || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">License Type</p>
                <p className="font-medium capitalize">{seller.license_type || 'Not specified'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">License Expiry</p>
                <p className="font-medium">
                  {seller.license_expiry
                    ? new Date(seller.license_expiry).toLocaleDateString()
                    : 'Not specified'}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">GSTIN</p>
                <p className="font-medium">{seller.gstin || 'Not provided'}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-muted-foreground">Address</p>
                <p className="font-medium">{seller.address || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Authorized Person</p>
                <p className="font-medium">{seller.authorized_person || 'Not provided'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Contact</p>
                <p className="font-medium">{seller.authorized_person_contact || 'Not provided'}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Documents */}
        {seller.documents && seller.documents.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Submitted Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {seller.documents.map((doc, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded border"
                  >
                    <span className="text-sm font-medium truncate">{doc}</span>
                    <a
                      href={`${API_BASE_URL}${doc}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm"
                    >
                      View
                    </a>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="space-y-4">
          {/* Approved CTA */}
          {isApproved && (
            <Card className="border-green-200 bg-green-50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-6 w-6 text-green-600" />
                    <div>
                      <h4 className="font-semibold text-green-900">Congratulations!</h4>
                      <p className="text-sm text-green-700">
                        Your application has been approved. You can now access the seller dashboard.
                      </p>
                    </div>
                  </div>
                  <Button
                    onClick={handleGoToDashboard}
                    className="flex-shrink-0"
                    size="sm"
                  >
                    Go to Dashboard
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Changes Required */}
          {needsChanges && (
            <Card className="border-amber-200 bg-amber-50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <AlertCircle className="h-6 w-6 text-amber-600" />
                    <div>
                      <h4 className="font-semibold text-amber-900">Changes Required</h4>
                      <p className="text-sm text-amber-700">
                        Please address the required changes listed above and resubmit your application.
                      </p>
                    </div>
                  </div>
                  <Button
                    onClick={handleReEdit}
                    className="flex-shrink-0"
                    variant="outline"
                    size="sm"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Re-Edit
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Rejected */}
          {isRejected && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-red-900">Application Rejected</h4>
                    <p className="text-sm text-red-700 mt-1">
                      Your application was not approved at this time. Please contact support for more details.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Pending Status */}
          {!isApproved && !needsChanges && !isRejected && (
            <Card className="border-blue-200 bg-blue-50">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <Clock className="h-6 w-6 text-blue-600 animate-spin flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-blue-900">Under Review</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Our admin team is reviewing your application. You'll receive an email once we've made a decision. (Auto-refreshing every 15 seconds)
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Manual Refresh Button */}
          <Button
            onClick={loadSellerStatus}
            variant="outline"
            disabled={polling}
            className="w-full"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${polling ? 'animate-spin' : ''}`} />
            {polling ? 'Refreshing...' : 'Refresh Status'}
          </Button>
        </div>
      </div>
    </div>
  );
}
