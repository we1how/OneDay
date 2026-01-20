import sqlite3
import json
from datetime import datetime
import hashlib

# 数据库文件路径
DB_FILE = "time_manage.db"

class StorageEngine:
    """SQLite存储引擎"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表结构"""
        # 1. 行为记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS core_behavior (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                mood INTEGER DEFAULT 3,
                start_ts INTEGER NOT NULL,
                end_ts INTEGER NOT NULL,
                base_score REAL,
                dynamic_coeff REAL,
                final_score REAL,
                energy_consume REAL,
                create_ts INTEGER DEFAULT (strftime('%s', 'now')),
                md5_check TEXT
            )
        ''')
        
        # 2. 用户状态表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                id INTEGER PRIMARY KEY DEFAULT 1,
                current_energy REAL DEFAULT 100,
                combo_count INTEGER DEFAULT 0,
                today_total_score REAL DEFAULT 0,
                today_behavior_count INTEGER DEFAULT 0,
                last_record_ts INTEGER,
                efficient_periods TEXT
            )
        ''')
        
        # 3. 配置表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        ''')
        
        # 4. 行为定义表（用于存储用户添加的行为）
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_def (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                level TEXT NOT NULL,
                category TEXT DEFAULT '未分类',
                base_score_per_min REAL NOT NULL,
                energy_cost_per_min REAL NOT NULL,
                create_ts INTEGER DEFAULT (strftime('%s', 'now'))
            )
        ''')
        
        # 5. 成就表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                unlock_ts INTEGER,
                count INTEGER DEFAULT 1
            )
        ''')
        
        # 创建索引
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_behavior_ts ON core_behavior(start_ts)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_behavior_level ON core_behavior(level)')
        
        # 开启WAL模式
        self.cursor.execute('PRAGMA journal_mode=WAL')
        
        self.conn.commit()
    
    def _level_to_int(self, level):
        """将等级字符串转换为整数（S=5/A=4/B=3/C=2/D=1）"""
        level_map = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 1}
        return level_map.get(level.upper(), 3)  # 默认B级
    
    def _int_to_level(self, level_int):
        """将整数转换为等级字符串"""
        level_map = {5: 'S', 4: 'A', 3: 'B', 2: 'C', 1: 'D'}
        return level_map.get(level_int, 'B')
    
    def _generate_md5(self, level, duration, final_score):
        """生成MD5校验码"""
        str_to_check = f"{level}_{duration}_{final_score}"
        return hashlib.md5(str_to_check.encode()).hexdigest()
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        return int(datetime.now().timestamp())
    
    # ----------------- 行为定义相关 -----------------
    def add_behavior(self, name, level, category, base_score_per_min, energy_cost_per_min):
        """添加行为定义"""
        try:
            self.cursor.execute('''
                INSERT INTO behavior_def (name, level, category, base_score_per_min, energy_cost_per_min)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, level, category, base_score_per_min, energy_cost_per_min))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # 行为已存在
    
    def get_all_behaviors(self):
        """获取所有行为定义"""
        self.cursor.execute('SELECT * FROM behavior_def')
        rows = self.cursor.fetchall()
        
        behaviors = {}
        for row in rows:
            behaviors[row[1]] = {
                "name": row[1],
                "level": row[2],
                "category": row[3],
                "base_score_per_min": row[4],
                "energy_cost_per_min": row[5]
            }
        return behaviors
    
    def get_behaviors_by_level(self, level):
        """根据等级获取行为定义"""
        self.cursor.execute('SELECT * FROM behavior_def WHERE level = ?', (level,))
        rows = self.cursor.fetchall()
        
        behaviors = {}
        for row in rows:
            behaviors[row[1]] = {
                "name": row[1],
                "level": row[2],
                "category": row[3],
                "base_score_per_min": row[4],
                "energy_cost_per_min": row[5]
            }
        return behaviors
    
    # ----------------- 行为记录相关 -----------------
    def add_behavior_record(self, level, duration, mood, start_ts, end_ts, base_score, dynamic_coeff, final_score, energy_consume):
        """添加行为记录"""
        level_int = self._level_to_int(level)
        md5_check = self._generate_md5(level_int, duration, final_score)
        
        try:
            self.cursor.execute('''
                INSERT INTO core_behavior (level, duration, mood, start_ts, end_ts, base_score, dynamic_coeff, final_score, energy_consume, md5_check)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (level_int, duration, mood, start_ts, end_ts, base_score, dynamic_coeff, final_score, energy_consume, md5_check))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加行为记录失败: {e}")
            return False
    
    def get_today_records(self):
        """获取今日行为记录"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_start_ts = int(datetime.strptime(today, '%Y-%m-%d').timestamp())
        
        self.cursor.execute('SELECT * FROM core_behavior WHERE start_ts >= ?', (today_start_ts,))
        rows = self.cursor.fetchall()
        
        records = []
        for row in rows:
            records.append({
                "id": row[0],
                "level": self._int_to_level(row[1]),
                "duration": row[2],
                "mood": row[3],
                "start_ts": row[4],
                "end_ts": row[5],
                "base_score": row[6],
                "dynamic_coeff": row[7],
                "final_score": row[8],
                "energy_consume": row[9],
                "create_ts": row[10],
                "md5_check": row[11]
            })
        return records
    
    def get_total_score(self):
        """获取总得分"""
        self.cursor.execute('SELECT SUM(final_score) FROM core_behavior')
        result = self.cursor.fetchone()[0]
        return result or 0
    
    # ----------------- 用户状态相关 -----------------
    def get_user_state(self):
        """获取用户状态"""
        self.cursor.execute('SELECT * FROM user_state WHERE id = 1')
        row = self.cursor.fetchone()
        
        if not row:
            # 初始化用户状态
            self.cursor.execute('INSERT INTO user_state DEFAULT VALUES')
            self.conn.commit()
            return self.get_user_state()
        
        return {
            "id": row[0],
            "current_energy": row[1],
            "combo_count": row[2],
            "today_total_score": row[3],
            "today_behavior_count": row[4],
            "last_record_ts": row[5],
            "efficient_periods": json.loads(row[6]) if row[6] else []
        }
    
    def update_user_state(self, **kwargs):
        """更新用户状态"""
        if not kwargs:
            return True
        
        # 构建更新语句
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        
        try:
            # 先检查是否存在记录
            self.cursor.execute('SELECT id FROM user_state WHERE id = 1')
            exists = self.cursor.fetchone()
            
            if exists:
                # 更新现有记录
                sql = f"UPDATE user_state SET {set_clause} WHERE id = 1"
                self.cursor.execute(sql, values)
            else:
                # 插入新记录
                columns = ', '.join(['id'] + list(kwargs.keys()))
                placeholders = ', '.join(['?'] * (len(kwargs) + 1))
                sql = f"INSERT INTO user_state ({columns}) VALUES ({placeholders})"
                self.cursor.execute(sql, [1] + values)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新用户状态失败: {e}")
            return False
    
    # ----------------- 配置相关 -----------------
    def set_config(self, key, value):
        """设置配置"""
        json_value = json.dumps(value)
        try:
            self.cursor.execute('''
                INSERT INTO system_config (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = ?
            ''', (key, json_value, json_value))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"设置配置失败: {e}")
            return False
    
    def get_config(self, key, default=None):
        """获取配置"""
        self.cursor.execute('SELECT value FROM system_config WHERE key = ?', (key,))
        row = self.cursor.fetchone()
        
        if not row:
            return default
        
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return default
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
