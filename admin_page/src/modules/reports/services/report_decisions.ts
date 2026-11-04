import { localStorageService } from "@/modules/shared/services/local_storage";
import { mockDataStore } from "@/modules/shared/services/mock_storage";
import { ReportRecord } from "@/modules/shared/types/cirp_schema";

const DECISIONS_KEY = "cirp-demo-report-decisions";
interface Decision { status: "DISPUTED"; reason: string; department_id: string; report_code: string; department_name: string; rejected_at: string; }
type DecisionMap = Record<string, Decision>;

export function withDemoDecisions(report: ReportRecord): ReportRecord {
  const decision = localStorageService.getItem<DecisionMap>(DECISIONS_KEY)?.[report.id];
  return decision?.department_id === report.department_id
    ? { ...report, status: decision.status }
    : report;
}

export function getDemoRejectionReason(reportId: string): string | undefined {
  return localStorageService.getItem<DecisionMap>(DECISIONS_KEY)?.[reportId]?.reason;
}

export function rejectDemoReport(reportId: string, departmentId: string, reason: string): ReportRecord {
  const report = mockDataStore.getReportById(reportId);
  if (!report || report.department_id !== departmentId || report.status !== "NEW") {
    throw new Error("This report is no longer available for a decision in your department.");
  }
  const decisions = localStorageService.getItem<DecisionMap>(DECISIONS_KEY) || {};
  decisions[reportId] = {
    status: "DISPUTED", reason, department_id: departmentId,
    report_code: report.report_code, department_name: report.department_name,
    rejected_at: new Date().toISOString(),
  };
  localStorageService.setItem(DECISIONS_KEY, decisions);
  return { ...report, status: "DISPUTED" };
}
