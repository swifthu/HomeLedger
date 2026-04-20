import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { RecordList } from '../components/RecordList';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function Records() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['records', page, startDate, endDate, category, status],
    queryFn: () => api.getRecords({
      page,
      page_size: 20,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
      category: category || undefined,
      status: status || undefined,
    }),
  });

  return (
    <div className="page records">
      <h1>支出记录</h1>

      <div className="filters">
        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} placeholder="开始日期" />
        <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} placeholder="结束日期" />
        <input type="text" value={category} onChange={e => setCategory(e.target.value)} placeholder="分类" />
        <select value={status} onChange={e => setStatus(e.target.value)}>
          <option value="">全部状态</option>
          <option value="confirmed">已确认</option>
          <option value="pending_review">待审核</option>
        </select>
        <button onClick={() => setPage(1)}>筛选</button>
      </div>

      {isLoading ? <div>加载中...</div> : (
        <RecordList
          records={data?.items ?? []}
          total={data?.total ?? 0}
          page={page}
          pageSize={20}
          onPageChange={p => setPage(p)}
          onEdit={id => navigate(`/records/${id}`)}
        />
      )}
    </div>
  );
}
