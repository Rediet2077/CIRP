import { executeApiRequest } from "@/modules/shared/services/api_client";
import { mockDataStore } from "@/modules/shared/services/mock_storage";
import { DEMO_STREET_LIGHTING_DEPARTMENT } from "../../services/demo_departments";
import {
  DepartmentListResponseSchema,
  DepartmentListResponse,
} from "../../types/department_types";

export const DEPARTMENT_LIST_QUERY_KEY = ["departments", "list"] as const;

export async function fetchDepartmentList(): Promise<DepartmentListResponse["departments"]> {
  const response = await executeApiRequest({
    endpoint: "/departments",
    method: "GET",
    outputSchema: DepartmentListResponseSchema,
    mockFallback: () => ({ departments: [...mockDataStore.getDepartments(), DEMO_STREET_LIGHTING_DEPARTMENT] }),
  });
  
  return response.departments;
}
