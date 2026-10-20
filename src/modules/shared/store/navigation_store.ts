import { create } from "zustand";
import { AdminNavigationTab, UserRole } from "../types/enums";

interface NavigationState {
  activeTab: AdminNavigationTab;
  selectedDepartmentFilter: string;
  currentUserRole: UserRole;
  activeOfficerDepartmentId: string;
  searchQuery: string;

  setActiveTab: (tab: AdminNavigationTab) => void;
  setSelectedDepartmentFilter: (deptId: string) => void;
  setCurrentUserRole: (role: UserRole) => void;
  setActiveOfficerDepartmentId: (deptId: string) => void;
  setSearchQuery: (query: string) => void;
}

export const useNavigationStore = create<NavigationState>((set) => ({
  activeTab: "dashboard",
  selectedDepartmentFilter: "all",
  // Start with the least privileged role until a real login supplies a role.
  currentUserRole: "DEPARTMENT_ADMIN",
  activeOfficerDepartmentId: "__unassigned__",
  searchQuery: "",

  setActiveTab: (tab) => set({ activeTab: tab }),
  setSelectedDepartmentFilter: (deptId) => set({ selectedDepartmentFilter: deptId }),
  setCurrentUserRole: (role) => set({ currentUserRole: role }),
  setActiveOfficerDepartmentId: (deptId) => set({ activeOfficerDepartmentId: deptId }),
  setSearchQuery: (query) => set({ searchQuery: query }),
}));
