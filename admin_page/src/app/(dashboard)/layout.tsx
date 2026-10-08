import React from "react";
import { SidebarInset, SidebarProvider } from "@/ui/sidebar";
import { CIRPQueryProvider } from "@/modules/shared/components/query_provider";
import { AppSidebar } from "@/modules/shared/components/app_sidebar";
import { TopNavbar } from "@/modules/shared/components/top_navbar";
import { AuthSessionProvider } from "@/modules/auth/components/auth_session_provider";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <CIRPQueryProvider>
      <AuthSessionProvider>
        <SidebarProvider defaultOpen={true}>
          <AppSidebar />
          <SidebarInset className="flex flex-col">
            <TopNavbar />
            <main className="flex-1 overflow-auto bg-muted/30">
              <div className="container max-w-screen-2xl mx-auto">
                {children}
              </div>
            </main>
          </SidebarInset>
        </SidebarProvider>
      </AuthSessionProvider>
    </CIRPQueryProvider>
  );
}
