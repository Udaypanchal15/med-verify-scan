import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { Navigation } from '@/components/Navigation';
import { getAccessToken } from '@/lib/auth';
import { Upload, CheckCircle2, AlertCircle, Building2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// Allowed file types and max size
const ALLOWED_FILE_TYPES = ['application/pdf', 'image/png', 'image/jpeg'];
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB per file
const MAX_FILES = 5;

export default function SellerApply() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState([]);
  const [fileErrors, setFileErrors] = useState({});

  const [formData, setFormData] = useState({
    company_name: '',
    license_number: '',
    license_type: '',
    license_expiry: '',
    gstin: '',
    address: '',
    authorized_person: '',
    authorized_person_contact: '',
    email_company: '',
  });

  const [errors, setErrors] = useState({});

  // Client-side validation
  const validateForm = () => {
    const newErrors = {};

    if (!formData.company_name.trim()) newErrors.company_name = 'Company name is required';
    if (!formData.license_number.trim()) newErrors.license_number = 'License number is required';
    if (!formData.license_type.trim()) newErrors.license_type = 'License type is required';
    if (!formData.license_expiry) newErrors.license_expiry = 'License expiry date is required';
    
    // Validate expiry is in future
    if (formData.license_expiry) {
      const expiryDate = new Date(formData.license_expiry);
      if (expiryDate <= new Date()) {
        newErrors.license_expiry = 'License expiry must be in the future';
      }
    }

    if (!formData.gstin.trim()) newErrors.gstin = 'GSTIN is required';
    if (!formData.address.trim()) newErrors.address = 'Address is required';
    if (!formData.authorized_person.trim()) newErrors.authorized_person = 'Authorized person name is required';
    if (!formData.authorized_person_contact.trim()) newErrors.authorized_person_contact = 'Contact is required';

    // Phone validation (basic)
    if (formData.authorized_person_contact && !/^\d{10,}$/.test(formData.authorized_person_contact.replace(/\D/g, ''))) {
      newErrors.authorized_person_contact = 'Invalid phone number';
    }

    if (files.length === 0) newErrors.files = 'At least one document is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    const newErrors = {};

    if (selectedFiles.length + files.length > MAX_FILES) {
      newErrors.upload = `Maximum ${MAX_FILES} files allowed`;
      setFileErrors(newErrors);
      toast({
        title: 'Error',
        description: `Maximum ${MAX_FILES} files allowed`,
        variant: 'destructive',
      });
      return;
    }

    selectedFiles.forEach((file, idx) => {
      if (!ALLOWED_FILE_TYPES.includes(file.type)) {
        newErrors[idx] = 'Only PDF, PNG, and JPEG files allowed';
      }
      if (file.size > MAX_FILE_SIZE) {
        newErrors[idx] = `File size must be less than 5MB`;
      }
    });

    if (Object.keys(newErrors).length > 0) {
      setFileErrors(newErrors);
      toast({
        title: 'File Error',
        description: 'Some files failed validation',
        variant: 'destructive',
      });
      return;
    }

    setFiles([...files, ...selectedFiles]);
    setFileErrors({});
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      toast({
        title: 'Validation Error',
        description: 'Please fill all required fields correctly',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);

    try {
      // Create FormData for multipart submission
      const submitData = new FormData();
      submitData.append('company_name', formData.company_name);
      submitData.append('license_number', formData.license_number);
      submitData.append('license_type', formData.license_type);
      submitData.append('license_expiry', formData.license_expiry);
      submitData.append('gstin', formData.gstin);
      submitData.append('address', formData.address);
      submitData.append('authorized_person', formData.authorized_person);
      submitData.append('authorized_person_contact', formData.authorized_person_contact);
      submitData.append('email_company', formData.email_company);

      // Append files
      files.forEach((file) => {
        submitData.append('documents', file);
      });

      const token = getAccessToken();
      if (!token) {
        throw new Error('Not authenticated. Please login again.');
      }

      const response = await fetch(`${API_BASE_URL}/seller/apply`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: submitData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Registration failed');
      }

      const result = await response.json();

      toast({
        title: 'Success',
        description: 'Registration submitted — please login to check status',
      });

      // Redirect to seller status page
      navigate('/seller/status');
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to submit registration',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: '',
      }));
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-4xl mx-auto p-4 pt-20 pb-10">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Building2 className="h-6 w-6" />
              <div>
                <CardTitle className="text-2xl">Seller Registration</CardTitle>
                <CardDescription>Complete your seller application and get verified</CardDescription>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Company Information Section */}
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Company Information</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="company_name">Company Name *</Label>
                    <Input
                      id="company_name"
                      placeholder="Your company name"
                      value={formData.company_name}
                      onChange={(e) => handleInputChange('company_name', e.target.value)}
                      className={errors.company_name ? 'border-red-500' : ''}
                    />
                    {errors.company_name && (
                      <p className="text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.company_name}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="license_number">License Number *</Label>
                    <Input
                      id="license_number"
                      placeholder="License number"
                      value={formData.license_number}
                      onChange={(e) => handleInputChange('license_number', e.target.value)}
                      className={errors.license_number ? 'border-red-500' : ''}
                    />
                    {errors.license_number && (
                      <p className="text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.license_number}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="license_type">License Type *</Label>
                    <select
                      id="license_type"
                      value={formData.license_type}
                      onChange={(e) => handleInputChange('license_type', e.target.value)}
                      className={`w-full px-3 py-2 border rounded-md text-sm ${
                        errors.license_type ? 'border-red-500' : 'border-gray-300'
                      }`}
                    >
                      <option value="">Select license type</option>
                      <option value="wholesale">Wholesale</option>
                      <option value="retail">Retail</option>
                      <option value="distribution">Distribution</option>
                      <option value="manufacturer">Manufacturer</option>
                    </select>
                    {errors.license_type && (
                      <p className="text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.license_type}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="license_expiry">License Expiry Date *</Label>
                    <Input
                      id="license_expiry"
                      type="date"
                      value={formData.license_expiry}
                      onChange={(e) => handleInputChange('license_expiry', e.target.value)}
                      className={errors.license_expiry ? 'border-red-500' : ''}
                    />
                    {errors.license_expiry && (
                      <p className="text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.license_expiry}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="gstin">GSTIN *</Label>
                    <Input
                      id="gstin"
                      placeholder="15-digit GSTIN"
                      value={formData.gstin}
                      onChange={(e) => handleInputChange('gstin', e.target.value)}
                      className={errors.gstin ? 'border-red-500' : ''}
                    />
                    {errors.gstin && (
                      <p className="text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.gstin}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email_company">Company Email</Label>
                    <Input
                      id="email_company"
                      type="email"
                      placeholder="company@example.com"
                      value={formData.email_company}
                      onChange={(e) => handleInputChange('email_company', e.target.value)}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Address *</Label>
                  <Textarea
                    id="address"
                    placeholder="Full company address"
                    value={formData.address}
                    onChange={(e) => handleInputChange('address', e.target.value)}
                    className={`${errors.address ? 'border-red-500' : ''} h-20`}
                  />
                  {errors.address && (
                    <p className="text-sm text-red-600 flex items-center gap-1">
                      <AlertCircle className="h-4 w-4" />
                      {errors.address}
                    </p>
                  )}
                </div>
              </div>

              {/* Authorized Person Section */}
              <div className="space-y-6 pt-6 border-t">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Authorized Person</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="authorized_person">Name *</Label>
                    <Input
                      id="authorized_person"
                      placeholder="Full name"
                      value={formData.authorized_person}
                      onChange={(e) => handleInputChange('authorized_person', e.target.value)}
                      className={errors.authorized_person ? 'border-red-500' : ''}
                    />
                    {errors.authorized_person && (
                      <p className="text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.authorized_person}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="authorized_person_contact">Contact Number *</Label>
                    <Input
                      id="authorized_person_contact"
                      type="tel"
                      placeholder="10-digit phone number"
                      value={formData.authorized_person_contact}
                      onChange={(e) => handleInputChange('authorized_person_contact', e.target.value)}
                      className={errors.authorized_person_contact ? 'border-red-500' : ''}
                    />
                    {errors.authorized_person_contact && (
                      <p className="text-sm text-red-600 flex items-center gap-1">
                        <AlertCircle className="h-4 w-4" />
                        {errors.authorized_person_contact}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Document Upload Section */}
              <div className="space-y-6 pt-6 border-t">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Documents *</h3>
                  <p className="text-sm text-muted-foreground">
                    Upload license copy, GSTIN certificate, and any other relevant documents (PDF, PNG, JPEG max 5MB each, max 5 files)
                  </p>
                </div>

                {fileErrors.upload && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-700 ml-2">
                      {fileErrors.upload}
                    </AlertDescription>
                  </Alert>
                )}

                {errors.files && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-700 ml-2">
                      {errors.files}
                    </AlertDescription>
                  </Alert>
                )}

                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                  <label className="cursor-pointer flex flex-col items-center justify-center">
                    <Upload className="h-8 w-8 text-gray-400 mb-2" />
                    <span className="text-sm font-medium">Click to upload or drag and drop</span>
                    <span className="text-xs text-gray-500">PNG, JPEG, PDF up to 5MB</span>
                    <input
                      type="file"
                      multiple
                      accept=".pdf,.png,.jpg,.jpeg"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                </div>

                {files.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Selected files ({files.length}/{MAX_FILES})</p>
                    <div className="space-y-1">
                      {files.map((file, idx) => (
                        <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="text-sm truncate">{file.name}</span>
                          <button
                            type="button"
                            onClick={() => removeFile(idx)}
                            className="text-red-600 hover:text-red-700 text-sm font-medium"
                          >
                            Remove
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Terms and Submit */}
              <div className="space-y-4 pt-6 border-t">
                <Alert>
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertDescription className="ml-2">
                    Your information will be verified by our admin team within 2-3 business days.
                  </AlertDescription>
                </Alert>

                <div className="flex gap-4">
                  <Button
                    type="submit"
                    disabled={loading}
                    size="lg"
                    className="flex-1"
                  >
                    {loading ? 'Submitting...' : 'Submit Application'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="lg"
                    onClick={() => navigate('/login')}
                    disabled={loading}
                  >
                    Back to Login
                  </Button>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
