import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { RecordCard } from '../components/RecordCard';
import { useNavigate } from 'react-router-dom';

export function Review() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['records', 'pending'],
    queryFn: () => api.getRecords({ status: 'pending_review', page: 1, page_size: 100 }),
  });

  const update = useMutation({
    mutationFn: ({ id, action, data }: { id: number; action: 'accept' | 'reject'; data?: any }) => {
      if (action === 'accept') {
        return api.updateRecord(id, { ...data, status: 'confirmed' });
      } else {
        return api.deleteRecord(id);
      }
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['records', 'pending'] }),
  });

  return (
    <div className="page review">
      <h1>待审核记录</h1>
      {isLoading ? <div>加载中...</div> : (
        <div className="review-list">
          {data?.items.map(r => (
            <div key={r.id} className="review-item">
              <RecordCard record={r} />
              <div className="review-actions">
                <button onClick={() => update.mutate({ id: r.id, action: 'accept' })}>接受</button>
                <button onClick={() => navigate(`/records/${r.id}`)}>修改</button>
                <button onClick={() => update.mutate({ id: r.id, action: 'reject' })}>拒绝</button>
              </div>
            </div>
          ))}
          {data?.items.length === 0 && <div>暂无待审核记录</div>}
        </div>
      )}
    </div>
  );
}
