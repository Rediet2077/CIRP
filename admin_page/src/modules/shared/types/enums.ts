export type AssetTypeKey =
  | "street_light"
  | "road"
  | "water_point"
  | "drainage"
  | "waste_bin"
  | "public_building";

export type AssetStatus = "ACTIVE" | "INACTIVE";

export type AssetCondition = "EXCELLENT" | "GOOD" | "FAIR" | "POOR" | "CRITICAL";

export type ReportPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type UserRole = 
  | "SUPER_ADMIN"
  | "ROAD_ADMIN" 
  | "WATER_ADMIN"
  | "ELECTRICITY_ADMIN"
  | "DRAINAGE_ADMIN"
  | "WASTE_ADMIN"
  | "STREETLIGHT_ADMIN"
  | "PUBLIC_FACILITIES_ADMIN"
  | "SYSTEM_ADMIN"  // Legacy alias for SUPER_ADMIN
  | "DEPARTMENT_ADMIN";  // Generic department admin

type DepartmentStatus = "PENDING" | "ACTIVE" | "INACTIVE";

export type AdminNavigationTab =
  | "dashboard"
  | "all_assets"
  | "register_asset"
  | "asset_types"
  | "reports"
  | "report_details"
  | "tasks"
  | "deadlines"
  | "extensions"
  | "map"
  | "departments"
  | "department_profile"
  | "contractors"
  | "analytics"
  | "audit_logs";
