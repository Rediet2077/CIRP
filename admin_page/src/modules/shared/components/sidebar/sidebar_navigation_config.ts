import React from "react";
import {
  HouseIcon,
  BuildingsIcon,
  UsersIcon,
  BellIcon,
  GearIcon,
  FileTextIcon,
  PackageIcon,
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
  // City Administrator (SYSTEM_ADMIN) Menu
  if (userRole === "SYSTEM_ADMIN") {
    return [
      {
        label: "City Administration",
        items: [
          {
            title: "Dashboard",
            url: "/dashboard",
            icon: HouseIcon,
          },
          {
            title: "Departments",
            url: "/dashboard/departments",
            icon: BuildingsIcon,
          },
          {
            title: "New Applicants",
            url: "/dashboard/users",
            icon: UsersIcon,
          },
        ],
      },
    ];
  }

  // Department Administrator (DEPARTMENT_ADMIN) Menu
  if (userRole === "DEPARTMENT_ADMIN") {
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
            url: "/dashboard/all_assets",
            icon: PackageIcon,
          },
        ],
      },
    ];
  }

  // Default menu (fallback)
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
          title: "Notifications",
          url: "/dashboard/notifications",
          icon: BellIcon,
          badgeCount: counts.unreadNotificationsCount,
          badgeVariant: "destructive",
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
