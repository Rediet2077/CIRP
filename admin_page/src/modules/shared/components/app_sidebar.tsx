"use client";

import React, { useEffect, useState } from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarRail,
} from "@/ui/sidebar";
import { useNavigationStore } from "../store/navigation_store";
import { useNotificationList } from "@/modules/notifications/hooks/list/use_notification_list";
import { SidebarHeaderSection } from "./sidebar/sidebar_header";
import { SidebarNavGroup } from "./sidebar/sidebar_nav_group";
import { SidebarUserFooter } from "./sidebar/sidebar_footer";
import { getSidebarNavigationGroups } from "./sidebar/sidebar_navigation_config";
import { localStorageService } from "../services/local_storage";

interface AuthSession {
  user: {
    email: string;
    role: string;
  };
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const {
    currentUserRole,
    selectedDepartmentFilter,
    activeOfficerDepartmentId,
  } = useNavigationStore();

  const [debugInfo, setDebugInfo] = useState<any>(null);

  useEffect(() => {
    // Debug: Check localStorage
    const session = localStorageService.getItem<AuthSession>("authSession");
    setDebugInfo({
      storageRole: session?.user?.role,
      storageEmail: session?.user?.email,
      storeRole: currentUserRole,
    });
  }, [currentUserRole]);

  const effectiveDept =
    currentUserRole === "DEPARTMENT_ADMIN"
      ? activeOfficerDepartmentId
      : selectedDepartmentFilter;

  const { data: notifications } = useNotificationList(effectiveDept);

  const notificationList = notifications || [];

  const counts = {
    unreadNotificationsCount: notificationList.filter((n) => !n.is_read).length,
  };

  const navGroups = getSidebarNavigationGroups(counts, currentUserRole);

  // Debug logging
  if (typeof window !== 'undefined' && debugInfo) {
    console.log('🔍 AppSidebar Debug:', {
      currentUserRole,
      storageRole: debugInfo.storageRole,
      storageEmail: debugInfo.storageEmail,
      navGroupsCount: navGroups.length,
      firstGroupLabel: navGroups[0]?.label,
      itemsCount: navGroups[0]?.items.length,
      allGroupLabels: navGroups.map(g => g.label),
      allItemCounts: navGroups.map(g => g.items.length)
    });
  }

  return (
    <Sidebar collapsible="icon" className="border-r border-border bg-sidebar" {...props}>
      <SidebarHeaderSection />

      <SidebarContent>
        {navGroups.map((group) => (
          <SidebarNavGroup key={group.label} group={group} />
        ))}
      </SidebarContent>

      <SidebarUserFooter />
      <SidebarRail />
    </Sidebar>
  );
}
