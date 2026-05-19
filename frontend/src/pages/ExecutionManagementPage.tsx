import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Card,
  message,
  Popconfirm,
  Tabs,
} from 'antd';
import {
  PlayCircleOutlined,
  EyeOutlined,
  FileTextOutlined,
  DeleteOutlined,
  ReloadOutlined,
  RocketOutlined,
  FolderOutlined,
} from '@ant-design/icons';
import { apiService, type ExecutionResponse, type TaskResponse } from '../services/api';

const { TabPane } = Tabs;

export default function ExecutionManagementPage() {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTask, setSelectedTask] = useState<TaskResponse | null>(null);
  const [taskExecutions, setTaskExecutions] = useState<ExecutionResponse[]>([]);
  const [logModalVisible, setLogModalVisible] = useState(false);
  const [currentExecution, setCurrentExecution] = useState<ExecutionResponse | null>(null);
  const [logs, setLogs] = useState<string>('');
  const [activeTab, setActiveTab] = useState<string>('tasks');

  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await apiService.listTasks({ page_size: 100 });
      if (response.code === 0 && response.data) {
        setTasks(response.data.items || []);
      }
    } catch (error) {
      console.error('加载任务列表失败', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleViewResults = async (task: TaskResponse) => {
    setSelectedTask(task);
    setActiveTab('results');
    setLoading(true);
    try {
      const response = await apiService.listTaskExecutions(task.id);
      if (response.code === 0 && response.data) {
        setTaskExecutions(response.data.items || []);
      }
    } catch (error) {
      message.error('加载执行结果失败');
    } finally {
      setLoading(false);
    }
  };

  const handleViewLogs = async (execution: ExecutionResponse) => {
    setCurrentExecution(execution);
    setLogModalVisible(true);
    setLogs('加载中...');

    try {
      const response = await apiService.getExecutionLogs(execution.id);
      if (response.code === 0 && response.data) {
        const logText = response.data.logs
          .map((log) => {
            const time = new Date(log.timestamp).toLocaleTimeString();
            const prefix = log.log_type === 'system' ? '[系统]' : log.log_type === 'stderr' ? '[错误]' : '[输出]';
            return `${time} ${prefix} ${log.content}`;
          })
          .join('\n');
        setLogs(logText || '暂无日志');
      }
    } catch (error: any) {
      setLogs('加载日志失败');
    }
  };

  const handleRestartTask = async (task: TaskResponse) => {
    try {
      await apiService.executeSuite(task.suite_id);
      message.success('任务已重新启动');
      loadTasks();
    } catch (error: any) {
      message.error(error.response?.data?.message || '重新启动失败');
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await apiService.deleteTask(taskId);
      message.success('任务已删除');
      loadTasks();
    } catch (error: any) {
      message.error(error.response?.data?.message || '删除失败');
    }
  };

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      pending: { color: 'default', text: '等待中' },
      running: { color: 'processing', text: '执行中' },
      completed: { color: 'success', text: '已完成' },
      failed: { color: 'error', text: '失败' },
      stopped: { color: 'warning', text: '已停止' },
    };
    const config = statusMap[status] || { color: 'default', text: status };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const taskColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
      align: 'center' as const,
    },
    {
      title: '类型',
      dataIndex: 'task_type',
      key: 'task_type',
      width: 120,
      align: 'center' as const,
      render: (taskType: string, record: TaskResponse) => {
        if (taskType === 'single_script') {
          return (
            <Space>
              <Tag color="blue" icon={<RocketOutlined />}>独立执行</Tag>
            </Space>
          );
        }
        return (
          <Space>
            <Tag color="green" icon={<FolderOutlined />}>套件</Tag>
          </Space>
        );
      },
    },
    {
      title: '名称',
      dataIndex: 'suite_name',
      key: 'suite_name',
      width: 150,
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      align: 'center' as const,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '进度',
      key: 'progress',
      width: 180,
      render: (_: any, record: TaskResponse) => (
        <span>
          <Tag color="success">成功 {record.success_count}</Tag>
          <Tag color="error">失败 {record.failed_count}</Tag>
          <span style={{ marginLeft: 8 }}>共 {record.total_count}</span>
        </span>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 160,
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      width: 160,
      render: (time: string | null) => time ? new Date(time).toLocaleString('zh-CN') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 280,
      fixed: 'right' as const,
      render: (_: any, record: TaskResponse) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleRestartTask(record)}
          >
            启动
          </Button>
          <Button
            type="default"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewResults(record)}
          >
            查看结果
          </Button>
          <Button
            type="default"
            size="small"
            icon={<FileTextOutlined />}
            onClick={() => {
              setSelectedTask(record);
              setActiveTab('detail');
            }}
          >
            详情
          </Button>
          <Popconfirm
            title="确定删除此任务吗？"
            onConfirm={() => handleDeleteTask(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const executionColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
      align: 'center' as const,
    },
    {
      title: '脚本名称',
      dataIndex: 'script_name',
      key: 'script_name',
      width: 180,
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      align: 'center' as const,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '退出码',
      dataIndex: 'exit_code',
      key: 'exit_code',
      width: 80,
      align: 'center' as const,
      render: (code: number | undefined) => (
        code !== undefined ? (
          <Tag color={code === 0 ? 'success' : 'error'}>{code}</Tag>
        ) : '-'
      ),
    },
    {
      title: '执行时长',
      dataIndex: 'duration_seconds',
      key: 'duration_seconds',
      width: 100,
      align: 'right' as const,
      render: (duration: number | null | undefined) =>
        duration != null ? `${duration.toFixed(2)}s` : '-',
    },
    {
      title: '开始时间',
      dataIndex: 'started_at',
      key: 'started_at',
      width: 160,
      render: (time: string | undefined) =>
        time ? new Date(time).toLocaleString('zh-CN') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right' as const,
      render: (_: any, record: ExecutionResponse) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewLogs(record)}
        >
          日志
        </Button>
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
        <div style={{ fontSize: '18px', fontWeight: 600, color: '#262626', marginBottom: 16 }}>
          执行管理
        </div>

        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="任务列表" key="tasks">
            <Button
              icon={<ReloadOutlined />}
              onClick={() => loadTasks()}
              style={{ borderRadius: '6px', height: '36px', marginBottom: 16 }}
            >
              刷新
            </Button>
            <Table
              columns={taskColumns}
              dataSource={tasks}
              rowKey="id"
              loading={loading}
              pagination={{
                pageSize: 20,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 个任务`,
              }}
            />
          </TabPane>

          <TabPane tab="执行结果" key="results">
            {selectedTask ? (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                  <Space size="large">
                    <span>类型: {selectedTask.task_type === 'single_script' ? 
                      <Tag color="blue" icon={<RocketOutlined />}>独立执行</Tag> : 
                      <Tag color="green" icon={<FolderOutlined />}>套件</Tag>}
                    </span>
                    <span>名称: <strong>{selectedTask.suite_name}</strong></span>
                    <span>状态: {getStatusTag(selectedTask.status)}</span>
                    <span>成功: <strong style={{ color: '#52c41a' }}>{selectedTask.success_count}</strong></span>
                    <span>失败: <strong style={{ color: '#ff4d4f' }}>{selectedTask.failed_count}</strong></span>
                    <span>总计: <strong>{selectedTask.total_count}</strong></span>
                  </Space>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={() => handleViewResults(selectedTask)}
                    style={{ borderRadius: '6px', height: '36px' }}
                  >
                    刷新
                  </Button>
                </div>
                <Table
                  columns={executionColumns}
                  dataSource={taskExecutions}
                  rowKey="id"
                  loading={loading}
                  pagination={false}
                  scroll={{ x: 900 }}
                />
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
                请从"任务列表"中选择一个任务，点击"查看结果"
              </div>
            )}
          </TabPane>

          <TabPane tab="任务详情" key="detail">
            {selectedTask ? (
              <div style={{ padding: '16px 0' }}>
                <div style={{ background: '#f5f5f5', padding: 24, borderRadius: 8 }}>
                  <p><strong>类型:</strong> {selectedTask.task_type === 'single_script' ? 
                    <Tag color="blue" icon={<RocketOutlined />}>独立执行</Tag> : 
                    <Tag color="green" icon={<FolderOutlined />}>套件执行</Tag>}
                  </p>
                  <p><strong>名称:</strong> {selectedTask.suite_name}</p>
                  <p><strong>状态:</strong> {getStatusTag(selectedTask.status)}</p>
                  <p><strong>进度:</strong> 成功 {selectedTask.success_count} / 失败 {selectedTask.failed_count} / 总计 {selectedTask.total_count}</p>
                  <p><strong>创建时间:</strong> {new Date(selectedTask.created_at).toLocaleString('zh-CN')}</p>
                  {selectedTask.completed_at && (
                    <p><strong>完成时间:</strong> {new Date(selectedTask.completed_at).toLocaleString('zh-CN')}</p>
                  )}
                </div>
                <div style={{ marginTop: 24, padding: 24, background: '#f0f7ff', borderRadius: 8, border: '1px solid #91caff' }}>
                  <div style={{ color: '#1677ff', fontSize: 14 }}>
                    <FileTextOutlined style={{ marginRight: 8 }} />
                    Trace覆盖率功能（开发中）
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
                请从"任务列表"中选择一个任务，点击"详情"
              </div>
            )}
          </TabPane>
        </Tabs>
      </Card>

      {/* 查看日志 Modal */}
      <Modal
        title={`执行日志：${currentExecution?.script_name} (ID: ${currentExecution?.id})`}
        open={logModalVisible}
        onCancel={() => {
          setLogModalVisible(false);
          setCurrentExecution(null);
          setLogs('');
        }}
        footer={[
          <Button key="close" onClick={() => setLogModalVisible(false)} type="primary">
            关闭
          </Button>,
        ]}
        width={1000}
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
          {logs}
        </pre>
      </Modal>
    </div>
  );
}
