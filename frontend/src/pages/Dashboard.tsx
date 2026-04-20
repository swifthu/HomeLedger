import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { ChatInput } from '../components/ChatInput';
import { StatCard } from '../components/StatCard';
import { RecordCard } from '../components/RecordCard';
import { ReviewBanner } from '../components/ReviewBanner';
import { useNavigate } from 'react-router-dom';

export function Dashboard() {
  const navigate = useNavigate();
  const now = new Date();
  const monthStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

  const stats = useQuery({
    queryKey: ['stats', monthStr],
    queryFn: () => api.getMonthlyStats(monthStr),
  });

  const recent = useQuery({
    queryKey: ['records', 1, 5],
    queryFn: () => api.getRecords({ page: 1, page_size: 5 }),
  });

  const pendingCount = useQuery({
    queryKey: ['pendingCount'],
    queryFn: async () => {
      const res = await api.getRecords({ status: 'pending_review', page_size: 1 });
      return res.total;
    },
  });

  const accountsSummary = useQuery({
    queryKey: ['accountsSummary'],
    queryFn: api.getAccountsSummary,
  });

  return (
    <div className="page dashboard">
      <ReviewBanner count={pendingCount.data ?? 0} />

      {accountsSummary.data && (
        <div className="account-summary">
          <div className="summary-item">
            <span className="summary-label">总资产</span>
            <span className="summary-value">¥{accountsSummary.data.total_assets.toFixed(2)}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">总负债</span>
            <span className="summary-value negative">¥{Math.abs(accountsSummary.data.total_liabilities).toFixed(2)}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">净资产</span>
            <span className={`summary-value ${accountsSummary.data.net_worth < 0 ? 'negative' : 'positive'}`}>
              ¥{accountsSummary.data.net_worth.toFixed(2)}
            </span>
          </div>
        </div>
      )}

      <div className="stats-grid">
        <StatCard
          label="本月支出"
          value={stats.data ? `¥${stats.data.total_records}` : '-'}
          icon="💰"
        />
        <StatCard
          label="AI准确率"
          value={stats.data ? `${(stats.data.accuracy_rate * 100).toFixed(1)}%` : '-'}
          icon="🎯"
        />
        <StatCard
          label="待审核"
          value={pendingCount.data ?? '-'}
          icon="📋"
        />
      </div>

      <div className="section">
        <h2>快速记账</h2>
        <ChatInput onCreated={() => recent.refetch()} />
      </div>

      <div className="section">
        <h2>最近记录</h2>
        {recent.data?.items.map(r => (
          <RecordCard key={r.id} record={r} onEdit={id => navigate(`/records/${id}`)} />
        ))}
      </div>
    </div>
  );
}
