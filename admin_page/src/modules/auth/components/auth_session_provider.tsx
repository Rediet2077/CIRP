"use client";

import { useEffect } from "react";
import { useNavigationStore } from "@/modules/shared/store/navigation_store";
import { localStorageService } from "@/modules/shared/services/local_storage";

interface AuthSession {
  access: string;
  refresh: string;
  user: {
    id: string;
    email: string;
    role: string;
    department?: {
      id: string;
      name: string;
    };
  };
}

export function AuthSessionProvider({ children }: { children: React.ReactNode }) {
  const { setCurrentUserRole, setActiveOfficerDepartmentId } = useNavigationStore();

  useEffect(() => {
    // Restore session from localStorage on mount
    const session = localStorageService.getItem<AuthSession>("authSession");
    
    console.log('🔐 Auth Session Restore:', {
      hasSession: !!session,
      userRole: session?.user?.role,
      userEmail: session?.user?.email
    });
    
    if (session?.user?.role) {
      const role = session.user.role;
      
      // Set role for all admin types
      const adminRoles = [
        "SUPER_ADMIN",
        "SYSTEM_ADMIN",
        "DEPARTMENT_ADMIN",
        "ROAD_ADMIN",
        "WATER_ADMIN",
        "ELECTRICITY_ADMIN",
        "DRAINAGE_ADMIN",
        "WASTE_ADMIN",
        "STREETLIGHT_ADMIN",
        "PUBLIC_FACILITIES_ADMIN",
      ];

      if (adminRoles.includes(role)) {
        console.log('✅ Setting role:', role);
        setCurrentUserRole(role as any);
      } else {
        console.warn('⚠️ Unrecognized role:', role);
      }

      if (session.user.department) {
        setActiveOfficerDepartmentId(session.user.department.id);
      }
    } else {
      console.warn('⚠️ No session or user role found');
    }
  }, [setCurrentUserRole, setActiveOfficerDepartmentId]);

  return <>{children}</>;
}
