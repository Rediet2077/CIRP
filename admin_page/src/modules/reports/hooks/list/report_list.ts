import { getReports } from "@/lib/api-client";
import { ReportListResponse } from "../../types/report_types";

export const REPORT_LIST_QUERY_KEY = ["reports", "list"] as const;

const BACKEND_BASE_URL = "http://localhost:8000";

function resolveMediaUrl(url?: string): string {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) {
    return url;
  }
  return `${BACKEND_BASE_URL}${url.startsWith("/") ? "" : "/"}${url}`;
}

export async function fetchReportList(departmentId?: string, query?: string): Promise<ReportListResponse> {
  // Fetch reports from the backend API
  const response = await getReports({
    search: query,
    page_size: 1000, // Get all reports for now
  });

  if (!response.success || !response.data) {
    throw new Error(response.error || "Failed to fetch reports");
  }

  // Handle various DRF response wrappers (data array, data.data, or data.results)
  let rawReports: any[] = [];
  if (Array.isArray(response.data)) {
    rawReports = response.data;
  } else if (response.data && Array.isArray((response.data as any).data)) {
    rawReports = (response.data as any).data;
  } else if (response.data && Array.isArray((response.data as any).results)) {
    rawReports = (response.data as any).results;
  }

  // Filter out REJECTED reports so they automatically disappear from the admin page
  rawReports = rawReports.filter((r: any) => r.status !== "REJECTED");

  // Transform backend report format to frontend format
  const reports = rawReports.map((report: any) => ({
    id: report.id,
    report_code: report.report_number || `RPT-${report.id.substring(0, 8)}`,
    title: report.title,
    description: report.description,
    category_name: report.category?.name || "General Infrastructure",
    asset_id: null,
    asset_code: null,
    asset_type_label: null,
    department_id: report.assigned_department || "",
    department_name: report.assigned_department ? "Assigned Dept" : "Unassigned",
    citizen_name: report.citizen ? `${report.citizen.first_name || ""} ${report.citizen.last_name || ""}`.trim() || report.citizen.email : "Citizen",
    citizen_contact: report.citizen?.phone || report.citizen?.email || "",
    citizen_latitude: report.latitude || 0,
    citizen_longitude: report.longitude || 0,
    address: report.address || "",
    landmark: "",
    status: mapBackendStatusToFrontend(report.status),
    priority: report.priority || "MEDIUM",
    submitted_at: report.created_at,
    media_photos: report.media?.map((m: any) => resolveMediaUrl(m.file || m.file_url)) || [],
    linked_task_id: null,
    public_delay_explanation: report.admin_feedback,
    resolution_notes: report.completion_notes,
    resolved_at: report.resolved_at,
  }));

  return reports;
}

// Map backend status to frontend status
function mapBackendStatusToFrontend(
  status: string
): "NEW" | "ACCEPTED" | "IN_PROGRESS" | "COMPLETED_PENDING_VERIFICATION" | "RESOLVED" | "DISPUTED" {
  const statusMap: Record<string, "NEW" | "ACCEPTED" | "IN_PROGRESS" | "COMPLETED_PENDING_VERIFICATION" | "RESOLVED" | "DISPUTED"> = {
    SUBMITTED: "NEW",
    UNDER_REVIEW: "NEW",
    ACCEPTED: "ACCEPTED",
    ASSIGNED: "ACCEPTED",
    IN_PROGRESS: "IN_PROGRESS",
    PENDING_VERIFICATION: "COMPLETED_PENDING_VERIFICATION",
    RESOLVED: "RESOLVED",
    REJECTED: "RESOLVED",
    DISPUTED: "DISPUTED",
    REOPENED: "NEW",
    MERGED: "RESOLVED",
    CLOSED: "RESOLVED",
  };

  return statusMap[status] || "NEW";
}
