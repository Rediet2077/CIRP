import type { DepartmentRecord } from "../types/department_types";

export const DEMO_STREET_LIGHTING_DEPARTMENT: DepartmentRecord = {
  id: "dept-light",
  code: "LITE",
  name: "Street Lighting Department",
  description: "Streetlight maintenance and public lighting repairs.",
  contact_email: "streetlighting@municipality.gov.et",
  contact_phone: "",
  office_location: "",
  responsible_asset_types: ["street_light"],
  total_assets: 0,
  active_reports: 0,
  active_tasks: 0,
  overdue_tasks: 0,
  resolved_reports: 0,
  resolution_rate_percent: 0,
  avg_acceptance_hours: 0,
  avg_completion_days: 0,
};
