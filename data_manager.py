import json
from datetime import datetime

# 配置文件路径
CONFIG_FILE = "config.json"

def load_config():
    """从外部文件加载配置"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"配置文件 {CONFIG_FILE} 未找到，使用默认配置")
        return get_default_config()
    except json.JSONDecodeError:
        print(f"配置文件 {CONFIG_FILE} 格式错误，使用默认配置")
        return get_default_config()

def get_default_config():
    """获取默认配置"""
    return {
        "level_config": {
            "S": {
                "base_score_per_min": 1.8,
                "energy_cost_per_min": 0.35,
                "mental_anchor": "突破性成长",
                "example": "深度工作、攻克难题、高强度训练"
            },
            "A": {
                "base_score_per_min": 1.2,
                "energy_cost_per_min": 0.25,
                "mental_anchor": "有效进步",
                "example": "学习新知识、创造性工作、专注阅读"
            },
            "B": {
                "base_score_per_min": 0.7,
                "energy_cost_per_min": 0.18,
                "mental_anchor": "稳定维持",
                "example": "复习、整理、轻度运动、家务"
            },
            "C": {
                "base_score_per_min": -0.5,
                "energy_cost_per_min": 0.10,
                "mental_anchor": "时间流逝",
                "example": "无目的刷手机、看无聊视频"
            },
            "D": {
                "base_score_per_min": -1.0,
                "energy_cost_per_min": 0.15,
                "mental_anchor": "自我损害",
                "example": "熬夜、暴食、过度放纵"
            },
            "R": {
                "base_score_per_min": 0,
                "energy_cost_per_min": 0,
                "mental_anchor": "恢复行为",
                "example": "散步、冥想、午睡",
                "sublevels": {
                    "R1": {
                        "base_score_per_min": 0.2,
                        "energy_cost_per_min": -0.10,
                        "mental_anchor": "轻度放松",
                        "example": "喝茶、听音乐、短暂休息"
                    },
                    "R2": {
                        "base_score_per_min": 0.3,
                        "energy_cost_per_min": -0.20,
                        "mental_anchor": "中等恢复",
                        "example": "散步、瑜伽、阅读休闲书"
                    },
                    "R3": {
                        "base_score_per_min": 0.4,
                        "energy_cost_per_min": -0.30,
                        "mental_anchor": "深度恢复",
                        "example": "午睡、冥想、正念练习"
                    }
                }
            }
        },
        "mood_config": {
            "1": {
                "coefficient": 0.7,
                "description": "显著降低",
                "text": "承认今天的艰难"
            },
            "2": {
                "coefficient": 0.85,
                "description": "适度降低",
                "text": "不太理想但可接受"
            },
            "3": {
                "coefficient": 1.0,
                "description": "无影响",
                "text": "标准状态"
            },
            "4": {
                "coefficient": 1.2,
                "description": "适度提升",
                "text": "状态不错"
            },
            "5": {
                "coefficient": 1.4,
                "description": "显著提升",
                "text": "巅峰体验"
            }
        },
        "global_config": {
            "per_time": 1,
            "energy_max": 120,  # 精力上限
            "energy_low_threshold": 30,  # 低精力阈值
            "energy_zero_threshold": 0,  # 精力为0时不得分
            "low_energy_positive_coeff": 0.9,  # 低精力时正面行为系数上限
            "low_energy_recovery_bonus": 1.2,  # 低精力时恢复行为加成
            "passive_recovery_rate": 0.02,  # 行为间隔>30分钟时的恢复率
            "no_behavior_recovery_rate": 1.5,  # 无行为时每小时恢复率
            "cross_day_recovery_default": 50,  # 跨天默认恢复值
            "b_level_recovery_percent": 0.3,  # B级行为后恢复其消耗的百分比
            "max_combo_bonus": 1.3,  # 最大连击奖励
            "rebound_bonus": 1.1,  # 反弹奖励
            "start_bonus_duration": 5,  # 开始奖励时长
            "start_bonus_score": 1.2,  # 开始奖励得分系数
            "start_bonus_energy": 0.8,  # 开始奖励精力系数
            "beginner_period_days": 7,  # 新手期天数
            "novice_bonus": 1.2,  # 新手奖励系数
            "enable_time_period_coeff": False,  # 是否启用时段系数
            "enable_lucky_coeff": False,  # 是否启用幸运系数
            "enable_mood_coeff": False  # 是否启用心情系数
        },
        "time_period_config": {
            "golden": {
                "time_ranges": [[9, 11], [15, 17]],
                "coefficient": 1.3,
                "description": "认知高峰期"
            },
            "silver": {
                "time_ranges": [[8, 9], [14, 15], [19, 21]],
                "coefficient": 1.1,
                "description": "次佳工作期"
            },
            "standard": {
                "time_ranges": [],
                "coefficient": 1.0,
                "description": "正常效率"
            },
            "fatigue": {
                "time_ranges": [[13, 14], [22, 24]],
                "coefficient": 0.8,
                "description": "生理低谷"
            },
            "rest": {
                "time_ranges": [[0, 6]],
                "coefficient": 0.5,
                "description": "应睡眠时间"
            }
        }
    }

# 加载配置
config = load_config()

# 配置常量
LEVEL_CONFIG = config["level_config"]
MOOD_CONFIG = {int(k): v for k, v in config["mood_config"].items()}  # 转换为整数键
GLOBAL_CONFIG = config["global_config"]
TIME_PERIOD_CONFIG = config["time_period_config"]

# 转换时间范围为元组格式，便于处理
for period in TIME_PERIOD_CONFIG.values():
    period["time_ranges"] = [tuple(range_) for range_ in period["time_ranges"]]

# 延迟导入，避免循环依赖
from storage_engine import StorageEngine

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

def load_behaviors():
    """加载行为列表 - 使用SQLite存储引擎"""
    storage = StorageEngine()
    behaviors = storage.get_all_behaviors()
    storage.close()
    return behaviors

def save_behaviors(behaviors):
    """保存行为列表 - 使用SQLite存储引擎"""
    # 由于我们直接通过add_behavior添加行为，这里不再需要批量保存
    pass

def load_user_data():
    """加载用户数据 - 使用SQLite存储引擎"""
    storage = StorageEngine()
    
    # 获取用户状态
    user_state = storage.get_user_state()
    
    # 获取今日行为记录
    today_records = storage.get_today_records()
    
    # 获取总得分
    total_score = storage.get_total_score()
    
    storage.close()
    
    # 构建兼容的用户数据格式
    user_data = DEFAULT_USER_DATA.copy()
    user_data.update({
        "day_energy": user_state["current_energy"],
        "combo_count": user_state["combo_count"],
        "day_score": user_state["today_total_score"],
        "today_behaviors_count": user_state["today_behavior_count"],
        "last_record_time": datetime.fromtimestamp(user_state["last_record_ts"]).isoformat() if user_state["last_record_ts"] else None,
        "efficient_periods": user_state["efficient_periods"],
        "total_score": total_score,
        "behavior_day_list": today_records,
        "recent_behaviors": today_records[-3:],  # 最近3个行为
    })
    
    return user_data

def save_user_data(user_data):
    """保存用户数据 - 使用SQLite存储引擎"""
    pass  # 数据直接通过StorageEngine更新，不需要批量保存

def get_behaviors_by_level(level):
    """根据等级获取行为列表"""
    storage = StorageEngine()
    behaviors = storage.get_behaviors_by_level(level)
    storage.close()
    return behaviors

def add_behavior_to_db(name, level, category, base_score_per_min, energy_cost_per_min):
    """向数据库添加行为"""
    storage = StorageEngine()
    result = storage.add_behavior(name, level, category, base_score_per_min, energy_cost_per_min)
    storage.close()
    return result

def add_behavior_record(level, duration, mood, start_ts, end_ts, base_score, dynamic_coeff, final_score, energy_consume):
    """向数据库添加行为记录"""
    storage = StorageEngine()
    result = storage.add_behavior_record(
        level, duration, mood, start_ts, end_ts, base_score, dynamic_coeff, final_score, energy_consume
    )
    
    # 更新用户状态
    user_state = storage.get_user_state()
    new_energy = max(0, user_state["current_energy"] - energy_consume)
    
    # B级行为后恢复其消耗的30%
    if level == "B":
        # 计算恢复量：消耗的30%
        recovery_amount = energy_consume * GLOBAL_CONFIG["b_level_recovery_percent"]
        new_energy += recovery_amount
    
    # 应用精力上限
    new_energy = min(new_energy, GLOBAL_CONFIG["energy_max"])
    
    storage.update_user_state(
        current_energy=new_energy,
        today_total_score=user_state["today_total_score"] + final_score,
        today_behavior_count=user_state["today_behavior_count"] + 1,
        last_record_ts=end_ts
    )
    
    storage.close()
    return result

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
        
        # 跨天恢复机制
        # 前日剩余精力
        previous_energy = user_data["day_energy"]
        
        # 睡眠恢复：默认8小时×7点=56点
        sleep_recovery = 56
        
        # 计算新一天的初始精力
        new_day_energy = previous_energy + sleep_recovery
        
        # 若无睡眠数据，默认+50点
        # 注：此处简化处理，实际应基于授权数据或用户输入
        if not user_data["last_record_time"]:
            new_day_energy = previous_energy + GLOBAL_CONFIG["cross_day_recovery_default"]
        
        # 应用精力上限
        new_day_energy = min(GLOBAL_CONFIG["energy_max"], new_day_energy)
        
        # 重置当日数据
        user_data["day_score"] = 0
        user_data["day_energy"] = new_day_energy
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
    
    recovery = 0
    
    # 间隔>30分钟才恢复
    if time_diff > 30:
        # 1. 基础被动恢复：每分钟恢复0.02点
        recovery += time_diff * GLOBAL_CONFIG["passive_recovery_rate"]
        
        # 2. 无行为被动回复：间隔>1小时时，每小时恢复1-2点
        if time_diff > 60:
            # 转换为小时
            hours_diff = time_diff / 60
            
            # 根据当前时间段调整恢复率
            current_hour = now.hour
            if 6 <= current_hour < 12 or 14 <= current_hour < 18:  # 早晨/下午
                hourly_recovery = 2.0
            elif 12 <= current_hour < 14 or 18 <= current_hour < 22:  # 中午/晚上
                hourly_recovery = 1.5
            else:  # 深夜/凌晨
                hourly_recovery = 1.0
            
            # 计算无行为恢复
            no_behavior_recovery = hours_diff * hourly_recovery
            recovery += no_behavior_recovery
    
    return recovery
