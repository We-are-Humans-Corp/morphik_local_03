# UI Update Guide for Morphik

This guide provides step-by-step instructions for updating the Morphik UI while preserving all custom functionality, especially authentication.

## Prerequisites

- Running Morphik installation with Docker Compose
- Access to GitHub for downloading new UI versions
- Python 3.x installed for auth-service
- Basic understanding of Docker and Next.js

## Table of Contents

1. [Backup Current Configuration](#1-backup-current-configuration)
2. [Download and Prepare New UI Version](#2-download-and-prepare-new-ui-version)
3. [Preserve Authentication Service](#3-preserve-authentication-service)
4. [Update UI Components](#4-update-ui-components)
5. [Restore Custom Integrations](#5-restore-custom-integrations)
6. [Test and Verify](#6-test-and-verify)
7. [Troubleshooting](#7-troubleshooting)

## 1. Backup Current Configuration

Before updating, backup these critical files:

```bash
# Create backup directory
mkdir -p ./backups/$(date +%Y%m%d)

# Backup important files
cp morphik.toml ./backups/$(date +%Y%m%d)/
cp docker-compose.yml ./backups/$(date +%Y%m%d)/
cp .env ./backups/$(date +%Y%m%d)/
cp -r auth-service ./backups/$(date +%Y%m%d)/
cp core/routes/auth.py ./backups/$(date +%Y%m%d)/
```

## 2. Download and Prepare New UI Version

### Step 2.1: Download from GitHub
```bash
# Download specific version (replace v0.4.7 with desired version)
wget https://github.com/morphik-ai/morphik/archive/refs/tags/v0.4.7.tar.gz

# Extract archive
tar -xzf v0.4.7.tar.gz

# Navigate to UI component
cd morphik-0.4.7/ee/ui-component
```

### Step 2.2: Backup Current UI
```bash
# Backup existing UI
mv ee/ui-component ee/ui-component-backup-$(date +%Y%m%d)

# Copy new UI
cp -r morphik-0.4.7/ee/ui-component ./ee/ui-component
```

## 3. Preserve Authentication Service

The authentication service should remain unchanged. Ensure it's running:

### Step 3.1: Verify Auth Service Structure
```
auth-service/
├── login.html       # Login page
├── register.html    # Registration page
├── redirect.html    # Token transfer page
├── index.html       # Landing page
└── server.py        # Python HTTP server
```

### Step 3.2: Start Auth Service
```bash
cd auth-service
python3 server.py
# Server should run on http://localhost:8080
```

## 4. Update UI Components

### Step 4.1: Create Callback Endpoint

Create file `ee/ui-component/app/api/auth/callback/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const token = searchParams.get('token');
  const userStr = searchParams.get('user');
  
  if (!token || !userStr) {
    return NextResponse.redirect('http://localhost:8080/login.html');
  }
  
  try {
    const user = JSON.parse(decodeURIComponent(userStr));
    
    const html = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Setting up...</title>
        <style>
          body {
            font-family: sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }
        </style>
      </head>
      <body>
        <div>Setting up your session...</div>
        <script>
          try {
            const token = ${JSON.stringify(token)};
            const user = ${JSON.stringify(user)};
            
            localStorage.setItem('authToken', token);
            localStorage.setItem('user', JSON.stringify(user));
            document.cookie = 'authToken=' + token + '; path=/; max-age=86400';
            
            setTimeout(() => {
              window.location.href = '/';
            }, 500);
          } catch (error) {
            console.error('Error:', error);
            window.location.href = 'http://localhost:8080/login.html';
          }
        </script>
      </body>
      </html>
    `;
    
    return new NextResponse(html, {
      status: 200,
      headers: {
        'Content-Type': 'text/html',
        'Set-Cookie': `authToken=${token}; Path=/; Max-Age=86400; SameSite=Lax`
      }
    });
  } catch (error) {
    return NextResponse.redirect('http://localhost:8080/login.html');
  }
}
```

### Step 4.2: Update Middleware

Update `ee/ui-component/middleware.ts`:

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname
  const apiPaths = ['/api/']
  const isApiPath = apiPaths.some(p => path.startsWith(p))
  const token = request.cookies.get('authToken')?.value
  
  // Allow API requests
  if (isApiPath) {
    return NextResponse.next()
  }
  
  // Redirect to auth service if no token
  if (!token && path !== '/login' && path !== '/register') {
    return NextResponse.redirect('http://localhost:8080/login.html')
  }
  
  // Redirect login/register to auth service
  if (path === '/login' || path === '/register') {
    const authPath = path === '/login' ? 'login.html' : 'register.html'
    return NextResponse.redirect(`http://localhost:8080/${authPath}`)
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}
```

### Step 4.3: Update MorphikContext

In `ee/ui-component/contexts/morphik-context.tsx`, update:

1. **User Profile Loading**:
```typescript
const [userProfile, setUserProfile] = useState<any>(() => {
  if (typeof window !== "undefined") {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        if (user) {
          return {
            name: user.username || user.name || "User",
            email: user.email || "",
            avatar: user.avatar || "",
            username: user.username || ""
          };
        }
      } catch {
        return null;
      }
    }
  }
  return null;
});
```

2. **Logout Handler**:
```typescript
const onLogout = React.useCallback(() => {
  setAuthToken(null);
  setUserProfile(null);
  if (typeof window !== "undefined") {
    localStorage.removeItem("authToken");
    localStorage.removeItem("user");
    document.cookie = "authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    window.location.href = "http://localhost:8080/login.html";
  }
}, []);
```

### Step 4.4: Remove Built-in Auth Pages

```bash
# Remove default login/register pages
rm -rf ee/ui-component/app/login
rm -rf ee/ui-component/app/register
```

### Step 4.5: Remove Duplicate User Profile

In `ee/ui-component/components/dynamic-site-header.tsx`:
- Remove line containing `<UserProfile />`
- Remove import: `import { UserProfile } from "@/components/user-profile";`

## 5. Restore Custom Integrations

### Step 5.1: Environment Variables

Ensure docker-compose.yml has correct environment variables:

```yaml
ui:
  build:
    context: ./ee/ui-component
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  environment:
    - NEXT_PUBLIC_API_URL=http://localhost:8000
    - INTERNAL_API_URL=http://morphik:8000
    - NODE_ENV=production
  depends_on:
    - morphik
  networks:
    - morphik-network
```

### Step 5.2: Database Connection

Verify PostgreSQL connection in docker-compose.yml:

```yaml
environment:
  - POSTGRES_URI=postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik
```

## 6. Test and Verify

### Step 6.1: Rebuild and Start Services

```bash
# Rebuild UI container
docker-compose build ui

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f ui
```

### Step 6.2: Verification Checklist

- [ ] Open http://localhost:3000 in incognito mode
- [ ] Verify redirect to http://localhost:8080/login.html
- [ ] Register a new user
- [ ] Login with credentials
- [ ] Verify username displays correctly in sidebar
- [ ] Test logout functionality
- [ ] Verify redirect back to login page

### Step 6.3: Debug Page

Create a debug page at `ee/ui-component/app/debug/page.tsx`:

```typescript
"use client";

import { useEffect, useState } from "react";

export default function DebugPage() {
  const [authData, setAuthData] = useState<any>({});

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    const user = localStorage.getItem("user");
    const cookies = document.cookie;
    
    setAuthData({
      token: token ? "EXISTS" : "NOT FOUND",
      user: user ? JSON.parse(user) : "NOT FOUND",
      cookies: cookies || "NO COOKIES"
    });
  }, []);

  return (
    <div style={{ padding: "20px", color: "white" }}>
      <h1>Debug Auth Data</h1>
      <pre>{JSON.stringify(authData, null, 2)}</pre>
      <button onClick={() => {
        localStorage.clear();
        document.cookie.split(";").forEach(c => {
          document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        window.location.reload();
      }}>
        Clear All Auth Data
      </button>
    </div>
  );
}
```

## 7. Troubleshooting

### Common Issues and Solutions

#### Issue: User shows as "Morphik User" instead of actual username
**Solution**: Check localStorage in browser console:
```javascript
console.log(localStorage.getItem('user'));
```
Ensure user data is properly stored after login.

#### Issue: Redirect loop between login pages
**Solution**: 
1. Verify `/login` and `/register` folders are deleted from UI
2. Check middleware.ts redirects
3. Clear browser cache and cookies

#### Issue: Cannot login after UI update
**Solution**:
1. Check auth service is running on port 8080
2. Verify callback endpoint exists
3. Check browser console for errors

#### Issue: Logout doesn't work
**Solution**: Verify logout handler in morphik-context.tsx redirects to correct URL:
```typescript
window.location.href = "http://localhost:8080/login.html";
```

### Useful Commands

```bash
# Check UI logs
docker logs morphik_local-ui-1 --tail 50

# Check auth service
curl http://localhost:8080/login.html

# Test API authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'

# Check PostgreSQL users
docker exec morphik_local-morphik-1 python -c "
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def check_users():
    engine = create_async_engine('postgresql+asyncpg://morphik:morphik@135.181.106.12:5432/morphik')
    async with engine.begin() as conn:
        result = await conn.execute(text('SELECT username, email FROM users'))
        for row in result:
            print(f'Username: {row[0]}, Email: {row[1]}')

asyncio.run(check_users())
"
```

## Summary

This guide ensures smooth UI updates while preserving:
- User authentication system
- Database connections
- Custom configurations
- User sessions and data

Always test in a development environment before applying updates to production.

## Support

For issues or questions, check:
- MORPHIK_CHANGELOG.md for version-specific changes
- Docker logs for runtime errors
- Browser console for client-side issues
- PostgreSQL logs for database issues