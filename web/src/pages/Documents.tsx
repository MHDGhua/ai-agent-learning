import React, { useState } from 'react';
import { Card, Form, Input, Select, Button, Alert, Typography, Tag, Space, Divider, Tabs } from 'antd';
import { FileTextOutlined, CheckCircleOutlined, WarningOutlined, DownloadOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Text, Paragraph } = Typography;

const DOCUMENT_TYPES = [
  { value: '仲裁申请书', label: '仲裁申请书' },
  { value: '庭前调解申请书', label: '庭前调解申请书' },
  { value: '答辩书', label: '答辩书' },
  { value: '证据清单', label: '证据清单' },
  { value: '代理词', label: '代理词' },
];

const API_BASE = '/api';

interface GenerationResult {
  content: string;
  advice: string;
  document_type: string;
  generated_at: string;
}

const DocumentsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onGenerate = async (values: any) => {
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      document_type: values.document_type,
      case_data: {
        case_type: values.case_type || '劳动纠纷',
        facts: values.facts || '',
        evidence: values.evidence ? values.evidence.split('\n').filter((s: string) => s.trim()) : [],
        salary: values.salary ? parseFloat(values.salary) : undefined,
        amount: values.amount ? parseFloat(values.amount) : undefined,
        applicant_info: {
          name: values.applicant_name || '',
          employer_name: values.employer_name || '',
          phone: values.phone || '',
        },
      },
    };

    try {
      const res = await fetch(`${API_BASE}/arbitration/generate-document`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || errData.error || `服务器返回 ${res.status}`);
      }

      const data = await res.json();
      setResult({
        content: data.content,
        advice: data.advice,
        document_type: data.document_type,
        generated_at: data.generated_at,
      });
    } catch (err: any) {
      setError(err.message || '文书生成失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const blob = new Blob([result.content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${result.document_type}_${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const tabItems = [
    {
      key: 'form',
      label: '填写案件信息',
      children: (
        <Form form={form} layout="vertical" onFinish={onGenerate} style={{ maxWidth: 700 }}>
          <Form.Item label="文书类型" name="document_type" rules={[{ required: true, message: '请选择文书类型' }]}>
            <Select options={DOCUMENT_TYPES} placeholder="选择要生成的文书类型" />
          </Form.Item>
          <Form.Item label="案件类型" name="case_type" initialValue="劳动纠纷">
            <Input placeholder="如：违法解除劳动合同、拖欠工资" />
          </Form.Item>
          <Form.Item label="申请人姓名" name="applicant_name">
            <Input placeholder="申请人姓名" />
          </Form.Item>
          <Form.Item label="被申请人（用人单位）" name="employer_name">
            <Input placeholder="公司全称" />
          </Form.Item>
          <Form.Item label="联系电话" name="phone">
            <Input placeholder="联系电话" />
          </Form.Item>
          <Form.Item label="月工资（元）" name="salary">
            <Input placeholder="离职前12个月平均工资" type="number" />
          </Form.Item>
          <Form.Item label="请求金额（元）" name="amount">
            <Input placeholder="仲裁请求总金额（如有）" type="number" />
          </Form.Item>
          <Form.Item label="案件事实" name="facts" rules={[{ required: true, message: '请描述案件事实' }]}>
            <TextArea rows={5} placeholder="请按时间顺序描述：入职时间、岗位、工资、争议经过、目前诉求..." />
          </Form.Item>
          <Form.Item label="证据材料（每行一项）" name="evidence">
            <TextArea rows={3} placeholder="劳动合同&#10;工资流水&#10;解除通知&#10;聊天记录" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} icon={<FileTextOutlined />} size="large">
              生成文书
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'preview',
      label: result ? `预览：${result.document_type}` : '预览',
      disabled: !result,
      children: result ? (
        <div>
          <Space style={{ marginBottom: 16 }}>
            <Tag color="blue">{result.document_type}</Tag>
            <Tag>{result.generated_at}</Tag>
            <Button icon={<DownloadOutlined />} onClick={handleDownload} size="small">
              下载文书
            </Button>
          </Space>

          {result.advice && (
            <Alert
              message="校验提示"
              description={result.advice}
              type={result.advice.includes('自动校验发现') ? 'warning' : 'info'}
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

          <Card
            size="small"
            style={{
              background: '#fafafa',
              fontFamily: 'SimSun, serif',
              fontSize: 14,
              lineHeight: 2,
              whiteSpace: 'pre-wrap',
              maxHeight: '60vh',
              overflow: 'auto',
            }}
          >
            {result.content}
          </Card>
        </div>
      ) : null,
    },
  ];

  return (
    <div className="page-container">
      <Card title="文书生成与预览">
        {error && (
          <Alert
            message="生成失败"
            description={error}
            type="error"
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 16 }}
          />
        )}
        <Tabs items={tabItems} defaultActiveKey="form" />
      </Card>
    </div>
  );
};

export default DocumentsPage;
