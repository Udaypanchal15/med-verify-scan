import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';

export const UnverifiedMedicineWarning = ({ medicine }) => {
  return (
    <Card className="bg-yellow-50 border-yellow-400">
      <CardContent className="pt-6">
        <div className="flex gap-4">
          <div className="flex-shrink-0">
            <AlertTriangle className="h-6 w-6 text-yellow-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-yellow-900 mb-2">
              ⚠️ Unverified Medicine
            </h3>
            <p className="text-yellow-800 mb-4">
              This medicine has not been verified by our platform. It may be authentic, but we cannot confirm its authenticity through our verification system.
            </p>
            <div className="bg-white p-3 rounded mb-4">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-gray-500">Medicine Name</p>
                  <p className="font-semibold">{medicine?.name || 'Unknown'}</p>
                </div>
                <div>
                  <p className="text-gray-500">Batch Number</p>
                  <p className="font-semibold">{medicine?.batch_no || 'Unknown'}</p>
                </div>
                {medicine?.mfg_date && (
                  <div>
                    <p className="text-gray-500">Mfg Date</p>
                    <p className="font-semibold">{medicine.mfg_date}</p>
                  </div>
                )}
                {medicine?.expiry_date && (
                  <div>
                    <p className="text-gray-500">Expiry Date</p>
                    <p className="font-semibold">{medicine.expiry_date}</p>
                  </div>
                )}
              </div>
            </div>
            <div className="bg-yellow-100 p-3 rounded">
              <p className="text-sm text-yellow-900">
                <strong>⚠️ Use at your own risk.</strong> We recommend:
              </p>
              <ul className="text-sm text-yellow-900 mt-2 list-disc list-inside space-y-1">
                <li>Verify with the manufacturer directly</li>
                <li>Check the physical packaging and batch number</li>
                <li>Consult a healthcare professional</li>
                <li>Report suspicious medicines to the authorities</li>
              </ul>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
