import { UserRole } from "../types/enums";

/**
 * Role hierarchy and permissions utility
 */

export const DEPARTMENT_ADMIN_ROLES: UserRole[] = [
  "ROAD_ADMIN",
  "WATER_ADMIN",
  "ELECTRICITY_ADMIN",
  "DRAINAGE_ADMIN",
  "WASTE_ADMIN",
  "STREETLIGHT_ADMIN",
  "PUBLIC_FACILITIES_ADMIN",
];

export const SUPER_ADMIN_ROLES: UserRole[] = [
  "SUPER_ADMIN",
  "SYSTEM_ADMIN", // Legacy alias
];

/**
 * Check if user is a Super Admin
 */
export function isSuperAdmin(role: UserRole): boolean {
  return SUPER_ADMIN_ROLES.includes(role);
}

/**
 * Check if user is a Department Admin
 */
export function isDepartmentAdmin(role: UserRole): boolean {
  return DEPARTMENT_ADMIN_ROLES.includes(role) || role === "DEPARTMENT_ADMIN";
}

/**
 * Get department name from admin role
 */
export function getDepartmentFromRole(role: UserRole): string {
  const mapping: Record<string, string> = {
    ROAD_ADMIN: "Road",
    WATER_ADMIN: "Water",
    ELECTRICITY_ADMIN: "Electricity",
    DRAINAGE_ADMIN: "Drainage",
    WASTE_ADMIN: "Waste Management",
    STREETLIGHT_ADMIN: "Street Lighting",
    PUBLIC_FACILITIES_ADMIN: "Public Facilities",
  };
  return mapping[role] || "Unknown";
}

/**
 * Get role display name
 */
export function getRoleDisplayName(role: UserRole): string {
  const mapping: Record<string, string> = {
    SUPER_ADMIN: "Super Admin",
    SYSTEM_ADMIN: "Super Admin",
    ROAD_ADMIN: "Road Admin",
    WATER_ADMIN: "Water Admin",
    ELECTRICITY_ADMIN: "Electricity Admin",
    DRAINAGE_ADMIN: "Drainage Admin",
    WASTE_ADMIN: "Waste Management Admin",
    STREETLIGHT_ADMIN: "Street Lighting Admin",
    PUBLIC_FACILITIES_ADMIN: "Public Facilities Admin",
    DEPARTMENT_ADMIN: "Department Admin",
  };
  return mapping[role] || role;
}

/**
 * Get role color for badges
 */
export function getRoleColor(role: UserRole): string {
  if (isSuperAdmin(role)) {
    return "bg-purple-100 text-purple-800 border-purple-200";
  }
  if (isDepartmentAdmin(role)) {
    return "bg-blue-100 text-blue-800 border-blue-200";
  }
  return "bg-gray-100 text-gray-800 border-gray-200";
}

/**
 * Check if user can access a feature
 */
export function canAccessFeature(
  userRole: UserRole,
  feature: string
): boolean {
  // Super Admin has access to everything
  if (isSuperAdmin(userRole)) {
    return true;
  }

  // Department Admin restrictions
  if (isDepartmentAdmin(userRole)) {
    const restrictedFeatures = [
      "users",
      "departments",
      "categories",
      "system_settings",
      "audit_logs_full",
    ];
    return !restrictedFeatures.includes(feature);
  }

  return false;
}

/**
 * Get menu items based on role
 */
export function getMenuItemsForRole(role: UserRole) {
  const superAdminMenu = [
    { id: "dashboard", label: "Dashboard", icon: "📊" },
    { id: "reports", label: "Reports", icon: "📝" },
    { id: "tasks", label: "Tasks", icon: "✓" },
    { id: "users", label: "Users", icon: "👥" },
    { id: "departments", label: "Departments", icon: "🏢" },
    { id: "contractors", label: "Contractors", icon: "👷" },
    { id: "assets", label: "Assets", icon: "🏗️" },
    { id: "analytics", label: "Analytics", icon: "📈" },
    { id: "map", label: "Map", icon: "🗺️" },
    { id: "audit_logs", label: "Audit Logs", icon: "📋" },
    { id: "settings", label: "Settings", icon: "⚙️" },
  ];

  const departmentAdminMenu = [
    { id: "dashboard", label: "Dashboard", icon: "📊" },
    { id: "reports", label: "Reports", icon: "📝" },
    { id: "tasks", label: "Tasks", icon: "✓" },
    { id: "contractors", label: "Contractors", icon: "👷" },
    { id: "assets", label: "Assets", icon: "🏗️" },
    { id: "analytics", label: "Analytics", icon: "📈" },
    { id: "map", label: "Map", icon: "🗺️" },
  ];

  return isSuperAdmin(role) ? superAdminMenu : departmentAdminMenu;
}
