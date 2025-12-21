import { useState, useEffect, useRef, RefObject } from 'react';

// Throttled scroll position reader to reduce re-renders on scroll-heavy pages
export function useScrollPosition(throttleMs = 50) {
  const [scrollY, setScrollY] = useState(0);
  const ticking = useRef(false);
  const lastUpdate = useRef(0);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleScroll = () => {
      const now = performance.now();
      if (ticking.current || now - lastUpdate.current < throttleMs) return;
      ticking.current = true;

      requestAnimationFrame(() => {
        setScrollY(window.scrollY);
        lastUpdate.current = performance.now();
        ticking.current = false;
      });
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [throttleMs]);

  return scrollY;
}

// Detect clicks outside a ref to close popovers/menus
export function useOnClickOutside(
  ref: RefObject<HTMLElement>,
  handler: () => void
) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }
      handler();
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}

export { default as useSEO } from './useSEO';

