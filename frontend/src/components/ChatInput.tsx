import { useState } from 'react';
import { api } from '../api/client';
import type { ClassifyResult } from '../api/client';

interface Props {
  onCreated?: () => void;
}

export function ChatInput({ onCreated }: Props) {
  const [text, setText] = useState('');
  const [result, setResult] = useState<ClassifyResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleClassify = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await api.classifyExpense(text.trim());
      setResult(res);
    } catch {
      setError('分类失败，请重试');
    } finally {
      setLoading(false);
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
      });
      setText('');
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
      });
      setText('');
      setResult(null);
      onCreated?.();
    } catch {
      setError('创建失败');
    }
  };

  const handleReject = () => {
    setText('');
    setResult(null);
    setError('');
  };

  return (
    <div className="chat-input">
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="输入支出描述，如：早餐包子5元"
        rows={2}
      />
      {!result ? (
        <button onClick={handleClassify} disabled={loading || !text.trim()}>
          {loading ? '分类中...' : '分类'}
        </button>
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
