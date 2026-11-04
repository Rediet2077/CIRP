import { z } from "zod";
import { executeApiRequest } from "@/modules/shared/services/api_client";
import { ReportRecordSchema } from "@/modules/shared/types/cirp_schema";
import { rejectDemoReport } from "../../services/report_decisions";

const RejectInputSchema = z.object({ reportId: z.string(), departmentId: z.string(), reason: z.string().trim().min(5) });
export type RejectReportInput = z.infer<typeof RejectInputSchema>;

export function rejectReport(input: RejectReportInput) {
  const validated = RejectInputSchema.parse(input);
  return executeApiRequest({
    endpoint: `/reports/${validated.reportId}/reject/`,
    method: "POST",
    body: { department_id: validated.departmentId, reason: validated.reason },
    outputSchema: ReportRecordSchema,
    mockFallback: () => rejectDemoReport(validated.reportId, validated.departmentId, validated.reason),
  });
}
