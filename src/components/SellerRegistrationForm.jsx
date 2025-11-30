import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, Upload, CheckCircle2 } from 'lucide-react';

export default function SellerRegistrationForm({ onSubmit, loading, formData, onChange }) {
  const [documents, setDocuments] = useState([]);

  const requiredFields = [
    'company_name',
    'license_number',
    'license_type',
    'license_expiry',
    'gstin',
    'address',
    'authorized_person',
    'authorized_person_contact',
    'email_company',
  ];

  const isFormComplete = requiredFields.every(field => formData[field]?.trim());

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files || []);
    setDocuments(files);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!isFormComplete) {
      alert('Please fill in all required fields');
      return;
    }

    const formDataToSend = new FormData();
    
    // Add basic auth data
    Object.keys(formData).forEach(key => {
      if (formData[key]) {
        formDataToSend.append(key, formData[key]);
      }
    });

    // Add documents
    documents.forEach((doc, index) => {
      formDataToSend.append(`document_${index}`, doc);
    });

    onSubmit(formDataToSend);
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Company Registration Details</CardTitle>
        <CardDescription>Complete all fields for admin verification</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          <Alert className="border-blue-200 bg-blue-50">
            <AlertCircle className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-sm text-blue-700">
              Your seller application will be verified by our admin team. You can login only after approval.
            </AlertDescription>
          </Alert>

          {/* Company Information Section */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="font-semibold">Company Information</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="company_name">Company Name *</Label>
                <Input
                  id="company_name"
                  placeholder="Enter company name"
                  value={formData.company_name || ''}
                  onChange={(e) => onChange('company_name', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="license_number">Drug License Number *</Label>
                <Input
                  id="license_number"
                  placeholder="Enter license number"
                  value={formData.license_number || ''}
                  onChange={(e) => onChange('license_number', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="license_type">License Type *</Label>
                <Input
                  id="license_type"
                  placeholder="e.g., Wholesale, Retail, Manufacturing"
                  value={formData.license_type || ''}
                  onChange={(e) => onChange('license_type', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="license_expiry">License Expiry Date *</Label>
                <Input
                  id="license_expiry"
                  type="date"
                  value={formData.license_expiry || ''}
                  onChange={(e) => onChange('license_expiry', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="gstin">GSTIN (GST Identification Number) *</Label>
                <Input
                  id="gstin"
                  placeholder="15-digit GSTIN"
                  value={formData.gstin || ''}
                  onChange={(e) => onChange('gstin', e.target.value)}
                  maxLength="15"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email_company">Official Company Email *</Label>
                <Input
                  id="email_company"
                  type="email"
                  placeholder="company@example.com"
                  value={formData.email_company || ''}
                  onChange={(e) => onChange('email_company', e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Registered Company Address *</Label>
              <Textarea
                id="address"
                placeholder="Enter full company address"
                value={formData.address || ''}
                onChange={(e) => onChange('address', e.target.value)}
                required
                className="h-20"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="company_website">Company Website (Optional)</Label>
              <Input
                id="company_website"
                type="url"
                placeholder="https://example.com"
                value={formData.company_website || ''}
                onChange={(e) => onChange('company_website', e.target.value)}
              />
            </div>
          </div>

          {/* Authorized Person Section */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="font-semibold">Authorized Person</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="authorized_person">Authorized Person Name *</Label>
                <Input
                  id="authorized_person"
                  placeholder="Full name"
                  value={formData.authorized_person || ''}
                  onChange={(e) => onChange('authorized_person', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="authorized_person_contact">Contact Number *</Label>
                <Input
                  id="authorized_person_contact"
                  type="tel"
                  placeholder="10-digit phone number"
                  value={formData.authorized_person_contact || ''}
                  onChange={(e) => onChange('authorized_person_contact', e.target.value)}
                  maxLength="10"
                  required
                />
              </div>
            </div>
          </div>

          {/* Documents Section */}
          <div className="space-y-4 border-t pt-4">
            <h3 className="font-semibold">Verification Documents</h3>
            <p className="text-sm text-muted-foreground">
              Upload scans/copies of your drug license, GST certificate, and business registration
            </p>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
              <Input
                id="documents"
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={handleFileChange}
                className="cursor-pointer text-center"
              />
              {documents.length > 0 && (
                <div className="mt-3 text-sm">
                  <p className="text-green-600 font-medium">{documents.length} file(s) selected</p>
                  {documents.map((doc, idx) => (
                    <p key={idx} className="text-xs text-muted-foreground">{doc.name}</p>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Completion Status */}
          <div className="border-t pt-4">
            {isFormComplete ? (
              <div className="flex items-center text-sm text-green-600">
                <CheckCircle2 className="h-5 w-5 mr-2" />
                All required fields completed
              </div>
            ) : (
              <div className="flex items-center text-sm text-amber-600">
                <AlertCircle className="h-5 w-5 mr-2" />
                Please fill in all required fields (marked with *)
              </div>
            )}
          </div>
        </CardContent>

        <div className="px-6 py-4 border-t bg-gray-50 flex justify-end">
          <Button 
            type="submit" 
            disabled={!isFormComplete || loading}
            className="w-full md:w-auto"
          >
            {loading ? 'Registering...' : 'Complete Registration'}
          </Button>
        </div>
      </form>
    </Card>
  );
}
