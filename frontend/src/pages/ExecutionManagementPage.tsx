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
  Select,
} from 'antd';
import {
  PlayCircleOutlined,
  StopOutlined,
  EyeOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { apiService, ExecutionResponse, ScriptResponse } from '../services/api';

export default function ExecutionManagementPage() {
  const [executions, setExecutions] = useState<ExecutionResponse[]>([]);
  const [scripts, setScripts] = useState<ScriptResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [scriptFilter, setScriptFilter] = useState<number | undefined>();
  const [logModalVisible, setLogModalVisible] = useState(false);
  const [currentExecution, setCurrentExecution] = useState<ExecutionResponse | null>(null);
  const [logs, setLogs] = useState<string>('');

  const loadExecutions = async () => {
    setLoading(true);
    try {
      const response = await apiService.listExecutions({
        page,
        page_size: pageSize,
        status: statusFilter,
        script_id: scriptFilter,
      });
      if (response.code === 0 && response.data) {
        setExecutions(response.data.items);
        setTotal(response.data.total);
      }
    } catch (error: any) {
      message.error('加载执行列表失败');
    } finally {
      setLoading(false);
    }
  };

  const loadScripts = async () => {
    try {
      const response = await apiService.listScripts({ page: 1, page_size: 100 });
      if (response.code === 0 && response.data) {
        setScripts(response.data.items);
      }
    } catch (error) {
      console.error('加载脚本列表失败', error);
    }
  };

  useEffect(() => {
    loadScripts();
  }, []);

  useEffect(() => {
    loadExecutions();
    const interval = setInterval(loadExecutions, 3000); // 每3秒刷新一次
    return () => clearInterval(interval);
  }, [page, pageSize, statusFilter, scriptFilter]);

  const handleExecute = async (scriptId: number) => {
    try {
      await apiService.createExecution(scriptId);
      message.success('执行任务已创建');
      loadExecutions();
    } catch (error: any) {
      message.error(error.response?.data?.message || '创建执行任务失败');
    }
  };

  const handleStop = async (executionId: number) => {
    try {
      await apiService.stopExecution(executionId);
      message.success('执行已停止');
      loadExecutions();
    } catch (error: any) {
      message.error(error.response?.data?.message || '停止执行失败');
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

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '脚本名称',
      dataIndex: 'script_name',
      key: 'script_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '退出码',
      dataIndex: 'exit_code',
      key: 'exit_code',
      width: 100,
      render: (code: number | undefined) => (code !== undefined ? code : '-'),
    },
    {
      title: '执行时长',
      dataIndex: 'duration_seconds',
      key: 'duration_seconds',
      width: 120,
      render: (duration: number | undefined) =>
        duration !== undefined ? `${duration.toFixed(2)}s` : '-',
    },
    {
      title: '开始时间',
      dataIndex: 'started_at',
      key: 'started_at',
      width: 180,
      render: (time: string | undefined) =>
        time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      width: 180,
      render: (time: string | undefined) =>
        time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: ExecutionResponse) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewLogs(record)}
          >
            日志
          </Button>
          {record.status === 'running' && (
            <Popconfirm
              title="确定停止此执行吗？"
              onConfirm={() => handleStop(record.id)}
              okText="确定"
              cancelText="取消"
            >
              <Button type="link" size="small" danger icon={<StopOutlined />}>
                停止
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <Space style={{ marginBottom: 16 }} wrap>
          <Select
            placeholder="选择脚本"
            style={{ width: 200 }}
            allowClear
            onChange={(value) => {
              setScriptFilter(value);
              setPage(1);
            }}
          >
            {scripts.map((script) => (
              <Select.Option key={script.id} value={script.id}>
                {script.name}
              </Select.Option>
            ))}
          </Select>

          <Select
            placeholder="选择状态"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => {
              setStatusFilter(value);
              setPage(1);
            }}
          >
            <Select.Option value="pending">等待中</Select.Option>
            <Select.Option value="running">执行中</Select.Option>
            <Select.Option value="completed">已完成</Select.Option>
            <Select.Option value="failed">失败</Select.Option>
            <Select.Option value="stopped">已停止</Select.Option>
          </Select>

          <Select
            placeholder="快速执行脚本"
            style={{ width: 200 }}
            onChange={(value) => handleExecute(value)}
            value={undefined}
          >
            {scripts.map((script) => (
              <Select.Option key={script.id} value={script.id}>
                <PlayCircleOutlined /> {script.name}
              </Select.Option>
            ))}
          </Select>

          <Button icon={<ReloadOutlined />} onClick={loadExecutions}>
            刷新
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={executions}
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

      {/* 查看日志模态框 */}
      <Modal
        title={`执行日志：${currentExecution?.script_name} (ID: ${currentExecution?.id})`}
        open={logModalVisible}
        onCancel={() => {
          setLogModalVisible(false);
          setCurrentExecution(null);
          setLogs('');
        }}
        footer={[
          <Button key="close" onClick={() => setLogModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={900}
      >
        <pre
          style={{
            background: '#1e1e1e',
            color: '#d4d4d4',
            padding: 16,
            borderRadius: 4,
            maxHeight: 500,
            overflow: 'auto',
            fontFamily: 'Consolas, Monaco, monospace',
            fontSize: 13,
          }}
        >
          {logs}
        </pre>
      </Modal>
    </div>
  );
}
