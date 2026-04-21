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
import { apiService, type ScriptResponse } from '../services/api';

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
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [batchDeleteModalVisible, setBatchDeleteModalVisible] = useState(false);
  const [batchDeleteConfirmInput, setBatchDeleteConfirmInput] = useState('');
  const [batchExecuting, setBatchExecuting] = useState(false);

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

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys),
  };

  const handleBatchExecute = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要执行的脚本');
      return;
    }
    setBatchExecuting(true);
    try {
      const response = await apiService.batchExecuteAll();
      if (response.code === 0 && response.data) {
        const { total, succeeded, failed } = response.data;
        message.success(`批量执行完成: 成功 ${succeeded}/${total}`);
        if (failed > 0) {
          message.warning(`${failed} 个脚本执行失败`);
        }
        setSelectedRowKeys([]);
        setTimeout(() => {
          window.location.href = '/executions';
        }, 1500);
      }
    } catch (error: any) {
      message.error(error.response?.data?.error || '批量执行失败');
    } finally {
      setBatchExecuting(false);
    }
  };

  const handleBatchDeleteClick = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的脚本');
      return;
    }
    setBatchDeleteModalVisible(true);
    setBatchDeleteConfirmInput('');
  };

  const handleBatchDelete = async () => {
    if (batchDeleteConfirmInput !== 'delete') {
      message.error('请输入 "delete" 确认删除');
      return;
    }
    try {
      const response = await apiService.batchDeleteScripts(selectedRowKeys as number[]);
      if (response.code === 0 && response.data) {
        message.success(response.data.message);
        setBatchDeleteModalVisible(false);
        setBatchDeleteConfirmInput('');
        setSelectedRowKeys([]);
        loadScripts();
      }
    } catch (error: any) {
      message.error(error.response?.data?.error || '批量删除失败');
    }
  };

  const handleUpload = async (values: any) => {
    if (fileList.length === 0) {
      message.error('请选择文件');
      return;
    }

    const file = fileList[0].originFileObj;
    if (!file) {
      message.error('文件对象无效，请重新选择文件');
      return;
    }

    // Auto-detect language from file extension
    const ext = file.name.split('.').pop()?.toLowerCase();
    const languageMap: Record<string, string> = {
      py: 'python',
      sh: 'shell',
      js: 'javascript',
    };
    const language = languageMap[ext || ''] || 'python';

    try {
      await apiService.uploadScript({
        language,
        tags: values.tags ? values.tags.join(',') : undefined,
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
    const tagValue = Array.isArray(script.tags) ? script.tags.join(', ') : (script.tags || '');
    editForm.setFieldsValue({
      name: script.name,
      description: script.description,
      tags: tagValue,
    });
    setEditModalVisible(true);
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
      title: '脚本名称',
      dataIndex: 'name',
      key: 'name',
      width: 180,
      ellipsis: true,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 250,
      ellipsis: true,
    },
    {
      title: '语言',
      dataIndex: 'language',
      key: 'language',
      width: 90,
      align: 'center' as const,
      render: (language: string) => (
        <Tag color={language === 'python' ? 'blue' : language === 'shell' ? 'green' : 'orange'}>
          {language.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 150,
      render: (tags: string | string[]) => {
        const tagArray = Array.isArray(tags) ? tags : (typeof tags === 'string' && tags ? tags.split(',').map(t => t.trim()).filter(t => t) : []);
        if (tagArray.length === 0) return null;
        return (
          <>
            {tagArray.map((tag) => (
              <Tag key={tag} color="cyan">{tag}</Tag>
            ))}
          </>
        );
      },
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      align: 'right' as const,
      render: (size: number) => `${(size / 1024).toFixed(2)} KB`,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 260,
      fixed: 'right' as const,
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
            type="default"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          <Button
            type="default"
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
            📝 脚本管理
          </div>
          <Space size="middle">
            <Input.Search
              placeholder="搜索脚本名称或描述"
              style={{ width: 280 }}
              onSearch={(value) => {
                setKeyword(value);
                setPage(1);
                loadScripts();
              }}
              allowClear
            />
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={handleBatchExecute}
              loading={batchExecuting}
              disabled={scripts.length === 0}
              style={{
                background: 'linear-gradient(135deg, #52c41a 0%, #237804 100%)',
                border: 'none',
                borderRadius: '6px',
                height: '36px'
              }}
            >
              一键执行全部
            </Button>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setUploadModalVisible(true)}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: '6px',
                height: '36px'
              }}
            >
              上传脚本
            </Button>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleBatchDeleteClick}
              disabled={selectedRowKeys.length === 0}
              style={{ borderRadius: '6px', height: '36px' }}
            >
              批量删除{selectedRowKeys.length > 0 ? ` (${selectedRowKeys.length})` : ''}
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadScripts}
              style={{ borderRadius: '6px', height: '36px' }}
            >
              刷新
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={scripts}
          rowKey="id"
          rowSelection={rowSelection}
          loading={loading}
          scroll={{ x: 1400 }}
          style={{ marginTop: 16 }}
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
        okText="确定"
        cancelText="取消"
      >
        <Form form={uploadForm} layout="vertical" onFinish={handleUpload}>
          <Form.Item label="脚本文件" required>
            <Upload
              fileList={fileList}
              beforeUpload={(file) => {
                const uploadFile: UploadFile = {
                  uid: file.uid || `${Date.now()}`,
                  name: file.name,
                  status: 'done',
                  originFileObj: file,
                };
                setFileList([uploadFile]);
                return false;
              }}
              onRemove={() => setFileList([])}
              maxCount={1}
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
            <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
              支持 .py, .sh, .js 文件及 ZIP 打包批量上传，最大 10MB
            </div>
          </Form.Item>

          <Form.Item name="tags" label="标签">
            <Select mode="tags" placeholder="选择或输入标签" style={{ width: '100%' }}>
              <Select.Option value="GIDS">GIDS</Select.Option>
              <Select.Option value="BGW">BGW</Select.Option>
              <Select.Option value="MediaCache">MediaCache</Select.Option>
              <Select.Option value="E2E">E2E</Select.Option>
            </Select>
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
        okText="确定"
        cancelText="取消"
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
          <Button key="close" onClick={() => setViewModalVisible(false)} type="primary">
            关闭
          </Button>,
        ]}
        width={900}
      >
        <pre
          style={{
            background: '#1e1e1e',
            color: '#d4d4d4',
            padding: 20,
            borderRadius: 8,
            maxHeight: 500,
            overflow: 'auto',
            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
            fontSize: 13,
            lineHeight: 1.6
          }}
        >
          {scriptContent}
        </pre>
      </Modal>

      {/* 批量删除确认模态框 */}
      <Modal
        title="批量删除脚本"
        open={batchDeleteModalVisible}
        onCancel={() => {
          setBatchDeleteModalVisible(false);
          setBatchDeleteConfirmInput('');
        }}
        onOk={handleBatchDelete}
        okText="确认删除"
        cancelText="取消"
        okButtonProps={{ danger: true, disabled: batchDeleteConfirmInput !== 'delete' }}
      >
        <div style={{ marginBottom: 16 }}>
          <p style={{ color: '#ff4d4f', fontWeight: 500 }}>
            警告：即将删除 {selectedRowKeys.length} 个脚本，此操作不可恢复！
          </p>
        </div>
        <div style={{ marginBottom: 16 }}>
          <p>请在下方输入 <strong>delete</strong> 确认删除：</p>
          <Input
            value={batchDeleteConfirmInput}
            onChange={(e) => setBatchDeleteConfirmInput(e.target.value)}
            placeholder="请输入 delete"
          />
        </div>
      </Modal>
    </div>
  );
}
