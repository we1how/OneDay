import json
from datetime import datetime

# 2.0版本等级信息配置
LEVEL_CONFIG = {
    "S": {
        "base_score_per_min": 1.8,  # 基础分/分钟
        "energy_cost_per_min": 0.35,  # 精力消耗/分钟
        "mental_anchor": "突破性成长",
        "example": "深度工作、攻克难题、高强度训练"
    },
    "A": {
        "base_score_per_min": 1.2,  # 基础分/分钟
        "energy_cost_per_min": 0.25,  # 精力消耗/分钟
        "mental_anchor": "有效进步",
        "example": "学习新知识、创造性工作、专注阅读"
    },
    "B": {
        "base_score_per_min": 0.7,  # 基础分/分钟
        "energy_cost_per_min": 0.18,  # 精力消耗/分钟
        "mental_anchor": "稳定维持",
        "example": "复习、整理、轻度运动、家务"
    },
    "C": {
        "base_score_per_min": -0.5,  # 基础分/分钟
        "energy_cost_per_min": 0.10,  # 精力消耗/分钟
        "mental_anchor": "时间流逝",
        "example": "无目的刷手机、看无聊视频"
    },
    "D": {
        "base_score_per_min": -1.0,  # 基础分/分钟
        "energy_cost_per_min": 0.15,  # 精力消耗/分钟
        "mental_anchor": "自我损害",
        "example": "熬夜、暴食、过度放纵"
    }
}

# 心情系数配置
MOOD_CONFIG = {
    1: {"coefficient": 0.7, "description": "显著降低", "text": "承认今天的艰难"},
    2: {"coefficient": 0.85, "description": "适度降低", "text": "不太理想但可接受"},
    3: {"coefficient": 1.0, "description": "无影响", "text": "标准状态"},
    4: {"coefficient": 1.2, "description": "适度提升", "text": "状态不错"},
    5: {"coefficient": 1.4, "description": "显著提升", "text": "巅峰体验"}
}

# 全局参数配置
GLOBAL_CONFIG = {
    "per_time": 1,  # 每几分钟计算得分
    "base_luck_rate": 0.15,  # 每日基础幸运率15%
    "fatigue_factor": 0.95,  # 幸运率衰减因子
    "max_combo_bonus": 1.3,  # 最大连击奖励
    "rebound_bonus": 1.1,  # 反弹奖励
    "start_bonus_duration": 5,  # 开始奖励时长（分钟）
    "start_bonus_score": 1.2,  # 开始奖励得分系数
    "start_bonus_energy": 0.8,  # 开始奖励精力系数
    "perfect_finish_bonus": 1.3,  # 完美收官奖励
    "beginner_period_days": 7,  # 新手期天数
    "novice_bonus": 1.2  # 新手奖励系数
}

# 时段系数配置
TIME_PERIOD_CONFIG = {
    "golden": {"time_ranges": [(9, 11), (15, 17)], "coefficient": 1.3, "description": "认知高峰期"},
    "silver": {"time_ranges": [(8, 9), (14, 15), (19, 21)], "coefficient": 1.1, "description": "次佳工作期"},
    "standard": {"time_ranges": [], "coefficient": 1.0, "description": "正常效率"},
    "fatigue": {"time_ranges": [(13, 14), (22, 24)], "coefficient": 0.8, "description": "生理低谷"},
    "rest": {"time_ranges": [(0, 6)], "coefficient": 0.5, "description": "应睡眠时间"}
}

