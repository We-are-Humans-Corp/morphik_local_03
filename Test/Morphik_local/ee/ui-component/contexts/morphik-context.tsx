"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { extractTokenFromUri, getApiBaseUrlFromUri } from "@/lib/utils";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

interface MorphikContextType {
  connectionUri: string | null;
  authToken: string | null;
  apiBaseUrl: string;
  isReadOnlyUri: boolean;
  updateConnectionUri: (uri: string) => void;
  setAuthToken: (token: string | null) => void;
  userProfile?: {
    name?: string;
    email?: string;
    avatar?: string;
    tier?: string;
  };
  onLogout?: () => void;
  onProfileNavigate?: (section: "account" | "billing" | "notifications") => void;
  onBackClick?: () => void;
}

const MorphikContext = createContext<MorphikContextType | undefined>(undefined);

export function MorphikProvider({
  children,
  initialConnectionUri = null,
  isReadOnlyUri = false,
  connectionUri: externalConnectionUri,
  onBackClick,
  userProfile,
  onLogout,
  onProfileNavigate,
}: {
  children: React.ReactNode;
  initialConnectionUri?: string | null;
  isReadOnlyUri?: boolean;
  connectionUri?: string | null;
  onBackClick?: () => void;
  userProfile?: {
    name?: string;
    email?: string;
    avatar?: string;
    tier?: string;
  };
  onLogout?: () => void;
  onProfileNavigate?: (section: "account" | "billing" | "notifications") => void;
}) {
  const [connectionUri, setConnectionUri] = useState<string | null>(externalConnectionUri || initialConnectionUri);
  const [authTokenState, setAuthTokenState] = useState<string | null>(null);

  // Initialize auth token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setAuthTokenState(storedToken);
    }
  }, []);

  const authToken = authTokenState || (connectionUri ? extractTokenFromUri(connectionUri) : null);
  const apiBaseUrl = connectionUri ? getApiBaseUrlFromUri(connectionUri) : DEFAULT_API_BASE_URL;

  const updateConnectionUri = (uri: string) => {
    if (!isReadOnlyUri) {
      setConnectionUri(uri);
    }
  };

  const setAuthToken = (token: string | null) => {
    setAuthTokenState(token);
    if (token) {
      localStorage.setItem('authToken', token);
      document.cookie = `authToken=${token}; path=/; max-age=604800`; // 7 days
    } else {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      document.cookie = 'authToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
  };

  return (
    <MorphikContext.Provider
      value={{
        connectionUri,
        authToken,
        apiBaseUrl,
        isReadOnlyUri,
        updateConnectionUri,
        setAuthToken,
        userProfile,
        onLogout,
        onProfileNavigate,
        onBackClick,
      }}
    >
      {children}
    </MorphikContext.Provider>
  );
}

export function useMorphik() {
  const context = useContext(MorphikContext);
  if (context === undefined) {
    throw new Error("useMorphik must be used within a MorphikProvider");
  }
  return context;
}
