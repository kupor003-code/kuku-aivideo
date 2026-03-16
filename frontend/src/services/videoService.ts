/*视频生成服务*/
import api from './api';

export interface GenerateVideoRequest {
  prompt: string;
  image_url?: string;
  duration?: number;
  fps?: number;
}

export interface GenerateVideoResponse {
  task_id: string;
  status: string;
}

export interface VideoResult {
  id: string;
  url: string;
  prompt: string;
  duration?: number;
}

export interface VideoTaskStatus {
  task_id: string;
  status: string;
  results?: VideoResult[];
  progress?: number;
}

export const videoService = {
  /**
   * 生成视频
   */
  async generateVideo(request: GenerateVideoRequest): Promise<GenerateVideoResponse> {
    return api.post('/video/generate', request);
  },

  /**
   * 查询任务状态
   */
  async getTaskStatus(taskId: string): Promise<VideoTaskStatus> {
    return api.get(`/video/task/${taskId}`);
  },

  /**
   * 轮询任务状态直到完成
   */
  async waitForCompletion(
    taskId: string,
    onProgress?: (progress: number) => void,
    interval: number = 3000
  ): Promise<VideoTaskStatus> {
    while (true) {
      const status = await this.getTaskStatus(taskId);

      if (status.progress && onProgress) {
        onProgress(status.progress);
      }

      if (status.status === 'SUCCEEDED') {
        return status;
      }

      if (status.status === 'FAILED') {
        throw new Error('视频生成失败');
      }

      await new Promise(resolve => setTimeout(resolve, interval));
    }
  },
};
