import { z } from "zod";
import { executeApiRequest } from "@/modules/shared/services/api_client";

export function deleteReport(reportId: string) {
  return executeApiRequest({
    endpoint: `/reports/${reportId}`,
    method: "DELETE",
    outputSchema: z.object({ success: z.boolean() }).passthrough(),
    mockFallback: () => ({ success: true }),
  });
}
