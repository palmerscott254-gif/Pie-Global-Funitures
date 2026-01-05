import React, { Component, ReactNode } from 'react';
import { motion } from 'framer-motion';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    // Log error details for debugging
    console.error('Error stack:', error.stack);
    console.error('Component stack:', errorInfo.componentStack);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-50"
        >
          <div className="text-center p-8 bg-white rounded-2xl shadow-xl max-w-md">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200 }}
              className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <span className="text-4xl">⚠️</span>
            </motion.div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">Oops! Something went wrong</h1>
            <p className="text-gray-600 mb-4">
              We're sorry for the inconvenience. Please refresh the page or try again later.
            </p>
            {this.state.error && (
              <details className="mb-4 text-left bg-gray-50 p-3 rounded text-xs max-h-40 overflow-auto">
                <summary className="font-semibold cursor-pointer text-gray-700 mb-2">
                  Error Details (for debugging)
                </summary>
                <p className="text-red-600 font-mono break-all">
                  {this.state.error.message}
                </p>
              </details>
            )}
            <button
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              Refresh Page
            </button>
          </div>
        </motion.div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
