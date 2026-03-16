/*会话服务*/
import api from './api';
import type { Message } from '../types';

export interface SessionCreate {
  project_id: string;
  agent_type: string;
}

export interface SessionResponse {
  id: string;
  project_id: string;
  agent_type: string;
  messages: Message[];
  context: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AppendMessagesRequest {
  messages: Message[];
  context?: Record<string, any>;
}

export const sessionService = {
  /**
   * 创建会话
   */
  async create(data: SessionCreate): Promise<SessionResponse> {
    return api.post('/sessions/', data);
  },

  /**
   * 获取会话详情
   */
  async get(sessionId: string): Promise<SessionResponse> {
    return api.get(`/sessions/${sessionId}`);
  },

  /**
   * 获取项目的所有会话
   */
  async getProjectSessions(projectId: string, agentType?: string): Promise<SessionResponse[]> {
    return api.get(`/sessions/project/${projectId}`, {
      params: agentType ? { agent_type: agentType } : undefined,
    });
  },

  /**
   * 追加消息
   */
  async appendMessages(sessionId: string, messages: Message[], context?: Record<string, any>): Promise<SessionResponse> {
    return api.post(`/sessions/${sessionId}/messages`, {
      messages,
      context,
    });
  },

  /**
   * 更新会话
   */
  async update(sessionId: string, data: { messages?: Message[]; context?: Record<string, any> }): Promise<SessionResponse> {
    return api.put(`/sessions/${sessionId}`, data);
  },
};
