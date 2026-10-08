"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
} from "@/ui/sidebar";
import { Badge } from "@/ui/badge";
import { CaretDownIcon } from "@phosphor-icons/react";
import { SidebarNavGroupConfig, SidebarNavItem } from "./sidebar_navigation_config";
import { cn } from "@/lib/utils";

export function SidebarNavGroup({ group }: { group: SidebarNavGroupConfig }) {
  const pathname = usePathname();

  return (
    <SidebarGroup>
      <SidebarGroupLabel className="px-4 mb-2">
        {group.label}
      </SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>
          {group.items.map((item) => (
            <SidebarNavEntry key={item.title} item={item} pathname={pathname} />
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}

function SidebarNavEntry({
  item,
  pathname,
}: {
  item: SidebarNavItem;
  pathname: string;
}) {
  const IconComponent = item.icon;

  if (item.subItems && item.subItems.length > 0) {
    const isSubActive = item.subItems.some(
      (sub) => pathname === sub.url || pathname.startsWith(sub.url)
    );
    return <SidebarSubmenuEntry item={item} isSubActive={isSubActive} pathname={pathname} />;
  }

  const isActive =
    item.url === "/dashboard"
      ? pathname === "/dashboard"
      : pathname === item.url || pathname.startsWith(item.url);

  return (
    <SidebarMenuItem>
      <Link 
        href={item.url}
        style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%', padding: '10px 16px' }}
        className={cn(
          "rounded-lg text-sm font-medium transition-colors",
          isActive 
            ? "bg-primary/10 text-primary font-semibold" 
            : "text-foreground hover:bg-accent"
        )}
      >
        <IconComponent
          weight={isActive ? "fill" : "bold"}
          size={20}
          style={{ flexShrink: 0 }}
        />
        <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {item.title}
        </span>
      </Link>
      {Boolean(item.badgeCount && item.badgeCount > 0) && (
        <SidebarMenuBadge>
          <Badge
            variant={item.badgeVariant || "outline"}
            className="text-xs"
          >
            {item.badgeCount}
          </Badge>
        </SidebarMenuBadge>
      )}
    </SidebarMenuItem>
  );
}

function SidebarSubmenuEntry({
  item,
  isSubActive,
  pathname,
}: {
  item: SidebarNavItem;
  isSubActive: boolean;
  pathname: string;
}) {
  const IconComponent = item.icon;
  const [isOpen, setIsOpen] = useState<boolean>(isSubActive);

  return (
    <SidebarMenuItem>
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%', padding: '10px 16px', textAlign: 'left' }}
        className={cn(
          "rounded-lg text-sm font-medium transition-colors",
          isSubActive 
            ? "bg-accent text-accent-foreground" 
            : "text-foreground hover:bg-accent"
        )}
      >
        <IconComponent
          weight={isSubActive ? "fill" : "bold"}
          size={20}
          style={{ flexShrink: 0 }}
        />
        <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {item.title}
        </span>
        <CaretDownIcon
          size={16}
          style={{ flexShrink: 0 }}
          className={cn(
            "transition-transform duration-200",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {isOpen && item.subItems && (
        <SidebarMenuSub>
          {item.subItems.map((sub) => {
            const SubIcon = sub.icon;
            const isChildActive = pathname === sub.url;
            return (
              <SidebarMenuSubItem key={sub.title}>
                <Link
                  href={sub.url}
                  style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%', padding: '8px 16px 8px 48px' }}
                  className={cn(
                    "rounded-lg text-sm transition-colors",
                    isChildActive 
                      ? "bg-primary/10 text-primary font-semibold" 
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  )}
                >
                  <SubIcon size={16} style={{ flexShrink: 0 }} />
                  <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {sub.title}
                  </span>
                </Link>
              </SidebarMenuSubItem>
            );
          })}
        </SidebarMenuSub>
      )}
    </SidebarMenuItem>
  );
}
