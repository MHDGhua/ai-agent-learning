import React, { useState, useEffect } from 'react';
import { Card, Form, Input, InputNumber, Switch, Select, Button, message, Divider, Spin } from 'antd';
import { settingsService } from '@/services/api';
import type { SystemSettings } from '@/types';

const AdminSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    settingsService.getSettings().then((settings) => {
      form.setFieldsValue(settings);
      setLoading(false);
    });
  }, [form]);

  const onFinish = async (values: SystemSettings) => {
    setSaving(true);
    try {
      await settingsService.saveSettings(values);
      message.success('系统设置已保存');
    } catch (err: any) {
      message.error(err.message || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 80 }}><Spin size="large" /></div>;
  }

  return (
    <div className="page-container">
      <Card title="系统设置（管理员）">
        <Form form={form} layout="vertical" onFinish={onFinish} style={{ maxWidth: 600 }}>
          <Divider orientation="left">AI 模型配置</Divider>
          <Form.Item label="LLM 提供商" name="llmProvider" rules={[{ required: true }]}>
            <Select options={[
              { value: 'local', label: '本地模式（无需API）' },
              { value: 'openai', label: 'OpenAI' },
              { value: 'deepseek', label: 'DeepSeek' },
              { value: 'magic_tower', label: '通义千问（魔搭）' },
              { value: 'azure', label: 'Azure OpenAI' },
            ]} />
          </Form.Item>
          <Form.Item label="模型名称" name="modelName">
            <Input placeholder="如 deepseek-v3, gpt-4o" />
          </Form.Item>
          <Form.Item label="Temperature" name="temperature">
            <InputNumber min={0} max={2} step={0.1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="最大 Token 数" name="maxTokens">
            <InputNumber min={256} max={32768} step={256} style={{ width: '100%' }} />
          </Form.Item>

          <Divider orientation="left">知识库配置</Divider>
          <Form.Item label="知识库路径" name="knowledgeBasePath">
            <Input placeholder="data/chroma_db" />
          </Form.Item>
          <Form.Item label="启用 ChromaDB 检索" name="enableChromaRetrieval" valuePropName="checked">
            <Switch checkedChildren="开" unCheckedChildren="关" />
          </Form.Item>

          <Divider orientation="left">功能开关</Divider>
          <Form.Item label="启用红蓝对抗审查" name="enableOppositionReview" valuePropName="checked">
            <Switch checkedChildren="开" unCheckedChildren="关" />
          </Form.Item>
          <Form.Item label="API 速率限制（次/分钟）" name="apiRateLimit">
            <InputNumber min={1} max={1000} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={saving}>
              保存设置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default AdminSettings;
