import { cn, getStatusLabel } from '@/lib/utils';
import type { ProgressBarProps } from '@/types';

export function ProgressBar({ status, progress = 0 }: ProgressBarProps) {
  const statusColors = {
    queued: 'bg-yellow-500',
    running: 'bg-blue-500',
    ready: 'bg-green-500',
    failed: 'bg-red-500',
  };

  const statusLabels = {
    queued: 'Queued',
    running: 'Processing',
    ready: 'Complete',
    failed: 'Failed',
  };

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm font-medium text-gray-700">
          {statusLabels[status]}
        </span>
        <span className="text-sm text-gray-500">
          {status === 'running' ? `${Math.round(progress)}%` : ''}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={cn(
            "h-2 rounded-full transition-all duration-500",
            statusColors[status]
          )}
          style={{
            width: status === 'running' ? `${progress}%` : status === 'ready' ? '100%' : '0%'
          }}
        />
      </div>
    </div>
  );
}
