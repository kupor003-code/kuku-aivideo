/*对话服务*/
import api from './api';

export interface ConversationMessage {
  id: string;
  project_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  agent_type?: string;
  agent_name?: string;
  related_node_id?: string;
  related_node_type?: string;
  meta?: any;
  created_at: string;
}

export interface SendMessageRequest {
  role: 'user' | 'assistant' | 'system';
  content: string;
  agent_type?: string;
  agent_name?: string;
  related_node_id?: string;
  related_node_type?: string;
  meta?: any;
}

export const conversationService = {
  /**
   * 获取项目的对话消息列表
   */
  async getMessages(projectId: string): Promise<ConversationMessage[]> {
    return api.get(`/projects/${projectId}/messages`);
  },

  /**
   * 发送消息
   */
  async sendMessage(projectId: string, message: SendMessageRequest): Promise<ConversationMessage> {
    return api.post(`/projects/${projectId}/messages`, message);
  },

  /**
   * 删除消息
   */
  async deleteMessage(projectId: string, messageId: string): Promise<void> {
    return api.delete(`/projects/${projectId}/messages/${messageId}`);
  },

  /**
   * 清空对话历史
   */
  async clearConversation(projectId: string): Promise<void> {
    return api.delete(`/projects/${projectId}/messages`);
  },
};
