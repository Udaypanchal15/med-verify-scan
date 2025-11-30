import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { getAuthHeader, getUserRole } from '@/lib/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

/**
 * SellerDashboardGuard - Higher-order component that protects seller dashboard access
 * Only allows access if user is a seller with approved status
 * Redirects to /seller/status if not approved
 */
export function SellerDashboardGuard({ children }) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAccess = async () => {
      try {
        // Check user role
        const role = getUserRole();
        if (role !== 'seller') {
          navigate('/');
          return;
        }

        // Fetch seller status
        const response = await fetch(`${API_BASE_URL}/seller/status`, {
          headers: getAuthHeader(),
        });

        if (!response.ok) {
          if (response.status === 401) {
            navigate('/login');
            return;
          }
          throw new Error('Failed to fetch seller status');
        }

        const data = await response.json();
        const seller = data.data;

        // Check if approved
        if (seller.status === 'approved') {
          setIsAuthorized(true);
        } else {
          toast({
            title: 'Not Yet Approved',
            description: `Your application status is "${seller.status.replace('_', ' ')}". You can access the dashboard once approved.`,
            variant: 'destructive',
          });
          navigate('/seller/status');
        }
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to verify seller status',
          variant: 'destructive',
        });
        navigate('/seller/status');
      } finally {
        setLoading(false);
      }
    };

    checkAccess();
  }, [navigate, toast]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-muted-foreground">Verifying your access...</p>
      </div>
    );
  }

  if (!isAuthorized) {
    return null;
  }

  return children;
}
