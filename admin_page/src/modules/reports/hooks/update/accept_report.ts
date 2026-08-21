import { API_BASE_URL } from "@/lib/api-client";
import { mockDataStore } from "@/modules/shared/services/mock_storage";
import { TaskRecord } from "@/modules/shared/types/cirp_schema";
import { AcceptReportInput } from "../../types/report_types";

export async function acceptReport(input: AcceptReportInput): Promise<TaskRecord | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/reports/${input.reportId}/accept/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
    });

    const resData = await response.json();

    if (response.ok && resData.success) {
      const taskId = resData.task_id || `task-${Date.now()}`;
      const taskNumber = resData.task_number || `TSK-${input.reportId.substring(0, 8)}`;
      
      const taskRecord: TaskRecord = {
        id: taskId,
        task_code: taskNumber,
        report_id: input.reportId,
        report_code: `RPT-${input.reportId.substring(0, 8)}`,
        asset_id: "asset-01",
        asset_code: "INFRA-GENERAL",
        asset_type_label: "Infrastructure Malfunction",
        department_id: "dept-01",
        department_name: "Public Works & Maintenance",
        assigned_worker_id: input.assignedWorkerId || "worker-01",
        assigned_worker_name: "Field Technician Lead",
        is_contractor: false,
        work_description: input.workDescription,
        internal_note: input.internalNote,
        priority: input.priority || "HIGH",
        status: "ASSIGNED",
        progress_percentage: 0,
        created_at: new Date().toISOString(),
        deadline_date: input.deadlineDate || new Date(Date.now() + 3 * 86400000).toISOString().split('T')[0],
        original_deadline_date: input.deadlineDate || new Date(Date.now() + 3 * 86400000).toISOString().split('T')[0],
        is_overdue: false,
        days_overdue: 0,
        progress_notes: [],
        extensions: [],
      };

      return taskRecord;
    }
  } catch (error) {
    console.warn("API error on acceptReport, using fallback:", error);
  }

  // Fallback to local store
  let task = mockDataStore.acceptReport(input.reportId, {
    priority: input.priority,
    assignedWorkerId: input.assignedWorkerId,
    deadlineDate: input.deadlineDate,
    workDescription: input.workDescription,
    internalNote: input.internalNote,
  });

  if (!task) {
    // Generate synthetic task if report existed in live DB instead of mock store
    task = {
      id: `task-${Date.now()}`,
      task_code: `TSK-${input.reportId.substring(0, 8)}`,
      report_id: input.reportId,
      report_code: `RPT-${input.reportId.substring(0, 8)}`,
      asset_id: "asset-01",
      asset_code: "INFRA-GENERAL",
      asset_type_label: "Infrastructure Malfunction",
      department_id: "dept-01",
      department_name: "Public Works & Maintenance",
      assigned_worker_id: input.assignedWorkerId || "worker-01",
      assigned_worker_name: "Field Technician Lead",
      is_contractor: false,
      work_description: input.workDescription,
      internal_note: input.internalNote,
      priority: input.priority || "HIGH",
      status: "ASSIGNED",
      progress_percentage: 0,
      created_at: new Date().toISOString(),
      deadline_date: input.deadlineDate || new Date(Date.now() + 3 * 86400000).toISOString().split('T')[0],
      original_deadline_date: input.deadlineDate || new Date(Date.now() + 3 * 86400000).toISOString().split('T')[0],
      is_overdue: false,
      days_overdue: 0,
      progress_notes: [],
      extensions: [],
    };
  }

  return task;
}
