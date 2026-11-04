import { z } from "zod";
import { UserRecordSchema } from "@/modules/users/types/user_types";

const LoginInputSchema = z.object({
  email: z.string().email("Please enter a valid official email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});
export type LoginInput = z.infer<typeof LoginInputSchema>;

export const LoginResponseSchema = z.object({
  access: z.string(),
  refresh: z.string(),
  user: UserRecordSchema,
});
export type LoginResponse = z.infer<typeof LoginResponseSchema>;

const SignupInputSchema = z.object({
  department_name: z.string().min(2, "Department name is required"),
  department_code: z.string().min(2, "Department code is required"),
  department_email: z.string().email("Please enter a valid department email"),
  department_phone: z.string().min(8, "Department phone is required"),
  address: z.string().min(2, "Address is required"),
  representative_first_name: z.string().min(2, "First name is required"),
  representative_last_name: z.string().min(2, "Last name is required"),
  representative_email: z.string().email("Please enter a valid email address"),
  representative_phone: z.string().min(8, "Representative phone is required"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});
export type SignupInput = z.infer<typeof SignupInputSchema>;

export const SignupResponseSchema = z.object({
  message: z.string(),
});
export type SignupResponse = z.infer<typeof SignupResponseSchema>;

export interface DemoAccountPreset {
  title: string;
  name: string;
  email: string;
  role: "SYSTEM_ADMIN" | "DEPARTMENT_ADMIN";
  department_name: string;
  department_code: string;
  demo_password: string;
}

// Used only by the explicitly labeled, browser-side demo dataset.
export const DEMO_PASSWORD = "password123";

export const DEMO_PRESETS: DemoAccountPreset[] = [
  {
    title: "System Admin",
    name: "Admin User",
    email: "admin@cirp.com",
    role: "SYSTEM_ADMIN",
    department_name: "System Administration",
    department_code: "ADMIN",
    demo_password: "Test@123",
  },
  {
    title: "Public Works Admin",
    name: "Public Works Manager",
    email: "public.works@cirp.com",
    role: "DEPARTMENT_ADMIN",
    department_name: "Public Works & Infrastructure",
    department_code: "PW",
    demo_password: "Test@123",
  },
  {
    title: "Water & Sewage Admin",
    name: "Water & Sewage Manager",
    email: "water.sewage@cirp.com",
    role: "DEPARTMENT_ADMIN",
    department_name: "Water & Sewage",
    department_code: "WS",
    demo_password: "Test@123",
  },
  {
    title: "Sanitation Admin",
    name: "Sanitation Manager",
    email: "sanitation@cirp.com",
    role: "DEPARTMENT_ADMIN",
    department_name: "Sanitation & Waste Management",
    department_code: "SAN",
    demo_password: "Test@123",
  },
  {
    title: "Electrical Services Admin",
    name: "Electrical Services Manager",
    email: "electrical.services@cirp.com",
    role: "DEPARTMENT_ADMIN",
    department_name: "Electrical Services",
    department_code: "ELEC",
    demo_password: "Test@123",
  },
];
