import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import type { Account } from '../api/client';

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
  cash: '现金',
  virtual: '虚拟账户',
  liability: '负债',
  investment: '投资',
  prepaid: '预付',
};

const ACCOUNT_TYPE_ICONS: Record<string, string> = {
  cash: '💰',
  virtual: '👛',
  liability: '💳',
  investment: '📈',
  prepaid: '🎫',
};

interface AccountFormProps {
  account?: Account;
  onClose: () => void;
}

export function AccountForm({ account, onClose }: AccountFormProps) {
  const queryClient = useQueryClient();
  const isEdit = !!account;

  const [name, setName] = useState(account?.name ?? '');
  const [type, setType] = useState<Account['type']>(account?.type ?? 'cash');
  const [balance, setBalance] = useState(account?.balance?.toString() ?? '0');
  const [color, setColor] = useState(account?.color ?? '#4A90E2');
  const [icon, setIcon] = useState(account?.icon ?? '💰');

  useEffect(() => {
    if (!isEdit) {
      setIcon(ACCOUNT_TYPE_ICONS[type]);
    }
  }, [type, isEdit]);

  const createMutation = useMutation({
    mutationFn: (data: Partial<Account>) => api.createAccount(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['accountsSummary'] });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<Account>) => api.updateAccount(account!.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['accountsSummary'] });
      onClose();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.deleteAccount(account!.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['accountsSummary'] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = { name, type, balance: parseFloat(balance) || 0, color, icon };
    if (isEdit) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDelete = () => {
    if (confirm(`确认删除账户"${account!.name}"？`)) {
      deleteMutation.mutate();
    }
  };

  const isPending = createMutation.isPending || updateMutation.isPending || deleteMutation.isPending;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>{isEdit ? '编辑账户' : '创建账户'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>账户名称</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="如：招商银行信用卡"
              required
            />
          </div>

          <div className="form-group">
            <label>账户类型</label>
            <select value={type} onChange={e => setType(e.target.value as Account['type'])}>
              {Object.entries(ACCOUNT_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {ACCOUNT_TYPE_ICONS[value]} {label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>当前余额</label>
            <input
              type="number"
              value={balance}
              onChange={e => setBalance(e.target.value)}
              step="0.01"
            />
          </div>

          <div className="form-group">
            <label>图标</label>
            <input
              type="text"
              value={icon}
              onChange={e => setIcon(e.target.value)}
              placeholder="表情符号"
              maxLength={2}
            />
          </div>

          <div className="form-group">
            <label>颜色</label>
            <input
              type="color"
              value={color}
              onChange={e => setColor(e.target.value)}
            />
          </div>

          <div className="form-actions">
            {isEdit && (
              <button type="button" className="btn-danger" onClick={handleDelete} disabled={isPending}>
                删除
              </button>
            )}
            <button type="button" onClick={onClose} disabled={isPending}>取消</button>
            <button type="submit" disabled={isPending || !name.trim()}>
              {isPending ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
