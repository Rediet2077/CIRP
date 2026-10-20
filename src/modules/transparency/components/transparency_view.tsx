"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/card";
import { Input } from "@/ui/input";
import { fetchPublicReports } from "../services/public_report_list";

function statusVariant(status: string): "default" | "secondary" | "outline" | "destructive" {
  if (status === "Rejected") return "destructive";
  if (status === "Resolved") return "default";
  if (status === "Work in progress") return "secondary";
  return "outline";
}

export function TransparencyView() {
  const [search, setSearch] = useState("");
  const { data: reports = [], isLoading, error } = useQuery({
    queryKey: ["public", "reports"],
    queryFn: fetchPublicReports,
    staleTime: 30_000,
  });
  const filtered = reports.filter((report) =>
    `${report.reference} ${report.category} ${report.general_location || ""} ${report.status}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-6 p-4 md:p-8">
      <header className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-wide text-primary">Community Infrastructure Reporting Platform</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">Public report tracking</h1>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
            Follow public infrastructure reports by reference number and see their latest published status.
          </p>
        </div>
        {!process.env.NEXT_PUBLIC_API_URL && (
          <Badge variant="outline" className="w-fit border-amber-500/40 text-amber-700">Demo sample data</Badge>
        )}
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Published reports</CardTitle>
          <CardDescription>Reporter contact details, internal notes, and risk-review information are excluded.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            aria-label="Search public reports"
            placeholder="Search reference, category, location, or status"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          {isLoading ? (
            <p className="py-8 text-center text-sm text-muted-foreground" aria-live="polite">Loading published reports…</p>
          ) : error ? (
            <p className="rounded-md border border-destructive/40 p-4 text-sm text-destructive" role="alert">
              Public report tracking is temporarily unavailable. Please try again later.
            </p>
          ) : filtered.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">No published reports match your search.</p>
          ) : (
            <ul className="divide-y divide-border">
              {filtered.map((report) => (
                <li key={report.reference} className="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <p className="font-medium">{report.category}</p>
                    <p className="text-sm text-muted-foreground">
                      {report.reference} · {report.general_location || "Location not published"}
                    </p>
                    <p className="text-xs text-muted-foreground">Submitted {new Date(report.submitted_at).toLocaleDateString()}</p>
                  </div>
                  <Badge variant={statusVariant(report.status)} className="w-fit">{report.status}</Badge>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
