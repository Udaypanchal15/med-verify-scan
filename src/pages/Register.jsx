import { useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { register } from '@/lib/auth';
import { Navigation } from '@/components/Navigation';
import SellerRegistrationForm from '@/components/SellerRegistrationForm';
import { Info, Shield, User, ShoppingBag, CheckCircle2, AlertCircle } from 'lucide-react';
import { Eye, EyeOff } from 'lucide-react';

const validatePassword = (pwd) => {
  const errors = [];
  if (pwd.length < 8) {
    errors.push('At least 8 characters');
  }
  if (!/[A-Z]/.test(pwd)) {
    errors.push('One uppercase letter');
  }
  if (!/[a-z]/.test(pwd)) {
    errors.push('One lowercase letter');
  }
  if (!/\d/.test(pwd)) {
    errors.push('One digit');
  }
  return errors;
};

export default function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [role, setRole] = useState('user');
  const [loading, setLoading] = useState(false);
  const [sellerFormData, setSellerFormData] = useState({});
  const [error, setError] = useState('');
  const { toast } = useToast();
  const navigate = useNavigate();

  const passwordErrors = useMemo(() => validatePassword(password), [password]);
  const isPasswordValid = passwordErrors.length === 0 && password.length > 0;

  const handleSellerFormDataChange = (field, value) => {
    setSellerFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    if (e.preventDefault) {
      e.preventDefault();
    }

    setError(''); // Clear previous errors

    if (passwordErrors.length > 0) {
      setError(`Password must contain: ${passwordErrors.join(', ')}`);
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match. Please make sure both password fields are identical.");
      return;
    }

    setLoading(true);

    try {
      const registrationData = {
        email,
        password,
        role,
        ...sellerFormData
      };

      const data = await register(email, password, role, registrationData);

      toast({
        title: "Registration successful",
        description: role === 'seller'
          ? "Your seller application has been submitted. You can login after admin verification."
          : "Account created successfully!",
      });

      navigate('/login');

      // Trigger navigation bar update
      window.dispatchEvent(new Event('auth-state-changed'));
    } catch (error) {
      // Show error inline instead of toast
      setError(error.message || "Failed to create account. Please check your information and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/30 via-purple-50/20 to-pink-50/30 backdrop-blur-sm">
      <Navigation />
      <div className="flex items-center justify-center p-4 pt-20 pb-10">
      <div className="w-full max-w-2xl">
        {role === 'user' ? (
          <Card className="shadow-2xl border-2 backdrop-blur-md bg-white/95">
            <CardHeader>
              <CardTitle>Register</CardTitle>
              <CardDescription>Create a new account to get started</CardDescription>
            </CardHeader>
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-4">
                {/* Registration Error Alert */}
                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-sm text-red-700 ml-2">
                      {error}
                    </AlertDescription>
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
                  <Label htmlFor="role">Role</Label>
                  <Select value={role} onValueChange={setRole}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="user">
                        <div className="flex items-center">
                          <User className="h-4 w-4 mr-2" />
                          User - Scan and verify medicines
                        </div>
                      </SelectItem>
                      <SelectItem value="seller">
                        <div className="flex items-center">
                          <ShoppingBag className="h-4 w-4 mr-2" />
                          Seller - Register medicines and issue QR codes
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <Alert className="mt-2">
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Note:</strong> Admin accounts are created by system administrators only. 
                      Sellers must complete KYC verification after registration.
                    </AlertDescription>
                  </Alert>
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
                  {password && (
                    <div className="mt-2 space-y-1">
                      {isPasswordValid ? (
                        <div className="flex items-center text-sm text-green-600">
                          <CheckCircle2 className="h-4 w-4 mr-2" />
                          Password is valid
                        </div>
                      ) : (
                        <div className="space-y-1">
                          <p className="text-xs font-medium text-muted-foreground">Password must contain:</p>
                          {passwordErrors.map((error) => (
                            <div key={error} className="flex items-center text-xs text-red-600">
                              <AlertCircle className="h-3 w-3 mr-1.5" />
                              {error}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Confirm your password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword((prev) => !prev)}
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-muted-foreground hover:text-foreground"
                      aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex flex-col space-y-4">
                <Button type="submit" className="w-full" disabled={loading || passwordErrors.length > 0}>
                  {loading ? 'Registering...' : 'Register'}
                </Button>
                <div className="text-sm text-center text-muted-foreground">
                  Already have an account?{' '}
                  <Link to="/login" className="text-primary hover:underline">
                    Login
                  </Link>
                </div>
              </CardFooter>
            </form>
          </Card>
        ) : (
          <div className="space-y-4">
            {/* Basic Registration Card for Sellers */}
            <Card className="shadow-2xl border-2 backdrop-blur-md bg-white/95">
              <CardHeader>
                <CardTitle>Account Credentials</CardTitle>
                <CardDescription>Create your login credentials</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Registration Error Alert */}
                {error && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-sm text-red-700 ml-2">
                      {error}
                    </AlertDescription>
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
                  <Label htmlFor="role">Role</Label>
                  <Select value={role} onValueChange={setRole}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="user">
                        <div className="flex items-center">
                          <User className="h-4 w-4 mr-2" />
                          User - Scan and verify medicines
                        </div>
                      </SelectItem>
                      <SelectItem value="seller">
                        <div className="flex items-center">
                          <ShoppingBag className="h-4 w-4 mr-2" />
                          Seller - Register medicines and issue QR codes
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
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
                  {password && (
                    <div className="mt-2 space-y-1">
                      {isPasswordValid ? (
                        <div className="flex items-center text-sm text-green-600">
                          <CheckCircle2 className="h-4 w-4 mr-2" />
                          Password is valid
                        </div>
                      ) : (
                        <div className="space-y-1">
                          <p className="text-xs font-medium text-muted-foreground">Password must contain:</p>
                          {passwordErrors.map((error) => (
                            <div key={error} className="flex items-center text-xs text-red-600">
                              <AlertCircle className="h-3 w-3 mr-1.5" />
                              {error}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Confirm your password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                      className="pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword((prev) => !prev)}
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-muted-foreground hover:text-foreground"
                      aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Seller Registration Form */}
            <SellerRegistrationForm
              formData={sellerFormData}
              onChange={handleSellerFormDataChange}
              onSubmit={handleSubmit}
              loading={loading}
            />
          </div>
        )}
      </div>
      </div>
    </div>
  );
}

