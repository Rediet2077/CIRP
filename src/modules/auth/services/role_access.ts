import type { UserRole } from "@/modules/shared/types/enums";

const SYSTEM_MANAGEMENT_PATHS = [
  "/dashboard/departments",
  "/dashboard/users",
  "/dashboard/settings",
  "/dashboard/audit-logs",
];

/** UI navigation policy only; API permissions must still be enforced by the backend. */
export function canAccessPlatformManagement(role: UserRole): boolean {
  return role === "SYSTEM_ADMIN";
}

export function canAccessDashboardPath(role: UserRole, pathname: string): boolean {
  if (!SYSTEM_MANAGEMENT_PATHS.some((path) => pathname.startsWith(path))) return true;
  return canAccessPlatformManagement(role);
}
