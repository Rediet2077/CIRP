"use client";

import React, { useState } from "react";
import { Alert, AlertDescription } from "@/ui/alert";
import { Badge } from "@/ui/badge";
import { Button } from "@/ui/button";
import { Input } from "@/ui/input";
import { Label } from "@/ui/label";
import { Switch } from "@/ui/switch";
import { Textarea } from "@/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/ui/select";
import { ReportPriority } from "@/modules/shared/types/enums";
import { TaskRecord } from "@/modules/shared/types/cirp_schema";
import { useAcceptReport } from "../../hooks/update/use_accept_report";
import { ReportRecord } from "../../types/report_types";
import { StaffContractorRecord } from "@/modules/contractors/types/contractor_types";

interface AcceptReportFormProps {
  report: ReportRecord;
  staffContractors: StaffContractorRecord[];
  onClose: () => void;
}

const SLA_DAYS: Record<ReportPriority, number> = {
  LOW: 7,
  MEDIUM: 3,
  HIGH: 2,
  CRITICAL: 1,
};

function dateInDays(days: number): string {
  return new Date(Date.now() + days * 86400000).toISOString().substring(0, 10);
}

function deliveryText(channel?: { status: string; detail?: string }): {
  text: string;
  ok: boolean;
} {
  if (!channel) return { text: "Not requested", ok: false };
  if (channel.status === "sent") return { text: `Sent to ${channel.detail ?? "assignee"}`, ok: true };
  if (channel.status === "failed") return { text: `Failed: ${channel.detail ?? "unknown error"}`, ok: false };
  return { text: `Not sent: ${channel.detail ?? "skipped"}`, ok: false };
}

