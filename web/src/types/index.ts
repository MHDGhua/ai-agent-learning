export interface UserInfo {
  id: string;
  username: string;
  nickname: string;
  role: 'user' | 'admin';
  avatar?: string;
  email?: string;
  phone?: string;
  language: 'zh-CN' | 'en-US';
  notificationsEnabled: boolean;
  createdAt: string;
}

export interface LoginRequest {
  username: string;
  password: string;
  remember?: boolean;
}

export interface RegisterRequest {
  username: string;
  password: string;
  confirmPassword: string;
  nickname: string;
  email?: string;
  phone?: string;
  captcha: string;
}

export interface SystemSettings {
  llmProvider: string;
  modelName: string;
  temperature: number;
  maxTokens: number;
  knowledgeBasePath: string;
  enableChromaRetrieval: boolean;
  enableOppositionReview: boolean;
  apiRateLimit: number;
}

export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  children?: MenuItem[];
}
