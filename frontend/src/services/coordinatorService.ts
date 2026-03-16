/* Coordinator Service - 协调工作流服务 */
import axios from 'axios';
import type { WorkflowState, CreationPlan } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface CoordinatorChatRequest {
  message: string;
  project_id: string;
  session_id?: string;
  workflow_state?: WorkflowState;
}

export interface CoordinatorChatResponse {
  message: string;
  workflow_state: WorkflowState;
  suggestions: string[];
}

export interface GeneratePlanRequest {
  user_input: string;
  project_id: string;
}

export interface GeneratePlanResponse {
  plan: CreationPlan;
}

export interface RefinePromptRequest {
  original_prompt: string;
  user_feedback: string;
  prompt_type: 'storyboard' | 'video';
}

export interface RefinePromptResponse {
  refined_prompt: string;
}

export interface GenerateStoryboardImagesRequest {
  prompts: string[];
  project_id: string;
  size?: string;
}

export interface GenerateStoryboardImagesResponse {
  task_ids: string[];
  status: string;
}

class CoordinatorService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_URL}/coordinator`;
  }

  async chat(request: CoordinatorChatRequest): Promise<CoordinatorChatResponse> {
    const response = await axios.post<CoordinatorChatResponse>(
      `${this.baseUrl}/chat`,
      request
    );
    return response.data;
  }

  async generatePlan(request: GeneratePlanRequest): Promise<GeneratePlanResponse> {
    const response = await axios.post<GeneratePlanResponse>(
      `${this.baseUrl}/generate-plan`,
      request
    );
    return response.data;
  }

  async refinePrompt(request: RefinePromptRequest): Promise<RefinePromptResponse> {
    const response = await axios.post<RefinePromptResponse>(
      `${this.baseUrl}/refine-prompt`,
      request
    );
    return response.data;
  }

  async generateStoryboardImages(
    request: GenerateStoryboardImagesRequest
  ): Promise<GenerateStoryboardImagesResponse> {
    const response = await axios.post<GenerateStoryboardImagesResponse>(
      `${this.baseUrl}/generate-storyboard-images`,
      request
    );
    return response.data;
  }

  async generateVideoPrompt(storyboardImages: string[]): Promise<{ prompt: string }> {
    const response = await axios.post<{ prompt: string }>(
      `${this.baseUrl}/generate-video-prompt`,
      storyboardImages
    );
    return response.data;
  }

  async getWorkflowState(projectId: string): Promise<{ workflow_state: WorkflowState }> {
    const response = await axios.get<{ workflow_state: WorkflowState }>(
      `${this.baseUrl}/workflow-state/${projectId}`
    );
    return response.data;
  }

  async saveWorkflowState(
    projectId: string,
    workflowState: WorkflowState
  ): Promise<{ status: string; workflow_state: WorkflowState }> {
    const response = await axios.post<{ status: string; workflow_state: WorkflowState }>(
      `${this.baseUrl}/workflow-state/${projectId}`,
      workflowState
    );
    return response.data;
  }
}

export const coordinatorService = new CoordinatorService();
