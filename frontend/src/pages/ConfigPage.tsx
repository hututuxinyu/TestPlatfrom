import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  message,
  Popconfirm,
  Card,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { apiService, type ConfigResponse } from '../services/api';

const { TextArea } = Input;

export default function ConfigPage() {
  const [configs, setConfigs] = useState<ConfigResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingConfig, setEditingConfig] = useState<ConfigResponse | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const response = await apiService.listConfigs();
      if (response.code === 0 && response.data) {
        setConfigs(response.data.items || []);
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingConfig(null);
    form.resetFields();
    form.setFieldsValue({ key: 'GIDS_ADDR' });
    setModalVisible(true);
  };

  const handleEdit = (config: ConfigResponse) => {
    setEditingConfig(config);
    form.setFieldsValue({
      key: config.key,
      value: config.value,
      description: config.description,
    });
    setModalVisible(true);
  };

  const handleDelete = async (key: string) => {
    try {
      await apiService.deleteConfig(key);
      message.success('删除成功');
      loadConfigs();
    } catch (error: any) {
      message.error(error.response?.data?.message || '删除失败');
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      await apiService.createOrUpdateConfig({
        key: values.key,
        value: values.value,
        description: values.description || '',
      });
      message.success(editingConfig ? '更新成功' : '创建成功');
      setModalVisible(false);
      form.resetFields();
      loadConfigs();
    } catch (error: any) {
      message.error(error.response?.data?.message || '操作失败');
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
      align: 'center' as const,
    },
    {
      title: '配置键',
      dataIndex: 'key',
      key: 'key',
      width: 200,
    },
    {
      title: '配置值',
      dataIndex: 'value',
      key: 'value',
      width: 300,
      ellipsis: true,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 160,
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: ConfigResponse) => (
        <Space size="small">
          <Button
            type="default"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此配置吗？"
            onConfirm={() => handleDelete(record.key)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="default" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ maxWidth: '100%' }}>
      <Card
        variant="borderless"
        style={{
          borderRadius: '12px',
          boxShadow: '0 1px 2px rgba(0,0,0,0.03), 0 2px 8px rgba(0,0,0,0.06)'
        }}
      >
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 20,
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ fontSize: '18px', fontWeight: 600, color: '#262626' }}>
            ⚙️ 环境配置
          </div>
          <Space size="middle">
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: '6px',
                height: '36px'
              }}
            >
              添加配置
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadConfigs}
              style={{ borderRadius: '6px', height: '36px' }}
            >
              刷新
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={configs}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1000 }}
          style={{ marginTop: 16 }}
          pagination={false}
        />
      </Card>

      <Modal
        title={editingConfig ? '编辑配置' : '添加配置'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="配置键"
            name="key"
            initialValue="GIDS_ADDR"
          >
            <Input
              value="GIDS_ADDR"
              disabled
            />
          </Form.Item>

          <Form.Item
            label="配置值"
            name="value"
            rules={[{ required: true, message: '请输入配置值' }]}
          >
            <Input placeholder="例如: http://192.168.1.100:9090" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
          >
            <TextArea
              rows={3}
              placeholder="配置说明（可选）"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
