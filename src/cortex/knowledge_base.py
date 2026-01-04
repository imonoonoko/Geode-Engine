import sqlite3
import json
import os
from datetime import datetime

class KnowledgeBase:
    """
    Long-Term Memory (LTM) Storage using SQLite.
    Stores concepts and edges that are not currently in the active KnowledgeGraph (RAM).
    """
    
    DB_PATH = "memory_data/knowledge.db"

    def __init__(self, db_path=None):
        self.db_path = db_path or self.DB_PATH
        self._init_db()

    def _init_db(self):
        """ Initialize the database schema if it doesn't exist. """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Concepts Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                name TEXT PRIMARY KEY,
                attributes JSON,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP
            )
        ''')
        
        # Edges Table
        # Using a composite index for fast relation lookups
        c.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                source TEXT,
                target TEXT,
                relation TEXT,
                weight REAL,
                created_at TIMESTAMP,
                PRIMARY KEY (source, target, relation)
            )
        ''')
        
        # Index for reverse lookups (target -> source)
        c.execute('CREATE INDEX IF NOT EXISTS idx_edges_target ON edges (target)')
        
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def save_concept(self, name: str, attributes: dict = None):
        """ Save or update a concept in LTM. """
        if attributes is None:
            attributes = {}
            
        now = datetime.now().isoformat()
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('''
                    INSERT INTO concepts (name, attributes, created_at, last_accessed)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        attributes = excluded.attributes,
                        last_accessed = excluded.last_accessed
                ''', (name, json.dumps(attributes), now, now))
        finally:
            conn.close()

    def save_edge(self, source: str, target: str, relation: str, weight: float):
        """ Save or update an edge in LTM. """
        now = datetime.now().isoformat()
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('''
                    INSERT INTO edges (source, target, relation, weight, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(source, target, relation) DO UPDATE SET
                        weight = excluded.weight
                ''', (source, target, relation, weight, now))
        finally:
            conn.close()
            
    def bulk_save_edges(self, edges: list):
        """
        Bulk save edges for performance.
        edges: list of (source, target, relation, weight) tuples
        """
        now = datetime.now().isoformat()
        data = [(s, t, r, w, now) for s, t, r, w in edges]
        
        conn = self.get_connection()
        try:
            with conn:
                conn.executemany('''
                    INSERT INTO edges (source, target, relation, weight, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(source, target, relation) DO UPDATE SET
                        weight = excluded.weight
                ''', data)
        finally:
            conn.close()

    def get_concept(self, name: str) -> dict:
        """ Retrieve a concept's attributes. """
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT attributes FROM concepts WHERE name = ?', (name,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None
        finally:
            conn.close()

    def get_edges(self, source: str) -> list:
        """ Retrieve all edges starting from source. """
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT target, relation, weight FROM edges WHERE source = ?', (source,))
            return cursor.fetchall() # [(target, relation, weight), ...]
        finally:
            conn.close()

    def get_incoming_edges(self, target: str) -> list:
        """ Retrieve all edges pointing to target. """
        conn = self.get_connection()
        try:
            cursor = conn.execute('SELECT source, relation, weight FROM edges WHERE target = ?', (target,))
            return cursor.fetchall()
        finally:
            conn.close()
