import { z } from "zod";
import { executeApiRequest } from "@/modules/shared/services/api_client";
import { mockDataStore } from "@/modules/shared/services/mock_storage";
import { withDemoDecisions } from "@/modules/reports/services/report_decisions";

export const PublicReportSchema = z.object({
  reference: z.string(),
  category: z.string(),
  status: z.enum(["Under review", "Work in progress", "Awaiting confirmation", "Resolved", "Rejected"]),
  submitted_at: z.string(),
  general_location: z.string().nullable(),
}).strict();

export type PublicReport = z.infer<typeof PublicReportSchema>;
const PublicReportListSchema = z.array(PublicReportSchema);

function toPublicStatus(status: string): PublicReport["status"] {
  if (status === "RESOLVED") return "Resolved";
  if (status === "DISPUTED") return "Rejected";
  if (status === "REJECTED") return "Rejected";
  if (status === "COMPLETED_PENDING_VERIFICATION") return "Awaiting confirmation";
  if (status === "ACCEPTED" || status === "IN_PROGRESS") return "Work in progress";
  return "Under review";
}

export function toPublicReport(record: {
  report_code: string;
  category_name: string;
  status: string;
  submitted_at: string;
  address: string;
}): PublicReport {
  const locationParts = record.address.split(",").map((part) => part.trim()).filter(Boolean);
  const generalLocation = locationParts.length > 1
    ? locationParts.slice(-2).join(", ")
    : locationParts[0] || null;

  return PublicReportSchema.parse({
    reference: record.report_code,
    category: record.category_name,
    status: toPublicStatus(record.status),
    submitted_at: record.submitted_at,
    general_location: generalLocation,
  });
}

export async function fetchPublicReports(): Promise<PublicReport[]> {
  return executeApiRequest({
    endpoint: "/public/reports/",
    outputSchema: PublicReportListSchema,
    mockFallback: () => mockDataStore.getReports("all").map(withDemoDecisions).map(toPublicReport),
  });
}
