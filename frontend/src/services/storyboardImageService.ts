/*分镜图片服务*/
import api from './api';

export interface StoryboardImageCreate {
  project_id: string;
  prompt_id: string;
  url?: string;
  file_path?: string;
  metadata?: Record<string, any>;
}

export interface StoryboardImage {
  id: string;
  project_id: string;
  prompt_id: string;
  url?: string;
  file_path?: string;
  meta: Record<string, any>;
  created_at: string;
}

export const storyboardImageService = {
  /**
   * 创建分镜图片记录
   */
  async create(data: StoryboardImageCreate): Promise<StoryboardImage> {
    return api.post('/storyboard-images/', data);
  },

  /**
   * 获取项目的所有分镜图片
   */
  async getProjectImages(projectId: string): Promise<StoryboardImage[]> {
    return api.get(`/storyboard-images/project/${projectId}`);
  },

  /**
   * 删除分镜图片
   */
  async delete(imageId: string): Promise<{ message: string }> {
    return api.delete(`/storyboard-images/${imageId}`);
  },
};
