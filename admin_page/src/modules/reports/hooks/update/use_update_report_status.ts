"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { markReportInProgress, markReportResolved } from "./update_report_status";
import { REPORT_LIST_QUERY_KEY } from "../list/report_list";

export function useMarkReportInProgress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (reportId: string) => markReportInProgress(reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORT_LIST_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["tasks", "list"] });
    },
  });
}

export function useMarkReportResolved() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ reportId, note }: { reportId: string; note?: string }) =>
      markReportResolved(reportId, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REPORT_LIST_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["tasks", "list"] });
    },
  });
}
