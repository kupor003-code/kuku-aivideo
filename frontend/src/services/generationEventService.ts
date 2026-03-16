/**
 * 生成事件服务 - 在对话框和 Canvas 之间同步镜头生成流程
 * 支持实时进度同步和状态更新
 */

export interface GenerationProgress {
  shot_id: string;
  shot_number: number;
  type: 'image' | 'video';  // 生成类型
  status: 'pending' | 'generating' | 'paused' | 'completed' | 'failed';
  progress: number;  // 0-100
  message?: string;
  error?: string;
}

export interface ShotGenerationResult {
  shot_id: string;
  shot_number: number;
  image_ids?: string[];  // 生成的图片ID列表
  image_urls?: string[];  // 生成的图片URL列表
  video_id?: string;  // 生成的视频ID
  video_url?: string;  // 生成的视频URL
  error?: string;
}

class GenerationEventService {
  private listeners: Map<string, Set<Function>> = new Map();
  private progressMap: Map<string, GenerationProgress> = new Map();

  /**
   * 订阅生成进度事件
   */
  subscribe(eventType: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(callback);

    // 返回取消订阅函数
    return () => {
      this.listeners.get(eventType)?.delete(callback);
    };
  }

  /**
   * 发射事件
   */
  emit(eventType: string, data: any): void {
    this.listeners.get(eventType)?.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in event listener for ${eventType}:`, error);
      }
    });
  }

  /**
   * 更新镜头生成进度
   */
  updateProgress(shotId: string, progress: GenerationProgress): void {
    this.progressMap.set(shotId, progress);
    this.emit('progress', progress);
    this.emit(`progress:${shotId}`, progress);
  }

  /**
   * 获取镜头进度
   */
  getProgress(shotId: string): GenerationProgress | undefined {
    return this.progressMap.get(shotId);
  }

  /**
   * 开始图片生成
   */
  startImageGeneration(shotId: string, shotNumber: number): void {
    this.updateProgress(shotId, {
      shot_id: shotId,
      shot_number: shotNumber,
      type: 'image',
      status: 'generating',
      progress: 0,
      message: `正在生成镜头 ${shotNumber} 的图片...`,
    });
  }

  /**
   * 更新图片生成进度
   */
  updateImageProgress(shotId: string, progress: number, message?: string): void {
    const current = this.progressMap.get(shotId);
    if (current && current.type === 'image') {
      this.updateProgress(shotId, {
        ...current,
        progress,
        message,
      });
    }
  }

  /**
   * 图片生成完成
   */
  completeImageGeneration(
    shotId: string,
    shotNumber: number,
    imageIds: string[],
    imageUrls: string[]
  ): void {
    this.updateProgress(shotId, {
      shot_id: shotId,
      shot_number: shotNumber,
      type: 'image',
      status: 'completed',
      progress: 100,
      message: `镜头 ${shotNumber} 的图片已生成完成 (${imageIds.length}张)`,
    });

    // 发射完成事件
    this.emit('image-generation-complete', {
      shotId,
      shotNumber,
      imageIds,
      imageUrls,
    });
  }

  /**
   * 图片生成失败
   */
  failImageGeneration(shotId: string, shotNumber: number, error: string): void {
    this.updateProgress(shotId, {
      shot_id: shotId,
      shot_number: shotNumber,
      type: 'image',
      status: 'failed',
      progress: 0,
      error,
      message: `镜头 ${shotNumber} 生成失败: ${error}`,
    });
  }

  /**
   * 开始视频生成
   */
  startVideoGeneration(shotId: string, shotNumber: number): void {
    this.updateProgress(shotId, {
      shot_id: shotId,
      shot_number: shotNumber,
      type: 'video',
      status: 'generating',
      progress: 0,
      message: `正在生成镜头 ${shotNumber} 的视频...`,
    });
  }

  /**
   * 更新视频生成进度
   */
  updateVideoProgress(shotId: string, progress: number, message?: string): void {
    const current = this.progressMap.get(shotId);
    if (current && current.type === 'video') {
      this.updateProgress(shotId, {
        ...current,
        progress,
        message,
      });
    }
  }

  /**
   * 视频生成完成
   */
  completeVideoGeneration(
    shotId: string,
    shotNumber: number,
    videoId: string,
    videoUrl: string
  ): void {
    this.updateProgress(shotId, {
      shot_id: shotId,
      shot_number: shotNumber,
      type: 'video',
      status: 'completed',
      progress: 100,
      message: `镜头 ${shotNumber} 的视频已生成完成`,
    });

    // 发射完成事件
    this.emit('video-generation-complete', {
      shotId,
      shotNumber,
      videoId,
      videoUrl,
    });
  }

  /**
   * 视频生成失败
   */
  failVideoGeneration(shotId: string, shotNumber: number, error: string): void {
    this.updateProgress(shotId, {
      shot_id: shotId,
      shot_number: shotNumber,
      type: 'video',
      status: 'failed',
      progress: 0,
      error,
      message: `镜头 ${shotNumber} 视频生成失败: ${error}`,
    });
  }

  /**
   * 清空所有监听器
   */
  clear(): void {
    this.listeners.clear();
    this.progressMap.clear();
  }
}

// 导出单例
export const generationEventService = new GenerationEventService();
