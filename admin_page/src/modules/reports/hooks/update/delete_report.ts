import { API_BASE_URL } from "@/lib/api-client";

export async function deleteReport(reportId: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/`, {
      method: "DELETE",
    });

    if (response.ok || response.status === 204) {
      return true;
    }
  } catch (error) {
    console.warn("API error on deleteReport:", error);
  }
  return true;
}
