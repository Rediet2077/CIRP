"use client";

import React from "react";
import { Button } from "@/ui/button";
import { FieldGroup } from "@/ui/field";
import { useNavigationStore } from "@/modules/shared/store/navigation_store";
import { useDepartmentList } from "@/modules/departments/hooks/list/use_department_list";
import { useAddContractor } from "../../hooks/create/use_add_contractor";
import { useForm, FormProvider } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { addContractorSchema, AddContractorFormData } from "../../types/contractor_schemas";
import { AddContractorFields } from "./subcomponents/add_contractor_fields";

interface AddContractorFormProps {
  onClose: () => void;
}

export function AddContractorForm({ onClose }: AddContractorFormProps) {
  const { data: departments } = useDepartmentList();
  const addContractorMutation = useAddContractor();
  const { selectedDepartmentFilter, currentUserRole, activeOfficerDepartmentId } = useNavigationStore();
  const [submitError, setSubmitError] = React.useState<string | null>(null);
  // Default to the officer's own department so the new person shows up in their list
  const myDept = currentUserRole === "DEPARTMENT_ADMIN" ? activeOfficerDepartmentId : selectedDepartmentFilter;
  const defaultDept = (myDept && myDept !== "all" ? myDept : departments?.[0]?.id) || "";

  const methods = useForm<AddContractorFormData>({
    resolver: zodResolver(addContractorSchema),
    defaultValues: {
      name: "",
      phone: "+251 91 ",
      email: "",
      department_id: defaultDept,
      is_contractor: false,
      contractor_company_name: "",
      license_number: "",
      position_title: "Field Technician",
      specialization: "Electrical Maintenance",
    } as any, // Temporary cast, form keys mismatch defaults slightly but form hook handles it
  });

  const { handleSubmit, reset, getValues, setValue } = methods;

  // Departments may load after the form opens
  React.useEffect(() => {
    if (!getValues("department_id") && defaultDept) setValue("department_id", defaultDept);
  }, [defaultDept, getValues, setValue]);

  const onSubmit = async (data: AddContractorFormData) => {
    const dept = departments?.find((d) => d.id === data.department_id);

    setSubmitError(null);
    try {
    await addContractorMutation.mutateAsync({
      name: data.name,
      phone_number: data.phone,
      email: data.email,
      department_id: data.department_id,
      department_name: dept?.name || "",
      role_type: data.is_contractor ? "CONTRACTOR_LEAD" : "FIELD_TECHNICIAN",
      position_title: data.position_title,
      specialization: data.specialization,
      is_contractor: data.is_contractor,
      contractor_company_name: data.is_contractor ? data.contractor_company_name : undefined,
      license_number: data.is_contractor ? data.license_number : undefined,
      performance_score: 95,
      is_available: true,
    });

    onClose();
    reset();
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Could not save. Please try again.");
    }
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-2">
        <FieldGroup className="gap-3">
          <AddContractorFields />
        </FieldGroup>

        {submitError && (
          <p className="text-sm text-destructive" role="alert">{submitError}</p>
        )}

        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 pt-3 border-t border-border">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onClose}
            className="w-full sm:w-auto"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            size="sm"
            disabled={addContractorMutation.isPending}
            className="w-full sm:w-auto"
          >
            {addContractorMutation.isPending ? "Adding..." : "Confirm Registration"}
          </Button>
        </div>
      </form>
    </FormProvider>
  );
}
