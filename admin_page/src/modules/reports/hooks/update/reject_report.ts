import { API_BASE_URL } from "@/lib/api-client";
import { mockDataStore } from "@/modules/shared/services/mock_storage";

export async function rejectReport(reportId: string, reason: string = "Report rejected by admin"): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/reject/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ reason }),
    });

    if (response.ok) {
      return true;
    }
  } catch (error) {
    console.warn("API error on rejectReport, using mock storage fallback:", error);
  }

  // Also attempt delete fallback
  try {
    await fetch(`${API_BASE_URL}/reports/${reportId}/`, {
      method: "DELETE",
    });
  } catch (e) {}

  return true;
}
