"use client";

import React from "react";
import { ReportRecord } from "../../types/report_types";

interface ReportAiInsightsProps {
  report: ReportRecord;
}

export function ReportAiInsights({ report }: ReportAiInsightsProps) {
  if (!report.ai_category_prediction && !report.ai_duplicate_analysis) {
    return null;
  }

  return (
    <div className="space-y-3">
      <p className="rounded-md border border-amber-500/30 bg-amber-500/5 p-3 text-xs text-muted-foreground">
        Automated indicators are suggestions for staff review. They are not proof of fraud or a confirmed duplicate.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
      {report.ai_category_prediction && (
        <div className="text-sm space-y-1">
          <span className="text-muted-foreground font-medium">AI Category Prediction</span>
          <div className="font-medium text-foreground">
            {report.ai_category_prediction.suggested_category}
            <span className="text-muted-foreground font-normal ml-2">
              ({(report.ai_category_prediction.confidence * 100).toFixed(0)}% Confidence)
            </span>
          </div>
        </div>
      )}

      {report.ai_duplicate_analysis && (
        <div className="text-sm space-y-1">
          <span className="text-muted-foreground font-medium">Duplicate Detection</span>
          <div className="font-medium text-foreground">
            {report.ai_duplicate_analysis.has_potential_duplicate ? (
              <span className="text-amber-700">Potential match · review needed</span>
            ) : (
              <span>No duplicate indicator returned</span>
            )}
          </div>
          <div className="text-muted-foreground">
            {report.ai_duplicate_analysis.has_potential_duplicate ? (
              <span>
                Matches {report.ai_duplicate_analysis.duplicate_report_code} (
                {((report.ai_duplicate_analysis.similarity_score || 0) * 100).toFixed(0)}% similarity)
              </span>
            ) : (
              <span>No potential match was returned by the configured analysis.</span>
            )}
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
