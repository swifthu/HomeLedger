import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './pages/Dashboard';
import { Records } from './pages/Records';
import { RecordDetail } from './pages/RecordDetail';
import { Review } from './pages/Review';
import { Export } from './pages/Export';
import { Settings } from './pages/Settings';
import './App.css';

const queryClient = new QueryClient();

function Nav() {
  return (
    <nav>
      <Link to="/">记账</Link>
      <Link to="/records">记录</Link>
      <Link to="/review">审核</Link>
      <Link to="/export">导出</Link>
      <Link to="/settings">设置</Link>
    </nav>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Nav />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/records" element={<Records />} />
          <Route path="/records/:id" element={<RecordDetail />} />
          <Route path="/review" element={<Review />} />
          <Route path="/export" element={<Export />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
