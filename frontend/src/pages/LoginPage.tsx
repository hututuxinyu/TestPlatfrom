import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { apiService } from '../services/api';
import type { LoginRequest } from '../types/api';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: LoginRequest) => {
    setLoading(true);
    try {
      const response = await apiService.login(values);
      if (response.code === 0 && response.data) {
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('username', response.data.username);
        message.success('登录成功');
        navigate('/');
      } else {
        message.error(response.message || '登录失败');
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || '登录失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 50%, #80deea 100%)',
      backgroundImage: `
        linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 50%, #80deea 100%),
        repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255,255,255,.1) 35px, rgba(255,255,255,.1) 70px)
      `,
      position: 'relative'
    }}>
      {/* 顶部品牌区 */}
      <div style={{
        textAlign: 'center',
        marginBottom: '40px'
      }}>
        {/* Logo */}
        <div style={{
          width: '80px',
          height: '80px',
          margin: '0 auto 20px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 8px 24px rgba(102, 126, 234, 0.4)',
          fontSize: '40px'
        }}>
          ☁️
        </div>

        {/* 系统名称 */}
        <h1 style={{
          fontSize: '32px',
          fontWeight: 700,
          color: '#1a237e',
          margin: '0 0 8px 0',
          letterSpacing: '1px'
        }}>
          云手机测试系统
        </h1>

        {/* 系统描述 */}
        <p style={{
          fontSize: '14px',
          color: '#546e7a',
          margin: 0,
          fontWeight: 400
        }}>
          一站式云手机管控与自动化测试平台
        </p>
      </div>

      {/* 登录卡片 */}
      <div style={{
        width: '420px',
        background: '#ffffff',
        borderRadius: '16px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
        padding: '48px 40px',
        backdropFilter: 'blur(10px)'
      }}>
        {/* 卡片标题 */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: 600,
            color: '#263238',
            margin: '0 0 8px 0'
          }}>
            欢迎登录
          </h2>
          <p style={{
            fontSize: '14px',
            color: '#90a4ae',
            margin: 0
          }}>
            请输入账号信息访问系统
          </p>
        </div>

        {/* 登录表单 */}
        <Form
          name="login"
          initialValues={{ username: 'admin', password: 'admin123' }}
          onFinish={onFinish}
          size="large"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined style={{ color: '#90a4ae' }} />}
              placeholder="请输入用户名"
              style={{
                height: '48px',
                borderRadius: '8px',
                fontSize: '15px'
              }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
            style={{ marginBottom: '32px' }}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#90a4ae' }} />}
              placeholder="请输入密码"
              style={{
                height: '48px',
                borderRadius: '8px',
                fontSize: '15px'
              }}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{
                height: '48px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 600,
                background: 'linear-gradient(135deg, #26c6da 0%, #00acc1 100%)',
                border: 'none',
                boxShadow: '0 4px 12px rgba(38, 198, 218, 0.4)',
                transition: 'all 0.3s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(38, 198, 218, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(38, 198, 218, 0.4)';
              }}
            >
              登录
            </Button>
          </Form.Item>
        </Form>
      </div>

      {/* 底部版权信息 */}
      <div style={{
        position: 'absolute',
        bottom: '24px',
        textAlign: 'center',
        color: '#78909c',
        fontSize: '13px'
      }}>
        © 2026 云手机测试系统 版权所有
      </div>
    </div>
  );
}
