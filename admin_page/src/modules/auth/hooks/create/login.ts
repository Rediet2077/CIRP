import { executeApiRequest } from "@/modules/shared/services/api_client";
import { INITIAL_MOCK_USERS } from "@/modules/users/hooks/list/user_list";
import {
  DEMO_PASSWORD,
  DEMO_PRESETS,
  LoginInput,
  LoginResponse,
  LoginResponseSchema,
} from "../../types/auth_types";

export const AUTH_SESSION_QUERY_KEY = ["auth", "session"] as const;

export async function loginUser(input: LoginInput): Promise<LoginResponse> {
  return executeApiRequest({
    endpoint: "/auth/login/",
    method: "POST",
    body: input,
    outputSchema: LoginResponseSchema,
    mockFallback: () => {
      const existingUser = INITIAL_MOCK_USERS.find(
        (u) =>
          u.email.toLowerCase() === input.email.trim().toLowerCase() &&
          u.status === "ACTIVE"
      );

      const expectedPassword = DEMO_PRESETS.find((preset) =>
        preset.email.toLowerCase() === existingUser?.email.toLowerCase()
      )?.demo_password ?? DEMO_PASSWORD;
      if (!existingUser || input.password !== expectedPassword) {
        throw new Error("Invalid demo credentials. Select a listed demo account and use the displayed demo password.");
      }

      return {
        access: "demo-session",
        refresh: "demo-refresh",
        user: existingUser,
      };
    },
  });
}
