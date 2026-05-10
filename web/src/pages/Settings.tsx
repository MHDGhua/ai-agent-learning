import React, { useState } from 'react';
import { Card, Form, Input, Button, Switch, Select, Divider, message, Tabs } from 'antd';
import { useAuth } from '@/store/auth';
import { authService } from '@/services/api';

const SettingsPage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [profileLoading, setProfileLoading] = useState(false);
  const [pwdLoading, setPwdLoading] = useState(false);

  const onProfileFinish = async (values: any) => {
    setProfileLoading(true);
    try {
      await authService.updateProfile(values);
      updateUser(values);
      message.success('个人信息已更新');
    } catch (err: any) {
      message.error(err.message);
    } finally {
      setProfileLoading(false);
    }
  };

  const onPasswordFinish = async (values: any) => {
    setPwdLoading(true);
    try {
      await authService.changePassword(values.oldPassword, values.newPassword);
      message.success('密码修改成功');
    } catch (err: any) {
      message.error(err.message);
    } finally {
      setPwdLoading(false);
    }
  };

  const tabItems = [
    {
      key: 'profile',
      label: '基本信息',
      children: (
        <Form
          layout="vertical"
          initialValues={{
            nickname: user?.nickname,
            email: user?.email,
            phone: user?.phone,
            language: user?.language || 'zh-CN',
            notificationsEnabled: user?.notificationsEnabled ?? true,
          }}
          onFinish={onProfileFinish}
        >
          <Form.Item label="昵称" name="nickname" rules={[{ required: true, message: '请输入昵称' }]}>
            <Input placeholder="昵称" />
          </Form.Item>
          <Form.Item label="邮箱" name="email">
            <Input placeholder="邮箱" type="email" />
          </Form.Item>
          <Form.Item label="手机号" name="phone">
            <Input placeholder="手机号" />
          </Form.Item>
          <Form.Item label="偏好语言" name="language">
            <Select options={[
              { value: 'zh-CN', label: '简体中文' },
              { value: 'en-US', label: 'English' },
            ]} />
          </Form.Item>
          <Form.Item label="消息通知" name="notificationsEnabled" valuePropName="checked">
            <Switch checkedChildren="开" unCheckedChildren="关" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={profileLoading}>
              保存修改
            </Button>
          </Form.Item>
        </Form>
      ),
    },
    {
      key: 'password',
      label: '修改密码',
      children: (
        <Form layout="vertical" onFinish={onPasswordFinish}>
          <Form.Item label="原密码" name="oldPassword" rules={[{ required: true, message: '请输入原密码' }]}>
            <Input.Password placeholder="原密码" />
          </Form.Item>
          <Form.Item label="新密码" name="newPassword" rules={[
            { required: true, message: '请输入新密码' },
            { min: 6, message: '密码至少6位' },
          ]}>
            <Input.Password placeholder="新密码（至少6位）" />
          </Form.Item>
          <Form.Item label="确认新密码" name="confirmPassword" rules={[
            { required: true, message: '请确认新密码' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('newPassword') === value) return Promise.resolve();
                return Promise.reject(new Error('两次密码不一致'));
              },
            }),
          ]}>
            <Input.Password placeholder="确认新密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={pwdLoading}>
              修改密码
            </Button>
          </Form.Item>
        </Form>
      ),
    },
  ];

  return (
    <div className="page-container">
      <Card title="个人设置">
        <Tabs items={tabItems} />
      </Card>
    </div>
  );
};

export default SettingsPage;
