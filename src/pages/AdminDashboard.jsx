import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navigation } from '@/components/Navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getAuthHeader } from '@/lib/auth';
import {
  Users,
  Package,
  QrCode,
  BarChart3,
  Shield,
  CheckCircle2,
  Clock,
  XCircle,
  AlertCircle,
  TrendingUp,
  FileText,
  Building2
} from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalSellers: 0,
    pendingSellers: 0,
    approvedSellers: 0,
    totalMedicines: 0,
    pendingMedicines: 0,
    totalQRCodes: 0,
    totalScans: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch analytics
      const analyticsRes = await fetch('http://localhost:5000/admin/analytics', {
        headers: getAuthHeader(),
      });
      if (analyticsRes.ok) {
        const analyticsData = await analyticsRes.json();
        const data = analyticsData.data;

        // Fetch sellers for pending count
        const sellersRes = await fetch('http://localhost:5000/admin/sellers', {
          headers: getAuthHeader(),
        });
        let pendingSellers = 0;
        let approvedSellers = 0;
        if (sellersRes.ok) {
          const sellersData = await sellersRes.json();
          const sellers = sellersData.data || [];
          pendingSellers = sellers.filter(s => ['pending', 'viewed', 'verifying'].includes(s.status)).length;
          approvedSellers = sellers.filter(s => s.status === 'approved').length;
        }

        // Fetch medicines for pending count
        const medicinesRes = await fetch('http://localhost:5000/admin/medicines', {
          headers: getAuthHeader(),
        });
        let pendingMedicines = 0;
        if (medicinesRes.ok) {
          const medicinesData = await medicinesRes.json();
          const medicines = medicinesData.data || [];
          pendingMedicines = medicines.filter(m => m.approval_status === 'pending').length;
        }

        setStats({
          totalSellers: data.total_sellers || 0,
          pendingSellers,
          approvedSellers,
          totalMedicines: data.total_medicines || 0,
          pendingMedicines,
          totalQRCodes: data.total_qr_codes || 0,
          totalScans: Object.values(data.scan_counts || {}).reduce((a, b) => a + b, 0)
        });
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const featureCards = [
    {
      title: 'Seller Verification',
      description: 'Review and approve seller applications',
      icon: Building2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      count: stats.pendingSellers,
      countLabel: 'Pending',
      route: '/admin/sellers',
      actions: [
        { label: 'View All Sellers', route: '/admin/sellers' }
      ]
    },
    {
      title: 'Medicine Management',
      description: 'Approve and manage medicine database',
      icon: Package,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      count: stats.pendingMedicines,
      countLabel: 'Pending Approval',
      route: '/admin/medicines',
      actions: [
        { label: 'View All Medicines', route: '/admin/medicines' }
      ]
    },
    {
      title: 'QR Code System',
      description: 'Monitor QR code generation and scans',
      icon: QrCode,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      count: stats.totalQRCodes,
      countLabel: 'Total QR Codes',
      route: '/admin/qr-codes',
      actions: [
        { label: 'View QR Analytics', route: '/admin/qr-codes' }
      ]
    },
    {
      title: 'System Analytics',
      description: 'View platform statistics and insights',
      icon: BarChart3,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      count: stats.totalScans,
      countLabel: 'Total Scans',
      route: '/admin/analytics',
      actions: [
        { label: 'View Analytics', route: '/admin/analytics' }
      ]
    },
    {
      title: 'Audit Logs',
      description: 'Review system activity and admin actions',
      icon: FileText,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      count: '-',
      countLabel: 'Activity Logs',
      route: '/admin/audit-logs',
      actions: [
        { label: 'View Logs', route: '/admin/audit-logs' }
      ]
    },
    {
      title: 'Security',
      description: 'Manage revoked keys and security',
      icon: Shield,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      count: '-',
      countLabel: 'Security Status',
      route: '/admin/security',
      actions: [
        { label: 'View Security', route: '/admin/security' }
      ]
    }
  ];

  const statCards = [
    {
      title: 'Total Sellers',
      value: stats.totalSellers,
      description: `${stats.approvedSellers} approved`,
      icon: Users,
      color: 'text-blue-600',
      trend: '+12%'
    },
    {
      title: 'Medicines',
      value: stats.totalMedicines,
      description: 'In database',
      icon: Package,
      color: 'text-green-600',
      trend: '+8%'
    },
    {
      title: 'QR Codes',
      value: stats.totalQRCodes,
      description: 'Generated',
      icon: QrCode,
      color: 'text-purple-600',
      trend: '+15%'
    },
    {
      title: 'Total Scans',
      value: stats.totalScans,
      description: 'All time',
      icon: TrendingUp,
      color: 'text-orange-600',
      trend: '+23%'
    }
  ];

  if (loading) {
    return (
      <main className="min-h-screen bg-background">
        <Navigation />
        <div className="container mx-auto py-8 px-4">
          <p>Loading admin dashboard...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background">
      <Navigation />
      <div className="container mx-auto py-8 px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold">Admin Dashboard</h1>
          </div>
          <p className="text-muted-foreground">
            Manage sellers, medicines, and monitor system activity
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statCards.map((stat, index) => (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.description}
                </p>
                {stat.trend && (
                  <Badge variant="outline" className="mt-2 text-xs">
                    {stat.trend} from last month
                  </Badge>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Pending Actions Alert */}
        {(stats.pendingSellers > 0 || stats.pendingMedicines > 0) && (
          <Card className="mb-8 border-amber-200 bg-amber-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-amber-900">
                <AlertCircle className="h-5 w-5" />
                Pending Actions Required
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {stats.pendingSellers > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-amber-800">
                    {stats.pendingSellers} seller{stats.pendingSellers > 1 ? 's' : ''} awaiting verification
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate('/admin/sellers')}
                    className="border-amber-300"
                  >
                    Review Sellers
                  </Button>
                </div>
              )}
              {stats.pendingMedicines > 0 && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-amber-800">
                    {stats.pendingMedicines} medicine{stats.pendingMedicines > 1 ? 's' : ''} awaiting approval
                  </span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigate('/admin/medicines')}
                    className="border-amber-300"
                  >
                    Review Medicines
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Feature Cards */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Admin Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featureCards.map((feature, index) => (
              <Card
                key={index}
                className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(feature.route)}
              >
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg ${feature.bgColor} flex items-center justify-center mb-4`}>
                    <feature.icon className={`h-6 w-6 ${feature.color}`} />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <div className="text-2xl font-bold">{feature.count}</div>
                      <div className="text-sm text-muted-foreground">{feature.countLabel}</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {feature.actions.map((action, actionIndex) => (
                      <Button
                        key={actionIndex}
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(action.route);
                        }}
                      >
                        {action.label}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common administrative tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => navigate('/admin/sellers')}
              >
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Approve Sellers
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => navigate('/admin/medicines')}
              >
                <Package className="h-4 w-4 mr-2" />
                Review Medicines
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => navigate('/admin/audit-logs')}
              >
                <FileText className="h-4 w-4 mr-2" />
                View Audit Logs
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
};

export default AdminDashboard;
