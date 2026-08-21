/**
 * API Client for CIRP Backend
 * Handles all HTTP requests to the Django backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

/**
 * Get stored authentication token
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Store authentication token
 */
function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('auth_token', token);
}

/**
 * Remove authentication token
 */
function removeAuthToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
}

/**
 * Make HTTP request to API
 */
async function request<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.detail || data.message || 'An error occurred',
        data: data,
      };
    }

    return {
      success: true,
      data: data,
    };
  } catch (error) {
    console.error('API request error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

// ============================================================================
// Authentication
// ============================================================================

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  role: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

/**
 * Login user
 */
export async function login(credentials: LoginCredentials): Promise<ApiResponse<AuthResponse>> {
  const response = await request<AuthResponse>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });

  if (response.success && response.data) {
    setAuthToken(response.data.access);
    if (typeof window !== 'undefined') {
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
  }

  return response;
}

/**
 * Register new user
 */
export async function register(data: RegisterData): Promise<ApiResponse<AuthResponse>> {
  return request<AuthResponse>('/auth/register/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Logout user
 */
export function logout(): void {
  removeAuthToken();
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<ApiResponse<User>> {
  return request<User>('/auth/profile/');
}

// ============================================================================
// Reports
// ============================================================================

export interface Report {
  id: string;
  report_number: string;
  title: string;
  description: string;
  latitude: number | null;
  longitude: number | null;
  address: string | null;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'SUBMITTED' | 'UNDER_REVIEW' | 'ACCEPTED' | 'ASSIGNED' | 'IN_PROGRESS' | 'PENDING_VERIFICATION' | 'RESOLVED' | 'REJECTED' | 'DISPUTED' | 'REOPENED' | 'MERGED' | 'CLOSED';
  created_at: string;
  updated_at: string;
  citizen: User;
  category: Category;
  media?: ReportMedia[];
}

export interface ReportMedia {
  id: string;
  file: string;
  media_type: 'IMAGE' | 'VIDEO' | 'DOCUMENT';
  created_at: string;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  icon: string | null;
  color: string | null;
}

export interface Department {
  id: string;
  name: string;
  description: string;
  contact_email: string | null;
  contact_phone: string | null;
}

export interface CreateReportData {
  title: string;
  description: string;
  category: string;
  latitude?: number;
  longitude?: number;
  address?: string;
  priority?: string;
  media?: string[]; // base64 encoded images
}

export interface UpdateReportData {
  status?: string;
  priority?: string;
  assigned_department?: string;
}

/**
 * Get all reports with optional filters
 */
export async function getReports(params?: {
  status?: string;
  priority?: string;
  category?: string;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<ApiResponse<{ results: Report[]; count: number }>> {
  const queryParams = new URLSearchParams();
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString());
      }
    });
  }

  const queryString = queryParams.toString();
  return request<{ results: Report[]; count: number }>(
    `/reports/${queryString ? `?${queryString}` : ''}`
  );
}

/**
 * Get single report by ID
 */
export async function getReport(id: string): Promise<ApiResponse<Report>> {
  return request<Report>(`/reports/${id}/`);
}

/**
 * Get user's own reports
 */
export async function getMyReports(params?: {
  status?: string;
  page?: number;
}): Promise<ApiResponse<{ results: Report[]; count: number }>> {
  const queryParams = new URLSearchParams();
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString());
      }
    });
  }

  const queryString = queryParams.toString();
  return request<{ results: Report[]; count: number }>(
    `/reports/my-reports/${queryString ? `?${queryString}` : ''}`
  );
}

/**
 * Create new report
 */
export async function createReport(data: CreateReportData): Promise<ApiResponse<Report>> {
  return request<Report>('/reports/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Update report (admin only - change status, priority, etc.)
 */
export async function updateReport(id: string, data: UpdateReportData): Promise<ApiResponse<Report>> {
  return request<Report>(`/reports/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

/**
 * Delete report
 */
export async function deleteReport(id: string): Promise<ApiResponse<void>> {
  return request<void>(`/reports/${id}/`, {
    method: 'DELETE',
  });
}

// ============================================================================
// Categories
// ============================================================================

/**
 * Get all categories
 */
export async function getCategories(): Promise<ApiResponse<Category[]>> {
  return request<Category[]>('/categories/');
}

/**
 * Get single category
 */
export async function getCategory(id: string): Promise<ApiResponse<Category>> {
  return request<Category>(`/categories/${id}/`);
}

// ============================================================================
// Departments
// ============================================================================

/**
 * Get all departments
 */
export async function getDepartments(): Promise<ApiResponse<Department[]>> {
  return request<Department[]>('/departments/');
}

/**
 * Get single department
 */
export async function getDepartment(id: string): Promise<ApiResponse<Department>> {
  return request<Department>(`/departments/${id}/`);
}

// ============================================================================
// Dashboard Stats
// ============================================================================

export interface DashboardStats {
  total_reports: number;
  pending_reports: number;
  in_progress_reports: number;
  resolved_reports: number;
  critical_reports: number;
  recent_reports: Report[];
  reports_by_category: Array<{ category: string; count: number }>;
  reports_by_status: Array<{ status: string; count: number }>;
}

/**
 * Get dashboard statistics
 */
export async function getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
  return request<DashboardStats>('/dashboard/stats/');
}

// ============================================================================
// Users (Admin)
// ============================================================================

/**
 * Get all users (admin only)
 */
export async function getUsers(params?: {
  role?: string;
  search?: string;
  page?: number;
}): Promise<ApiResponse<{ results: User[]; count: number }>> {
  const queryParams = new URLSearchParams();
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value.toString());
      }
    });
  }

  const queryString = queryParams.toString();
  return request<{ results: User[]; count: number }>(
    `/users/${queryString ? `?${queryString}` : ''}`
  );
}

/**
 * Get single user
 */
export async function getUser(id: string): Promise<ApiResponse<User>> {
  return request<User>(`/users/${id}/`);
}

/**
 * Update user (admin only)
 */
export async function updateUser(id: string, data: Partial<User>): Promise<ApiResponse<User>> {
  return request<User>(`/users/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// Export API base URL for direct use
export { API_BASE_URL };
