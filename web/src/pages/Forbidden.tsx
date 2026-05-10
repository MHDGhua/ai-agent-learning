import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';

const ForbiddenPage: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <Result
        status="403"
        title="403"
        subTitle="抱歉，您没有权限访问此页面。"
        extra={
          <Button type="primary" onClick={() => navigate('/app/consultation')}>
            返回首页
          </Button>
        }
      />
    </div>
  );
};

export default ForbiddenPage;
