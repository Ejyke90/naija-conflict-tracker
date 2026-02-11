/**
 * Next.js Middleware for Emergency Demo Mode
 * 
 * In demo mode, skip all auth checks and redirect login/register pages to dashboard
 */

import { NextRequest, NextResponse } from 'next/server';

// Emergency Demo Mode - Force authentication for demo
const DEMO_MODE = true;

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // In demo mode, redirect auth pages to dashboard
  if (DEMO_MODE) {
    if (pathname === '/login' || pathname === '/register' || pathname === '/request-access') {
      const url = request.nextUrl.clone();
      url.pathname = '/dashboard';
      return NextResponse.redirect(url);
    }
  }

  // For non-demo mode, you could add normal auth middleware logic here
  // For now, just continue with the request

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public (public files)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|public).*)',
  ],
};
