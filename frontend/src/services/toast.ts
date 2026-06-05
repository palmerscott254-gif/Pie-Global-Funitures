import { toast, Toaster } from 'react-hot-toast';

declare global {
	interface Window {
		pgfToast?: typeof toast;
	}
}

if (typeof window !== 'undefined') {
	window.pgfToast = toast;
}

export const showToastError = (message: string) => {
	return window.pgfToast ? window.pgfToast.error(message) : toast.error(message);
};

export const showToastSuccess = (message: string) => {
	return window.pgfToast ? window.pgfToast.success(message) : toast.success(message);
};

export { toast, Toaster };