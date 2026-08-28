"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { loginUser, AUTH_SESSION_QUERY_KEY } from "./login";
import { LoginInput, LoginResponse } from "../../types/auth_types";
import { useNavigationStore } from "@/modules/shared/store/navigation_store";
import { localStorageService } from "@/modules/shared/services/local_storage";

/** Writes a cookie accessible by the Next.js Edge middleware. */
function setAuthCookie(name: string, value: string, days = 7) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

/** Clears an auth cookie. */
export function clearAuthCookies() {
  document.cookie = "cirp_token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
  document.cookie = "cirp_role=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
}

export function useLogin() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { setCurrentUserRole, setActiveOfficerDepartmentId } = useNavigationStore();

  return useMutation<LoginResponse, Error, LoginInput>({
    mutationFn: (input: LoginInput) => loginUser(input),
    onSuccess: (data) => {
      const role = data.user.role;

      if (role === "SYSTEM_ADMIN" || role === "DEPARTMENT_ADMIN") {
        setCurrentUserRole(role);
      }

      if (data.user.department) {
        setActiveOfficerDepartmentId(data.user.department.id);
      }

      // Mirror auth info into cookies so Next.js Edge middleware can read them
      setAuthCookie("cirp_token", data.access);
      setAuthCookie("cirp_role", role);

      queryClient.setQueryData(AUTH_SESSION_QUERY_KEY, data);
      localStorageService.setItem("authSession", data);
      queryClient.invalidateQueries({ queryKey: ["users", "list"] });
      router.push("/dashboard");
    },
  });
}
