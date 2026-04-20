import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8022',
  timeout: 30000,
});

export interface ExpenseRecord {
  id: number;
  created_at: string;
  updated_at: string;
  category: string;
  amount: number;
  description: string;
  ai_confidence: number;
  status: 'confirmed' | 'pending_review';
  source: 'ai' | 'rule' | 'manual';
  ground_truth_category?: string;
  ground_truth_amount?: number;
  user_corrected: boolean;
}

export interface Category {
  id: number;
  name: string;
  icon: string;
  color: string;
}

export interface MonthlyStats {
  month: string;
  total_records: number;
  ai_records: number;
  rule_records: number;
  manual_records: number;
  accuracy_rate: number;
  zero_miss_rate: number;
  computed_at: string;
}

export interface ClassifyResult {
  category: string;
  amount: number;
  confidence: number;
}

export interface PageResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export const api = {
  getRecords: (params?: { page?: number; page_size?: number; start_date?: string; end_date?: string; category?: string; status?: string }) =>
    client.get<PageResult<ExpenseRecord>>('/api/records', { params }).then(r => r.data),

  createRecord: (data: Partial<ExpenseRecord>) =>
    client.post<ExpenseRecord>('/api/records', data).then(r => r.data),

  updateRecord: (id: number, data: Partial<ExpenseRecord>) =>
    client.put<ExpenseRecord>(`/api/records/${id}`, data).then(r => r.data),

  deleteRecord: (id: number) =>
    client.delete(`/api/records/${id}`).then(r => r.data),

  classifyExpense: (description: string) =>
    client.post<ClassifyResult>('/api/ai/classify', { description }).then(r => r.data),

  getMonthlyStats: (month?: string) =>
    client.get<MonthlyStats[]>('/api/stats/monthly', { params: { month } }).then(r => r.data[0]),

  getCategories: () =>
    client.get<Category[]>('/api/categories').then(r => r.data),

  exportExcel: (params?: { start_date?: string; end_date?: string }) =>
    client.get('/api/export/excel', { params, responseType: 'blob' }).then(r => r.data),

  createBackup: () =>
    client.get('/api/backup', { responseType: 'blob' }).then(r => r.data),

  restoreBackup: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return client.post('/api/backup/restore', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data);
  },
};
