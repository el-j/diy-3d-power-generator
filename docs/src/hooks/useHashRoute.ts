import { useState, useEffect } from 'react';

export type RouteId = 'home' | 'playground' | 'docs' | 'build-guide' | 'bom' | 'downloads';

function parse(hash: string): RouteId {
  const h = hash.replace(/^#\/?/, '').trim().toLowerCase();
  if (h === 'playground') return 'playground';
  if (h === 'docs') return 'docs';
  if (h === 'build-guide') return 'build-guide';
  if (h === 'bom') return 'bom';
  if (h === 'downloads') return 'downloads';
  return 'home';
}

export function useHashRoute(): [RouteId, (r: RouteId) => void] {
  const [route, setRoute] = useState<RouteId>(() => parse(location.hash));

  useEffect(() => {
    const onHash = () => setRoute(parse(location.hash));
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  function navigate(r: RouteId): void {
    location.hash = r === 'home' ? '/' : `/${r}`;
  }

  return [route, navigate];
}
