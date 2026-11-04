import { executeApiRequest } from "@/modules/shared/services/api_client";
import { mockDataStore } from "@/modules/shared/services/mock_storage";
import {
  TaskListResponseSchema,
  TaskListResponse,
} from "../../types/task_types";

export const TASK_LIST_QUERY_KEY = ["tasks", "list"] as const;

export async function fetchTaskList(departmentId?: string, query?: string): Promise<TaskListResponse["tasks"]> {
  const response = await executeApiRequest({
    endpoint: "/tasks",
    method: "GET",
    query: { department_id: departmentId, search: query },
    outputSchema: TaskListResponseSchema,
    mockFallback: () => ({ tasks: mockDataStore.getTasks(departmentId, query) }),
  });
  
  return response.tasks;
}
