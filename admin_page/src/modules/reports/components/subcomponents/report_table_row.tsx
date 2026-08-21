"use client";

import React from "react";
import { TableRow, TableCell } from "@/ui/table";
import { Badge } from "@/ui/badge";
import { Button } from "@/ui/button";
import { ArrowSquareOutIcon, CheckIcon, XIcon, TrashIcon, PlayIcon, CheckCircleIcon } from "@phosphor-icons/react";
import { getPriorityBadge, getReportStatusBadge } from "@/modules/shared/components/triage_badges";
import { ReportRecord as CitizenReportItem } from "../../types/report_types";
import { useRejectReport } from "../../hooks/update/use_reject_report";
import { useDeleteReport } from "../../hooks/update/use_delete_report";
import { useMarkReportInProgress, useMarkReportResolved } from "../../hooks/update/use_update_report_status";

interface ReportTableRowProps {
  report: CitizenReportItem;
  onOpenAccept: (id: string) => void;
  onOpenDetails: (id: string) => void;
}

export function ReportTableRow({ report, onOpenAccept, onOpenDetails }: ReportTableRowProps) {
  const rejectReportMutation = useRejectReport();
  const deleteReportMutation = useDeleteReport();
  const inProgressMutation = useMarkReportInProgress();
  const resolveMutation = useMarkReportResolved();

  const handleReject = () => {
    if (confirm(`Are you sure you want to reject report ${report.report_code}? It will be removed from the active queue.`)) {
      rejectReportMutation.mutate({ reportId: report.id, reason: "Rejected by municipal admin." });
    }
  };

  const handleDelete = () => {
    if (confirm(`Are you sure you want to delete report ${report.report_code}? This action cannot be undone.`)) {
      deleteReportMutation.mutate(report.id);
    }
  };

  const handleStartWork = () => {
    inProgressMutation.mutate(report.id);
  };

  const handleResolve = () => {
    if (confirm(`Mark report ${report.report_code} as Resolved?`)) {
      resolveMutation.mutate({ reportId: report.id, note: "Verified and resolved by municipal administrator." });
    }
  };

  return (
    <TableRow className="border-border hover:bg-muted/30 transition-colors">
      <TableCell className="font-medium text-sm whitespace-nowrap">
        {report.report_code}
      </TableCell>
      <TableCell className="text-sm font-medium text-foreground max-w-[200px] truncate">
        {report.title}
      </TableCell>
      <TableCell className="text-sm font-normal text-muted-foreground whitespace-nowrap">
        {report.category_name}
      </TableCell>
      <TableCell className="text-sm whitespace-nowrap">
        {report.asset_code ? (
          <span className="font-medium text-foreground">{report.asset_code}</span>
        ) : (
          <Badge variant="outline" className="text-sm font-normal text-muted-foreground border-dashed">
            Unlinked
          </Badge>
        )}
      </TableCell>
      <TableCell className="text-sm font-normal text-foreground whitespace-nowrap">
        {report.department_name}
      </TableCell>
      <TableCell className="text-sm whitespace-nowrap">
        {getPriorityBadge(report.priority)}
      </TableCell>
      <TableCell className="text-sm whitespace-nowrap">
        {getReportStatusBadge(report.status)}
      </TableCell>
      <TableCell className="text-sm font-normal text-muted-foreground whitespace-nowrap">
        {report.submitted_at.split(" ")[0]}
      </TableCell>
      <TableCell className="text-right text-sm whitespace-nowrap min-w-[260px]">
        <div className="flex items-center justify-end gap-1.5">
          {report.status === "NEW" && (
            <>
              <Button
                size="sm"
                className="h-8 px-2.5 text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white gap-1"
                onClick={() => onOpenAccept(report.id)}
              >
                <CheckIcon className="w-3.5 h-3.5" />
                Accept
              </Button>

              <Button
                variant="destructive"
                size="sm"
                className="h-8 px-2.5 text-xs font-semibold gap-1"
                disabled={rejectReportMutation.isPending}
                onClick={handleReject}
              >
                <XIcon className="w-3.5 h-3.5" />
                Reject
              </Button>
            </>
          )}

          {report.status === "ACCEPTED" && (
            <Button
              size="sm"
              className="h-8 px-2.5 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white gap-1"
              disabled={inProgressMutation.isPending}
              onClick={handleStartWork}
            >
              <PlayIcon className="w-3.5 h-3.5" />
              Start Work
            </Button>
          )}

          {(report.status === "IN_PROGRESS" || report.status === "COMPLETED_PENDING_VERIFICATION") && (
            <Button
              size="sm"
              className="h-8 px-2.5 text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white gap-1"
              disabled={resolveMutation.isPending}
              onClick={handleResolve}
            >
              <CheckCircleIcon className="w-3.5 h-3.5" />
              Resolve
            </Button>
          )}

          {report.status === "RESOLVED" && (
            <Button
              variant="outline"
              size="sm"
              className="h-8 px-2 text-xs text-rose-600 hover:bg-rose-50 border-rose-200 font-medium gap-1"
              disabled={deleteReportMutation.isPending}
              onClick={handleDelete}
            >
              <TrashIcon className="w-3.5 h-3.5 text-rose-600" />
              Delete
            </Button>
          )}

          <Button
            variant="ghost"
            size="sm"
            className="h-8 px-2 text-xs text-primary font-medium gap-1"
            onClick={() => onOpenDetails(report.id)}
          >
            <span>Details</span>
            <ArrowSquareOutIcon className="w-3.5 h-3.5" />
          </Button>
        </div>
      </TableCell>
    </TableRow>
  );
}
