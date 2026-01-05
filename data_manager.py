import json
from datetime import datetime

# 等级信息配置
LEVEL_CONFIG = {
    "S": {
        "base_score": 5,
        "energy_cost": 5,
        "level_weight": 1,
        "chain_weight": 1
    },
    "A": {
        "base_score": 3,
        "energy_cost": 3,
        "level_weight": 1,
        "chain_weight": 1
    },
    "B": {
        "base_score": 1,
        "energy_cost": 1,
        "level_weight": 1,
        "chain_weight": 1
    },
    "C": {
        "base_score": -3,
        "energy_cost": 3,
        "level_weight": 1,
        "chain_weight": 1
    },
    "D": {
        "base_score": -5,
        "energy_cost": 5,
        "level_weight": 1,
        "chain_weight": 1
    }
}

# 全局参数配置
GLOBAL_CONFIG = {
    "per_time": 1  # 每几分钟计算得分
}

# 默认用户数据结构
DEFAULT_USER_DATA = {
    "behavior_list": [],  # 存储所有行为信息
    "behavior_day_list": [],  # 存储当日行为信息
    "total_score": 0,  # 总得分
    "day_score": 0,  # 当日得分
    "history_score": [],  # 历史得分列表
    "total_energy": 100,  # 总精力
    "day_energy": 100,  # 当日精力剩余
    "day_energy_cost": 0,  # 当日精力消耗
    "history_energy_cost": []  # 历史精力消耗
}

# 行为数据存储文件
BEHAVIOR_FILE = "behaviors.json"
# 用户数据存储文件
USER_DATA_FILE = "user_data.json"

def load_behaviors():
    """加载行为列表"""
    try:
        with open(BEHAVIOR_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_behaviors(behaviors):
    """保存行为列表"""
    with open(BEHAVIOR_FILE, 'w', encoding='utf-8') as f:
        json.dump(behaviors, f, ensure_ascii=False, indent=2)

def load_user_data():
    """加载用户数据"""
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_USER_DATA.copy()
    except json.JSONDecodeError:
        return DEFAULT_USER_DATA.copy()

def save_user_data(user_data):
    """保存用户数据"""
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

def get_today_date():
    """获取当前日期，格式：YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")

def reset_daily_data_if_needed(user_data):
    """如果不是当天的数据，重置当日数据"""
    today = get_today_date()
    # 检查是否需要重置当日数据
    if not user_data["history_score"] or user_data["history_score"][-1]["date"] != today:
        # 保存昨天的得分
        if user_data["day_score"] != 0 or user_data["day_energy_cost"] != 0:
            user_data["history_score"].append({
                "date": get_today_date(),
                "score": user_data["day_score"]
            })
            user_data["history_energy_cost"].append({
                "date": get_today_date(),
                "cost": user_data["day_energy_cost"]
            })
        # 重置当日数据
        user_data["day_score"] = 0
        user_data["day_energy"] = 100
        user_data["day_energy_cost"] = 0
        user_data["behavior_day_list"] = []
    return user_data
