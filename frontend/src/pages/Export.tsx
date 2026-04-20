import { useState } from 'react';
import { api } from '../api/client';

export function Export() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      const blob = await api.exportExcel({ start_date: startDate, end_date: endDate });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `expenses_${startDate || 'all'}_${endDate || 'all'}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page export">
      <h1>导出数据</h1>
      <div className="export-form">
        <label>开始日期</label>
        <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
        <label>结束日期</label>
        <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
        <button onClick={handleExport} disabled={loading}>
          {loading ? '导出中...' : '下载Excel'}
        </button>
      </div>
    </div>
  );
}
