"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
import { parseConnectionUri, ConnectionInfo, isLocalUri } from "@/lib/connection-utils";

const DEFAULT_API_BASE_URL = "http://localhost:8000";
const CONNECTION_URI_STORAGE_KEY = "morphik-connection-uri";
const AUTH_TOKEN_KEY = "morphik-auth-token";
const USER_PROFILE_KEY = "morphik-user-profile";

interface MorphikContextType {
  connectionUri: string | null;
  connectionInfo: ConnectionInfo | null;
  authToken: string | null;
  apiBaseUrl: string;
  isLocal: boolean;
  isReadOnlyUri: boolean;
  updateConnectionUri: (uri: string) => void;
  userProfile?: {
    name?: string;
    email?: string;
    avatar?: string;
    tier?: string;
  };
  onLogout?: () => void;
  onProfileNavigate?: (section: "account" | "billing" | "notifications") => void;
  onUpgradeClick?: () => void;
  onBackClick?: () => void;
}

const MorphikContext = createContext<MorphikContextType | undefined>(undefined);

// Helper function to safely access localStorage with migration
function getStoredConnectionUri(): string | null {
  if (typeof window === "undefined") return null;
  
  try {
    // Try to get from current key
    const stored = localStorage.getItem(CONNECTION_URI_STORAGE_KEY);
    if (stored) return stored;
    
    // Try legacy key for migration
    const legacy = localStorage.getItem("connectionUri");
    if (legacy) {
      // Migrate to new key
      localStorage.setItem(CONNECTION_URI_STORAGE_KEY, legacy);
      localStorage.removeItem("connectionUri");
      return legacy;
    }
    
    return null;
  } catch {
    return null;
  }
}

function setStoredConnectionUri(uri: string | null) {
  if (typeof window === "undefined") return;
  
  try {
    if (uri) {
      localStorage.setItem(CONNECTION_URI_STORAGE_KEY, uri);
    } else {
      localStorage.removeItem(CONNECTION_URI_STORAGE_KEY);
    }
  } catch {
    // Ignore storage errors
  }
}

interface MorphikProviderProps {
  children: React.ReactNode;
  connectionUri?: string | null;
  userProfile?: {
    name?: string;
    email?: string;
    avatar?: string;
    tier?: string;
  };
  readOnly?: boolean;
  onLogout?: () => void;
  onProfileNavigate?: (section: "account" | "billing" | "notifications") => void;
  onUpgradeClick?: () => void;
  onBackClick?: () => void;
}

