import axios, { AxiosInstance } from 'axios';
import type { ApiResponse, LoginRequest, LoginResponse, UserInfo } from '../types/api';

export interface ScriptUploadRequest {
  name: string;
  description?: string;
  language?: string;
  tags?: string;
  file: File;
}

export interface ScriptResponse {
  id: number;
  name: string;
  description?: string;
  file_path: string;
  file_size: number;
  file_hash: string;
  language: string;
  tags: string[];
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface ScriptListResponse {
  total: number;
  page: number;
  page_size: number;
  items: ScriptResponse[];
}

export interface ExecutionResponse {
  id: number;
  script_id: number;
  script_name: string;
  status: string;
  exit_code?: number;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  created_by: number;
  created_at: string;
}

export interface ExecutionListResponse {
  total: number;
  page: number;
  page_size: number;
  items: ExecutionResponse[];
}

export interface ExecutionLogResponse {
  id: number;
  execution_id: number;
  log_type: string;
  content: string;
  timestamp: string;
}

export interface ExecutionLogsResponse {
  execution_id: number;
  logs: ExecutionLogResponse[];
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
    });

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async login(data: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    const response = await this.client.post<ApiResponse<LoginResponse>>('/api/v1/auth/login', data);
    return response.data;
  }

  async logout(): Promise<ApiResponse<null>> {
    const response = await this.client.post<ApiResponse<null>>('/api/v1/auth/logout');
    return response.data;
  }

  async getCurrentUser(): Promise<ApiResponse<UserInfo>> {
    const response = await this.client.get<ApiResponse<UserInfo>>('/api/v1/auth/me');
    return response.data;
  }

  async healthCheck(): Promise<ApiResponse<{ database: boolean }>> {
    const response = await this.client.get<ApiResponse<{ database: boolean }>>('/api/v1/health');
    return response.data;
  }

  async uploadScript(data: ScriptUploadRequest): Promise<ApiResponse<ScriptResponse>> {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('name', data.name);
    if (data.description) formData.append('description', data.description);
    if (data.language) formData.append('language', data.language);
    if (data.tags) formData.append('tags', data.tags);

    const response = await this.client.post<ApiResponse<ScriptResponse>>('/api/v1/scripts/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async listScripts(params: {
    page?: number;
    page_size?: number;
    keyword?: string;
    language?: string;
    tags?: string;
  }): Promise<ApiResponse<ScriptListResponse>> {
    const response = await this.client.get<ApiResponse<ScriptListResponse>>('/api/v1/scripts', { params });
    return response.data;
  }

  async getScript(scriptId: number): Promise<ApiResponse<ScriptResponse>> {
    const response = await this.client.get<ApiResponse<ScriptResponse>>(`/api/v1/scripts/${scriptId}`);
    return response.data;
  }

  async getScriptContent(scriptId: number): Promise<ApiResponse<{ content: string }>> {
    const response = await this.client.get<ApiResponse<{ content: string }>>(`/api/v1/scripts/${scriptId}/content`);
    return response.data;
  }

  async updateScript(scriptId: number, data: {
    name?: string;
    description?: string;
    tags?: string[];
  }): Promise<ApiResponse<ScriptResponse>> {
    const response = await this.client.put<ApiResponse<ScriptResponse>>(`/api/v1/scripts/${scriptId}`, data);
    return response.data;
  }

  async deleteScript(scriptId: number): Promise<ApiResponse<null>> {
    const response = await this.client.delete<ApiResponse<null>>(`/api/v1/scripts/${scriptId}`);
    return response.data;
  }

  async createExecution(scriptId: number): Promise<ApiResponse<ExecutionResponse>> {
    const response = await this.client.post<ApiResponse<ExecutionResponse>>('/api/v1/executions', {
      script_id: scriptId,
    });
    return response.data;
  }

  async listExecutions(params: {
    page?: number;
    page_size?: number;
    script_id?: number;
    status?: string;
  }): Promise<ApiResponse<ExecutionListResponse>> {
    const response = await this.client.get<ApiResponse<ExecutionListResponse>>('/api/v1/executions', { params });
    return response.data;
  }

  async getExecution(executionId: number): Promise<ApiResponse<ExecutionResponse>> {
    const response = await this.client.get<ApiResponse<ExecutionResponse>>(`/api/v1/executions/${executionId}`);
    return response.data;
  }

  async getExecutionLogs(executionId: number): Promise<ApiResponse<ExecutionLogsResponse>> {
    const response = await this.client.get<ApiResponse<ExecutionLogsResponse>>(`/api/v1/executions/${executionId}/logs`);
    return response.data;
  }

  async stopExecution(executionId: number): Promise<ApiResponse<null>> {
    const response = await this.client.post<ApiResponse<null>>(`/api/v1/executions/${executionId}/stop`);
    return response.data;
  }
}

export const apiService = new ApiService();
