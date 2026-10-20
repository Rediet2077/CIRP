import { executeApiRequest } from "@/modules/shared/services/api_client";
import { mockDataStore } from "@/modules/shared/services/mock_storage";
import { withDemoDecisions } from "../../services/report_decisions";
import {
  ReportListResponseSchema,
  ReportListResponse,
} from "../../types/report_types";

export const REPORT_LIST_QUERY_KEY = ["reports", "list"] as const;

export async function fetchReportList(departmentId?: string, query?: string): Promise<ReportListResponse> {
  return executeApiRequest({
    endpoint: "/reports",
    method: "GET",
    query: { department_id: departmentId, search: query },
    outputSchema: ReportListResponseSchema,
    mockFallback: () => mockDataStore.getReports(departmentId, query).map(withDemoDecisions),
  });
}
