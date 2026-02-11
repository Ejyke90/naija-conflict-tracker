import type { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';
import Head from 'next/head';
import { AuthProvider } from '@/contexts/AuthContext';
import ErrorBoundary from '@/components/ErrorBoundary';
import 'mapbox-gl/dist/mapbox-gl.css';
import '../styles/globals.css';
import '../styles/map.css';
import 'leaflet/dist/leaflet.css';

function MyApp({ Component, pageProps }: AppProps) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
    },
  }));

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <Head>
            {/* Font preloading for tactical theme */}
            <link 
              rel="preload" 
              href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" 
              as="style" 
              crossOrigin="anonymous"
            />
            <link 
              rel="preload" 
              href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" 
              as="style" 
              crossOrigin="anonymous"
            />
            <link 
              href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" 
              rel="stylesheet"
            />
            <link 
              href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" 
              rel="stylesheet"
            />
          </Head>
          {/* Skip to main content link for keyboard navigation */}
          <a 
            href="#main-content" 
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-tactical-slate-dark focus:text-tactical-e-ink focus:rounded-md focus:shadow-lg"
          >
            Skip to main content
          </a>
          <Component {...pageProps} />
          {process.env.NODE_ENV === 'development' && (
            <ReactQueryDevtools initialIsOpen={false} />
          )}
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default MyApp;
