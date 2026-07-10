import { useState, useEffect } from 'react';
import { Provider } from '@/constants/messages';

interface UseAuthReturn {
  membApiKey: string;
  openaiApiKey: string;
  provider: Provider;
  user: string;
  setAuth: (memb: string, openai: string, provider: Provider) => void;
  setUser: (user: string) => void;
  clearAuth: () => void;
  clearUser: () => void;
}

export const useAuth = (): UseAuthReturn => {
  const [membApiKey, setMemBApiKey] = useState<string>('');
  const [openaiApiKey, setOpenaiApiKey] = useState<string>('');
  const [provider, setProvider] = useState<Provider>('openai');
  const [user, setUser] = useState<string>('');

  useEffect(() => {
    const memb = localStorage.getItem('membApiKey');
    const openai = localStorage.getItem('openaiApiKey');
    const savedProvider = localStorage.getItem('provider') as Provider;
    const savedUser = localStorage.getItem('user');

    if (memb && openai && savedProvider) {
      setAuth(memb, openai, savedProvider);
    }
    if (savedUser) {
      setUser(savedUser);
    }
  }, []);

  const setAuth = (memb: string, openai: string, provider: Provider) => {
    setMemBApiKey(memb);
    setOpenaiApiKey(openai);
    setProvider(provider);
    localStorage.setItem('membApiKey', memb);
    localStorage.setItem('openaiApiKey', openai);
    localStorage.setItem('provider', provider);
  };

  const clearAuth = () => {
    localStorage.removeItem('membApiKey');
    localStorage.removeItem('openaiApiKey');
    localStorage.removeItem('provider');
    setMemBApiKey('');
    setOpenaiApiKey('');
    setProvider('openai');
  };

  const updateUser = (user: string) => {
    setUser(user);
    localStorage.setItem('user', user);
  };

  const clearUser = () => {
    localStorage.removeItem('user');
    setUser('');
  };

  return {
    membApiKey,
    openaiApiKey,
    provider,
    user,
    setAuth,
    setUser: updateUser,
    clearAuth,
    clearUser,
  };
}; 