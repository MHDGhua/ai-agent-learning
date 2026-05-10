import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, Spin, Tag, Collapse, List, Typography, Alert, Space } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Text, Title, Paragraph } = Typography;

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  data?: any;
}

const API_BASE = '/api';

const riskColors: Record<string, string> = {
  '低': 'green',
  '中': 'orange',
  '高': 'red',
  'low': 'green',
  'medium': 'orange',
  'high': 'red',
};

const ConsultationPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const payload = {
        case_type: '劳动纠纷',
        facts: text,
        evidence: [],
        applicant_info: {},
      };

      const res = await fetch(`${API_BASE}/arbitration/workup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`服务器返回 ${res.status}`);
      }

      const data = await res.json();
      const analysis = data.analysis || {};
      const summary = analysis.summary || '分析完成，请查看详细结果。';

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: summary,
        timestamp: new Date().toLocaleTimeString(),
        data,
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `分析请求失败：${err.message}。请确认后端服务已启动（端口 8000）。`,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderAnalysisCard = (data: any) => {
    const analysis = data.analysis || {};
    const intake = data.intake || {};
    const successPrediction = data.success_prediction || {};
    const references = data.local_references || [];
    const suggestedDocs = data.suggested_documents || [];

    const collapseItems = [
      {
        key: 'claims',
        label: `仲裁请求项 (${(analysis.claim_items || []).length})`,
        children: (
          <List
            size="small"
            dataSource={analysis.claim_items || []}
            renderItem={(item: any) => (
              <List.Item>
                <Text strong>{item.name}</Text>
                {item.amount && <Tag color="blue">{item.amount}元</Tag>}
              </List.Item>
            )}
          />
        ),
      },
      {
        key: 'recommendations',
        label: '建议措施',
        children: (
          <List
            size="small"
            dataSource={analysis.recommendations || []}
            renderItem={(item: string) => <List.Item>{item}</List.Item>}
          />
        ),
      },
      {
        key: 'missing',
        label: `待补充信息 (${(intake.missing_questions || []).length})`,
        children: (
          <List
            size="small"
            dataSource={intake.missing_questions || []}
            renderItem={(item: string) => <List.Item><Text type="warning">{item}</Text></List.Item>}
          />
        ),
      },
      {
        key: 'references',
        label: `重庆本地参考 (${references.length})`,
        children: (
          <List
            size="small"
            dataSource={references}
            renderItem={(item: any) => (
              <List.Item>
                <Text strong>{item.title}</Text>
                {item.source && <Text type="secondary"> — {item.source}</Text>}
              </List.Item>
            )}
          />
        ),
      },
    ];

    return (
      <div style={{ marginTop: 12 }}>
        <Space wrap style={{ marginBottom: 12 }}>
          <Tag color={riskColors[analysis.risk_level] || 'default'}>
            风险：{analysis.risk_level}
          </Tag>
          <Tag color="blue">
            成功率：{successPrediction.success_probability || '未知'}
          </Tag>
          <Tag>阶段：{data.workflow_stage}</Tag>
        </Space>
        {suggestedDocs.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <Text type="secondary">建议文书：</Text>
            {suggestedDocs.map((doc: string) => (
              <Tag key={doc} color="geekblue">{doc}</Tag>
            ))}
          </div>
        )}
        <Collapse items={collapseItems} size="small" />
      </div>
    );
  };

  return (
    <div style={{ height: 'calc(100vh - 160px)', display: 'flex', flexDirection: 'column' }}>
      <Card
        title="智能咨询对话"
        style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
        styles={{ body: { flex: 1, overflow: 'auto', padding: '16px' } }}
      >
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
            <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
            <Paragraph type="secondary">
              请描述您的劳动争议情况，系统将为您提供案件分析、风险评估和策略建议。
            </Paragraph>
            <Paragraph type="secondary" style={{ fontSize: 12 }}>
              示例：我在重庆某公司工作3年，月薪8000元，公司以经营困难为由将我辞退，未支付任何补偿。
            </Paragraph>
          </div>
        )}

        {messages.map(msg => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: 16,
            }}
          >
            <div style={{
              maxWidth: '80%',
              padding: '12px 16px',
              borderRadius: 12,
              background: msg.role === 'user' ? '#1a5ab8' : '#f5f5f5',
              color: msg.role === 'user' ? '#fff' : '#333',
            }}>
              <div style={{ fontSize: 12, opacity: 0.7, marginBottom: 4 }}>
                {msg.role === 'user' ? '您' : '法律助手'} · {msg.timestamp}
              </div>
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
              {msg.data && renderAnalysisCard(msg.data)}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 16 }}>
            <div style={{ padding: '12px 16px', borderRadius: 12, background: '#f5f5f5' }}>
              <Spin size="small" /> <Text type="secondary">正在分析案件...</Text>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </Card>

      <div style={{ padding: '12px 0', display: 'flex', gap: 12 }}>
        <TextArea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="描述您的劳动争议情况...（Enter 发送，Shift+Enter 换行）"
          autoSize={{ minRows: 1, maxRows: 4 }}
          style={{ flex: 1 }}
          disabled={loading}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={sendMessage}
          loading={loading}
          style={{ height: 'auto' }}
        >
          发送
        </Button>
      </div>
    </div>
  );
};

export default ConsultationPage;
