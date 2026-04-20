import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { useState } from 'react';

export function Settings() {
  const [restoreLoading, setRestoreLoading] = useState(false);

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: api.getCategories,
  });

  const handleBackup = async () => {
    const blob = await api.createBackup();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `homeledger_backup_${new Date().toISOString().slice(0, 10)}.db`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleRestore = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setRestoreLoading(true);
    try {
      await api.restoreBackup(file);
      alert('恢复成功');
    } catch {
      alert('恢复失败');
    } finally {
      setRestoreLoading(false);
    }
  };

  return (
    <div className="page settings">
      <h1>设置</h1>

      <section>
        <h2>分类管理</h2>
        <ul className="category-list">
          {categories?.map(c => (
            <li key={c.id}>
              <span>{c.icon}</span> {c.name}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2>数据备份</h2>
        <button onClick={handleBackup}>下载备份</button>
      </section>

      <section>
        <h2>数据恢复</h2>
        <input type="file" accept=".db" onChange={handleRestore} disabled={restoreLoading} />
        {restoreLoading && <span>恢复中...</span>}
      </section>
    </div>
  );
}
