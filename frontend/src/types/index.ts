// Types definition

export const ProjectStatus = {
  DRAFT: 'draft',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  ARCHIVED: 'archived',
} as const;

export type ProjectStatus = typeof ProjectStatus[keyof typeof ProjectStatus];

export const PromptType = {
  IMAGE: 'image',
  VIDEO: 'video',
} as const;

export type PromptType = typeof PromptType[keyof typeof PromptType];

export const TaskStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
} as const;

export type TaskStatus = typeof TaskStatus[keyof typeof TaskStatus];

export const TaskType = {
  TEXT_TO_VIDEO: 'text_to_video',
  IMAGE_TO_VIDEO: 'image_to_video',
} as const;

export type TaskType = typeof TaskType[keyof typeof TaskType];

export interface Project {
  id: string;
  title: string;
  description?: string;
  status: ProjectStatus;
  canvas_data?: {
    nodes: any[];
    edges: any[];
  };
  meta?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface ImageResult {
  id: string;
  url: string;
  prompt: string;
  size: string;
}

export interface Session {
  id: string;
  project_id: string;
  agent_type: string;
  messages: Message[];
  context: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Prompt {
  id: string;
  project_id: string;
  type: PromptType;
  content: string;
  version: number;
  parent_id?: string;
  source: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface StoryboardImage {
  id: string;
  project_id: string;
  prompt_id: string;
  url?: string;
  file_path?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface VideoTask {
  id: string;
  project_id: string;
  storyboard_id?: string;
  prompt_id: string;
  task_type: TaskType;
  status: TaskStatus;
  url?: string;
  progress: number;
  error_message?: string;
  metadata?: Record<string, any>;
  created_at: string;
  completed_at?: string;
}

export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export const AgentType = {
  CREATIVE: 'creative',
  STORYBOARD: 'storyboard',
  DIRECTOR: 'director',
  PROMPT: 'prompt',
  COORDINATOR: 'coordinator',
} as const;

export type AgentType = typeof AgentType[keyof typeof AgentType];

export type WorkflowStep =
  | 'input'
  | 'planning'
  | 'storyboard_prompts'
  | 'generating_storyboard'
  | 'video_prompts'
  | 'generating_video'
  | 'completed';

export interface CreationPlan {
  overview: string;
  steps: string[];
  storyboard_prompts: string[];
  video_prompts: string[];
  estimated_duration: string;
}

export interface WorkflowState {
  current_step: WorkflowStep;
  plan?: CreationPlan;
  selected_storyboard_prompt?: string;
  storyboard_images?: string[];
  selected_video_prompt?: string;
  video_url?: string;
}
