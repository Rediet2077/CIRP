import { executeApiRequest } from "@/modules/shared/services/api_client";
import { mockDataStore } from "@/modules/shared/services/mock_storage";
import {
  SignupInput,
  SignupResponse,
  SignupResponseSchema,
} from "../../types/auth_types";

export const AUTH_SIGNUP_QUERY_KEY = ["auth", "signup"] as const;

export async function signupUser(input: SignupInput): Promise<SignupResponse> {
  return executeApiRequest({
    endpoint: "/departments/apply/",
    method: "POST",
    body: input,
    outputSchema: SignupResponseSchema,
    mockFallback: async () => {
      // Add the pending department application
      mockDataStore.addPendingDepartment({
        department_name: input.department_name,
        department_code: input.department_code,
        department_email: input.department_email,
        department_phone: input.department_phone,
        address: input.address,
      });
      
      return {
        message: "Department application submitted successfully. Awaiting approval.",
      };
    },
  });
}
