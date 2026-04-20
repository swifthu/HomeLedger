import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ExpenseRecord, Account } from '../api/client';

interface Props {
  record: ExpenseRecord;
  onEdit?: (id: string) => void;
}

const CATEGORY_ICONS: Record<string, string> = {
  餐饮: '🍜', 交通: '🚗', 购物: '🛒', 居住: '🏠',
  医疗: '💊', 娱乐: '🎮', 教育: '📚', 其他: '📌',
};

export function RecordCard({ record, onEdit }: Props) {
  const icon = CATEGORY_ICONS[record.category] ?? '📌';
  const isPending = record.status === 'pending_review';

  const { data: account } = useQuery<Account | undefined>({
    queryKey: ['account', record.account_id],
    queryFn: () => api.getAccounts().then(accs => accs.find(a => a.id === record.account_id)),
    enabled: !!record.account_id,
  });

  return (
    <div className={`record-card ${isPending ? 'pending' : ''}`} onClick={() => onEdit?.(record.id)}>
      <span className="record-icon">{icon}</span>
      <div className="record-info">
        <span className="record-category">{record.category}</span>
        <span className="record-desc">{record.description}</span>
        <span className="record-date">{new Date(record.created_at).toLocaleDateString()}</span>
        {account && <span className="record-account">{account.icon} {account.name}</span>}
      </div>
      <div className="record-amount">
        <span>¥{record.amount.toFixed(2)}</span>
        {isPending && <span className="badge pending">待审核</span>}
      </div>
    </div>
  );
}
