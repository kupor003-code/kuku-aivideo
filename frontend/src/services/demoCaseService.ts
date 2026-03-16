/**
 * 演示案例服务
 * 用于保存和获取真实生成的演示内容
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

export interface DemoCase {
  id?: string;
  title: string;
  description?: string;
  script: string;
  total_duration: number;
  fragments: any[];
  total_images: number;
  total_videos: number;
  created_at?: string;
  updated_at?: string;
}

export interface DemoCaseResponse {
  id: string;
  title: string;
  description?: string;
  script: string;
  total_duration: number;
  fragments: any[];
  total_images: number;
  total_videos: number;
  created_at: string;
  updated_at: string;
}

class DemoCaseService {
  /**
   * 保存为演示案例
   */
  async saveAsDemoCase(demoCase: DemoCase): Promise<DemoCaseResponse> {
    try {
      const response = await axios.post(`${API_URL}/demo-cases`, demoCase);
      return response.data;
    } catch (error: any) {
      console.error('保存演示案例失败:', error);
      throw error;
    }
  }

  /**
   * 获取演示案例列表
   */
  async getDemoCases(skip: number = 0, limit: number = 10): Promise<DemoCaseResponse[]> {
    try {
      const response = await axios.get(`${API_URL}/demo-cases`, {
        params: { skip, limit }
      });
      return response.data;
    } catch (error: any) {
      console.error('获取演示案例失败:', error);
      throw error;
    }
  }

  /**
   * 获取单个演示案例
   */
  async getDemoCase(caseId: string): Promise<DemoCaseResponse> {
    try {
      const response = await axios.get(`${API_URL}/demo-cases/${caseId}`);
      return response.data;
    } catch (error: any) {
      console.error('获取演示案例失败:', error);
      throw error;
    }
  }

  /**
   * 获取最新的演示案例
   */
  async getLatestDemoCase(): Promise<DemoCaseResponse> {
    try {
      const response = await axios.get(`${API_URL}/demo-cases/latest`);
      return response.data;
    } catch (error: any) {
      console.error('获取最新演示案例失败:', error);
      throw error;
    }
  }

  /**
   * 更新演示案例
   */
  async updateDemoCase(caseId: string, demoCase: DemoCase): Promise<DemoCaseResponse> {
    try {
      const response = await axios.put(`${API_URL}/demo-cases/${caseId}`, demoCase);
      return response.data;
    } catch (error: any) {
      console.error('更新演示案例失败:', error);
      throw error;
    }
  }
}

export const demoCaseService = new DemoCaseService();
