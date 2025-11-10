'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DomainForm } from '@/components/new/DomainForm';
import { benchmarkApi } from '@/lib/api';
import type { DomainFormData } from '@/types';
import type { CreateJobRequest } from '@/lib/api';

export default function NewDatasetPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (formData: DomainFormData) => {
    setLoading(true);
    try {
      // Transform form data to match API expectations
      const apiData = {
        domain: formData.domain,
        keywords: formData.keywords,
        languages: formData.languages,
        time_range: {
          start: formData.timeRange.start,
          end: formData.timeRange.end
        },
        quality_tier: formData.qualityTier,
        estimated_scale: formData.estimatedScale || null,
        email: formData.email
      };

      const response = await benchmarkApi.createJob(apiData as CreateJobRequest);
      router.push("/dashboard");
    } catch (error) {
      console.error('Failed to create benchmark job:', error);
      alert('Failed to create benchmark job. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return <DomainForm onSubmit={handleSubmit} isLoading={loading} />;
}
