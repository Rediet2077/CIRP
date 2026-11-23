"use client";

import React, { useState } from "react";
import { useNotificationList } from "../hooks/list/use_notification_list";
import { useNavigationStore } from "@/modules/shared/store/navigation_store";
import { NotificationsHeader } from "./notifications_header";
import { NotificationsCards } from "./notifications_cards";
import { NotificationsList } from "./notifications_list";
import { useQueryClient } from "@tanstack/react-query";
import { NOTIFICATION_LIST_QUERY_KEY } from "../hooks/list/notification_list";
import { setNotificationsRead } from "../hooks/list/notification_read";
import { NotificationRecord } from "../types/notification_types";

export function NotificationsView() {
  const {
    currentUserRole,
    selectedDepartmentFilter,
    activeOfficerDepartmentId,
  } = useNavigationStore();

  const effectiveDept =
    currentUserRole === "DEPARTMENT_ADMIN"
      ? activeOfficerDepartmentId
      : selectedDepartmentFilter;

  const { data: notifications, isLoading } = useNotificationList(effectiveDept);
  const queryClient = useQueryClient();
  const save = (ids: string[], read: boolean) =>
    setNotificationsRead(ids, read)
      .then(() => queryClient.invalidateQueries({ queryKey: NOTIFICATION_LIST_QUERY_KEY }))
      .catch(() => {});
  const [localList, setLocalList] = useState<NotificationRecord[] | null>(null);

  // Newly fetched data replaces the local copy
  React.useEffect(() => {
    setLocalList(null);
  }, [notifications]);

  const notificationList = localList || notifications || [];

  // Show the change at once, then save it so it is still read after a refresh
  const handleMarkAllRead = () => {
    const unreadIds = notificationList.filter((n) => !n.is_read).map((n) => n.id);
    setLocalList(notificationList.map((n) => ({ ...n, is_read: true })));
    if (unreadIds.length > 0) save(unreadIds, true);
  };

  const handleToggleRead = (id: string) => {
    const target = notificationList.find((n) => n.id === id);
    if (!target) return;
    setLocalList(
      notificationList.map((n) => (n.id === id ? { ...n, is_read: !n.is_read } : n))
    );
    save([id], !target.is_read);
  };

  if (isLoading && !localList) {
    return (
      <div className="flex flex-1 flex-col gap-6 p-4 md:p-6 w-full">
        <div className="animate-pulse flex flex-col gap-4">
          <div className="h-10 bg-muted/30 rounded w-1/3" />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-muted/20 rounded-lg border border-border" />
            ))}
          </div>
          <div className="h-64 bg-muted/20 rounded-lg border border-border" />
        </div>
      </div>
    );
  }

  const unreadCount = notificationList.filter((n) => !n.is_read).length;

  return (
    <div className="flex flex-1 flex-col gap-6 p-4 md:p-6 w-full">
      <NotificationsHeader
        unreadCount={unreadCount}
        totalCount={notificationList.length}
        onMarkAllRead={handleMarkAllRead}
      />
      <NotificationsCards notifications={notificationList} />
      <NotificationsList
        notifications={notificationList}
        onToggleRead={handleToggleRead}
      />
    </div>
  );
}
