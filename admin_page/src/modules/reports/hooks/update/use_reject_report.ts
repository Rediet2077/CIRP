"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { rejectReport, RejectReportInput } from "./reject_report";
import { REPORT_LIST_QUERY_KEY } from "../list/report_list";
import { REPORT_DETAILS_QUERY_KEY } from "../items/report_details";

export function useRejectReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: RejectReportInput) => rejectReport(input),
    onSuccess: (_report, input) => {
      queryClient.invalidateQueries({ queryKey: REPORT_LIST_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: [...REPORT_DETAILS_QUERY_KEY, input.reportId] });
      queryClient.invalidateQueries({ queryKey: ["public", "reports"] });
    },
  });
}
