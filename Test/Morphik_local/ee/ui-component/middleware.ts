import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname
  
  // API paths that should always be accessible
  const apiPaths = ['/api/']
  
  // Check if this is an API path
  const isApiPath = apiPaths.some(p => path.startsWith(p))
  
  // Get the token from cookies
  const token = request.cookies.get('authToken')?.value
  
  // Allow API requests to pass through
  if (isApiPath) {
    return NextResponse.next()
  }
  
  // Redirect to external auth service if no token
  if (!token && path !== '/login' && path !== '/register') {
    // Redirect to external auth service
    return NextResponse.redirect('http://localhost:8080/login.html')
  }
  
  // If user tries to access /login or /register, redirect to external auth
  if (path === '/login' || path === '/register') {
    const authPath = path === '/login' ? 'login.html' : 'register.html'
    return NextResponse.redirect(`http://localhost:8080/${authPath}`)
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}