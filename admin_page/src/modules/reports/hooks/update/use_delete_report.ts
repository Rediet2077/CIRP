"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteReport } from "./delete_report";
import { REPORT_LIST_QUERY_KEY } from "../list/report_list";

export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reportId: string) => deleteReport(reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORT_LIST_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["tasks", "list"] });
    },
  });
}
