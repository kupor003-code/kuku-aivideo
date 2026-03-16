/*项目配置服务*/
import api from './api';

export interface ProjectConfig {
  image_generation: {
    ai_recommend_images: boolean;
    default_images_per_scene: number;
    allow_manual_adjust: boolean;
    min_images: number;
    max_images: number;
  };
  video_generation: {
    resolution: '720p' | '1080p' | '4K';
    duration: number;  // 秒
    fps: 24 | 30 | 60;
    style_strength: 'low' | 'medium' | 'high';
  };
  agent_config: {
    enable_auto_generate: boolean;
    require_user_confirm: boolean;
  };
}

export const projectConfigService = {
  /**
   * 获取项目配置
   */
  async getConfig(projectId: string): Promise<ProjectConfig> {
    return api.get(`/projects/${projectId}/config`).then((res: any) => res.config);
  },

  /**
   * 更新项目配置
   */
  async updateConfig(projectId: string, config: ProjectConfig): Promise<ProjectConfig> {
    return api.put(`/projects/${projectId}/config`, config).then((res: any) => res.config);
  },

  /**
   * 部分更新配置
   */
  async patchConfig(projectId: string, configUpdate: Partial<ProjectConfig>): Promise<ProjectConfig> {
    return api.patch(`/projects/${projectId}/config`, configUpdate).then((res: any) => res.config);
  },
};
