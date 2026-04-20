import type { ExpenseRecord } from '../api/client';
import { RecordCard } from './RecordCard';

interface Props {
  records: ExpenseRecord[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onEdit?: (id: number) => void;
}

export function RecordList({ records, total, page, pageSize, onPageChange, onEdit }: Props) {
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="record-list">
      {records.map(r => (
        <RecordCard key={r.id} record={r} onEdit={onEdit} />
      ))}
      {totalPages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => onPageChange(page - 1)}>上一页</button>
          <span>{page} / {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>下一页</button>
        </div>
      )}
    </div>
  );
}
