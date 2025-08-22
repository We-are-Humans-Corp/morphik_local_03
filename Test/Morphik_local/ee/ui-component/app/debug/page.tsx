"use client";

import { useEffect, useState } from "react";

export default function DebugPage() {
  const [authData, setAuthData] = useState<any>({});

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    const user = localStorage.getItem("user");
    const cookies = document.cookie;
    
    setAuthData({
      token: token ? "EXISTS" : "NOT FOUND",
      user: user ? JSON.parse(user) : "NOT FOUND",
      cookies: cookies || "NO COOKIES"
    });
  }, []);

  return (
    <div style={{ padding: "20px", color: "white" }}>
      <h1>Debug Auth Data</h1>
      <pre>{JSON.stringify(authData, null, 2)}</pre>
      <button onClick={() => {
        localStorage.clear();
        document.cookie.split(";").forEach(c => {
          document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        window.location.reload();
      }}>
        Clear All Auth Data
      </button>
    </div>
  );
}
