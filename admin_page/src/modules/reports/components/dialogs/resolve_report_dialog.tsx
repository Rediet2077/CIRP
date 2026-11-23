"use client";

import React, { useState } from "react";
import { Button } from "@/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/ui/dialog";
import { Label } from "@/ui/label";
import { Textarea } from "@/ui/textarea";
import { useVerifyResolveTask } from "@/modules/tasks/hooks/update/use_verify_resolve_task";
import { ReportRecord } from "../../types/report_types";

interface ResolveReportDialogProps {
  report: ReportRecord;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ResolveReportDialog({ report, open, onOpenChange }: ResolveReportDialogProps) {
  const [note, setNote] = useState("Repair completed and checked on site.");
  const mutation = useVerifyResolveTask();

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!report.linked_task_id) return;
    await mutation.mutateAsync({
      taskId: report.linked_task_id,
      officerName: "Department Officer",
      resolutionNotes: note.trim() || "Resolved.",
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Mark {report.report_code} as resolved</DialogTitle>
          <DialogDescription>
            The citizen will see this report as Resolved at 100% in the mobile app and get a notification.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="resolve-note">Resolution note (the citizen sees this)</Label>
            <Textarea id="resolve-note" value={note} onChange={(e) => setNote(e.target.value)} />
          </div>
          {!report.linked_task_id && (
            <p role="alert" className="text-sm text-destructive">
              This report has no assigned work order yet. Assign it first.
            </p>
          )}
          {mutation.error && (
            <p role="alert" className="text-sm text-destructive">{mutation.error.message}</p>
          )}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={mutation.isPending || !report.linked_task_id}>
              {mutation.isPending ? "Saving..." : "Mark as resolved"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
