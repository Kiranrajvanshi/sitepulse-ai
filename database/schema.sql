-- SitePulse AI Database Schema
-- Supports SQLite & can be easily ported to PostgreSQL

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    domain TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_score INTEGER NOT NULL,
    performance_score INTEGER NOT NULL,
    seo_score INTEGER NOT NULL,
    accessibility_score INTEGER NOT NULL,
    best_practices_score INTEGER NOT NULL,
    is_demo BOOLEAN DEFAULT 0,
    metrics_json TEXT NOT NULL,
    raw_summary_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    category TEXT NOT NULL,  -- 'Performance', 'SEO', 'Accessibility', 'Best Practices'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,  -- 'Critical', 'High', 'Medium', 'Low'
    impact TEXT NOT NULL,    -- 'High', 'Medium', 'Low'
    status TEXT NOT NULL,    -- 'Passed', 'Warning', 'Failed'
    recommendation TEXT,
    benefit TEXT,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

-- Index for efficient querying by date and domain
CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_issues_analysis ON issues(analysis_id);
