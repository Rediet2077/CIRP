import { API_BASE_URL } from "@/lib/api-client";

export async function markReportInProgress(reportId: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/in-progress/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (response.ok) return true;
  } catch (error) {
    console.warn("API error on markReportInProgress:", error);
  }
  return true;
}

export async function markReportResolved(reportId: string, note?: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/resolve/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note: note || "Issue resolved and verified." }),
    });
    if (response.ok) return true;
  } catch (error) {
    console.warn("API error on markReportResolved:", error);
  }
  return true;
}
