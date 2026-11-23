"use client";

import React from "react";
import { Button } from "@/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/ui/dialog";
import { useDeleteReport } from "../../hooks/update/use_delete_report";
import { ReportRecord } from "../../types/report_types";

interface DeleteReportDialogProps {
  report: ReportRecord;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DeleteReportDialog({ report, open, onOpenChange }: DeleteReportDialogProps) {
  const mutation = useDeleteReport();

  const confirm = async () => {
    await mutation.mutateAsync(report.id);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Delete {report.report_code}?</DialogTitle>
          <DialogDescription>
            This permanently removes the resolved report "{report.title}", its work order and its photos.
            It also disappears from the citizen&apos;s app. This cannot be undone.
          </DialogDescription>
        </DialogHeader>
        {mutation.error && (
          <p role="alert" className="text-sm text-destructive">{mutation.error.message}</p>
        )}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button type="button" variant="destructive" onClick={confirm} disabled={mutation.isPending}>
            {mutation.isPending ? "Deleting..." : "Delete permanently"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
