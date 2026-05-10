import type { LoginRequest, RegisterRequest, UserInfo, SystemSettings } from '@/types';

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const MOCK_USER: UserInfo = {
  id: 'usr_001',
  username: 'admin',
  nickname: '系统管理员',
  role: 'admin',
  email: 'admin@lerap.cq',
  phone: '138****8888',
  language: 'zh-CN',
  notificationsEnabled: true,
  createdAt: '2024-01-15T08:00:00Z',
};

const MOCK_SETTINGS: SystemSettings = {
  llmProvider: 'local',
  modelName: 'deepseek-v3',
  temperature: 0.3,
  maxTokens: 4096,
  knowledgeBasePath: 'data/chroma_db',
  enableChromaRetrieval: true,
  enableOppositionReview: true,
  apiRateLimit: 60,
};

export const authService = {
  async login(req: LoginRequest): Promise<{ user: UserInfo; token: string }> {
    await delay(800);
    if (req.username === 'admin' && req.password === 'admin123') {
      return { user: MOCK_USER, token: 'mock_token_' + Date.now() };
    }
    if (req.password.length >= 6) {
      return {
        user: { ...MOCK_USER, id: 'usr_002', username: req.username, nickname: req.username, role: 'user' },
        token: 'mock_token_' + Date.now(),
      };
    }
    throw new Error('用户名或密码错误');
  },

  async register(req: RegisterRequest): Promise<{ user: UserInfo; token: string }> {
    await delay(1000);
    if (req.username.length < 3) throw new Error('用户名至少3个字符');
    if (req.password !== req.confirmPassword) throw new Error('两次密码不一致');
    if (req.captcha !== '8888') throw new Error('验证码错误');
    const newUser: UserInfo = {
      id: 'usr_' + Date.now(),
      username: req.username,
      nickname: req.nickname,
      role: 'user',
      email: req.email,
      phone: req.phone,
      language: 'zh-CN',
      notificationsEnabled: true,
      createdAt: new Date().toISOString(),
    };
    return { user: newUser, token: 'mock_token_' + Date.now() };
  },

  async updateProfile(updates: Partial<UserInfo>): Promise<UserInfo> {
    await delay(500);
    return { ...MOCK_USER, ...updates };
  },

  async changePassword(oldPwd: string, newPwd: string): Promise<void> {
    await delay(600);
    if (oldPwd.length < 6) throw new Error('原密码错误');
    if (newPwd.length < 6) throw new Error('新密码至少6位');
  },
};

export const settingsService = {
  async getSettings(): Promise<SystemSettings> {
    await delay(400);
    return { ...MOCK_SETTINGS };
  },

  async saveSettings(settings: SystemSettings): Promise<SystemSettings> {
    await delay(600);
    return { ...settings };
  },
};
