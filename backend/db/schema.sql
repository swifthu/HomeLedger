-- HomeLedger Database Schema

CREATE TABLE IF NOT EXISTS records (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    ai_confidence REAL,
    status TEXT DEFAULT 'confirmed',
    source TEXT DEFAULT 'ai',
    ground_truth_category TEXT,
    ground_truth_amount REAL,
    user_corrected INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE,
    icon TEXT,
    color TEXT
);

CREATE TABLE IF NOT EXISTS monthly_stats (
    id TEXT PRIMARY KEY,
    month TEXT UNIQUE,
    total_records INTEGER,
    ai_records INTEGER,
    rule_records INTEGER,
    manual_records INTEGER,
    accuracy_rate REAL,
    zero_miss_rate REAL,
    computed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_records_created_at ON records(created_at);
CREATE INDEX IF NOT EXISTS idx_records_status ON records(status);

-- Seed categories
INSERT OR IGNORE INTO categories (id, name, icon, color) VALUES
    ('cat_food', '餐饮', '🍜', '#FF6B6B'),
    ('cat_transport', '交通', '🚗', '#4ECDC4'),
    ('cat_shopping', '购物', '🛒', '#45B7D1'),
    ('cat_housing', '居住', '🏠', '#96CEB4'),
    ('cat_medical', '医疗', '💊', '#FF8C94'),
    ('cat_entertainment', '娱乐', '🎮', '#DDA0DD'),
    ('cat_education', '教育', '📚', '#98D8C8'),
    ('cat_other', '其他', '📦', '#C0C0C0');
