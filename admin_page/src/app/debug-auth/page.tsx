"use client";

import { useEffect, useState } from "react";
import { useNavigationStore } from "@/modules/shared/store/navigation_store";

export default function DebugAuthPage() {
  const [storageData, setStorageData] = useState<any>(null);
  const [allKeys, setAllKeys] = useState<string[]>([]);
  const { currentUserRole } = useNavigationStore();

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const authSession = localStorage.getItem("authSession");
      if (authSession) {
        try {
          setStorageData(JSON.parse(authSession));
        } catch (e) {
          setStorageData({ error: "Failed to parse", raw: authSession });
        }
      }
      setAllKeys(Object.keys(localStorage));
    }
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "monospace", color: "#fff", background: "#000", minHeight: "100vh" }}>
      <h1>🔍 Debug Auth Information</h1>
      
      <h2>Zustand Store currentUserRole:</h2>
      <pre style={{ background: "#222", padding: "10px", color: "#0f0" }}>
        {currentUserRole || "NOT SET"}
      </pre>

      <h2>LocalStorage authSession:</h2>
      <pre style={{ background: "#222", padding: "10px", color: "#0ff", overflow: "auto" }}>
        {storageData ? JSON.stringify(storageData, null, 2) : "NO DATA"}
      </pre>

      <h2>All LocalStorage Keys:</h2>
      <pre style={{ background: "#222", padding: "10px", color: "#ff0" }}>
        {allKeys.length > 0 ? allKeys.join(", ") : "NO KEYS"}
      </pre>

      <h2>Expected Role:</h2>
      <pre style={{ background: "#222", padding: "10px", color: "#f0f" }}>
        SUPER_ADMIN
      </pre>

      <h2>Actual Role from Storage:</h2>
      <pre style={{ background: "#222", padding: "10px", color: "#f00" }}>
        {storageData?.user?.role || "NOT FOUND"}
      </pre>
    </div>
  );
}
