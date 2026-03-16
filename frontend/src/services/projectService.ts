/*项目服务*/
import api from './api';
import type { Project } from '../types';

export interface ProjectCreate {
  title: string;
  description?: string;
}

export interface ProjectUpdate {
  title?: string;
  description?: string;
  status?: 'draft' | 'in_progress' | 'completed' | 'archived';
  canvas_data?: {
    nodes: any[];
    edges: any[];
  };
  metadata?: Record<string, any>;
}

export const projectService = {
  /**
   * 创建项目
   */
  async create(data: ProjectCreate): Promise<Project> {
    return api.post('/projects/', data);
  },

  /**
   * 获取项目列表
   */
  async list(skip = 0, limit = 100): Promise<Project[]> {
    return api.get('/projects/', { params: { skip, limit } });
  },

  /**
   * 获取项目详情
   */
  async get(projectId: string): Promise<Project> {
    return api.get(`/projects/${projectId}`);
  },

  /**
   * 更新项目
   */
  async update(projectId: string, data: ProjectUpdate): Promise<Project> {
    return api.put(`/projects/${projectId}`, data);
  },

  /**
   * 删除项目
   */
  async delete(projectId: string): Promise<{ message: string }> {
    return api.delete(`/projects/${projectId}`);
  },
};
