export interface StoredAuthUser {
  email?: string;
  name?: string;
  id?: string | number;
  is_staff?: boolean;
  is_superuser?: boolean;
}

const AUTH_CURRENT_KEY = 'pgf-auth-current';
const AUTH_ACCESS_KEY = 'pgf-auth-access';
const AUTH_REFRESH_KEY = 'pgf-auth-refresh';

export const getStoredAuthUser = (): StoredAuthUser | null => {
  if (typeof window === 'undefined') return null;

  try {
    const raw = localStorage.getItem(AUTH_CURRENT_KEY);
    return raw ? (JSON.parse(raw) as StoredAuthUser) : null;
  } catch {
    return null;
  }
};

export const isAdminUser = (user?: StoredAuthUser | null): boolean => {
  const current = user ?? getStoredAuthUser();
  return !!(current?.is_staff || current?.is_superuser);
};

export const clearAuthState = () => {
  if (typeof window === 'undefined') return;

  localStorage.removeItem(AUTH_CURRENT_KEY);
  localStorage.removeItem(AUTH_ACCESS_KEY);
  localStorage.removeItem(AUTH_REFRESH_KEY);
  sessionStorage.removeItem(AUTH_CURRENT_KEY);
  sessionStorage.removeItem(AUTH_ACCESS_KEY);
  sessionStorage.removeItem(AUTH_REFRESH_KEY);
  window.dispatchEvent(new Event('pgf-auth-changed'));
};
