import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const token = searchParams.get('token');
  const userStr = searchParams.get('user');
  
  console.log('Callback received:', { token: token ? 'EXISTS' : 'MISSING', user: userStr ? 'EXISTS' : 'MISSING' });
  
  if (!token || !userStr) {
    console.error('Missing token or user data');
    return NextResponse.redirect('http://localhost:8080/login.html');
  }
  
  try {
    const user = JSON.parse(decodeURIComponent(userStr));
    console.log('Parsed user:', user);
    
    // Create HTML page that sets localStorage and redirects
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
          .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            text-align: center;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <h2>Setting up your session...</h2>
          <p>Please wait...</p>
        </div>
        <script>
          try {
            // Set auth data in localStorage
            const token = ${JSON.stringify(token)};
            const user = ${JSON.stringify(user)};
            
            localStorage.setItem('authToken', token);
            localStorage.setItem('user', JSON.stringify(user));
            
            // Set cookie
            document.cookie = 'authToken=' + token + '; path=/; max-age=86400';
            
            console.log('Auth data set successfully');
            
            // Redirect to home
            setTimeout(() => {
              window.location.href = '/';
            }, 500);
          } catch (error) {
            console.error('Error setting auth data:', error);
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
    console.error('Callback error:', error);
    return NextResponse.redirect('http://localhost:8080/login.html');
  }
}