export function AcceptReportForm({ report, staffContractors, onClose }: AcceptReportFormProps) {
  const acceptReportMutation = useAcceptReport();

  // The API may return lowercase priorities ("high")
  const initialPriority = (report.priority || "HIGH").toUpperCase() as ReportPriority;
  const [priority, setPriority] = useState<ReportPriority>(initialPriority);
  const [pickedWorkerId, setPickedWorkerId] = useState<string>("");
  const [deadlineDate, setDeadlineDate] = useState<string>(
    dateInDays(SLA_DAYS[initialPriority] ?? SLA_DAYS.HIGH)
  );
  const [deadlineEdited, setDeadlineEdited] = useState(false);
  const [workDescription, setWorkDescription] = useState<string>(
    "Inspect infrastructure damage, isolate fault, deploy replacement parts and perform functional verification."
  );
  const [internalNote, setInternalNote] = useState<string>("");
  const [notifyEmail, setNotifyEmail] = useState(true);
  const [notifySms, setNotifySms] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);
  const [createdTask, setCreatedTask] = useState<TaskRecord | null>(null);

  // Contractors first, then staff; the list loads after the form mounts
  const sortedStaff = [...staffContractors].sort(
    (a, b) => Number(b.is_contractor) - Number(a.is_contractor)
  );
  const assignedWorkerId = pickedWorkerId || sortedStaff[0]?.id || "";
  const worker = sortedStaff.find((w) => w.id === assignedWorkerId);

  const handlePriorityChange = (value: ReportPriority) => {
    setPriority(value);
    if (!deadlineEdited) setDeadlineDate(dateInDays(SLA_DAYS[value]));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    if (!assignedWorkerId) {
      setFormError("Select who will handle this problem.");
      return;
    }
    try {
      const task = await acceptReportMutation.mutateAsync({
        reportId: report.id,
        priority,
        assignedWorkerId,
        deadlineDate,
        workDescription,
        internalNote,
        notifyEmail: notifyEmail && Boolean(worker?.email),
        notifySms: notifySms && Boolean(worker?.phone_number),
      });
      if (task?.notification) {
        setCreatedTask(task);
      } else {
        onClose();
      }
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Could not assign this report.");
    }
  };

  if (createdTask) {
    const email = deliveryText(createdTask.notification?.email);
    const sms = deliveryText(createdTask.notification?.sms);
    return (
      <div className="flex flex-col gap-4 py-2">
        <Alert>
          <AlertDescription className="text-sm">
            Work order <span className="font-medium">{createdTask.task_code}</span> was created and
            assigned to <span className="font-medium">{createdTask.assigned_worker_name}</span>.
          </AlertDescription>
        </Alert>
        <div className="rounded-lg border border-border divide-y divide-border text-sm">
          <div className="flex items-start justify-between gap-3 p-3">
            <span className="text-muted-foreground">Email</span>
            <span className={email.ok ? "text-foreground" : "text-destructive"}>{email.text}</span>
          </div>
          <div className="flex items-start justify-between gap-3 p-3">
            <span className="text-muted-foreground">SMS</span>
            <span className={sms.ok ? "text-foreground" : "text-muted-foreground"}>{sms.text}</span>
          </div>
        </div>
        <div className="flex justify-end pt-3 border-t border-border">
          <Button type="button" size="sm" onClick={onClose} className="h-9 text-sm font-medium">
            Done
          </Button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 py-2">
      {/* Target Asset Reference */}
      <div className="p-3 bg-muted/30 rounded-lg border border-border flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-sm">
        <div>
          <span className="text-sm text-muted-foreground block font-normal">Target Infrastructure Asset</span>
          <span className="font-medium text-foreground">
            {report.asset_code || "Unlinked Infrastructure"}
          </span>
          <span className="text-sm text-muted-foreground block font-normal">{report.department_name}</span>
        </div>
        <Badge variant="outline" className="text-sm font-normal py-0.5 self-start sm:self-auto">
          {report.category_name}
        </Badge>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Priority Assignment */}
        <div className="space-y-1.5">
          <Label className="text-sm font-medium">Assigned Priority SLA</Label>
          <Select
            value={priority}
            onValueChange={(val) => {
              if (val) handlePriorityChange(val as ReportPriority);
            }}
          >
            <SelectTrigger className="h-9 text-sm font-normal">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="LOW" label="LOW (7-Day SLA)" className="text-sm font-normal">LOW (7-Day SLA)</SelectItem>
              <SelectItem value="MEDIUM" label="MEDIUM (3-Day SLA)" className="text-sm font-normal">MEDIUM (3-Day SLA)</SelectItem>
              <SelectItem value="HIGH" label="HIGH (48-Hour SLA)" className="text-sm font-normal">HIGH (48-Hour SLA)</SelectItem>
              <SelectItem value="CRITICAL" label="CRITICAL (12-Hour SLA)" className="text-sm font-normal">CRITICAL (12-Hour SLA)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label className="text-sm font-medium">Assign Field Technician / Contractor</Label>
          <Select
            value={assignedWorkerId}
            onValueChange={(val) => {
              if (val) setPickedWorkerId(val);
            }}
          >
            <SelectTrigger className="h-9 text-sm font-normal">
              <SelectValue placeholder="Select Assignee" />
            </SelectTrigger>
            <SelectContent>
              {sortedStaff.map((w) => (
                <SelectItem key={w.id} value={w.id} label={`${w.name} (${w.is_contractor ? "Contractor" : "Staff"})`} className="text-sm font-normal">
                  {w.name} ({w.is_contractor ? "Contractor" : "Staff"})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {sortedStaff.length === 0 && (
        <Alert variant="destructive">
          <AlertDescription className="text-sm">
            No staff or contractors are registered yet. Add one on the Contractors page first.
          </AlertDescription>
        </Alert>
      )}

      {/* Who will be contacted */}
      {worker && (
        <div className="rounded-lg border border-border p-3 flex flex-col gap-3">
          <div className="text-sm">
            <span className="font-medium text-foreground">
              {worker.is_contractor && worker.contractor_company_name
                ? worker.contractor_company_name
                : worker.name}
            </span>
            <span className="block text-muted-foreground">
              {worker.email || "No email on file"} · {worker.phone_number || "No phone on file"}
            </span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label className="flex items-center justify-between gap-3 text-sm">
              <span>Inform by email</span>
              <Switch
                checked={notifyEmail && Boolean(worker.email)}
                onCheckedChange={setNotifyEmail}
                disabled={!worker.email}
              />
            </label>
            <label className="flex items-center justify-between gap-3 text-sm">
              <span>Inform by SMS</span>
              <Switch
                checked={notifySms && Boolean(worker.phone_number)}
                onCheckedChange={setNotifySms}
                disabled={!worker.phone_number}
              />
            </label>
          </div>
        </div>
      )}

      {/* Deadline */}
      <div className="space-y-1.5">
        <Label className="text-sm font-medium">Expected Completion Deadline Date</Label>
        <Input
          type="date"
          value={deadlineDate}
          min={dateInDays(0)}
          onChange={(e) => {
            setDeadlineEdited(true);
            setDeadlineDate(e.target.value);
          }}
          className="h-9 text-sm font-normal"
          required
        />
      </div>

      {/* Work Description */}
      <div className="space-y-1.5">
        <Label className="text-sm font-medium">Field Work Order Instructions</Label>
        <Textarea
          value={workDescription}
          onChange={(e) => setWorkDescription(e.target.value)}
          className="text-sm font-normal min-h-[70px]"
          required
        />
      </div>

      {/* Internal Notes */}
      <div className="space-y-1.5">
        <Label className="text-sm font-medium">Internal Operations Note</Label>
        <Input
          value={internalNote}
          onChange={(e) => setInternalNote(e.target.value)}
          className="h-9 text-sm font-normal"
        />
      </div>

      {formError && (
        <Alert variant="destructive">
          <AlertDescription className="text-sm">{formError}</AlertDescription>
        </Alert>
      )}

      <div className="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-end gap-2 pt-3 border-t border-border">
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onClose}
          className="w-full sm:w-auto h-9 text-sm font-normal"
        >
          Cancel
        </Button>
        <Button
          type="submit"
          size="sm"
          disabled={acceptReportMutation.isPending || sortedStaff.length === 0}
          className="w-full sm:w-auto h-9 text-sm font-medium"
        >
          {acceptReportMutation.isPending ? "Assigning..." : "Assign & Notify"}
        </Button>
      </div>
    </form>
  );
}