# 默认用户数据结构（2.0扩展版）
DEFAULT_USER_DATA = {
    "behavior_list": [],  # 存储所有行为信息
    "behavior_day_list": [],  # 存储当日行为信息
    "total_score": 0,  # 总得分
    "day_score": 0,  # 当日得分
    "history_score": [],  # 历史得分列表
    "total_energy": 100,  # 总精力
    "day_energy": 100,  # 当日精力剩余
    "day_energy_cost": 0,  # 当日精力消耗
    "history_energy_cost": [],  # 历史精力消耗
    "last_record_time": None,  # 上次记录时间
    "today_behaviors_count": 0,  # 当日已记录行为数
    "consecutive_unlucky_count": 0,  # 连续未触发幸运次数
    "combo_count": 0,  # 连击次数
    "last_behavior": None,  # 上次行为
    "last_behavior_level": None,  # 上次行为等级
    "last_behavior_category": None,  # 上次行为类别
    "beginner_period": True,  # 新手期标记
    "efficient_periods": [],  # 高效时段
    "recent_behaviors": [],  # 最近3个行为，用于连击检测
    "lucky_triggers_today": 0,  # 今日幸运触发次数
    "is_first_behavior_today": True  # 是否是今日第一个行为
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
            loaded_data = json.load(f)
        
        # 合并默认数据，确保所有新字段存在
        user_data = DEFAULT_USER_DATA.copy()
        for key, value in loaded_data.items():
            user_data[key] = value
        
        return user_data
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

def get_current_hour():
    """获取当前小时"""
    return datetime.now().hour

def calculate_energy_coefficient(current_energy):
    """计算精力系数"""
    if current_energy > 70:
        return 1.0 + (current_energy - 70) * 0.01
    elif current_energy > 40:
        return 0.85 + (current_energy - 40) * 0.005
    else:
        return 0.7  # 低能量保护

def calculate_time_period_coefficient():
    """计算时段系数"""
    current_hour = get_current_hour()
    
    # 检查各个时段
    for period, config in TIME_PERIOD_CONFIG.items():
        if period == "standard":
            continue  # 标准时段最后处理
        
        for start, end in config["time_ranges"]:
            if start <= current_hour < end:
                return {
                    "coefficient": config["coefficient"],
                    "period_type": period,
                    "description": config["description"]
                }
    
    # 默认返回标准时段
    return {
        "coefficient": TIME_PERIOD_CONFIG["standard"]["coefficient"],
        "period_type": "standard",
        "description": TIME_PERIOD_CONFIG["standard"]["description"]
    }

def calculate_combo_coefficient(recent_behaviors, current_level):
    """计算连击系数"""
    # 检查当前行为是否为正向行为（S/A/B）
    is_positive = current_level in ["S", "A", "B"]
    
    # 获取最近的正向行为
    positive_recent = [b for b in recent_behaviors if b["level"] in ["S", "A", "B"]]
    
    combo_count = len(positive_recent)
    
    # 计算连击系数
    if combo_count == 0:
        combo_coeff = 1.0
    elif combo_count == 1:
        combo_coeff = 1.1
    elif combo_count == 2:
        combo_coeff = 1.2
    else:
        combo_coeff = GLOBAL_CONFIG["max_combo_bonus"]  # 上限1.3
    
    # 检查是否是中断后的第一个正面行为
    is_negative_break = len(recent_behaviors) > 0 and recent_behaviors[-1]["level"] in ["C", "D"]
    if is_positive and is_negative_break:
        combo_coeff *= GLOBAL_CONFIG["rebound_bonus"]
    
    # 检查是否是同领域专精
    # 简化处理：假设相同等级为同领域
    is_same_field = len(positive_recent) > 0 and all(b["level"] == current_level for b in positive_recent)
    if is_same_field and combo_count >= 1:
        combo_coeff *= 1.15
    
    return {
        "coefficient": combo_coeff,
        "combo_count": combo_count,
        "is_same_field": is_same_field,
        "is_negative_break": is_negative_break
    }

def calculate_lucky_coefficient(behaviors_count, consecutive_unlucky):
    """计算幸运系数"""
    import random
    
    # 计算实际幸运率
    actual_luck_rate = GLOBAL_CONFIG["base_luck_rate"] * (GLOBAL_CONFIG["fatigue_factor"] ** behaviors_count)
    
    # 安慰幸运：连续3次未触发，下次必触发
    if consecutive_unlucky >= 3:
        is_lucky = True
        consecutive_unlucky = 0
    else:
        is_lucky = random.random() < actual_luck_rate
        
    if is_lucky:
        # 5%概率超级幸运
        if random.random() < 0.05:
            lucky_coeff = 2.0
            lucky_type = "super"
        else:
            lucky_coeff = 1.5
            lucky_type = "normal"
        consecutive_unlucky = 0
    else:
        lucky_coeff = 1.0
        lucky_type = "none"
        consecutive_unlucky += 1
    
    return {
        "coefficient": lucky_coeff,
        "is_lucky": is_lucky,
        "lucky_type": lucky_type,
        "new_unlucky_count": consecutive_unlucky
    }

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
        user_data["today_behaviors_count"] = 0
        user_data["consecutive_unlucky_count"] = 0
        user_data["combo_count"] = 0
        user_data["recent_behaviors"] = []
        user_data["lucky_triggers_today"] = 0
        user_data["is_first_behavior_today"] = True
    return user_data

def calculate_energy_recovery(last_record_time):
    """计算精力恢复"""
    if not last_record_time:
        return 0
    
    now = datetime.now()
    last_time = datetime.fromisoformat(last_record_time)
    time_diff = (now - last_time).total_seconds() / 60  # 转换为分钟
    
    # 间隔>30分钟才恢复
    if time_diff <= 30:
        return 0
    
    # 每分钟恢复0.02点
    recovery = time_diff * 0.02
    return recovery
