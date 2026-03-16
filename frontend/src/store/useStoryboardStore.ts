/*分镜工作台状态管理*/
import { create } from 'zustand';
import type { ImageResult } from '../types';

interface VideoResult {
  id: string;
  url: string;
  prompt: string;
  thumbnail?: string;
}

interface StoryboardState {
  images: ImageResult[];
  videos: VideoResult[];
  isGenerating: boolean;
  isGeneratingVideo: boolean;
  currentTaskId: string | null;
  selectedImage: ImageResult | null;
  prompt: string;
  size: string;
  count: number;

  setImages: (images: ImageResult[]) => void;
  addImage: (image: ImageResult) => void;
  removeImage: (imageId: string) => void;
  setSelectedImage: (image: ImageResult | null) => void;
  setGenerating: (generating: boolean) => void;
  setCurrentTaskId: (taskId: string | null) => void;
  setPrompt: (prompt: string) => void;
  setSize: (size: string) => void;
  setCount: (count: number) => void;
  addVideo: (video: VideoResult) => void;
  setVideos: (videos: VideoResult[]) => void;
  removeVideo: (videoId: string) => void;
  clearVideos: () => void;
  setGeneratingVideo: (generating: boolean) => void;
  clear: () => void;
}

export const useStoryboardStore = create<StoryboardState>((set) => ({
  images: [],
  videos: [],
  isGenerating: false,
  isGeneratingVideo: false,
  currentTaskId: null,
  selectedImage: null,
  prompt: '',
  size: '1024*1024',
  count: 2,  // 默认生成2张

  setImages: (images) => set({ images }),

  addImage: (image) =>
    set((state) => ({
      images: [...state.images, image],
    })),

  removeImage: (imageId) =>
    set((state) => ({
      images: state.images.filter((img) => img.id !== imageId),
      selectedImage:
        state.selectedImage?.id === imageId ? null : state.selectedImage,
    })),

  setSelectedImage: (selectedImage) => set({ selectedImage }),

  setGenerating: (isGenerating) => set({ isGenerating }),

  setCurrentTaskId: (currentTaskId) => set({ currentTaskId }),

  setPrompt: (prompt) => set({ prompt }),

  setSize: (size) => set({ size }),

  setCount: (count) => set({ count }),

  addVideo: (video) =>
    set((state) => ({
      videos: [...state.videos, video],
    })),

  setVideos: (videos) => set({ videos }),

  removeVideo: (videoId) =>
    set((state) => ({
      videos: state.videos.filter((v) => v.id !== videoId),
    })),

  clearVideos: () => set({ videos: [] }),

  setGeneratingVideo: (isGeneratingVideo) => set({ isGeneratingVideo }),

  clear: () =>
    set({
      images: [],
      videos: [],
      isGenerating: false,
      isGeneratingVideo: false,
      currentTaskId: null,
      selectedImage: null,
      prompt: '',
      size: '1024*1024',
      count: 2,  // 默认生成2张
    }),
}));
