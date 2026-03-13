import { NextRequest, NextResponse } from 'next/server';

// Define the supported locales
const locales = ['en', 'ur', 'hi'];

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Skip middleware for static files and special paths
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname === '/favicon.ico' ||
    pathname.endsWith('.css') ||
    pathname.endsWith('.js') ||
    pathname.endsWith('.png') ||
    pathname.endsWith('.jpg') ||
    pathname.endsWith('.svg')
  ) {
    return NextResponse.next();
  }

  // Skip middleware for auth pages and root
  const publicPaths = ['/', '/signin', '/signup'];
  if (publicPaths.includes(pathname)) {
    return NextResponse.next();
  }

  // Skip middleware for dashboard
  if (pathname.startsWith('/dashboard')) {
    return NextResponse.next();
  }

  // Check if the request path already has a locale
  const pathnameHasLocale = locales.some(locale => pathname.startsWith(`/${locale}`));
  if (pathnameHasLocale) {
    return NextResponse.next();
  }

  // Get the user's preferred language from headers
  const userPreferredLocale = request.headers.get('accept-language')?.split(',')[0]?.split('-')[0];
  const locale = (userPreferredLocale && locales.includes(userPreferredLocale)) ? userPreferredLocale : 'en';

  // Redirect to localized path
  return NextResponse.redirect(new URL(`/${locale}${pathname}`, request.url));
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|api/).*)',
  ],
};
