import { describe, expect, test } from "bun:test";
import { INITIAL_MOCK_USERS } from "@/modules/users/hooks/list/user_list";
import { canAccessDashboardPath, canAccessPlatformManagement } from "./role_access";

describe("dashboard role navigation policy", () => {
  test("reserves global management routes for the system administrator", () => {
    expect(canAccessPlatformManagement("SYSTEM_ADMIN")).toBe(true);
    expect(canAccessPlatformManagement("DEPARTMENT_ADMIN")).toBe(false);
    expect(canAccessDashboardPath("DEPARTMENT_ADMIN", "/dashboard/users")).toBe(false);
    expect(canAccessDashboardPath("SYSTEM_ADMIN", "/dashboard/departments")).toBe(true);
  });

  test("keeps operational routes available to department administrators", () => {
    expect(canAccessDashboardPath("DEPARTMENT_ADMIN", "/dashboard/reports")).toBe(true);
    expect(canAccessDashboardPath("DEPARTMENT_ADMIN", "/dashboard/tasks")).toBe(true);
    expect(canAccessDashboardPath("DEPARTMENT_ADMIN", "/dashboard/audit-logs-extra")).toBe(false);
  });

  test("sample accounts include one Super Admin and one active admin for each of seven departments", () => {
    const activeUsers = INITIAL_MOCK_USERS.filter((user) => user.status === "ACTIVE");
    const superAdmins = activeUsers.filter((user) => user.role === "SYSTEM_ADMIN");
    const departmentAdmins = activeUsers.filter((user) => user.role === "DEPARTMENT_ADMIN");

    expect(superAdmins).toHaveLength(1);
    expect(departmentAdmins).toHaveLength(7);
    expect(new Set(departmentAdmins.map((user) => user.department?.id)).size).toBe(7);
  });
});
