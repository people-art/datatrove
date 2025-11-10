'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { DomainForm } from '@/components/new/DomainForm';
import { benchmarkApi } from '@/lib/api';
import type { DomainFormData } from '@/types';

export default function NewDatasetPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (formData: DomainFormData) => {
    setLoading(true);
    try {
      const response = await benchmarkApi.createJob(formData);
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
