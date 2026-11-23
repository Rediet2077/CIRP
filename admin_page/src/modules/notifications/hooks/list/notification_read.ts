import { z } from "zod";
import { executeApiRequest } from "@/modules/shared/services/api_client";

const ReadResponseSchema = z.object({ success: z.boolean() });

export async function setNotificationsRead(ids: string[], read: boolean): Promise<void> {
  await executeApiRequest({
    endpoint: "/notifications/staff/read",
    method: "POST",
    body: { ids, read },
    outputSchema: ReadResponseSchema,
    mockFallback: () => ({ success: true }),
  });
}
