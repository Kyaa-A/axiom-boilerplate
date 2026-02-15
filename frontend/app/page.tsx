import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-4">
          AI Boilerplate
        </h1>
        <p className="text-center text-muted-foreground">
          Production-ready full-stack AI application foundation
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link href="/login" className="underline">
            Login
          </Link>
          <Link href="/dashboard" className="underline">
            Dashboard
          </Link>
        </div>
      </div>
    </main>
  );
}
