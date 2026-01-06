from data_manager import (
    load_behaviors, load_user_data, save_user_data,
    LEVEL_CONFIG, MOOD_CONFIG, GLOBAL_CONFIG,
    reset_daily_data_if_needed, calculate_energy_coefficient,
    calculate_time_period_coefficient, calculate_combo_coefficient,
    calculate_lucky_coefficient, calculate_energy_recovery
)
from datetime import datetime

def record_behavior():
    """记录行为界面（2.0版本）"""
    print("=== 记录行为界面（2.0版本） ===")
    
    # 加载行为和用户数据
    behaviors = load_behaviors()
    user_data = load_user_data()
    
    # 重置当日数据（如果需要）
    user_data = reset_daily_data_if_needed(user_data)
    
    # 计算精力恢复
    if user_data["last_record_time"]:
        recovery_energy = calculate_energy_recovery(user_data["last_record_time"])
        user_data["day_energy"] = min(100, user_data["day_energy"] + recovery_energy)
    
    # 如果没有行为，提示用户先添加行为
    if not behaviors:
        print("当前没有任何行为，请先使用增加行为功能添加行为！")
        return
    
    # 用户输入：行为等级
    while True:
        level = input("请输入行为等级（S/A/B/C/D）: ").upper()
        if level in LEVEL_CONFIG:
            break
        print("无效的等级，请重新输入！")
    
    # 筛选该等级的行为
    level_behaviors = {}
    for name, info in behaviors.items():
        if info["level"] == level:
            level_behaviors[name] = info
    
    # 如果该等级没有行为，提示用户
    if not level_behaviors:
        print(f"当前等级 {level} 没有任何行为，请先添加该等级的行为！")
        return
    
    # 显示该等级的所有行为
    print(f"\n=== 等级 {level} 的行为列表 ===")
    behavior_list = list(level_behaviors.keys())
    for i, behavior in enumerate(behavior_list, 1):
        print(f"{i}. {behavior} (类别: {level_behaviors[behavior]['category']})")
    
    # 选择行为
    while True:
        try:
            choice = int(input(f"\n请选择要记录的行为编号（1-{len(behavior_list)}）: "))
            if 1 <= choice <= len(behavior_list):
                selected_behavior = behavior_list[choice - 1]
                break
            print(f"无效的选择，请输入1-{len(behavior_list)}之间的数字！")
        except ValueError:
            print("无效的输入，请输入数字！")
    
    # 用户输入：时长
    while True:
        try:
            duration = int(input("请输入时长（分钟）: "))
            if duration <= 0:
                print("时长必须大于0，请重新输入！")
                continue
            break
        except ValueError:
            print("无效的输入，请输入数字！")
    
    # 用户输入：心情（可选，默认3星）
    while True:
        mood_input = input("请输入心情（1-5星，默认3星）: ").strip()
        if not mood_input:
            mood = 3
            break
        try:
            mood = int(mood_input)
            if 1 <= mood <= 5:
                break
            print("心情必须在1-5星之间，请重新输入！")
        except ValueError:
            print("无效的输入，请输入数字！")
    
    # 获取行为信息
    behavior_info = level_behaviors[selected_behavior]
    
    # 1. 计算各项系数
    
    # 精力系数
    energy_coeff = calculate_energy_coefficient(user_data["day_energy"])
    
    # 时段系数
    time_period_result = calculate_time_period_coefficient()
    time_coeff = time_period_result["coefficient"]
    
    # 连击系数
    combo_result = calculate_combo_coefficient(user_data["recent_behaviors"], level)
    combo_coeff = combo_result["coefficient"]
    
    # 幸运系数
    lucky_result = calculate_lucky_coefficient(
        user_data["today_behaviors_count"],
        user_data["consecutive_unlucky_count"]
    )
    lucky_coeff = lucky_result["coefficient"]
    
    # 动态系数 = 精力系数 × 时段系数 × 连击系数 × 幸运系数
    dynamic_coeff = energy_coeff * time_coeff * combo_coeff * lucky_coeff
    
    # 心情系数
    mood_coeff = MOOD_CONFIG[mood]["coefficient"]
    
    # 2. 上瘾循环机制
    
    # 开始奖励：前5分钟得分×1.2，精力消耗×0.8
    start_bonus_score = 1.0
    start_bonus_energy = 1.0
    if duration <= GLOBAL_CONFIG["start_bonus_duration"]:
        start_bonus_score = GLOBAL_CONFIG["start_bonus_score"]
        start_bonus_energy = GLOBAL_CONFIG["start_bonus_energy"]
    
    # 新手奖励：首周所有系数×1.2
    novice_bonus = 1.0
    if user_data["beginner_period"]:
        novice_bonus = GLOBAL_CONFIG["novice_bonus"]
    
    # 3. 基础分和精力消耗计算
    base_score_per_min = behavior_info["base_score_per_min"]
    energy_cost_per_min = behavior_info["energy_cost_per_min"]
    
    # 计算基础分
    base_score = base_score_per_min * duration
    
    # 4. 最终得分计算
    final_score = base_score * dynamic_coeff * mood_coeff * start_bonus_score * novice_bonus
    
    # 5. 精力消耗计算
    final_energy_cost = energy_cost_per_min * duration * start_bonus_energy
    
    # 6. 防滥用与平衡机制
    
    # 同一行为重复：第4次起收益递减20%
    same_behavior_count = sum(1 for b in user_data["behavior_day_list"] if b["name"] == selected_behavior)
    if same_behavior_count >= 3:
        final_score *= 0.8
    
    # 短时长高频：10分钟内重复记录，第二次起系数×0.7
    if user_data["last_record_time"]:
        last_time = datetime.fromisoformat(user_data["last_record_time"])
        current_time = datetime.now()
        time_diff = (current_time - last_time).total_seconds() / 60
        if time_diff < 10:
            final_score *= 0.7
    
    # 7. 完美收官奖励：当日最后一个正面行为×1.3（暂不实现）
    is_positive = level in ["S", "A", "B"]
    
    # 8. 创建行为记录
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.now().strftime("%Y-%m-%d")
    
    behavior_record = {
        "name": selected_behavior,
        "level": level,
        "category": behavior_info["category"],
        "duration": duration,
        "mood": mood,
        "start_time": current_time,
        "end_time": current_time,
        "date": today,
        "base_score": base_score,
        "dynamic_coefficient": dynamic_coeff,
        "mood_coefficient": mood_coeff,
        "energy_coefficient": energy_coeff,
        "time_period_coefficient": time_coeff,
        "combo_coefficient": combo_coeff,
        "lucky_coefficient": lucky_coeff,
        "start_bonus_score": start_bonus_score,
        "novice_bonus": novice_bonus,
        "final_score": final_score,
        "energy_cost": final_energy_cost,
        "is_lucky": lucky_result["is_lucky"],
        "lucky_type": lucky_result["lucky_type"],
        "combo_count": combo_result["combo_count"]
    }
    
    # 9. 更新用户数据
    
    # 更新精力
    user_data["day_energy"] = max(0, user_data["day_energy"] - final_energy_cost)
    user_data["day_energy_cost"] += final_energy_cost
    
    # 更新得分
    user_data["day_score"] += final_score
    user_data["total_score"] += final_score
    
    # 更新行为列表
    user_data["behavior_list"].append(behavior_record)
    user_data["behavior_day_list"].append(behavior_record)
    
    # 更新最近行为（最多保存3个）
    user_data["recent_behaviors"].append(behavior_record)
    if len(user_data["recent_behaviors"]) > 3:
        user_data["recent_behaviors"] = user_data["recent_behaviors"][-3:]
    
    # 更新其他统计数据
    user_data["today_behaviors_count"] += 1
    user_data["last_record_time"] = datetime.now().isoformat()
    user_data["consecutive_unlucky_count"] = lucky_result["new_unlucky_count"]
    
    if lucky_result["is_lucky"]:
        user_data["lucky_triggers_today"] += 1
    
    # 更新上次行为信息
    user_data["last_behavior"] = selected_behavior
    user_data["last_behavior_level"] = level
    user_data["last_behavior_category"] = behavior_info["category"]
    
    # 10. 保存用户数据
    save_user_data(user_data)
    
    # 11. 显示结果
    print(f"\n=== 行为记录成功！ ===")
    print(f"行为名称: {selected_behavior}")
    print(f"行为等级: {level}")
    print(f"行为类别: {behavior_info['category']}")
    print(f"时长: {duration} 分钟")
    print(f"心情: {mood}星 {MOOD_CONFIG[mood]['text']}")
    print(f"\n=== 得分详情 ===")
    print(f"基础分: {base_score:.2f} (等级基础分: {base_score_per_min}/分钟)")
    print(f"动态系数: {dynamic_coeff:.2f}")
    print(f"  ├ 精力系数: {energy_coeff:.2f} (当前精力: {user_data['day_energy']:.1f})")
    print(f"  ├ 时段系数: {time_coeff:.2f} ({time_period_result['period_type']})")
    print(f"  ├ 连击系数: {combo_coeff:.2f} (连击: {combo_result['combo_count']})")
    print(f"  └ 幸运系数: {lucky_coeff:.2f} ({'超级幸运' if lucky_result['lucky_type'] == 'super' else '幸运' if lucky_result['lucky_type'] == 'normal' else '普通'})")
    print(f"心情系数: {mood_coeff:.2f}")
    print(f"开始奖励: {start_bonus_score:.2f}")
    print(f"新手奖励: {novice_bonus:.2f}")
    print(f"最终得分: {final_score:.2f}")
    print(f"\n=== 精力消耗 ===")
    print(f"基础消耗: {energy_cost_per_min * duration:.2f} (等级消耗: {energy_cost_per_min}/分钟)")
    print(f"开始奖励: {start_bonus_energy:.2f}")
    print(f"最终消耗: {final_energy_cost:.2f}")
    print(f"\n=== 当前状态 ===")
    print(f"当日剩余精力: {user_data['day_energy']:.1f}")
    print(f"当日得分: {user_data['day_score']:.2f}")
    print(f"总得分: {user_data['total_score']:.2f}")
    print(f"当日已记录行为: {user_data['today_behaviors_count']} 个")
    print(f"今日幸运次数: {user_data['lucky_triggers_today']} 次")
    
    # 12. 渐进惊喜系统
    if final_score >= 200:
        print("🎉 恭喜！触发'大师时刻'全屏庆祝！")
    elif final_score >= 100:
        print("✨ 恭喜！触发'高效时刻'特效！")
    elif final_score >= 50:
        print("🌟 恭喜！解锁小成就动画！")
    
    print("========================")

if __name__ == "__main__":
    record_behavior()
