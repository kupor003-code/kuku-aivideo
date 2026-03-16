/*Canvas节点服务 - 支持节点间的数据传递*/
import api from './api';

export interface CanvasNodeUpdate {
  id: string;
  data: Record<string, any>;
}

export const canvasNodeService = {
  /**
   * 从图片生成视频 - 链式操作API
   * 这个方法直接调用视频生成API，支持从图片生成视频的链式操作
   */
  async generateVideoFromImage(
    projectId: string,
    imageUrl: string,
    prompt: string,
    duration?: number,
    fps?: number,
    sourceImageId?: string
  ): Promise<{
    task_id: string;
    status: string;
  }> {
    return api.post('/video/generate', {
      prompt,
      image_url: imageUrl,
      duration: duration || 5,
      fps: fps || 30,
      project_id: projectId,
      source_image_id: sourceImageId,
    });
  },

  /**
   * 获取项目中的所有图片
   */
  async getProjectImages(projectId: string): Promise<Array<Record<string, any>>> {
    return api.get(`/storyboard-images/project/${projectId}`);
  },

  /**
   * 获取项目中的所有视频
   */
  async getProjectVideos(projectId: string): Promise<Array<Record<string, any>>> {
    return api.get(`/video/project/${projectId}`);
  },
};
