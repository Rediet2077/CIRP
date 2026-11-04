'use client';

import { useEffect, useState } from 'react';

/**
 * Hook to prevent hydration mismatches by ensuring component only renders on client
 * Use this when you need browser-only APIs like window, localStorage, etc.
 */
export function useClientOnly() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return isClient;
}

/**
 * Component wrapper to prevent hydration mismatches
 * Renders children only on client side after hydration
 */
export function ClientOnly({ children }: { children: React.ReactNode }) {
  const isClient = useClientOnly();

  if (!isClient) {
    return null;
  }

  return <>{children}</>;
}
