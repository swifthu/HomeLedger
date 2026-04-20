import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ExpenseRecord } from '../api/client';
import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';

export function RecordDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Partial<ExpenseRecord>>({});

  const { data: record, isLoading } = useQuery({
    queryKey: ['record', id],
    queryFn: async () => {
      const res = await api.getRecords({ page: 1, page_size: 1 });
      return res.items.find(r => r.id === Number(id));
    },
    enabled: !!id,
  });

  const update = useMutation({
    mutationFn: (data: Partial<ExpenseRecord>) => api.updateRecord(Number(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['record', id] });
      setEditing(false);
    },
  });

  const handleSave = () => {
    update.mutate({
      ...form,
      ground_truth_category: form.category,
      ground_truth_amount: form.amount,
      user_corrected: true,
    });
  };

  if (isLoading) return <div>加载中...</div>;
  if (!record) return <div>记录不存在</div>;

  return (
    <div className="page record-detail">
      <h1>记录详情</h1>
      <button onClick={() => navigate('/records')}>返回</button>

      {editing ? (
        <div className="edit-form">
          <label>分类</label>
          <input value={form.category ?? record.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))} />
          <label>金额</label>
          <input type="number" value={form.amount ?? record.amount} onChange={e => setForm(f => ({ ...f, amount: Number(e.target.value) }))} />
          <label>描述</label>
          <input value={form.description ?? record.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          <button onClick={handleSave}>保存</button>
          <button onClick={() => setEditing(false)}>取消</button>
        </div>
      ) : (
        <div className="detail-view">
          <p>分类: {record.category}</p>
          <p>金额: ¥{record.amount.toFixed(2)}</p>
          <p>描述: {record.description}</p>
          <p>日期: {new Date(record.created_at).toLocaleString()}</p>
          <p>状态: {record.status === 'pending_review' ? '待审核' : '已确认'}</p>
          <p>来源: {record.source === 'ai' ? 'AI' : record.source === 'rule' ? '规则' : '手动'}</p>
          <p>AI置信度: {(record.ai_confidence * 100).toFixed(1)}%</p>
          <button onClick={() => setEditing(true)}>编辑</button>
        </div>
      )}
    </div>
  );
}
