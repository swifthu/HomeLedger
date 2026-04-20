import { useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { ClassifyResult, ImageUnderstandResult, Account } from '../api/client';

interface Props {
  onCreated?: () => void;
}

export function ChatInput({ onCreated }: Props) {
  const [text, setText] = useState('');
  const [merchant, setMerchant] = useState('');
  const [accountId, setAccountId] = useState('');
  const [result, setResult] = useState<ClassifyResult | null>(null);
  const [imageResult, setImageResult] = useState<ImageUnderstandResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: accounts = [] } = useQuery<Account[]>({
    queryKey: ['accounts'],
    queryFn: () => api.getAccounts(),
  });

  const handleClassify = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);
    setImageResult(null);
    try {
      const res = await api.classifyExpense(text.trim());
      setResult(res);
    } catch {
      setError('分类失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleImageSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Preview image
    const reader = new FileReader();
    reader.onload = (ev) => setImagePreview(ev.target?.result as string);
    reader.readAsDataURL(file);

    setLoading(true);
    setError('');
    setResult(null);
    setImageResult(null);

    try {
      const res = await api.understandImage(file);
      setImageResult(res);
    } catch {
      setError('图片分析失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptImage = async () => {
    if (!imageResult) return;
    const description = imageResult.items.map(i => i.name).join(', ') || '图片识别消费';
    const amount = imageResult.total || imageResult.items.reduce((sum, i) => sum + i.amount, 0) || 0;

    try {
      await api.createRecord({
        category: '其他',
        amount,
        description: `${imageResult.store || ''} ${description}`.trim(),
        ai_confidence: 0.9,
        status: 'pending_review',
        source: 'ai',
        user_corrected: false,
        merchant: merchant || imageResult.store || undefined,
        account_id: accountId || undefined,
      });
      setText('');
      setMerchant('');
      setImageResult(null);
      setImagePreview(null);
      onCreated?.();
    } catch {
      setError('创建失败');
    }
  };

  const handleAccept = async () => {
    if (!result) return;
    try {
      await api.createRecord({
        category: result.category,
        amount: result.amount,
        description: text.trim(),
        ai_confidence: result.confidence,
        status: 'confirmed',
        source: 'ai',
        user_corrected: false,
        merchant: merchant || undefined,
        account_id: accountId || undefined,
      });
      setText('');
      setMerchant('');
      setResult(null);
      onCreated?.();
    } catch {
      setError('创建失败');
    }
  };

  const handleModify = async (category: string, amount: number) => {
    try {
      await api.createRecord({
        category,
        amount,
        description: text.trim(),
        ai_confidence: result?.confidence ?? 0,
        status: 'pending_review',
        source: 'ai',
        user_corrected: true,
        merchant: merchant || undefined,
        account_id: accountId || undefined,
      });
      setText('');
      setMerchant('');
      setResult(null);
      setImageResult(null);
      setImagePreview(null);
      onCreated?.();
    } catch {
      setError('创建失败');
    }
  };

  const handleReject = () => {
    setText('');
    setMerchant('');
    setResult(null);
    setImageResult(null);
    setImagePreview(null);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="chat-input">
      {imagePreview && (
        <div className="image-preview">
          <img src={imagePreview} alt="Preview" />
        </div>
      )}
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="输入支出描述，如：早餐包子5元"
        rows={2}
      />
      <input
        value={merchant}
        onChange={e => setMerchant(e.target.value)}
        placeholder="商户（可选），如：瑞幸、美团"
      />
      <select value={accountId} onChange={e => setAccountId(e.target.value)}>
        <option value="">选择账户</option>
        {accounts.map(acc => (
          <option key={acc.id} value={acc.id}>
            {acc.icon || ''} {acc.name}
          </option>
        ))}
      </select>
      <div className="chat-input-toolbar">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageSelect}
          style={{ display: 'none' }}
        />
        <button onClick={() => fileInputRef.current?.click()} title="上传图片">
          📷 图片
        </button>
        {!result && !imageResult && (
          <button onClick={handleClassify} disabled={loading || !text.trim()}>
            {loading ? '分类中...' : '分类'}
          </button>
        )}
      </div>
      {imageResult && (
        <div className="classification-result">
          <span>商店: {imageResult.store || '未知'}</span>
          <span>项目: {imageResult.items.map(i => `${i.name} ¥${i.amount}`).join(', ') || '无'}</span>
          <span>总计: ¥{(imageResult.total || 0).toFixed(2)}</span>
          <div className="chat-input-actions">
            <button onClick={handleAcceptImage}>确认入账</button>
            <button onClick={() => handleModify('其他', imageResult.total || 0)}>修改</button>
            <button onClick={handleReject}>取消</button>
          </div>
        </div>
      )}
      {!result ? (
        <div />
      ) : (
        <div className="classification-result">
          <span>分类: {result.category}</span>
          <span>金额: ¥{result.amount.toFixed(2)}</span>
          <span>置信度: {(result.confidence * 100).toFixed(0)}%</span>
          <div className="chat-input-actions">
            <button onClick={handleAccept}>确认</button>
            <button onClick={() => handleModify(result.category, result.amount)}>修改</button>
            <button onClick={handleReject}>取消</button>
          </div>
        </div>
      )}
      {error && <div className="error">{error}</div>}
    </div>
  );
}
