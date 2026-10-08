import React from "react";
import { cn } from "@/lib/utils";

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Standard page container with consistent padding and spacing
 * Use this for all page-level content to maintain consistent layout
 */
export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <div className={cn("flex flex-1 flex-col gap-6 p-6 md:p-8 w-full", className)}>
      {children}
    </div>
  );
}
