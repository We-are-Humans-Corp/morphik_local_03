'use client';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    try {
      const token = searchParams.get('token');
      const user_id = searchParams.get('user_id');
      const username = searchParams.get('username');

      if (token && user_id && username) {
        // Save to localStorage with CORRECT keys that UI expects
        localStorage.setItem('morphik-auth-token', token);  // Changed from morphik_token
        localStorage.setItem('morphik-user-profile', JSON.stringify({
          id: user_id,
          username: username,
          email: `${username}@morphik.local`
        }));
        
        console.log('✅ Auth success:', { user_id, username });
        setStatus('success');

        setTimeout(() => {
          router.push('/');
        }, 1000);
      } else {
        console.error('❌ Missing auth data');
        setStatus('error');
        setTimeout(() => {
          window.location.href = 'http://localhost:8000/login';
        }, 2000);
      }
    } catch (error) {
      console.error('❌ Callback error:', error);
      setStatus('error');
    }
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center p-8">
        {status === 'loading' && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p>Completing authentication...</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="text-green-500 text-6xl mb-4">✅</div>
            <p className="text-green-600">Login successful! Redirecting...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="text-red-500 text-6xl mb-4">❌</div>
            <p className="text-red-600">Login failed. Redirecting to login...</p>
          </>
        )}
      </div>
    </div>
  );
}
