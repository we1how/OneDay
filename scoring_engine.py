from datetime import datetime
from data_manager import (
    calculate_energy_coefficient,
    calculate_combo_coefficient,
    LEVEL_CONFIG, GLOBAL_CONFIG
)

class ScoringEngine:
    """得分计算引擎（V3.0版本）"""
    
    def __init__(self, user_data):
        """初始化得分计算引擎"""
        self.user_data = user_data
    
    def _infer_r_sublevel(self, level, duration, mood):
        """推测R级的子级（R1/R2/R3）"""
        # 如果用户已经指定了子级（如R1），直接返回
        if len(level) > 1:
            return level
        
        # 基于心情推测
        if mood <= 2:
            inferred_sublevel = "R1"
        elif mood == 3:
            inferred_sublevel = "R2"
        else:  # 4-5星
            inferred_sublevel = "R3"
        
        # 基于时长调整
        if duration < 15:
            inferred_sublevel = "R1"
        elif 15 <= duration <= 30:
            inferred_sublevel = "R2"
        else:  # >30分钟
            inferred_sublevel = "R3"
        
        # 基于上下文（前一个行为）
        if self.user_data["recent_behaviors"]:
            last_behavior = self.user_data["recent_behaviors"][-1]
            if last_behavior["level"] in ["S", "A"]:
                # 前行为是高消耗，提升恢复子级
                if inferred_sublevel == "R1":
                    inferred_sublevel = "R2"
                elif inferred_sublevel == "R2":
                    inferred_sublevel = "R3"
        
        return inferred_sublevel
    
    def get_behavior_info(self, level, duration, mood):
        """获取行为信息，处理R级子级推测"""
        if level.startswith("R"):
            # 处理R级行为
            r_level = self._infer_r_sublevel(level, duration, mood)
            # 获取R级配置
            r_config = LEVEL_CONFIG["R"]
            # 获取子级配置
            sublevel_config = r_config["sublevels"][r_level]
            
            return {
                "name": level,
                "level": level,
                "category": "恢复行为",
                "base_score_per_min": sublevel_config["base_score_per_min"],
                "energy_cost_per_min": sublevel_config["energy_cost_per_min"],
                "mental_anchor": sublevel_config["mental_anchor"],
                "example": sublevel_config["example"],
                "inferred_sublevel": r_level
            }
        else:
            # 普通行为，直接返回
            return LEVEL_CONFIG[level]
    
    def calculate_energy_cost(self, behavior_info, level, duration, current_energy):
        """计算精力消耗/恢复"""
        # 开始奖励：前5分钟精力消耗×0.8
        start_bonus_energy = 1.0
        if duration <= GLOBAL_CONFIG["start_bonus_duration"]:
            start_bonus_energy = GLOBAL_CONFIG["start_bonus_energy"]
        
        energy_cost_per_min = behavior_info["energy_cost_per_min"]
        
        # 应用低精力保护
        final_energy_cost = energy_cost_per_min * duration * start_bonus_energy
        
        # 低精力时恢复行为加成
        if current_energy < GLOBAL_CONFIG["energy_low_threshold"] and energy_cost_per_min < 0:
            final_energy_cost *= GLOBAL_CONFIG["low_energy_recovery_bonus"]
        
        return {
            "final_energy_cost": final_energy_cost,
            "base_energy_cost": energy_cost_per_min * duration,
            "start_bonus_energy": start_bonus_energy,
            "is_recovery": energy_cost_per_min < 0
        }
    
    def calculate_score(self, behavior_info, level, duration, mood, current_energy):
        """计算最终得分（V3.0版本，去除主观/随机因素）"""
        # 1. 检查精力为0时不得分
        if current_energy <= GLOBAL_CONFIG["energy_zero_threshold"]:
            return {
                "final_score": 0,
                "base_score": 0,
                "dynamic_coefficient": 0,
                "energy_coefficient": 0,
                "combo_coefficient": 0,
                "start_bonus_score": 1.0,
                "novice_bonus": 1.0,
                "is_energy_zero": True
            }
        
        # 2. 计算各项系数
        
        # 精力系数
        energy_coeff = calculate_energy_coefficient(current_energy)
        
        # 应用低精力正面行为系数上限
        if current_energy < GLOBAL_CONFIG["energy_low_threshold"] and level in ["S", "A", "B"]:
            energy_coeff = min(energy_coeff, GLOBAL_CONFIG["low_energy_positive_coeff"])
        
        # 连击系数
        combo_result = calculate_combo_coefficient(self.user_data["recent_behaviors"], level)
        combo_coeff = combo_result["coefficient"]
        
        # 动态系数 = 精力系数 × 连击系数（去除了时段、幸运、心情系数）
        dynamic_coeff = energy_coeff * combo_coeff
        
        # 3. 上瘾循环机制
        
        # 开始奖励：前5分钟得分×1.2
        start_bonus_score = 1.0
        if duration <= GLOBAL_CONFIG["start_bonus_duration"]:
            start_bonus_score = GLOBAL_CONFIG["start_bonus_score"]
        
        # 新手奖励：首周所有系数×1.2
        novice_bonus = 1.0
        if self.user_data["beginner_period"]:
            novice_bonus = GLOBAL_CONFIG["novice_bonus"]
        
        # 4. 基础分计算
        base_score_per_min = behavior_info["base_score_per_min"]
        base_score = base_score_per_min * duration
        
        # 5. 最终得分计算（V3.0公式：单次得分 = 基础分 × 动态系数）
        final_score = base_score * dynamic_coeff * start_bonus_score * novice_bonus
        
        return {
            "final_score": final_score,
            "base_score": base_score,
            "dynamic_coefficient": dynamic_coeff,
            "energy_coefficient": energy_coeff,
            "combo_coefficient": combo_coeff,
            "start_bonus_score": start_bonus_score,
            "novice_bonus": novice_bonus,
            "combo_result": combo_result,
            "is_energy_zero": False
        }
    
    def apply_balance_mechanisms(self, score_details, same_behavior_count, is_short_frequency, level):
        """应用防滥用与平衡机制"""
        final_score = score_details["final_score"]
        
        # 同一行为重复第4次起收益递减20%
        if same_behavior_count >= 3:
            final_score *= 0.8
        
        # 短时长高频（10分钟内重复）第二次起系数×0.7
        if is_short_frequency:
            final_score *= 0.7
        
        # 防刷R机制：连续R级>2次，恢复率降低
        # 这里简化处理，直接在score上调整
        if level.startswith("R"):
            r_count = sum(1 for b in self.user_data["recent_behaviors"] if b["level"].startswith("R"))
            if r_count >= 2:
                final_score *= 0.8
        
        # 更新最终得分
        score_details["final_score"] = final_score
        score_details["applied_balance"] = {
            "same_behavior_count": same_behavior_count,
            "is_short_frequency": is_short_frequency
        }
        
        return score_details
    
    def generate_behavior_record(self, selected_behavior, behavior_info, level, duration, mood, score_details, specific_time="", feeling=""):
        """生成行为记录"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.now().strftime("%Y-%m-%d")
        
        return {
            "name": selected_behavior,
            "level": level,
            "category": behavior_info.get("category", "未分类"),
            "duration": duration,
            "mood": mood,
            "specific_time": specific_time,
            "feeling": feeling,
            "start_time": current_time,
            "end_time": current_time,
            "date": today,
            "base_score": score_details["base_score"],
            "dynamic_coefficient": score_details["dynamic_coefficient"],
            "energy_coefficient": score_details["energy_coefficient"],
            "combo_coefficient": score_details["combo_coefficient"],
            "start_bonus_score": score_details["start_bonus_score"],
            "novice_bonus": score_details["novice_bonus"],
            "final_score": score_details["final_score"],
            "combo_count": score_details["combo_result"]["combo_count"],
            "inferred_sublevel": behavior_info.get("inferred_sublevel", None)
        }
    
    def update_energy(self, current_energy, energy_cost):
        """更新精力，应用精力上限"""
        new_energy = current_energy - energy_cost  # 注意：恢复行为的energy_cost是负数
        
        # 应用精力上限
        if new_energy > GLOBAL_CONFIG["energy_max"]:
            new_energy = GLOBAL_CONFIG["energy_max"]
        
        # 确保精力不低于0
        new_energy = max(0, new_energy)
        
        return new_energy
    
    def update_user_data(self, user_data, behavior_record, energy_cost_details, current_energy):
        """更新用户数据 - 使用数据库存储"""
        # 向数据库添加行为记录
        from data_manager import add_behavior_record
        
        # 转换时间字符串为时间戳
        start_ts = int(datetime.strptime(behavior_record["start_time"], "%Y-%m-%d %H:%M:%S").timestamp())
        end_ts = int(datetime.strptime(behavior_record["end_time"], "%Y-%m-%d %H:%M:%S").timestamp())
        
        # 添加记录到数据库
        add_behavior_record(
            behavior_record["level"],
            behavior_record["duration"],
            behavior_record["mood"],
            start_ts,
            end_ts,
            behavior_record["base_score"],
            behavior_record["dynamic_coefficient"],
            behavior_record["final_score"],
            energy_cost_details["final_energy_cost"]
        )
        
        # 重新加载最新的用户数据
        from data_manager import load_user_data
        return load_user_data()
