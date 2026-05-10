import React, { useState } from 'react';
import { Card, Form, Input, Button, Checkbox, message, Typography } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/store/auth';
import { authService } from '@/services/api';

const { Title } = Typography;

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string; remember: boolean }) => {
    setLoading(true);
    try {
      const { user, token } = await authService.login({
        username: values.username,
        password: values.password,
        remember: values.remember,
      });
      login(user, token);
      message.success('登录成功');
      navigate('/app/consultation');
    } catch (err: any) {
      message.error(err.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <Card className="auth-card" title="重庆劳动法专家系统">
        <div className="auth-logo">⚖️</div>
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          size="large"
          layout="vertical"
        >
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          <Form.Item>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox>记住我</Checkbox>
              </Form.Item>
              <a href="#" onClick={(e) => { e.preventDefault(); message.info('请联系管理员重置密码'); }}>
                忘记密码？
              </a>
            </div>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
          <div style={{ textAlign: 'center' }}>
            还没有账号？<Link to="/register">立即注册</Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
