/**
 * Workflow Service - V2 工作流服务
 *
 * 这个服务对接我们新的 V2 工作流 API：
 * - POST /api/v1/workflow/plan/generate - 生成执行计划
 * - POST /api/v1/workflow/execute - 执行工作流
 * - GET /api/v1/workflow/status/{project_id} - 查询执行状态
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface WorkflowStep {
  order: number;
  agent: string;
  action: string;
  description: string;
  inputs: Record<string, any>;
}

export interface WorkflowPlan {
  task_type: string;
  overview: string;
  steps: WorkflowStep[];
  estimated_duration: string;
  requirements: string[];
}

export interface WorkflowIntent {
  task_type: string;
  topic: string;
  has_document: boolean;
  document_type: string;
  style_preference: string;
  duration_preference: string;
  specific_requirements: string[];
  urgency: string;
  confidence: number;
}

export interface GeneratePlanRequest {
  user_input: string;
  project_id?: string;
}

export interface GeneratePlanResponse {
  success: boolean;
  intent: WorkflowIntent;
  execution_plan: WorkflowPlan;
  message: string;
  next_agent: string | null;
}

export interface ExecuteWorkflowRequest {
  user_input: string;
  project_id: string;
  auto_execute: boolean;
}

export interface WorkflowExecutionState {
  project_id: string;
  progress: number;
  is_completed: boolean;
  is_failed: boolean;
  current_step: WorkflowStep | null;
  completed_steps: Array<{
    step: WorkflowStep;
    result: any;
    completed_at: string;
  }>;
  failed_steps: Array<{
    step: WorkflowStep;
    error: string;
    failed_at: string;
  }>;
}

export interface ExecuteWorkflowResponse {
  success: boolean;
  project_id: string;
  execution_state?: WorkflowExecutionState;
  message: string;
  error?: string;
}

export interface WorkflowStatusResponse {
  success: boolean;
  execution_state?: WorkflowExecutionState;
  project_id: string;
}

class WorkflowService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_URL}/workflow`;
  }

  /**
   * 生成执行计划
   */
  async generatePlan(request: GeneratePlanRequest): Promise<GeneratePlanResponse> {
    const response = await axios.post<GeneratePlanResponse>(
      `${this.baseUrl}/plan/generate`,
      request
    );
    return response.data;
  }

  /**
   * 执行工作流
   */
  async executeWorkflow(request: ExecuteWorkflowRequest): Promise<ExecuteWorkflowResponse> {
    const response = await axios.post<ExecuteWorkflowResponse>(
      `${this.baseUrl}/execute`,
      request
    );
    return response.data;
  }

  /**
   * 查询执行状态
   */
  async getWorkflowStatus(projectId: string): Promise<WorkflowStatusResponse> {
    const response = await axios.get<WorkflowStatusResponse>(
      `${this.baseUrl}/status/${projectId}`
    );
    return response.data;
  }

  /**
   * 取消执行
   */
  async cancelWorkflow(projectId: string): Promise<{ success: boolean; message: string; project_id: string }> {
    const response = await axios.post<{ success: boolean; message: string; project_id: string }>(
      `${this.baseUrl}/cancel/${projectId}`
    );
    return response.data;
  }
}

export const workflowService = new WorkflowService();
