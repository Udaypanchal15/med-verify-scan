import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { login, getCurrentUser } from '@/lib/auth';
import { Navigation } from '@/components/Navigation';
import { Eye, EyeOff, AlertCircle, Clock, XCircle } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showVerificationAlert, setShowVerificationAlert] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [error, setError] = useState('');
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setShowVerificationAlert(false);
    setError(''); // Clear previous errors

    try {
      const data = await login(email, password);

      // Check for seller verification status
      if (data.data?.user?.role === 'seller') {
        const sellerStatus = data.seller_status;

        // Handle rejected/revoked - prevent login
        if (sellerStatus === 'rejected') {
          setVerificationStatus('rejected');
          setShowVerificationAlert(true);
          return;
        }
        if (sellerStatus === 'revoked') {
          setVerificationStatus('revoked');
          setShowVerificationAlert(true);
          return;
        }

        toast({
          title: "Login successful",
          description: "Welcome back!",
        });

        // Trigger navigation bar update
        window.dispatchEvent(new Event('auth-state-changed'));

        // Redirect based on seller status
        if (sellerStatus === 'no_application') {
          // Seller hasn't applied yet - redirect to application page
          navigate('/seller/apply');
        } else if (sellerStatus === 'approved') {
          // Approved seller - redirect to dashboard
          navigate('/seller/dashboard');
        } else {
          // Pending/viewed/verifying - redirect to status page
          navigate('/seller/status');
        }
        return;
      }

      toast({
        title: "Login successful",
        description: "Welcome back!",
      });

      // Redirect non-sellers to home page
      if (data.data?.user?.role === 'admin') {
        navigate('/admin/dashboard');
      } else if (data.data?.user?.role === 'user') {
        navigate('/user/dashboard');
      } else {
        navigate('/');
      }

      // Trigger navigation bar update
      window.dispatchEvent(new Event('auth-state-changed'));
    } catch (error) {
      // Show error inline instead of toast
      setError(error.message || "Invalid email or password. Please check your credentials and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/30 via-purple-50/20 to-pink-50/30 backdrop-blur-sm">
      <Navigation />
      <div className="flex items-center justify-center p-4 pt-20">
      <Card className="w-full max-w-md shadow-2xl border-2 backdrop-blur-md bg-white/95">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>Enter your credentials to access your account</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {/* Login Error Alert */}
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-sm text-red-700 ml-2">
                  {error}
                </AlertDescription>
              </Alert>
            )}

            {/* Seller Verification Alert */}
            {showVerificationAlert && (
              <Alert className="border-red-200 bg-red-50">
                {verificationStatus === 'rejected' ? (
                  <>
                    <XCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-sm text-red-700 ml-2">
                      Your seller application has been rejected. Please contact support for more information.
                    </AlertDescription>
                  </>
                ) : (
                  <>
                    <XCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-sm text-red-700 ml-2">
                      Your seller account has been revoked. Please contact support.
                    </AlertDescription>
                  </>
                )}
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="user@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-muted-foreground hover:text-foreground"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={loading || showVerificationAlert}>
              {loading ? 'Logging in...' : 'Login'}
            </Button>
            <div className="text-sm text-center text-muted-foreground">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary hover:underline">
                Register
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
      </div>
    </div>
  );
}

