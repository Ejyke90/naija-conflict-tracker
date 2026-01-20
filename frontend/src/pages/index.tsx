import React from 'react';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ConflictDashboard } from '@/components/dashboard/ConflictDashboard';

export default function Home() {
  return (
    <DashboardLayout>
      <ConflictDashboard />
    </DashboardLayout>
  );
}