export function MorphikProvider({
  children,
  connectionUri: externalConnectionUri,
  userProfile: externalUserProfile,
  readOnly = false,
  onLogout,
  onProfileNavigate,
  onUpgradeClick,
  onBackClick,
}: MorphikProviderProps) {
  const [initialConnectionUri] = useState(() => {
    if (typeof window === "undefined") return null;
    
    // Check if we're in a readonly context (e.g., public share)
    const isReadOnlyPage = window.location.pathname.startsWith("/public/") || 
                          window.location.pathname.startsWith("/share/");
    
    if (isReadOnlyPage) {
      // For readonly pages, don't load from storage
      return null;
    }
    
    // If we're on the auth callback page, don't load from storage
    // to avoid conflicts with the new auth being processed
    if (window.location.pathname === "/auth/callback") {
      return null;
    }
    
    return getStoredConnectionUri();
  });

  const isReadOnlyUri = readOnly || 
    (typeof window !== "undefined" && 
     (window.location.pathname.startsWith("/public/") || 
      window.location.pathname.startsWith("/share/")));

  // Initialize with external prop to avoid hydration mismatch
  const [userProfile, setUserProfile] = useState(externalUserProfile);

  // Load auth token from localStorage and allow it to be updated
  // Use null initially to avoid hydration mismatch, then load from localStorage in useEffect
  const [storedAuthToken, setStoredAuthToken] = useState<string | null>(null);

  // Initialize with external prop to avoid hydration mismatch
  const [connectionUri, setConnectionUri] = useState<string | null>(
    externalConnectionUri || initialConnectionUri
  );

  const connectionInfo = React.useMemo(() => {
    if (!connectionUri) return null;
    return parseConnectionUri(connectionUri);
  }, [connectionUri]);

  const authToken = connectionInfo?.authToken || storedAuthToken || null;

  // Ensure apiBaseUrl is always a valid HTTP(S) URL
  const apiBaseUrl = React.useMemo(() => {
    if (!connectionInfo?.apiBaseUrl) {
      return DEFAULT_API_BASE_URL;
    }

    let url = connectionInfo.apiBaseUrl.trim();

    // Safety check: ensure it's a proper HTTP(S) URL
    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      console.error("[MorphikContext] Invalid apiBaseUrl:", url);
      return DEFAULT_API_BASE_URL;
    }

    // Force HTTPS for morphik.ai domains to avoid CORS preflight redirect failures
    try {
      const parsed = new URL(url);
      if (parsed.protocol === "http:" && parsed.hostname.endsWith("morphik.ai")) {
        parsed.protocol = "https:";
        url = parsed.toString().replace(/\/$/, "");
      }
    } catch {
      // ignore URL parse errors; fallback to original url
    }

    return url;
  }, [connectionInfo]);

  const isLocal = connectionInfo?.type === "local" || !connectionInfo;

  // Load auth token from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      if (token) {
        console.log("[MorphikContext] Loaded auth token from localStorage");
        setStoredAuthToken(token);
      } else {
        console.log("[MorphikContext] No auth token found in localStorage");
      }

      // Also load user profile if exists
      const profileStr = localStorage.getItem(USER_PROFILE_KEY);
      if (profileStr) {
        try {
          const profile = JSON.parse(profileStr);
          console.log("[MorphikContext] Loaded user profile from localStorage:", profile);
          setUserProfile(profile);
        } catch (e) {
          console.error("[MorphikContext] Failed to parse user profile:", e);
        }
      }
    }
  }, []); // Run only once on mount

  // Effect to persist connectionUri changes to localStorage
  useEffect(() => {
    // Only store non-local URIs persistently
    if (connectionUri && connectionInfo && connectionInfo.type === "cloud") {
      setStoredConnectionUri(connectionUri);
    } else if (connectionUri && connectionInfo && connectionInfo.type === "local") {
      // For local connections, we can optionally store temporarily
      // but it will be cleared on next app restart
      console.log("Local connection - will be cleared on restart:", connectionUri);
      setStoredConnectionUri(connectionUri);
    } else {
      // Clear storage if no URI
      setStoredConnectionUri(null);
    }
  }, [connectionUri, connectionInfo]);

  const updateConnectionUri = (uri: string) => {
    if (!isReadOnlyUri) {
      console.log("[MorphikContext] updateConnectionUri:", uri);
      setConnectionUri(uri);
    }
  };

  // Check for profile updates on mount and when window gets focus
  useEffect(() => {
    const checkAndUpdateProfile = () => {
      console.log("[MorphikContext] Checking for profile updates...");
      
      // First check for temporary auth cookie from callback
      if (typeof document !== "undefined") {
        const cookies = document.cookie.split(';');
        const authCookie = cookies.find(c => c.trim().startsWith('morphik-auth-temp='));
        
        if (authCookie) {
          try {
            const cookieValue = authCookie.split('=')[1];
            const authData = JSON.parse(decodeURIComponent(cookieValue));
            console.log("[MorphikContext] Found auth cookie:", authData);
            
            // Save to localStorage
            if (authData.token) {
              localStorage.setItem(AUTH_TOKEN_KEY, authData.token);
              // Update the stored token state
              setStoredAuthToken(authData.token);
            }
            if (authData.profile) {
              localStorage.setItem(USER_PROFILE_KEY, JSON.stringify(authData.profile));
            }
            
            // Clear the temporary cookie
            document.cookie = 'morphik-auth-temp=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
            
            // Update state
            if (authData.profile) {
              setUserProfile(authData.profile);
            }
            
            return;
          } catch (error) {
            console.error("[MorphikContext] Failed to parse auth cookie:", error);
          }
        }
      }
      
      // Check localStorage for existing auth
      if (typeof localStorage !== "undefined") {
        const storedProfile = localStorage.getItem(USER_PROFILE_KEY);
        const storedToken = localStorage.getItem(AUTH_TOKEN_KEY);
        
        if (storedProfile) {
          try {
            const profile = JSON.parse(storedProfile);
            console.log("[MorphikContext] Found stored profile:", profile);
            setUserProfile(profile);
          } catch (error) {
            console.error("[MorphikContext] Failed to parse stored profile:", error);
          }
        }
        
        if (storedToken && storedToken !== storedAuthToken) {
          console.log("[MorphikContext] Found updated token in localStorage");
          setStoredAuthToken(storedToken);
        }
      }
    };

    // Check on mount
    checkAndUpdateProfile();

    // Check when window gets focus (user might have logged in in another tab)
    const handleFocus = () => {
      console.log("[MorphikContext] Window focused, checking for updates...");
      checkAndUpdateProfile();
    };

    window.addEventListener('focus', handleFocus);
    
    // Also check periodically for cross-tab sync
    const interval = setInterval(checkAndUpdateProfile, 5000);

    return () => {
      window.removeEventListener('focus', handleFocus);
      clearInterval(interval);
    };
  }, [storedAuthToken]);

  // Debug logging
  React.useEffect(() => {
    console.log("[MorphikContext] Current values:", {
      connectionUri,
      connectionInfo,
      apiBaseUrl,
      authToken,
      isLocal,
      userProfile,
    });
  }, [connectionUri, connectionInfo, apiBaseUrl, authToken, isLocal, userProfile]);

  return (
    <MorphikContext.Provider
      value={{
        connectionUri,
        connectionInfo,
        authToken,
        apiBaseUrl,
        isLocal,
        isReadOnlyUri,
        updateConnectionUri,
        userProfile,
        onLogout,
        onProfileNavigate,
        onUpgradeClick,
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