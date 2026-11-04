"use client";

import React from "react";
import Link from "next/link";
import { Badge } from "@/ui/badge";
import { Button } from "@/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/ui/select";
import { PlusIcon } from "@phosphor-icons/react";
import { useMapData } from "../hooks/list/use_map_data";
import { useReportList } from "@/modules/reports/hooks/list/use_report_list";
import { useReportUIStore } from "@/modules/reports/store/report_ui_store";
import { ReportDetailsDialog } from "@/modules/reports/components/dialogs/report_details_dialog";
import { isValidGeographicPoint } from "./subcomponents/coordinate_projection";
import { useMapUIStore } from "../store/map_ui_store";
import { useAssetUIStore } from "@/modules/assets/store/asset_ui_store";
import { useNavigationStore } from "@/modules/shared/store/navigation_store";
import { MapCanvas } from "./subcomponents/map_canvas";
import { MapAssetOverlay } from "./subcomponents/map_asset_overlay";

export function MapView() {
  const { selectedDepartmentFilter, currentUserRole, activeOfficerDepartmentId } = useNavigationStore();
  const effectiveDept = currentUserRole === "DEPARTMENT_ADMIN" ? activeOfficerDepartmentId : selectedDepartmentFilter;

  const { data: assets, isLoading, error: assetsError } = useMapData(effectiveDept);
  const { data: reports, isLoading: reportsLoading, error: reportsError } = useReportList(effectiveDept);
  const { layerFilter, setLayerFilter, selectedPinAsset, setSelectedPinAsset } = useMapUIStore();
  const { openDetailsDialog } = useAssetUIStore();
  const openReportDetails = useReportUIStore((state) => state.openDetailsDialog);

  const assetList = assets || [];

  const visibleAssets = assetList.filter((asset) => {
    if (layerFilter === "reports") return false;
    if (layerFilter === "all") return true;
    return asset.asset_type_id === layerFilter;
  });
  const reportList = reports || [];
  const visibleReports = layerFilter === "all" || layerFilter === "reports" ? reportList : [];
  const plottedCount = visibleAssets.filter(isValidGeographicPoint).length + visibleReports.filter((report) =>
    isValidGeographicPoint({ latitude: report.citizen_latitude, longitude: report.citizen_longitude }),
  ).length;

  return (
    <div className="flex flex-1 flex-col gap-6 p-4 md:p-6 w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            GIS Reports & Infrastructure Map
          </h1>
          <p className="text-sm font-normal text-muted-foreground mt-1">
            Plots reports and assets from their recorded coordinates. No road basemap or boundary service is configured.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/dashboard/register-asset">
            <Button
              size="sm"
              className="h-9 text-sm font-medium gap-1.5"
            >
              <PlusIcon weight="bold" className="size-3.5" />
              <span>Register Asset</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Layer Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-lg border border-border bg-card">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Map Layer:</span>
          <Select value={layerFilter} onValueChange={(val) => setLayerFilter(val || "all")}>
            <SelectTrigger className="h-9 text-sm font-normal w-52 bg-background">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all" className="text-sm font-normal">Reports & Assets</SelectItem>
              <SelectItem value="reports" className="text-sm font-normal">Reports only</SelectItem>
              <SelectItem value="street_light" className="text-sm font-normal">Street Lights & Poles</SelectItem>
              <SelectItem value="road" className="text-sm font-normal">Roads & Corridors</SelectItem>
              <SelectItem value="water_point" className="text-sm font-normal">Water Points & Mains</SelectItem>
              <SelectItem value="drainage" className="text-sm font-normal">Drainage Canals</SelectItem>
              <SelectItem value="waste_bin" className="text-sm font-normal">Waste Compactor Depots</SelectItem>
              <SelectItem value="public_building" className="text-sm font-normal">Public Buildings</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-4 text-sm font-normal text-muted-foreground">
          <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-full bg-emerald-500 inline-block" /> Active asset</span>
          <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-full bg-red-500 inline-block" /> Critical report</span>
          <span className="flex items-center gap-1.5"><span className="size-2.5 rounded-full bg-blue-600 inline-block" /> Other report</span>
          <Badge variant="outline" className="text-sm font-normal px-2.5 py-0.5">
            {plottedCount} Locations Plotted
          </Badge>
        </div>
      </div>

      {/* Interactive GIS Vector Map Canvas */}
      <div className="relative w-full h-[600px] rounded-xl border border-border bg-card overflow-hidden shadow-inner flex items-center justify-center">
        {assetsError || reportsError ? (
          <div role="alert" className="m-6 rounded-md border border-destructive/40 p-4 text-sm text-destructive">
            Map data could not be loaded: {assetsError?.message || reportsError?.message}
          </div>
        ) : (
          <MapCanvas
            visibleAssets={visibleAssets}
            visibleReports={visibleReports}
            selectedPinAsset={selectedPinAsset}
            onSelectPin={setSelectedPinAsset}
            onSelectReport={(report) => {
              setSelectedPinAsset(null);
              openReportDetails(report.id);
            }}
            isLoading={isLoading || reportsLoading}
          />
        )}

        {selectedPinAsset && visibleAssets.some((asset) => asset.id === selectedPinAsset.id) && (
          <MapAssetOverlay
            asset={selectedPinAsset}
            onClose={() => setSelectedPinAsset(null)}
            onInspect={openDetailsDialog}
          />
        )}
      </div>
      <ReportDetailsDialog />
    </div>
  );
}
