import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, theme, Button } from 'antd';
import {
  MessageOutlined,
  FileTextOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { useAuth } from '@/store/auth';

const { Header, Sider, Content } = Layout;

const AppLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { token: themeToken } = theme.useToken();

  const menuItems = [
    { key: '/app/consultation', icon: <MessageOutlined />, label: '智能咨询' },
    { key: '/app/documents', icon: <FileTextOutlined />, label: '文书生成' },
    { key: '/app/settings', icon: <SettingOutlined />, label: '个人设置' },
    ...(user?.role === 'admin' ? [
      { key: '/app/admin', icon: <DashboardOutlined />, label: '系统管理' },
    ] : []),
  ];

  const userMenuItems = [
    { key: 'profile', icon: <UserOutlined />, label: '个人设置' },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', danger: true },
  ];

  const handleUserMenu = ({ key }: { key: string }) => {
    if (key === 'logout') {
      logout();
      navigate('/login');
    } else if (key === 'profile') {
      navigate('/app/settings');
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        breakpoint="lg"
        onBreakpoint={(broken) => setCollapsed(broken)}
        style={{ background: 'var(--sidebar-bg)' }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: collapsed ? 16 : 18,
          fontWeight: 600,
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
        }}>
          {collapsed ? 'CQ' : '重庆劳动法专家'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{
          padding: '0 24px',
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <Dropdown menu={{ items: userMenuItems, onClick: handleUserMenu }} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar style={{ backgroundColor: themeToken.colorPrimary }} icon={<UserOutlined />} />
              <span style={{ fontSize: 14 }}>{user?.nickname || user?.username}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24, minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
