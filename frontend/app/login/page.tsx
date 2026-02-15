'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { useAuth } from '@/lib/auth/auth-context';

export default function LoginPage() {
  const router = useRouter();
  const { isConfigured, isAuthenticated, signInWithPassword, signUpWithPassword } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated) return null;

  const handleSignIn = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    const signInError = await signInWithPassword(email, password);
    if (signInError) {
      setError(signInError);
      setLoading(false);
      return;
    }

    setLoading(false);
    router.replace('/dashboard');
  };

  const handleSignUp = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);

    const signUpError = await signUpWithPassword(email, password);
    if (signUpError) {
      setError(signUpError);
      setLoading(false);
      return;
    }

    setLoading(false);
    setMessage('Signup successful. Check your email if confirmation is enabled.');
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col items-center justify-center px-6">
      <div className="w-full space-y-4 rounded-lg border p-6">
        <h1 className="text-2xl font-semibold">Login</h1>
        <p className="text-sm text-muted-foreground">
          Sign in with Supabase email/password.
        </p>

        {!isConfigured && (
          <p className="text-sm text-red-500">
            Supabase frontend env vars are not configured.
          </p>
        )}

        <form className="space-y-3" onSubmit={handleSignIn}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="w-full rounded border px-3 py-2"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="w-full rounded border px-3 py-2"
            required
          />

          {error && <p className="text-sm text-red-500">{error}</p>}
          {message && <p className="text-sm text-green-600">{message}</p>}

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading || !isConfigured}
              className="rounded bg-black px-3 py-2 text-white disabled:opacity-50"
            >
              {loading ? 'Please wait...' : 'Sign In'}
            </button>
            <button
              type="button"
              onClick={handleSignUp}
              disabled={loading || !isConfigured}
              className="rounded border px-3 py-2 disabled:opacity-50"
            >
              Sign Up
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
