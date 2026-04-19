import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import ScriptManagementPage from './pages/ScriptManagementPage';
import ExecutionManagementPage from './pages/ExecutionManagementPage';
import ConfigPage from './pages/ConfigPage';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/scripts" replace />} />
          <Route path="scripts" element={<ScriptManagementPage />} />
          <Route path="executions" element={<ExecutionManagementPage />} />
          <Route path="configs" element={<ConfigPage />} />
          <Route path="reports" element={<div>测试报告（开发中）</div>} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
