import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import Config

logger = logging.getLogger("sitepulse.db")

def get_db_connection() -> sqlite3.Connection:
    """
    Creates and returns a SQLite database connection with row factory
    and foreign key constraints enabled.
    """
    db_path = Config.DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    # Ensure foreign key support is enabled in SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db() -> None:
    """
    Initializes the database schema if tables do not already exist.
    """
    schema_file = Path(__file__).resolve().parent / "schema.sql"
    if not schema_file.exists():
        logger.error(f"Schema file not found at {schema_file}")
        return
        
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with get_db_connection() as conn:
        conn.executescript(schema_sql)
        conn.commit()
    logger.info("Database initialized successfully.")

def save_analysis(data: Dict[str, Any]) -> int:
    """
    Saves an analysis record and its corresponding issues in a single transaction.
    Returns the newly created analysis ID.
    Uses strictly parameterized queries.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Insert analysis header
        insert_analysis_sql = """
            INSERT INTO analyses (
                url, domain, created_at, overall_score,
                performance_score, seo_score, accessibility_score,
                best_practices_score, is_demo, metrics_json, raw_summary_json
            ) VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        
        metrics_json = json.dumps(data.get("metrics", {}))
        raw_summary_json = json.dumps(data.get("summary", {}))
        is_demo_val = 1 if data.get("is_demo", False) else 0
        
        cursor.execute(insert_analysis_sql, (
            data.get("url", ""),
            data.get("domain", ""),
            data.get("overall_score", 0),
            data.get("performance_score", 0),
            data.get("seo_score", 0),
            data.get("accessibility_score", 0),
            data.get("best_practices_score", 0),
            is_demo_val,
            metrics_json,
            raw_summary_json
        ))
        
        analysis_id = cursor.lastrowid
        
        # 2. Insert detected issues
        issues = data.get("issues", [])
        if issues and analysis_id is not None:
            insert_issue_sql = """
                INSERT INTO issues (
                    analysis_id, category, title, description,
                    severity, impact, status, recommendation, benefit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            issue_params = [
                (
                    analysis_id,
                    issue.get("category", "General"),
                    issue.get("title", ""),
                    issue.get("description", ""),
                    issue.get("severity", "Medium"),
                    issue.get("impact", "Medium"),
                    issue.get("status", "Warning"),
                    issue.get("recommendation", ""),
                    issue.get("benefit", "")
                )
                for issue in issues
            ]
            cursor.executemany(insert_issue_sql, issue_params)
            
        conn.commit()
        return analysis_id

def get_all_analyses(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetches past analyses ordered by creation date descending.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id, url, domain, created_at, overall_score,
                   performance_score, seo_score, accessibility_score,
                   best_practices_score, is_demo
            FROM analyses
            ORDER BY datetime(created_at) DESC
            LIMIT ?;
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a complete analysis record and all attached issues by ID.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Fetch analysis
        cursor.execute("SELECT * FROM analyses WHERE id = ?;", (analysis_id,))
        analysis_row = cursor.fetchone()
        if not analysis_row:
            return None
            
        result = dict(analysis_row)
        
        # Parse JSON columns safely
        try:
            result["metrics"] = json.loads(result.get("metrics_json", "{}"))
        except Exception:
            result["metrics"] = {}
            
        try:
            result["summary"] = json.loads(result.get("raw_summary_json", "{}"))
        except Exception:
            result["summary"] = {}
            
        # Fetch issues
        cursor.execute("""
            SELECT id, category, title, description, severity, impact, status, recommendation, benefit
            FROM issues
            WHERE analysis_id = ?
            ORDER BY 
                CASE severity 
                    WHEN 'Critical' THEN 1 
                    WHEN 'High' THEN 2 
                    WHEN 'Medium' THEN 3 
                    WHEN 'Low' THEN 4 
                    ELSE 5 
                END;
        """, (analysis_id,))
        issue_rows = cursor.fetchall()
        result["issues"] = [dict(r) for r in issue_rows]
        
        return result

def delete_analysis(analysis_id: int) -> bool:
    """
    Deletes a specific analysis and cascades to its issues.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?;", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0

def clear_all_analyses() -> int:
    """
    Clears all saved analyses and issues.
    Returns the number of deleted records.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses;")
        count = cursor.rowcount
        conn.commit()
        return count
