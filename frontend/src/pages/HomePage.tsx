import { useEffect, useState } from 'react';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, message } from 'antd';
import { LogoutOutlined, FileTextOutlined, PlayCircleOutlined, BarChartOutlined } from '@ant-design/icons';
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
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#001529' }}>
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          云手机测试平台
        </div>
        <div style={{ color: 'white' }}>
          <span style={{ marginRight: 16 }}>欢迎，{username}</span>
          <Button
            type="text"
            icon={<LogoutOutlined />}
            onClick={handleLogout}
            style={{ color: 'white' }}
          >
            退出
          </Button>
        </div>
      </Header>
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>
        <Layout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: '#fff',
            }}
          >
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
}
