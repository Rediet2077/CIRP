"use client";

import React from "react";
import { AssetRecord } from "@/modules/assets/types/asset_types";
import { ReportRecord } from "@/modules/reports/types/report_types";
import { getCoordinateBounds, isValidGeographicPoint, projectCoordinate } from "./coordinate_projection";

interface MapCanvasProps {
  visibleAssets: AssetRecord[];
  visibleReports: ReportRecord[];
  selectedPinAsset: AssetRecord | null;
  onSelectPin: (asset: AssetRecord) => void;
  onSelectReport: (report: ReportRecord) => void;
  isLoading: boolean;
}

export function MapCanvas({
  visibleAssets,
  visibleReports,
  selectedPinAsset,
  onSelectPin,
  onSelectReport,
  isLoading,
}: MapCanvasProps) {
  const assetsWithLocation = visibleAssets.filter(isValidGeographicPoint);
  const reportsWithLocation = visibleReports.filter((report) =>
    isValidGeographicPoint({ latitude: report.citizen_latitude, longitude: report.citizen_longitude }),
  );
  const coordinates = [
    ...assetsWithLocation,
    ...reportsWithLocation.map((report) => ({ latitude: report.citizen_latitude, longitude: report.citizen_longitude })),
  ];
  const bounds = coordinates.length ? getCoordinateBounds(coordinates) : null;
  const toMapX = (lng: number) => bounds ? projectCoordinate(lng, bounds.minLng, bounds.maxLng) : 50;
  const toMapY = (lat: number) => bounds ? 92 - projectCoordinate(lat, bounds.minLat, bounds.maxLat) : 50;

  if (isLoading) {
    return (
      <div className="text-sm font-normal text-muted-foreground">
        Loading GIS telemetry data...
      </div>
    );
  }

  if (!coordinates.length || !bounds) {
    return <div className="p-8 text-center text-sm text-muted-foreground">No assets or reports with valid coordinates are available in this scope.</div>;
  }

  return (
    <svg
      viewBox="0 0 100 100"
      className="w-full h-full object-cover select-none cursor-crosshair"
      preserveAspectRatio="none"
    >
      <defs>
        <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
          <path d="M 10 0 L 0 0 0 10" fill="none" stroke="currentColor" strokeWidth="0.1" className="text-border/60" />
        </pattern>
      </defs>

      <rect width="100" height="100" fill="url(#grid)" />
      <text x="8" y="5" className="text-[2px] fill-muted-foreground">Recorded coordinates · no basemap or boundary data configured</text>
      <text x="8" y="97" className="text-[2px] fill-muted-foreground">{bounds.minLng.toFixed(4)}° to {bounds.maxLng.toFixed(4)}° longitude</text>
      <text x="91" y="95" textAnchor="end" className="text-[2px] fill-muted-foreground">{bounds.minLat.toFixed(4)}° to {bounds.maxLat.toFixed(4)}° latitude</text>

      {/* Interactive Pins */}
      {assetsWithLocation.map((asset) => {
        const x = toMapX(asset.longitude);
        const y = toMapY(asset.latitude);
        const isSelected = selectedPinAsset?.id === asset.id;

        let fillColor = "#10b981";
        if (asset.status === "UNDER_MAINTENANCE") fillColor = "#f59e0b";
        if (asset.status === "DAMAGED") fillColor = "#ef4444";
        if (asset.status === "INACTIVE" || asset.status === "DECOMMISSIONED") fillColor = "#64748b";

        return (
          <g
            key={asset.id}
            onClick={() => onSelectPin(asset)}
            className="cursor-pointer transition-transform duration-150 hover:scale-125"
            style={{ transformOrigin: `${x}px ${y}px` }}
          >
            {asset.status === "DAMAGED" && (
              <circle
                cx={x}
                cy={y}
                r="3.5"
                fill="none"
                stroke="#ef4444"
                strokeWidth="0.4"
                opacity="0.7"
                className="animate-ping"
              />
            )}

            {isSelected && (
              <circle
                cx={x}
                cy={y}
                r="4"
                fill="none"
                stroke="#ffffff"
                strokeWidth="0.6"
                strokeDasharray="1 0.5"
              />
            )}

            <circle
              cx={x}
              cy={y}
              r={isSelected ? "2.2" : "1.6"}
              fill={fillColor}
              stroke="#000000"
              strokeWidth="0.4"
            />

            <text
              x={x + 2.5}
              y={y + 0.8}
              className="text-[1.8px] font-medium fill-foreground select-none pointer-events-none drop-shadow-md"
            >
              {asset.asset_code}
            </text>
          </g>
        );
      })}

      {reportsWithLocation.map((report) => {
        const x = toMapX(report.citizen_longitude);
        const y = toMapY(report.citizen_latitude);
        const color = report.priority === "CRITICAL" ? "#dc2626" : report.priority === "HIGH" ? "#ea580c" : report.priority === "MEDIUM" ? "#d97706" : "#2563eb";
        return (
          <g
            key={`report-${report.id}`}
            role="button"
            tabIndex={0}
            aria-label={`${report.report_code}, ${report.priority} priority, ${report.status}`}
            onClick={() => onSelectReport(report)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onSelectReport(report);
              }
            }}
            className="cursor-pointer"
          >
            <title>{`${report.report_code} · ${report.priority} · ${report.status}`}</title>
            <path d={`M ${x} ${y - 2.8} C ${x - 2.2} ${y - 0.3}, ${x - 2} ${y + 1.6}, ${x} ${y + 2} C ${x + 2} ${y + 1.6}, ${x + 2.2} ${y - 0.3}, ${x} ${y - 2.8} Z`} fill={color} stroke="white" strokeWidth="0.4" />
            <circle cx={x} cy={y - 0.4} r="0.65" fill="white" />
          </g>
        );
      })}
    </svg>
  );
}
