"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { rejectReport } from "./reject_report";
import { REPORT_LIST_QUERY_KEY } from "../list/report_list";

export function useRejectReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ reportId, reason }: { reportId: string; reason?: string }) =>
      rejectReport(reportId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORT_LIST_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["tasks", "list"] });
    },
  });
}
