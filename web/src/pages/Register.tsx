import React, { useState } from 'react';
import { Card, Form, Input, Button, message, Progress, Typography } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined, SafetyOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/store/auth';
import { authService } from '@/services/api';

const RegisterPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const { login } = useAuth();
  const navigate = useNavigate();

  const calcStrength = (pwd: string): number => {
    let score = 0;
    if (pwd.length >= 6) score += 25;
    if (pwd.length >= 10) score += 25;
    if (/[A-Z]/.test(pwd)) score += 15;
    if (/[a-z]/.test(pwd)) score += 10;
    if (/[0-9]/.test(pwd)) score += 15;
    if (/[^A-Za-z0-9]/.test(pwd)) score += 10;
    return Math.min(100, score);
  };

  const getStrengthColor = (): string => {
    if (passwordStrength < 40) return '#ff4d4f';
    if (passwordStrength < 70) return '#faad14';
    return '#52c41a';
  };

  const getStrengthText = (): string => {
    if (passwordStrength < 40) return '弱';
    if (passwordStrength < 70) return '中';
    return '强';
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const { user, token } = await authService.register({
        username: values.username,
        password: values.password,
        confirmPassword: values.confirmPassword,
        nickname: values.nickname,
        email: values.email,
        phone: values.phone,
        captcha: values.captcha,
      });
      login(user, token);
      message.success('注册成功');
      navigate('/app/consultation');
    } catch (err: any) {
      message.error(err.message || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <Card className="auth-card" title="注册账号">
        <Form name="register" onFinish={onFinish} size="large" layout="vertical">
          <Form.Item name="username" rules={[
            { required: true, message: '请输入用户名' },
            { min: 3, message: '用户名至少3个字符' },
          ]}>
            <Input prefix={<UserOutlined />} placeholder="用户名（至少3个字符）" />
          </Form.Item>
          <Form.Item name="nickname" rules={[{ required: true, message: '请输入昵称' }]}>
            <Input prefix={<UserOutlined />} placeholder="昵称" />
          </Form.Item>
          <Form.Item name="email">
            <Input prefix={<MailOutlined />} placeholder="邮箱（选填）" type="email" />
          </Form.Item>
          <Form.Item name="phone">
            <Input prefix={<PhoneOutlined />} placeholder="手机号（选填）" />
          </Form.Item>
          <Form.Item name="password" rules={[
            { required: true, message: '请输入密码' },
            { min: 6, message: '密码至少6位' },
          ]}>
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码（至少6位）"
              onChange={(e) => setPasswordStrength(calcStrength(e.target.value))}
            />
          </Form.Item>
          {passwordStrength > 0 && (
            <div style={{ marginBottom: 16 }}>
              <Progress
                percent={passwordStrength}
                strokeColor={getStrengthColor()}
                format={() => `密码强度：${getStrengthText()}`}
                size="small"
              />
            </div>
          )}
          <Form.Item name="confirmPassword" rules={[
            { required: true, message: '请确认密码' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) return Promise.resolve();
                return Promise.reject(new Error('两次密码不一致'));
              },
            }),
          ]}>
            <Input.Password prefix={<LockOutlined />} placeholder="确认密码" />
          </Form.Item>
          <Form.Item name="captcha" rules={[{ required: true, message: '请输入验证码' }]}
            extra="模拟验证码：8888"
          >
            <Input prefix={<SafetyOutlined />} placeholder="验证码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              注册
            </Button>
          </Form.Item>
          <div style={{ textAlign: 'center' }}>
            已有账号？<Link to="/login">返回登录</Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default RegisterPage;
