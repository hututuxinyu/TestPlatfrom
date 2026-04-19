import { useEffect, useState } from 'react';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, message } from 'antd';
import { LogoutOutlined, FileTextOutlined, PlayCircleOutlined, BarChartOutlined, SettingOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';

const { Header, Content, Sider } = Layout;

export default function HomePage() {
  const [username, setUsername] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) {
      setUsername(storedUsername);
    }
  }, []);

  const handleLogout = async () => {
    try {
      await apiService.logout();
      localStorage.removeItem('access_token');
      localStorage.removeItem('username');
      message.success('退出成功');
      navigate('/login');
    } catch (error) {
      message.error('退出失败');
    }
  };

  const menuItems = [
    {
      key: '/scripts',
      icon: <FileTextOutlined />,
      label: '脚本管理',
    },
    {
      key: '/executions',
      icon: <PlayCircleOutlined />,
      label: '执行管理',
    },
    {
      key: '/configs',
      icon: <SettingOutlined />,
      label: '环境配置',
    },
    {
      key: '/reports',
      icon: <BarChartOutlined />,
      label: '测试报告',
    },
  ];

  const handleMenuClick = (e: { key: string }) => {
    navigate(e.key);
  };

  const selectedKey = location.pathname === '/' ? '/scripts' : location.pathname;

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          padding: '0 24px',
          position: 'sticky',
          top: 0,
          zIndex: 1000
        }}
      >
        <div style={{
          color: 'white',
          fontSize: '22px',
          fontWeight: 600,
          letterSpacing: '0.5px'
        }}>
          ☁️ 云手机测试平台
        </div>
        <div style={{ color: 'white', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ opacity: 0.9 }}>欢迎，{username}</span>
          <Button
            type="text"
            icon={<LogoutOutlined />}
            onClick={handleLogout}
            style={{
              color: 'white',
              borderRadius: '6px',
              transition: 'all 0.3s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
            }}
          >
            退出
          </Button>
        </div>
      </Header>
      <Layout>
        <Sider
          width={220}
          style={{
            background: '#fff',
            boxShadow: '2px 0 8px rgba(0,0,0,0.06)',
            overflow: 'auto',
            height: 'calc(100vh - 64px)',
            position: 'sticky',
            top: 64,
            left: 0
          }}
        >
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            style={{
              height: '100%',
              borderRight: 0,
              paddingTop: '16px'
            }}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>
        <Layout style={{ background: '#f0f2f5' }}>
          <Content
            style={{
              padding: '24px',
              margin: 0,
              minHeight: 'calc(100vh - 64px)',
              overflow: 'auto'
            }}
          >
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}
