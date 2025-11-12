import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class Database:
    def __init__(self, db_path: str = "data/api_tests.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _init_database(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # API Configurations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                api_version TEXT NOT NULL,
                api_url TEXT NOT NULL,
                method TEXT NOT NULL,
                auth_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(task_name, api_version)
            )
        """)
        
        # Test Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id INTEGER NOT NULL,
                test_case_name TEXT NOT NULL,
                request_payload TEXT,
                response_data TEXT,
                status_code INTEGER,
                response_time REAL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (config_id) REFERENCES api_configs (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_api_config(self, task_name: str, api_version: str, api_url: str, 
                       method: str, auth_details: str) -> int:
        """Save API configuration"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO api_configs (task_name, api_version, api_url, method, auth_details)
                VALUES (?, ?, ?, ?, ?)
            """, (task_name, api_version, api_url, method, auth_details))
            
            config_id = cursor.lastrowid
            conn.commit()
            return config_id
        except sqlite3.IntegrityError:
            # If combination exists, update it
            cursor.execute("""
                UPDATE api_configs 
                SET api_url = ?, method = ?, auth_details = ?
                WHERE task_name = ? AND api_version = ?
            """, (api_url, method, auth_details, task_name, api_version))
            conn.commit()
            
            cursor.execute("""
                SELECT id FROM api_configs 
                WHERE task_name = ? AND api_version = ?
            """, (task_name, api_version))
            config_id = cursor.fetchone()[0]
            return config_id
        finally:
            conn.close()
    
    def get_all_configs(self) -> List[Dict]:
        """Get all API configurations"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM api_configs ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_tasks(self) -> List[str]:
        """Get all unique task names"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT task_name FROM api_configs ORDER BY task_name")
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def get_configs_by_task(self, task_name: str) -> List[Dict]:
        """Get all configurations for a specific task"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM api_configs WHERE task_name = ? ORDER BY api_version",
            (task_name,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_config(self, config_id: int):
        """Delete an API configuration"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM api_configs WHERE id = ?", (config_id,))
        conn.commit()
        conn.close()
    
    def save_test_result(self, config_id: int, test_case_name: str, 
                        request_payload: str, response_data: str, 
                        status_code: int, response_time: float):
        """Save test execution result"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO test_results 
            (config_id, test_case_name, request_payload, response_data, status_code, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (config_id, test_case_name, request_payload, response_data, status_code, response_time))
        
        conn.commit()
        conn.close()
    
    def get_test_cases_by_task(self, task_name: str) -> List[str]:
        """Get all unique test case names for a task"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT tr.test_case_name
            FROM test_results tr
            JOIN api_configs ac ON tr.config_id = ac.id
            WHERE ac.task_name = ?
            ORDER BY tr.test_case_name
        """, (task_name,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def get_results_for_comparison(self, task_name: str, test_case_name: str) -> List[Dict]:
        """Get test results for comparison (before and after)"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                tr.*,
                ac.task_name,
                ac.api_version,
                ac.api_url,
                ac.method
            FROM test_results tr
            JOIN api_configs ac ON tr.config_id = ac.id
            WHERE ac.task_name = ? AND tr.test_case_name = ?
            ORDER BY ac.api_version, tr.executed_at DESC
        """, (task_name, test_case_name))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Get the most recent result for each version
        results = {}
        for row in rows:
            version = row['api_version']
            if version not in results:
                results[version] = dict(row)
        
        return list(results.values())
    
    def get_all_test_results(self, limit: int = 50) -> List[Dict]:
        """Get all test results"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                tr.*,
                ac.task_name,
                ac.api_version,
                ac.api_url,
                ac.method
            FROM test_results tr
            JOIN api_configs ac ON tr.config_id = ac.id
            ORDER BY tr.executed_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_test_results_by_task(self, task_name: str, limit: int = 50) -> List[Dict]:
        """Get test results for a specific task"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                tr.*,
                ac.task_name,
                ac.api_version,
                ac.api_url,
                ac.method
            FROM test_results tr
            JOIN api_configs ac ON tr.config_id = ac.id
            WHERE ac.task_name = ?
            ORDER BY tr.executed_at DESC
            LIMIT ?
        """, (task_name, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
