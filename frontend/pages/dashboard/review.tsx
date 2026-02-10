import type { NextPage } from 'next';
import Head from 'next/head';
import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Shield, CheckCircle, List, CheckSquare } from 'lucide-react';
import ProtectedRoute from '../../components/ProtectedRoute';
import { lazy, Suspense } from 'react';

// Lazy load the review queue components
const ReviewQueue = lazy(() => import('../../src/components/dashboard/ReviewQueue'));
const BulkReviewQueue = lazy(() => import('../../src/components/dashboard/BulkReviewQueue'));

// Loading skeleton
const ReviewSkeleton = () => (
  <div className="animate-pulse">
    <div className="h-8 bg-slate-200 rounded w-64 mb-6"></div>
    <div className="bg-white rounded-xl shadow-sm border border-slate-200">
      <div className="p-4 border-b bg-slate-50">
        <div className="h-5 bg-slate-200 rounded w-32"></div>
      </div>
      <div className="divide-y">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="p-4">
            <div className="flex justify-between">
              <div className="flex-1">
                <div className="h-3 bg-slate-200 rounded w-3/4 mb-2"></div>
                <div className="h-2 bg-slate-200 rounded w-1/2 mb-2"></div>
                <div className="flex gap-2">
                  <div className="h-4 bg-slate-200 rounded w-16"></div>
                  <div className="h-4 bg-slate-200 rounded w-12"></div>
                </div>
              </div>
              <div className="h-8 bg-slate-200 rounded w-16"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const ReviewPage: NextPage = () => {
  const [activeTab, setActiveTab] = useState<'single' | 'bulk'>('single');

  return (
    <ProtectedRoute requiredRole="analyst">
      <Head>
        <title>Review Queue - Nigeria Conflict Tracker</title>
        <meta name="description" content="Review and verify conflict incidents" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-gradient-to-r from-blue-600 to-blue-700 border-b border-blue-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link 
                  href="/dashboard"
                  className="text-white hover:text-blue-200 transition-colors flex items-center gap-2"
                >
                  <ArrowLeft className="h-5 w-5" />
                  Back to Dashboard
                </Link>
                <div>
                  <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Shield className="h-6 w-6" />
                    Incident Review Queue
                  </h1>
                  <p className="text-blue-100 text-sm mt-1">
                    Verify and authenticate conflict incident reports
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-2 text-white">
                <CheckCircle className="h-5 w-5 text-green-300" />
                <span className="text-sm">Analyst Access</span>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Instructions */}
          <div className="bg-white rounded-lg p-6 mb-8 border border-slate-200">
            <h2 className="text-lg font-semibold text-slate-800 mb-3">Review Guidelines</h2>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600">
              <div>
                <h3 className="font-medium text-slate-700 mb-2">🎯 Priority Order</h3>
                <p>Incidents are sorted by severity (fatalities + kidnappings). Review high-impact incidents first.</p>
              </div>
              <div>
                <h3 className="font-medium text-slate-700 mb-2">✅ Verification Process</h3>
                <p>Click &quot;Verify&quot; for confirmed incidents. This updates the status and logs your action for audit purposes.</p>
              </div>
              <div>
                <h3 className="font-medium text-slate-700 mb-2">🔄 Auto-refresh</h3>
                <p>Queue refreshes every 30 seconds. Numbers update automatically as you verify incidents.</p>
              </div>
              <div>
                <h3 className="font-medium text-slate-700 mb-2">📊 Impact Metrics</h3>
                <p>Each incident shows fatality and kidnapping counts to help prioritize verification efforts.</p>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white rounded-lg border border-slate-200 mb-6">
            <div className="border-b border-slate-200">
              <nav className="flex -mb-px">
                <button
                  onClick={() => setActiveTab('single')}
                  className={`flex items-center gap-2 px-6 py-3 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === 'single'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                  }`}
                >
                  <List className="h-4 w-4" />
                  Single Review
                </button>
                <button
                  onClick={() => setActiveTab('bulk')}
                  className={`flex items-center gap-2 px-6 py-3 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === 'bulk'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                  }`}
                >
                  <CheckSquare className="h-4 w-4" />
                  Bulk Review
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'single' ? (
                <div>
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">Individual Incident Review</h3>
                  <p className="text-sm text-slate-600 mb-6">
                    Review incidents one by one. Ideal for detailed examination of each case.
                  </p>
                  <Suspense fallback={<ReviewSkeleton />}>
                    <ReviewQueue />
                  </Suspense>
                </div>
              ) : (
                <div>
                  <h3 className="text-lg font-semibold text-slate-800 mb-4">Bulk Incident Review</h3>
                  <p className="text-sm text-slate-600 mb-6">
                    Select and verify multiple incidents at once. Perfect for clearing trusted sources or AI-validated items.
                  </p>
                  <Suspense fallback={<ReviewSkeleton />}>
                    <BulkReviewQueue />
                  </Suspense>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
};

export default ReviewPage;
