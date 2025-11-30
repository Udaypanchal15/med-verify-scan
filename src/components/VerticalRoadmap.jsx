import { CheckCircle2, Clock, AlertCircle, XCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

/**
 * VerticalRoadmap Component
 * 
 * Displays seller application status in a vertical timeline format.
 * Shows steps: submitted -> viewed -> verifying -> approved/rejected
 * 
 * Props:
 * - status: 'pending' | 'viewed' | 'verifying' | 'approved' | 'rejected' | 'changes_required'
 * - submittedAt: ISO date string
 * - viewedAt: ISO date string (optional)
 * - verifyingAt: ISO date string (optional)
 * - approvedAt: ISO date string (optional)
 * - rejectedAt: ISO date string (optional)
 * - adminRemarks: string (optional)
 * - requiredChanges: [{field: string, message: string}] (optional)
 */

const STEPS = [
  {
    id: 'submitted',
    label: 'Application Submitted',
    description: 'Your application has been received',
  },
  {
    id: 'viewed',
    label: 'Admin Reviewed',
    description: 'Admin has viewed your application',
  },
  {
    id: 'verifying',
    label: 'Verifying Documents',
    description: 'Admin is verifying your documents',
  },
  {
    id: 'approved',
    label: 'Application Approved',
    description: 'You are now a verified seller',
  },
];

const TERMINAL_STEPS = {
  rejected: {
    label: 'Application Rejected',
    description: 'Your application was not approved',
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
  },
  changes_required: {
    label: 'Changes Required',
    description: 'Please update the required fields',
    icon: AlertCircle,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
  },
};

const STATUS_TIMESTAMPS = {
  pending: 'submittedAt',
  viewed: 'viewedAt',
  verifying: 'verifyingAt',
  approved: 'approvedAt',
  rejected: 'rejectedAt',
  changes_required: 'requiredChangesAt',
};

const getStepStatus = (stepId, currentStatus) => {
  // "Application Submitted" is ALWAYS completed if the application exists
  if (stepId === 'submitted') return 'completed';

  const steps = ['submitted', 'viewed', 'verifying', 'approved'];
  const statusMap = {
    'pending': 'submitted',
    'viewed': 'viewed',
    'verifying': 'verifying',
    'approved': 'approved',
    'rejected': 'verifying', // Show progress up to verifying before rejection
    'changes_required': 'viewed' // Show progress up to viewed before changes requested
  };

  const mappedStatus = statusMap[currentStatus] || 'submitted';
  const currentIndex = steps.indexOf(mappedStatus);
  const stepIndex = steps.indexOf(stepId);

  if (stepIndex < currentIndex) return 'completed';
  if (stepIndex === currentIndex) return 'current';
  return 'pending';
};

const formatDate = (dateString) => {
  if (!dateString) return null;
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const formatTime = (dateString) => {
  if (!dateString) return null;
  const date = new Date(dateString);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

const StepIcon = ({ status }) => {
  if (status === 'completed') {
    return <CheckCircle2 className="h-8 w-8 text-green-600" />;
  }
  if (status === 'current') {
    return <Clock className="h-8 w-8 text-blue-600 animate-spin" />;
  }
  return <div className="h-8 w-8 rounded-full border-2 border-gray-300" />;
};

export function VerticalRoadmap({
  status,
  submittedAt,
  viewedAt,
  verifyingAt,
  approvedAt,
  rejectedAt,
  adminRemarks,
  requiredChanges,
}) {
  const isTerminal = ['rejected', 'approved'].includes(status);
  const timestamps = {
    submittedAt,
    viewedAt,
    verifyingAt,
    approvedAt,
    rejectedAt,
  };

  return (
    <div className="space-y-8">
      {/* Main Timeline */}
      <div className="space-y-0">
        {STEPS.map((step, idx) => {
          const stepStatus = getStepStatus(step.id, status);
          const timestamp = timestamps[STATUS_TIMESTAMPS[step.id]];
          const isLast = idx === STEPS.length - 1;

          return (
            <div key={step.id} className="flex gap-6">
              {/* Timeline Column */}
              <div className="flex flex-col items-center">
                {/* Icon */}
                <StepIcon status={stepStatus} />

                {/* Connector Line */}
                {!isLast && (
                  <div
                    className={`w-1 h-16 my-2 ${
                      stepStatus === 'completed' ? 'bg-green-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>

              {/* Content Column */}
              <div className="flex-1 pt-1 pb-6">
                <Card
                  className={`${
                    stepStatus === 'current' ? 'border-blue-300 bg-blue-50' : ''
                  } ${stepStatus === 'completed' ? 'border-green-300 bg-green-50' : ''}`}
                >
                  <CardContent className="pt-4">
                    <h3 className="font-semibold text-lg">{step.label}</h3>
                    <p className="text-sm text-muted-foreground">{step.description}</p>
                    {timestamp && (
                      <div className="mt-2 text-xs text-gray-500">
                        <p>{formatDate(timestamp)}</p>
                        {formatTime(timestamp) && <p>{formatTime(timestamp)}</p>}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          );
        })}
      </div>

      {/* Terminal Status (Rejected/Changes Required) */}
      {status === 'rejected' || status === 'changes_required' ? (
        <div className="flex gap-6">
          <div className="flex flex-col items-center">
            {status === 'rejected' ? (
              <XCircle className="h-8 w-8 text-red-600" />
            ) : (
              <AlertCircle className="h-8 w-8 text-amber-600" />
            )}
          </div>

          <div className="flex-1 pt-1">
            <Card
              className={
                status === 'rejected'
                  ? 'border-red-300 bg-red-50'
                  : 'border-amber-300 bg-amber-50'
              }
            >
              <CardContent className="pt-4">
                <h3 className="font-semibold text-lg">
                  {status === 'rejected'
                    ? 'Application Rejected'
                    : 'Changes Required'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {status === 'rejected'
                    ? 'Your application was not approved at this time'
                    : 'Please address the required changes and resubmit'}
                </p>

                {rejectedAt && (
                  <div className="mt-2 text-xs text-gray-500">
                    <p>{formatDate(rejectedAt)}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      ) : null}

      {/* Admin Remarks */}
      {adminRemarks && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-4">
            <h4 className="font-semibold mb-2">Admin Remarks</h4>
            <p className="text-sm text-gray-700">{adminRemarks}</p>
          </CardContent>
        </Card>
      )}

      {/* Required Changes List */}
      {requiredChanges && requiredChanges.length > 0 && (
        <Card className="border-amber-200 bg-amber-50">
          <CardContent className="pt-4">
            <h4 className="font-semibold mb-3">Required Changes</h4>
            <ul className="space-y-2">
              {requiredChanges.map((change, idx) => (
                <li key={idx} className="flex gap-2">
                  <AlertCircle className="h-4 w-4 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {change.field}
                    </p>
                    <p className="text-sm text-gray-700">{change.message}</p>
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Status Legend */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-green-600" />
          <span className="text-sm">Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-blue-600" />
          <span className="text-sm">In Progress</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
          <span className="text-sm">Pending</span>
        </div>
      </div>
    </div>
  );
}
