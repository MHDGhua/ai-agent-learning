import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, App as AntApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { AuthProvider } from '@/store/auth';
import ProtectedRoute from '@/components/ProtectedRoute';
import AppLayout from '@/layouts/AppLayout';
import LoginPage from '@/pages/Login';
import RegisterPage from '@/pages/Register';
import ConsultationPage from '@/pages/Consultation';
import DocumentsPage from '@/pages/Documents';
import SettingsPage from '@/pages/Settings';
import AdminSettings from '@/pages/AdminSettings';
import NotFoundPage from '@/pages/NotFound';
import ForbiddenPage from '@/pages/Forbidden';
import '@/styles/global.css';

const themeConfig = {
  token: {
    colorPrimary: '#1a5ab8',
    borderRadius: 6,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif',
  },
};

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN} theme={themeConfig}>
      <AntApp>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/403" element={<ForbiddenPage />} />

              <Route path="/app" element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }>
                <Route index element={<Navigate to="/app/consultation" replace />} />
                <Route path="consultation" element={<ConsultationPage />} />
                <Route path="documents" element={<DocumentsPage />} />
                <Route path="settings" element={<SettingsPage />} />
                <Route path="admin" element={
                  <ProtectedRoute requireAdmin>
                    <AdminSettings />
                  </ProtectedRoute>
                } />
              </Route>

              <Route path="/" element={<Navigate to="/app/consultation" replace />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </AntApp>
    </ConfigProvider>
  );
};

export default App;
