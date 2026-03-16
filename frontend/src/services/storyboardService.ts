/*分镜图片服务*/
import api from './api';
import axios from 'axios';

const ZHIPU_API_KEY = '39e7431665754cc08fe332777f7968e7.ei00hbZ9bAYzSvEW';
const ZHIPU_API_URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions';

export interface GenerateImageRequest {
  prompt: string;
  size?: string;
  n?: number;
  seed?: number;
}

export interface GenerateImageResponse {
  task_id: string;
  status: string;
}

export interface ImageResult {
  id: string;
  url: string;
  prompt: string;
}

export interface ImageTaskStatus {
  task_id: string;
  status: string;
  results?: ImageResult[];
  progress?: number;
}

export interface RegenerateImageRequest {
  image_id: string;
  variations?: number;
  style_change?: string;
}

export interface OptimizePromptRequest {
  prompt: string;
  focus?: string;
}

// 分镜片段接口
export interface Fragment {
  fragment_id: string;
  number: number;
  duration: number;
  prompt: string;
  negative_prompt: string;
  audio_prompt: string;
  color?: string;
}

export interface StoryboardResult {
  fragments: Fragment[];
}

export const storyboardService = {
  /**
   * 使用智谱AI生成专业分镜（带总时长控制）
   * @param script 用户输入的剧本
   * @param totalDuration 目标总时长（秒），默认30秒
   */
  async generateFromScript(script: string, totalDuration: number = 30): Promise<StoryboardResult> {
    try {
      const prompt = `请将以下剧本拆分为适合AI视频生成的分镜片段。

**重要要求：**
1. 所有分镜的总时长必须严格控制在 ${totalDuration} 秒左右（误差±2秒）
2. 根据总时长合理分配分镜数量和每个分镜的时长
   - 短视频（${totalDuration < 20 ? '10-20秒' : totalDuration < 60 ? '20-60秒' : '60秒以上'}）：建议${totalDuration < 20 ? '2-4个分镜' : totalDuration < 60 ? '4-8个分镜' : '8-15个分镜'}
   - 每个分镜时长：${totalDuration < 20 ? '3-5秒' : '2-6秒'}
3. 为每个片段生成详细的中英文双语画面描述提示词
4. 包含镜头类型、景别、光线、色调等细节
5. 生成负面提示词
6. 为每个片段生成音频环境音设计

**示例计算**：
- 总时长：${totalDuration}秒
- 建议分镜数：${Math.max(3, Math.round(totalDuration / 5))}个
- 平均每镜：${(totalDuration / Math.max(3, Math.round(totalDuration / 5))).toFixed(1)}秒

输出格式（JSON）：
{
  "fragments": [
    {
      "fragment_id": "frag_001",
      "duration": 4.2,
      "prompt": "中文描述\\n\\nEnglish description with detailed visual cues",
      "negative_prompt": "cartoon, anime, low quality",
      "audio_prompt": "环境音描述"
    }
  ],
  "total_duration": ${totalDuration},
  "fragment_count": ${Math.max(3, Math.round(totalDuration / 5))}
}

**用户剧本**：
${script}

**请特别注意**：
- 所有分镜的duration总和必须接近 ${totalDuration} 秒
- 请严格按照JSON格式输出分镜结果
- 返回的fragments数组中，所有duration字段相加应该等于或非常接近 ${totalDuration} 秒`;

      const response = await axios.post(
        ZHIPU_API_URL,
        {
          model: 'glm-4-flash',
          messages: [
            {
              role: 'system',
              content: '你是一个专业的视频分镜设计师，擅长将剧本拆解为适合AI视频生成的分镜片段。'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.7,
          max_tokens: 4096,
        },
        {
          headers: {
            'Authorization': `Bearer ${ZHIPU_API_KEY}`,
            'Content-Type': 'application/json',
          },
          timeout: 60000,
        }
      );

      // 解析AI返回的JSON
      const content = response.data.choices[0].message.content;

      // 提取JSON部分
      let jsonStr = content;
      const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
      if (jsonMatch) {
        jsonStr = jsonMatch[1];
      } else {
        const braceMatch = content.match(/\{[\s\S]*\}/);
        if (braceMatch) {
          jsonStr = braceMatch[0];
        }
      }

      const result = JSON.parse(jsonStr);

      // 确保返回的数据格式正确
      if (!result.fragments || !Array.isArray(result.fragments)) {
        throw new Error('AI返回格式错误');
      }

      // 为每个片段添加ID和序号
      result.fragments = result.fragments.map((frag: any, index: number) => ({
        ...frag,
        fragment_id: frag.fragment_id || `frag_${Date.now()}_${index}`,
        number: index + 1,
      }));

      return result;

    } catch (error: any) {
      console.error('分镜生成失败:', error);
      throw new Error(`分镜生成失败: ${error.message}`);
    }
  },

  /**
   * 生成图片
   */
  async generateImage(request: GenerateImageRequest): Promise<GenerateImageResponse> {
    return api.post('/storyboard/generate', request);
  },

  /**
   * 查询任务状态
   */
  async getTaskStatus(taskId: string): Promise<ImageTaskStatus> {
    return api.get(`/storyboard/task/${taskId}`);
  },

  /**
   * 重新生成图片
   */
  async regenerateImage(request: RegenerateImageRequest): Promise<{ task_ids: string[]; count: number }> {
    return api.post('/storyboard/regenerate', request);
  },

  /**
   * 优化提示词
   */
  async optimizePrompt(request: OptimizePromptRequest): Promise<{ original: string; optimized: string }> {
    return api.post('/storyboard/optimize-prompt', request);
  },

  /**
   * 轮询任务状态直到完成
   */
  async waitForCompletion(
    taskId: string,
    onProgress?: (progress: number) => void,
    interval: number = 2000
  ): Promise<ImageTaskStatus> {
    while (true) {
      const status = await this.getTaskStatus(taskId);

      if (status.progress && onProgress) {
        onProgress(status.progress);
      }

      if (status.status === 'SUCCEEDED') {
        return status;
      }

      if (status.status === 'FAILED') {
        throw new Error('图片生成失败');
      }

      await new Promise(resolve => setTimeout(resolve, interval));
    }
  },
};
