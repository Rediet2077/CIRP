import { fetchReportList } from "../list/report_list";
import { ReportRecord } from "../../types/report_types";

export const REPORT_DETAILS_QUERY_KEY = ["reports", "details"] as const;

export async function fetchReportDetails(reportId: string): Promise<ReportRecord | undefined> {
  const reports = await fetchReportList();
  const match = reports.find((r) => r.id === reportId);
  if (match) return match;
  return undefined;
}
