"use client";

import React, { useState } from "react";
import { Button } from "@/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/ui/dialog";
import { Label } from "@/ui/label";
import { Textarea } from "@/ui/textarea";
import { useRejectReport } from "../../hooks/update/use_reject_report";
import { ReportRecord } from "../../types/report_types";

interface RejectReportDialogProps { report: ReportRecord; open: boolean; onOpenChange: (open: boolean) => void; }

export function RejectReportDialog({ report, open, onOpenChange }: RejectReportDialogProps) {
  const [reason, setReason] = useState("");
  const mutation = useRejectReport();
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    await mutation.mutateAsync({ reportId: report.id, departmentId: report.department_id, reason });
    setReason("");
    onOpenChange(false);
  };

  return <Dialog open={open} onOpenChange={onOpenChange}>
    <DialogContent className="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>Reject assignment for {report.report_code}</DialogTitle>
        <DialogDescription>This report will be marked rejected for {report.department_name}. Add a reason for the decision.</DialogDescription>
      </DialogHeader>
      <form onSubmit={submit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="reject-reason">Reason</Label>
          <Textarea id="reject-reason" value={reason} onChange={(event) => setReason(event.target.value)} minLength={5} required placeholder="Explain why this report cannot be handled by this department." />
        </div>
        {mutation.error && <p role="alert" className="text-sm text-destructive">{mutation.error.message}</p>}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button type="submit" variant="destructive" disabled={mutation.isPending || reason.trim().length < 5}>
            {mutation.isPending ? "Rejecting..." : "Confirm rejection"}
          </Button>
        </div>
      </form>
    </DialogContent>
  </Dialog>;
}
