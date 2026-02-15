'use client';

import Link from 'next/link';

import { useAuth } from '@/lib/auth/auth-context';

export default function DashboardPage() {
  const { loading, isAuthenticated, user, signOut } = useAuth();

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Loading session...</p>
      </main>
    );
  }

  if (!isAuthenticated) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p>Redirecting to login...</p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col gap-4 px-6 py-12">
      <h1 className="text-3xl font-semibold">Dashboard</h1>
      <p className="text-muted-foreground">
        You are authenticated as <span className="font-medium">{user?.email}</span>.
      </p>

      <div className="flex gap-3">
        <Link href="/" className="rounded border px-3 py-2">
          Home
        </Link>
        <button
          type="button"
          onClick={() => void signOut()}
          className="rounded bg-black px-3 py-2 text-white"
        >
          Sign Out
        </button>
      </div>
    </main>
  );
}
