/* eslint-disable @next/next/no-img-element */
import React from 'react';
import { HeroSection } from './HeroSection';
import { LivePulse } from './LivePulse';
import { HowItWorks } from './HowItWorks';
import { DashboardPeek } from './DashboardPeek';

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900">
      <HeroSection />
      <LivePulse />
      <HowItWorks />
      <DashboardPeek />
    </div>
  );
};

export default LandingPage;
