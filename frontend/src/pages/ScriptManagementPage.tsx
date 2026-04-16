import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Upload,
  Select,
  message,
  Popconfirm,
  Card,
} from 'antd';
import {
  UploadOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import type { UploadFile } from 'antd';
import { apiService, ScriptResponse } from '../services/api';

const { TextArea } = Input;

export default function ScriptManagementPage() {
  const [scripts, setScripts] = useState<ScriptResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [keyword, setKeyword] = useState('');
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [currentScript, setCurrentScript] = useState<ScriptResponse | null>(null);
  const [scriptContent, setScriptContent] = useState('');
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploadForm] = Form.useForm();
  const [editForm] = Form.useForm();

  const loadScripts = async () => {
    setLoading(true);
    try {
      const response = await apiService.listScripts({
        page,
        page_size: pageSize,
        keyword: keyword || undefined,
      });
      if (response.code === 0 && response.data) {
        setScripts(response.data.items);
        setTotal(response.data.total);
      }
    } catch (error: any) {
      message.error('加载脚本列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScripts();
  }, [page, pageSize]);

  const handleUpload = async (values: any) => {
    if (fileList.length === 0) {
      message.error('请选择文件');
      return;
    }

    try {
      const file = fileList[0].originFileObj as File;
      await apiService.uploadScript({
        name: values.name,
        description: values.description,
        language: values.language,
        tags: values.tags,
        file,
      });
      message.success('上传成功');
      setUploadModalVisible(false);
      uploadForm.resetFields();
      setFileList([]);
      loadScripts();
    } catch (error: any) {
      message.error(error.response?.data?.message || '上传失败');
    }
  };

  const handleEdit = async (values: any) => {
    if (!currentScript) return;

    try {
      await apiService.updateScript(currentScript.id, {
        name: values.name,
        description: values.description,
        tags: values.tags ? values.tags.split(',').map((t: string) => t.trim()) : [],
      });
      message.success('更新成功');
      setEditModalVisible(false);
      setCurrentScript(null);
      editForm.resetFields();
      loadScripts();
    } catch (error: any) {
      message.error(error.response?.data?.message || '更新失败');
    }
  };

  const handleDelete = async (scriptId: number) => {
    try {
      await apiService.deleteScript(scriptId);
      message.success('删除成功');
      loadScripts();
    } catch (error: any) {
      message.error(error.response?.data?.message || '删除失败');
    }
  };

  const handleExecute = async (scriptId: number) => {
    try {
      await apiService.createExecution(scriptId);
      message.success('执行任务已创建，请到执行管理页面查看');
      setTimeout(() => {
        window.location.href = '/executions';
      }, 1500);
    } catch (error: any) {
      message.error(error.response?.data?.message || '创建执行任务失败');
    }
  };

  const handleView = async (script: ScriptResponse) => {
    setCurrentScript(script);
    setViewModalVisible(true);
    try {
      const response = await apiService.getScriptContent(script.id);
      if (response.code === 0 && response.data) {
        setScriptContent(response.data.content);
      }
    } catch (error: any) {
      message.error('加载脚本内容失败');
    }
  };

  const handleEditClick = (script: ScriptResponse) => {
    setCurrentScript(script);
    editForm.setFieldsValue({
      name: script.name,
      description: script.description,
      tags: script.tags.join(', '),
    });
    setEditModalVisible(true);
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '脚本名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '语言',
      dataIndex: 'language',
      key: 'language',
      width: 100,
      render: (language: string) => (
        <Tag color={language === 'python' ? 'blue' : language === 'shell' ? 'green' : 'orange'}>
          {language}
        </Tag>
      ),
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: string[]) => (
        <>
          {tags.map((tag) => (
            <Tag key={tag}>{tag}</Tag>
          ))}
        </>
      ),
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 120,
      render: (size: number) => `${(size / 1024).toFixed(2)} KB`,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      render: (_: any, record: ScriptResponse) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleExecute(record.id)}
          >
            执行
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditClick(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除此脚本吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Input.Search
            placeholder="搜索脚本名称或描述"
            style={{ width: 300 }}
            onSearch={(value) => {
              setKeyword(value);
              setPage(1);
              loadScripts();
            }}
            allowClear
          />
          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => setUploadModalVisible(true)}
          >
            上传脚本
          </Button>
          <Button icon={<ReloadOutlined />} onClick={loadScripts}>
            刷新
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={scripts}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            onChange: (page, pageSize) => {
              setPage(page);
              setPageSize(pageSize);
            },
          }}
        />
      </Card>

      {/* 上传脚本模态框 */}
      <Modal
        title="上传测试脚本"
        open={uploadModalVisible}
        onCancel={() => {
          setUploadModalVisible(false);
          uploadForm.resetFields();
          setFileList([]);
        }}
        onOk={() => uploadForm.submit()}
        width={600}
      >
        <Form form={uploadForm} layout="vertical" onFinish={handleUpload}>
          <Form.Item
            name="name"
            label="脚本名称"
            rules={[{ required: true, message: '请输入脚本名称' }]}
          >
            <Input placeholder="例如：IMSI验证测试" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="脚本功能描述" />
          </Form.Item>

          <Form.Item
            name="language"
            label="语言"
            initialValue="python"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="python">Python</Select.Option>
              <Select.Option value="shell">Shell</Select.Option>
              <Select.Option value="javascript">JavaScript</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="tags" label="标签">
            <Input placeholder="多个标签用逗号分隔，例如：IMSI,功能测试" />
          </Form.Item>

          <Form.Item label="脚本文件" required>
            <Upload
              fileList={fileList}
              beforeUpload={(file) => {
                setFileList([file]);
                return false;
              }}
              onRemove={() => setFileList([])}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
            <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
              支持 .py, .sh, .js 文件，最大 10MB
            </div>
          </Form.Item>
        </Form>
      </Modal>

      {/* 编辑脚本模态框 */}
      <Modal
        title="编辑脚本"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          setCurrentScript(null);
          editForm.resetFields();
        }}
        onOk={() => editForm.submit()}
        width={600}
      >
        <Form form={editForm} layout="vertical" onFinish={handleEdit}>
          <Form.Item
            name="name"
            label="脚本名称"
            rules={[{ required: true, message: '请输入脚本名称' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item name="tags" label="标签">
            <Input placeholder="多个标签用逗号分隔" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 查看脚本内容模态框 */}
      <Modal
        title={`查看脚本：${currentScript?.name}`}
        open={viewModalVisible}
        onCancel={() => {
          setViewModalVisible(false);
          setCurrentScript(null);
          setScriptContent('');
        }}
        footer={[
          <Button key="close" onClick={() => setViewModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        <pre
          style={{
            background: '#f5f5f5',
            padding: 16,
            borderRadius: 4,
            maxHeight: 500,
            overflow: 'auto',
          }}
        >
          {scriptContent}
        </pre>
      </Modal>
    </div>
  );
}
