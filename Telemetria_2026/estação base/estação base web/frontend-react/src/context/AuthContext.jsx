import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const DEFAULT_TECH_PASSWORD = 'leviata2026';

export function AuthProvider({ children }) {
  const [isTech, setIsTech] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('leviata_auth_role');
    if (saved === 'tech') {
      setIsTech(true);
    }
  }, []);

  const loginTech = (pass) => {
    if (pass === DEFAULT_TECH_PASSWORD) {
      setIsTech(true);
      localStorage.setItem('leviata_auth_role', 'tech');
      setIsLoginModalOpen(false);
      return { success: true };
    }
    return { success: false, error: 'Senha incorreta da equipe técnica.' };
  };

  const logout = () => {
    setIsTech(false);
    localStorage.removeItem('leviata_auth_role');
  };

  return (
    <AuthContext.Provider value={{
      isTech,
      isViewer: !isTech,
      loginTech,
      logout,
      isLoginModalOpen,
      setIsLoginModalOpen
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
