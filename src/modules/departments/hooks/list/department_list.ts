import { executeApiRequest } from "@/modules/shared/services/api_client";
import { mockDataStore } from "@/modules/shared/services/mock_storage";
import { DEMO_STREET_LIGHTING_DEPARTMENT } from "../../services/demo_departments";
import {
  DepartmentListResponseSchema,
  DepartmentListResponse,
} from "../../types/department_types";

export const DEPARTMENT_LIST_QUERY_KEY = ["departments", "list"] as const;

export async function fetchDepartmentList(): Promise<DepartmentListResponse> {
  return executeApiRequest({
    endpoint: "/departments",
    method: "GET",
    outputSchema: DepartmentListResponseSchema,
    mockFallback: () => [...mockDataStore.getDepartments(), DEMO_STREET_LIGHTING_DEPARTMENT],
  });
}
