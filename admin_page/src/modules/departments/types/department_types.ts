import { z } from "zod";
import { DepartmentRecordSchema, DepartmentRecord } from "@/modules/shared/types/cirp_schema";

export type { DepartmentRecord };

// Backend returns {departments: [...]}
export const DepartmentListResponseSchema = z.object({
  departments: z.array(DepartmentRecordSchema)
});
export type DepartmentListResponse = z.infer<typeof DepartmentListResponseSchema>;
