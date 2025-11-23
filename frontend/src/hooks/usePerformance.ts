import { useEffect } from 'react';

interface PerformanceMetrics {
  lcp?: number; // Largest Contentful Paint
  fid?: number; // First Input Delay
  cls?: number; // Cumulative Layout Shift
}

export const usePerformanceMonitoring = () => {
  useEffect(() => {
    if ('PerformanceObserver' in window) {
      // Monitor Largest Contentful Paint (LCP)
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as any;
        console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

      // Monitor First Input Delay (FID)
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          console.log('FID:', entry.processingStart - entry.startTime);
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });

      // Monitor Cumulative Layout Shift (CLS)
      let clsScore = 0;
      const clsObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries() as any[]) {
          if (!entry.hadRecentInput) {
            clsScore += entry.value;
            console.log('CLS:', clsScore);
          }
        }
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });

      return () => {
        lcpObserver.disconnect();
        fidObserver.disconnect();
        clsObserver.disconnect();
      };
    }
  }, []);
};

export const reportWebVitals = (onPerfEntry?: (metric: PerformanceMetrics) => void) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    // Web Vitals reporting - optional advanced feature
    // Can be enabled if web-vitals package is installed: npm install web-vitals
    try {
      if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
        console.log('Performance monitoring enabled');
        // Basic performance metrics are already tracked by usePerformanceMonitoring
      }
    } catch (error) {
      console.log('Performance reporting not available');
    }
  }
};
