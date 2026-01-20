import json
import os
from storage_engine import StorageEngine
from datetime import datetime

class DataMigrator:
    """数据迁移工具，将JSON数据迁移到SQLite数据库"""
    
    def __init__(self):
        """初始化迁移工具"""
        self.storage = StorageEngine()
    
    def migrate_behaviors(self):
        """迁移behaviors.json数据"""
        behaviors_file = "behaviors.json"
        
        if not os.path.exists(behaviors_file):
            print(f"{behaviors_file} 不存在，跳过迁移")
            return True
        
        try:
            with open(behaviors_file, 'r', encoding='utf-8') as f:
                behaviors = json.load(f)
        except json.JSONDecodeError:
            print(f"{behaviors_file} 格式错误，跳过迁移")
            return False
        
        # 迁移行为数据
        for name, info in behaviors.items():
            # 确保数据格式正确
            level = info.get("level", "B")
            category = info.get("category", "未分类")
            
            # 处理不同版本的数据格式
            if "base_score_per_min" in info:
                base_score_per_min = info["base_score_per_min"]
                energy_cost_per_min = info["energy_cost_per_min"]
            elif "base_score" in info:
                base_score_per_min = info["base_score"]
                energy_cost_per_min = info["energy_cost"]
            else:
                print(f"跳过无效行为 {name}: 缺少必要的分数信息")
                continue
            
            # 添加到数据库
            if self.storage.add_behavior(name, level, category, base_score_per_min, energy_cost_per_min):
                print(f"迁移行为成功: {name}")
            else:
                print(f"迁移行为失败: {name} (可能已存在)")
        
        return True
    
    def migrate_user_data(self):
        """迁移user_data.json数据"""
        user_data_file = "user_data.json"
        
        if not os.path.exists(user_data_file):
            print(f"{user_data_file} 不存在，跳过迁移")
            return True
        
        try:
            with open(user_data_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
        except json.JSONDecodeError:
            print(f"{user_data_file} 格式错误，跳过迁移")
            return False
        
        # 迁移行为记录
        behavior_list = user_data.get("behavior_list", [])
        for behavior in behavior_list:
            # 确保数据格式正确
            level = behavior.get("level", "B")
            duration = behavior.get("duration", 0)
            mood = behavior.get("mood", 3)
            
            # 处理时间字段
            if "start_time" in behavior:
                start_ts = int(datetime.strptime(behavior["start_time"], "%Y-%m-%d %H:%M:%S").timestamp())
            else:
                start_ts = int(datetime.now().timestamp())
            
            if "end_time" in behavior:
                end_ts = int(datetime.strptime(behavior["end_time"], "%Y-%m-%d %H:%M:%S").timestamp())
            else:
                end_ts = start_ts
            
            base_score = behavior.get("base_score", 0)
            dynamic_coeff = behavior.get("dynamic_coefficient", 1.0)
            final_score = behavior.get("final_score", 0)
            energy_consume = behavior.get("energy_cost", 0)
            
            # 添加到数据库
            if self.storage.add_behavior_record(
                level, duration, mood, start_ts, end_ts, 
                base_score, dynamic_coeff, final_score, energy_consume
            ):
                print(f"迁移行为记录成功: {level}级, {duration}分钟")
            else:
                print(f"迁移行为记录失败: {level}级, {duration}分钟")
        
        # 迁移用户状态
        user_state = {
            "current_energy": user_data.get("day_energy", 100),
            "combo_count": user_data.get("combo_count", 0),
            "today_total_score": user_data.get("day_score", 0),
            "today_behavior_count": user_data.get("today_behaviors_count", 0)
        }
        
        if "last_record_time" in user_data:
            try:
                last_record_ts = int(datetime.strptime(user_data["last_record_time"], "%Y-%m-%d %H:%M:%S.%f").timestamp())
                user_state["last_record_ts"] = last_record_ts
            except ValueError:
                pass
        
        if self.storage.update_user_state(**user_state):
            print("迁移用户状态成功")
        else:
            print("迁移用户状态失败")
        
        return True
    
    def run_migration(self):
        """执行完整数据迁移"""
        print("开始数据迁移...")
        
        success = True
        success &= self.migrate_behaviors()
        success &= self.migrate_user_data()
        
        self.storage.close()
        
        if success:
            print("数据迁移完成！")
        else:
            print("数据迁移部分失败！")
        
        return success

if __name__ == "__main__":
    migrator = DataMigrator()
    migrator.run_migration()
