import React from "react";
import {
  HouseIcon,
  BuildingsIcon,
  UsersIcon,
  BellIcon,
  GearIcon,
  FileTextIcon,
  PackageIcon,
  MapPinIcon,
  ChartBarIcon,
  ListChecksIcon,
  UsersFourIcon,
  FolderIcon,
  CalendarIcon,
  ClockIcon,
  IconProps,
} from "@phosphor-icons/react";
import { UserRole } from "../../types/enums";

export interface SidebarSubItem {
  title: string;
  url: string;
  icon: React.ComponentType<IconProps>;
}

export interface SidebarNavItem {
  title: string;
  url: string;
  icon: React.ComponentType<IconProps>;
  badgeCount?: number;
  badgeVariant?: "destructive" | "outline";
  pulse?: boolean;
  subItems?: SidebarSubItem[];
}

export interface SidebarNavGroupConfig {
  label: string;
  items: SidebarNavItem[];
}

export function getSidebarNavigationGroups(
  counts: {
    unreadNotificationsCount?: number;
  },
  userRole?: UserRole
): SidebarNavGroupConfig[] {
  // Debug logging
  console.log('🎯 getSidebarNavigationGroups called with role:', userRole);
  
  // Super Admin (Full System Access) - Comprehensive menu
  // Both SUPER_ADMIN and SYSTEM_ADMIN get full access
  if (userRole === "SUPER_ADMIN" || userRole === "SYSTEM_ADMIN") {
    console.log('✅ Matched SUPER_ADMIN/SYSTEM_ADMIN - returning full comprehensive menu');
    return [
      {
        label: "Main",
        items: [
          {
            title: "Dashboard",
            url: "/dashboard",
            icon: HouseIcon,
          },
          {
            title: "Reports",
            url: "/dashboard/reports",
            icon: FileTextIcon,
          },
          {
            title: "Analytics",
            url: "/dashboard/analytics",
            icon: ChartBarIcon,
          },
        ],
      },
      {
        label: "Organization",
        items: [
          {
            title: "Departments",
            url: "/dashboard/departments",
            icon: BuildingsIcon,
          },
          {
            title: "Users",
            url: "/dashboard/users",
            icon: UsersIcon,
          },
          {
            title: "Contractors",
            url: "/dashboard/contractors",
            icon: UsersFourIcon,
          },
        ],
      },
      {
        label: "Assets",
        items: [
          {
            title: "All Assets",
            url: "/dashboard/all-assets",
            icon: PackageIcon,
          },
          {
            title: "Asset Types",
            url: "/dashboard/asset-types",
            icon: FolderIcon,
          },
          {
            title: "Register Asset",
            url: "/dashboard/register-asset",
            icon: PackageIcon,
          },
        ],
      },
      {
        label: "Operations",
        items: [
          {
            title: "Tasks",
            url: "/dashboard/tasks",
            icon: ListChecksIcon,
          },
          {
            title: "Deadlines",
            url: "/dashboard/deadlines",
            icon: CalendarIcon,
          },
          {
            title: "Extensions",
            url: "/dashboard/extensions",
            icon: ClockIcon,
          },
        ],
      },
      {
        label: "Mapping",
        items: [
          {
            title: "Map",
            url: "/dashboard/map",
            icon: MapPinIcon,
          },
        ],
      },
      {
        label: "System",
        items: [
          {
            title: "Notifications",
            url: "/dashboard/notifications",
            icon: BellIcon,
            badgeCount: counts.unreadNotificationsCount,
            badgeVariant: "destructive",
          },
          {
            title: "Audit Logs",
            url: "/dashboard/audit-logs",
            icon: FileTextIcon,
          },
          {
            title: "Settings",
            url: "/dashboard/settings",
            icon: GearIcon,
          },
        ],
      },
    ];
  }

  // Department Admins (Role-based access) - Limited menu
  const isDepartmentAdmin = [
    "ROAD_ADMIN",
    "WATER_ADMIN",
    "ELECTRICITY_ADMIN",
    "DRAINAGE_ADMIN",
    "WASTE_ADMIN",
    "STREETLIGHT_ADMIN",
    "PUBLIC_FACILITIES_ADMIN",
    "DEPARTMENT_ADMIN",
  ].includes(userRole || "");

  if (isDepartmentAdmin) {
    console.log('✅ Matched Department Admin - returning limited menu (4 items)');
    return [
      {
        label: "Department Management",
        items: [
          {
            title: "Dashboard",
            url: "/dashboard",
            icon: HouseIcon,
          },
          {
            title: "Reports",
            url: "/dashboard/reports",
            icon: FileTextIcon,
          },
          {
            title: "Assets",
            url: "/dashboard/all-assets",
            icon: PackageIcon,
          },
          {
            title: "Notifications",
            url: "/dashboard/notifications",
            icon: BellIcon,
            badgeCount: counts.unreadNotificationsCount,
            badgeVariant: "destructive",
          },
        ],
      },
    ];
  }

  // Default menu (fallback for unrecognized roles)
  console.warn('⚠️ No role match - returning default menu');
  return [
    {
      label: "Platform Navigation",
      items: [
        {
          title: "Dashboard",
          url: "/dashboard",
          icon: HouseIcon,
        },
        {
          title: "Notifications",
          url: "/dashboard/notifications",
          icon: BellIcon,
          badgeCount: counts.unreadNotificationsCount,
          badgeVariant: "destructive",
        },
      ],
    },
  ];
}
