"use client";

import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { LoginResponseSchema } from "@/modules/auth/types/auth_types";
import { canAccessDashboardPath } from "@/modules/auth/services/role_access";
import { useNavigationStore } from "../store/navigation_store";
import { localStorageService } from "../services/local_storage";

export function DashboardAccessGuard({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [authorizedPath, setAuthorizedPath] = useState<string | null>(null);
  const [sessionIssue, setSessionIssue] = useState<string | null>(null);
  const setCurrentUserRole = useNavigationStore((state) => state.setCurrentUserRole);
  const setActiveOfficerDepartmentId = useNavigationStore((state) => state.setActiveOfficerDepartmentId);

  useEffect(() => {
    const savedSession = localStorageService.getItem<unknown>("authSession");
    const parsed = LoginResponseSchema.safeParse(savedSession);

    if (!parsed.success) {
      setSessionIssue("unauthenticated");
      router.replace("/login");
      return;
    }

    const { user } = parsed.data;
    setCurrentUserRole(user.role);
    const departmentId = user.department?.id || "__unassigned__";
    setActiveOfficerDepartmentId(departmentId);
    if (user.role === "DEPARTMENT_ADMIN" && !user.department?.id) {
      setSessionIssue("missing-department");
      return;
    }
    setSessionIssue(null);

    if (!canAccessDashboardPath(user.role, pathname)) {
      router.replace("/dashboard");
      return;
    }

    setAuthorizedPath(pathname);
  }, [pathname, router, setActiveOfficerDepartmentId, setCurrentUserRole]);

  if (authorizedPath !== pathname) {
    if (sessionIssue === "missing-department") {
      return (
        <div role="alert" className="m-6 rounded-lg border border-amber-500/40 bg-amber-50 p-4 text-sm text-amber-950">
          This department administrator account has no assigned department. Ask a Super Admin to assign one.
        </div>
      );
    }
    return <div className="p-6 text-sm text-muted-foreground" aria-live="polite">Checking your session…</div>;
  }

  return children;
}
