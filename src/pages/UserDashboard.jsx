import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Navigation } from '@/components/Navigation';
import { getAuthHeader, getCurrentUser, getUserRole } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Search, CheckCircle2, AlertTriangle, Pill, Clock, Calendar, User, QrCode } from 'lucide-react';
const MEDICINE_CATEGORIES = [
  'All',
  'Diabetes',
  'Heart Disease',
  'High Blood Pressure',
  'Fever',
  'Cough & Cold',
  'Antibiotics',
  'Pain Relief',
  'Allergy',
  'Digestive',
  'Other'
];

import { AIMedicineAssistant } from '@/components/AIMedicineAssistant';
import { QRScanner } from '@/components/QRScanner';
import { UserMedicineDatabase } from '@/components/UserMedicineDatabase';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function UserDashboard() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const role = getUserRole();
    if (role !== 'user') {
      navigate('/');
      return;
    }
    
    const loadUser = async () => {
      const userData = await getCurrentUser();
      if (userData) {
        setUser(userData);
      }
    };

    loadUser();
    setLoading(false);
  }, [navigate]);

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
        {/* User Profile Section */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5" />
              <CardTitle>My Profile</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{user?.email}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Role</p>
                <p className="font-medium capitalize">{user?.role}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Timezone</p>
                <p className="font-medium">{user?.timezone || 'UTC'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Member Since</p>
                <p className="font-medium">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Tabs */}
        <Tabs defaultValue="medicines" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="medicines">
                <Pill className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Browse Medicines</span>
                <span className="sm:hidden">Medicines</span>
              </TabsTrigger>
              <TabsTrigger value="scan">
                <QrCode className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Scan Medicine</span>
                <span className="sm:hidden">Scan</span>
              </TabsTrigger>
              <TabsTrigger value="assistant">
                <span className="hidden sm:inline">AI Assistant</span>
                <span className="sm:hidden">AI</span>
              </TabsTrigger>
            </TabsList>

          {/* Browse Medicines Tab */}
          <TabsContent value="medicines" className="mt-6">
            <UserMedicineDatabase />
          </TabsContent>

          {/* Scan Medicine Tab */}
          <TabsContent value="scan" className="mt-6">
            <QRScanner />
          </TabsContent>

          {/* AI Assistant Tab */}
          <TabsContent value="assistant" className="mt-6">
            <AIMedicineAssistant />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
