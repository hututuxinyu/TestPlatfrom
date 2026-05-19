import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Upload,
  message,
  Popconfirm,
  Card,
  Row,
  Col,
} from 'antd';
import type { TableRowSelection } from 'antd/es/table/interface';
import {
  UploadOutlined,
  DeleteOutlined,
  EyeOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import type { UploadFile } from 'antd';
import { apiService, type ScriptResponse, type SuiteSummary, type SuiteDetailResponse } from '../services/api';

export default function ScriptManagementPage() {
  const params = useParams();
  const navigate = useNavigate();
  const suiteId = params.suiteId ? parseInt(params.suiteId) : null;

  // Suite grid view state
  const [suites, setSuites] = useState<SuiteSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [uploadForm] = Form.useForm();

  // Suite detail view state
  const [suiteDetail, setSuiteDetail] = useState<SuiteDetailResponse | null>(null);
  const [scripts, setScripts] = useState<ScriptResponse[]>([]);
  const [scriptLoading, setScriptLoading] = useState(false);
  const [uploadScriptModalVisible, setUploadScriptModalVisible] = useState(false);
  const [viewModalVisible, setViewModalVisible] = useState(false);
  const [currentScript, setCurrentScript] = useState<ScriptResponse | null>(null);
  const [scriptContent, setScriptContent] = useState('');
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [scriptUploadForm] = Form.useForm();
  const [batchExecuting, setBatchExecuting] = useState(false);
  const [selectedScriptKeys, setSelectedScriptKeys] = useState<React.Key[]>([]);

  // Load suites (grid view)
  const loadSuites = async () => {
    setLoading(true);
    try {
      const response = await apiService.listSuites();
      if (response.code === 0 && response.data) {
        setSuites(response.data.items || []);
      }
    } catch (error: any) {
      message.error('加载测试套列表失败');
    } finally {
      setLoading(false);
    }
  };

  // Load suite detail and scripts
  const loadSuiteDetail = async () => {
    if (!suiteId) return;
    setScriptLoading(true);
    try {
      const [detailResponse, scriptsResponse] = await Promise.all([
        apiService.getSuite(suiteId),
        apiService.listSuiteScripts(suiteId),
      ]);
      if (detailResponse.code === 0 && detailResponse.data) {
        setSuiteDetail(detailResponse.data);
      }
      if (scriptsResponse.code === 0 && scriptsResponse.data) {
        setScripts(scriptsResponse.data.items || []);
      }
    } catch (error: any) {
      message.error('加载测试套详情失败');
    } finally {
      setScriptLoading(false);
    }
  };

  useEffect(() => {
    if (suiteId) {
      loadSuiteDetail();
    } else {
      loadSuites();
    }
  }, [suiteId]);

  // Suite grid view handlers
  const handleUploadSuite = async (values: { name: string }) => {
    if (fileList.length === 0) {
      message.error('请选择文件');
      return;
    }

    const file = fileList[0].originFileObj;
    if (!file) {
      message.error('文件对象无效，请重新选择文件');
      return;
    }

    try {
      await apiService.createSuite(values.name, file);
      message.success('上传成功');
      setUploadModalVisible(false);
      uploadForm.resetFields();
      setFileList([]);
      loadSuites();
    } catch (error: any) {
      message.error(error.response?.data?.message || '上传失败');
    }
  };

  const handleDeleteSuite = async (suite: SuiteSummary) => {
    try {
      await apiService.deleteSuite(suite.id);
      message.success('删除成功');
      loadSuites();
    } catch (error: any) {
      message.error(error.response?.data?.message || '删除失败');
    }
  };

  const handleExportSuite = async (suite: SuiteSummary) => {
    try {
      const blob = await apiService.exportSuite(suite.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${suite.name}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch (error: any) {
      message.error('导出失败');
    }
  };

  const handlePreviewSuite = (suite: SuiteSummary) => {
    navigate(`/scripts/${suite.id}`);
  };

  // Suite detail view handlers
  const handleUploadScript = async () => {
    if (fileList.length === 0) {
      message.error('请选择文件');
      return;
    }

    const file = fileList[0].originFileObj;
    if (!file) {
      message.error('文件对象无效');
      return;
    }

    try {
      await apiService.uploadScriptToSuite(suiteId!, file);
      message.success('上传成功');
      setUploadScriptModalVisible(false);
      setFileList([]);
      loadSuiteDetail();
    } catch (error: any) {
      message.error(error.response?.data?.message || '上传失败');
    }
  };

  const handleExecuteScript = async (scriptId: number) => {
    try {
      await apiService.createExecution(scriptId);
      message.success('执行任务已创建，请到执行管理页面查看');
      setTimeout(() => {
        navigate('/executions');
      }, 1500);
    } catch (error: any) {
      message.error(error.response?.data?.message || '创建执行任务失败');
    }
  };

  const handleBatchExecute = async () => {
    if (scripts.length === 0) {
      message.warning('没有可执行的脚本');
      return;
    }
    setBatchExecuting(true);
    try {
      const response = await apiService.executeSuite(suiteId!);
      if (response.code === 0 && response.data) {
        const { total, succeeded, failed } = response.data;
        message.success(`执行完成: 成功 ${succeeded}/${total}`);
        if (failed > 0) {
          message.warning(`${failed} 个脚本执行失败`);
        }
        setTimeout(() => {
          navigate('/executions');
        }, 1500);
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || '执行失败');
    } finally {
      setBatchExecuting(false);
    }
  };

  const handleDeleteScript = async (scriptId: number) => {
    try {
      await apiService.deleteScript(scriptId);
      message.success('删除成功');
      loadSuiteDetail();
    } catch (error: any) {
      message.error(error.response?.data?.message || '删除失败');
    }
  };

  const handleBatchDelete = async () => {
    if (selectedScriptKeys.length === 0) {
      message.warning('请先勾选要删除的脚本');
      return;
    }
    try {
      const ids = selectedScriptKeys.map((k) => Number(k));
      await apiService.batchDeleteScripts(ids);
      message.success(`成功删除 ${ids.length} 个脚本`);
      setSelectedScriptKeys([]);
      loadSuiteDetail();
    } catch (error: any) {
      message.error(error.response?.data?.message || '批量删除失败');
    }
  };

  const handleViewScript = async (script: ScriptResponse) => {
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

  const handleBackToSuites = () => {
    navigate('/scripts');
  };

  // Script table columns (for suite detail view)
  const scriptColumns = [
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
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: ScriptResponse) => (
        <Space size="small">
          <Button
            type="primary"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleExecuteScript(record.id)}
          >
            执行
          </Button>
          <Button
            type="default"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewScript(record)}
          >
            查看
          </Button>
          <Popconfirm
            title="确定删除此脚本吗？"
            onConfirm={() => handleDeleteScript(record.id)}
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

  // Render Suite Grid View
  if (!suiteId) {
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
          }}>
            <div style={{ fontSize: '18px', fontWeight: 600, color: '#262626' }}>
              脚本管理
            </div>
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
              上传测试套 ZIP
            </Button>
          </div>

          <Row gutter={[16, 16]}>
            {suites.map((suite) => (
              <Col span={6} key={suite.id}>
                <div
                  style={{
                    background: 'linear-gradient(145deg, #f8f9fa 0%, #ececec 100%)',
                    borderRadius: '12px',
                    padding: '20px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    border: '1px solid #e8e8e8',
                    height: '100%',
                    minHeight: '160px',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                  onClick={() => handlePreviewSuite(suite)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.boxShadow = '0 6px 20px rgba(0,0,0,0.08)';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.04)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '16px',
                      fontWeight: 600,
                      color: '#262626',
                      marginBottom: '10px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}>
                      {suite.name}
                    </div>

                    <div style={{
                      display: 'flex',
                      gap: '10px',
                      marginBottom: '10px',
                    }}>
                      <div style={{
                        background: '#e6f4ff',
                        padding: '4px 10px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        color: '#1677ff',
                        fontWeight: 500,
                      }}>
                        {suite.script_count} 个脚本
                      </div>
                      <div style={{
                        background: '#f6ffed',
                        padding: '4px 10px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        color: '#52c41a',
                        fontWeight: 500,
                      }}>
                        {suite.total_lines} 行
                      </div>
                    </div>

                    <div style={{
                      color: '#999',
                      fontSize: '12px',
                    }}>
                      上传于 {suite.latest_upload ? new Date(suite.latest_upload).toLocaleDateString('zh-CN') : '-'}
                    </div>
                  </div>

                  <div style={{
                    display: 'flex',
                    justifyContent: 'flex-end',
                    gap: '8px',
                    borderTop: '1px solid #e0e0e0',
                    paddingTop: '12px',
                    marginTop: '12px',
                  }}>
                    <Button
                      size="small"
                      onClick={(e) => { e.stopPropagation(); handlePreviewSuite(suite); }}
                      style={{ fontSize: '12px', height: '26px', background: '#e6f4ff', color: '#1677ff', border: '1px solid #91caff' }}
                    >
                      预览
                    </Button>
                    <Button
                      size="small"
                      type="primary"
                      onClick={(e) => { e.stopPropagation(); handleExportSuite(suite); }}
                      style={{ fontSize: '12px', height: '26px' }}
                    >
                      导出
                    </Button>
                    <Popconfirm
                      title="确定删除此测试套吗？"
                      description="删除前会先删除套内所有脚本"
                      onConfirm={(e) => { e?.stopPropagation(); handleDeleteSuite(suite); }}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        size="small"
                        onClick={(e) => e.stopPropagation()}
                        style={{ fontSize: '12px', height: '26px', background: '#fff1f0', color: '#ff4d4f', border: '1px solid #ffccc7' }}
                      >
                        删除
                      </Button>
                    </Popconfirm>
                  </div>
                </div>
              </Col>
            ))}
          </Row>

          {suites.length === 0 && !loading && (
            <div style={{ textAlign: 'center', padding: '60px 0', color: '#999' }}>
              暂无测试套，点击右上角上传
            </div>
          )}
        </Card>

        {/* Upload Suite Modal */}
        <Modal
          title="上传测试套"
          open={uploadModalVisible}
          onCancel={() => {
            setUploadModalVisible(false);
            uploadForm.resetFields();
            setFileList([]);
          }}
          onOk={() => uploadForm.submit()}
          width={600}
          okText="确认上传"
          cancelText="取消"
        >
          <Form form={uploadForm} layout="vertical" onFinish={handleUploadSuite}>
            <Form.Item
              name="name"
              label="测试套名称"
              rules={[{ required: true, message: '请输入测试套名称' }]}
            >
              <Input placeholder="输入测试套名称" />
            </Form.Item>

            <Form.Item label="选择文件 (ZIP)" required>
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
                accept=".zip"
              >
                <Button icon={<UploadOutlined />}>选择 ZIP 文件</Button>
              </Upload>
              <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
                支持 .zip 打包的测试脚本文件
              </div>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    );
  }

  // Render Suite Detail View
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
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button
              type="default"
              icon={<ArrowLeftOutlined />}
              onClick={handleBackToSuites}
              style={{ borderRadius: '6px' }}
            >
              返回
            </Button>
            <div style={{ fontSize: '18px', fontWeight: 600, color: '#262626' }}>
              {suiteDetail?.suite?.name || '测试套'}
            </div>
          </div>
          <Space size="middle">
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={() => setUploadScriptModalVisible(true)}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: '6px',
                height: '36px'
              }}
            >
              上传脚本
            </Button>
            <Popconfirm
              title={`确定删除所选的 ${selectedScriptKeys.length} 个脚本吗？`}
              onConfirm={handleBatchDelete}
              okText="确定"
              cancelText="取消"
              disabled={selectedScriptKeys.length === 0}
            >
              <Button
                danger
                disabled={selectedScriptKeys.length === 0}
                style={{ borderRadius: '6px', height: '36px' }}
              >
                批量删除 ({selectedScriptKeys.length})
              </Button>
            </Popconfirm>
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
              icon={<ReloadOutlined />}
              onClick={loadSuiteDetail}
              style={{ borderRadius: '6px', height: '36px' }}
            >
              刷新
            </Button>
          </Space>
        </div>

        <Table
          columns={scriptColumns}
          dataSource={scripts}
          rowKey="id"
          loading={scriptLoading}
          rowSelection={{
            selectedRowKeys: selectedScriptKeys,
            onChange: (keys) => setSelectedScriptKeys(keys),
          } as TableRowSelection<ScriptResponse>}
          scroll={{ x: 1000 }}
          style={{ marginTop: 16 }}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      {/* Upload Script Modal */}
      <Modal
        title="上传脚本"
        open={uploadScriptModalVisible}
        onCancel={() => {
          setUploadScriptModalVisible(false);
          setFileList([]);
        }}
        onOk={() => scriptUploadForm.submit()}
        width={600}
        okText="确认上传"
        cancelText="取消"
      >
        <Form form={scriptUploadForm} layout="vertical" onFinish={handleUploadScript}>
          <Form.Item label="选择脚本文件" required>
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
              accept=".py,.sh,.js"
            >
              <Button icon={<UploadOutlined />}>选择脚本文件</Button>
            </Upload>
            <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
              支持 .py, .sh, .js 文件
            </div>
          </Form.Item>
        </Form>
      </Modal>

      {/* View Script Modal */}
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
    </div>
  );
}
