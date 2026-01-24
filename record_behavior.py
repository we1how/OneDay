from data_manager import (
    load_behaviors, load_user_data, save_user_data,
    reset_daily_data_if_needed, calculate_energy_recovery,
    LEVEL_CONFIG, MOOD_CONFIG, GLOBAL_CONFIG
)
from scoring_engine import ScoringEngine
from datetime import datetime
from visualization_engine import VisualizationEngine

def record_behavior():
    """记录行为界面（V3.0精力管理版本）"""
    print("=== 记录行为界面（V3.0精力管理版本） ===")
    
    # 加载行为和用户数据
    behaviors = load_behaviors()
    user_data = load_user_data()
    
    # 重置当日数据（如果需要）
    user_data = reset_daily_data_if_needed(user_data)
    
    # 计算精力恢复
    if user_data["last_record_time"]:
        recovery_energy = calculate_energy_recovery(user_data["last_record_time"])
        user_data["day_energy"] = min(GLOBAL_CONFIG["energy_max"], user_data["day_energy"] + recovery_energy)
    
    # 用户输入：行为等级
    while True:
        level = input("请输入行为等级（S/A/B/C/D/R）: ").upper()
        # 检查是否为有效等级或R级子级
        if level in LEVEL_CONFIG or (level.startswith("R") and level in ["R", "R1", "R2", "R3"]):
            break
        print("无效的等级，请重新输入！")
    
    # 从行为列表中选择该等级的行为
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
    
    # 初始化得分计算引擎
    scoring_engine = ScoringEngine(user_data)
    
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
    
    # 用户输入：心情（1-5星，默认3星）
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
    
    # 可选详细记录
    detailed_recording = input("是否添加详细记录？(y/n，默认n): ").strip().lower()
    
    specific_time = ""
    feeling = ""
    
    if detailed_recording == "y":
        # 具体时段
        specific_time = input("请输入具体时段（如：上午9:00-10:00，可选）: ").strip()
        
        # 当时的感受
        feeling = input("请输入当时的感受（如：感觉放松但分心，可选）: ").strip()
        
        # 如果没有输入感受，从心情推测
        if not feeling:
            mood_to_feeling = {
                1: "感觉疲惫",
                2: "感觉一般",
                3: "感觉正常",
                4: "感觉不错",
                5: "感觉很好"
            }
            feeling = mood_to_feeling[mood]
    
    # 获取当前精力
    current_energy = user_data["day_energy"]
    
    # 获取行为信息，处理R级子级推测
    behavior_info = scoring_engine.get_behavior_info(level, duration, mood)
    
    # 计算精力消耗/恢复
    energy_cost_details = scoring_engine.calculate_energy_cost(behavior_info, level, duration, current_energy)
    final_energy_cost = energy_cost_details["final_energy_cost"]
    is_recovery = energy_cost_details["is_recovery"]
    
    # 计算得分
    score_details = scoring_engine.calculate_score(behavior_info, level, duration, mood, current_energy)
    
    # 应用防滥用与平衡机制
    
    # 计算同一行为重复次数
    same_behavior_count = sum(1 for b in user_data["behavior_day_list"] if b["name"] == selected_behavior)
    
    # 检查是否为短时长高频
    is_short_frequency = False
    if user_data["last_record_time"]:
        last_time = datetime.fromisoformat(user_data["last_record_time"])
        current_time = datetime.now()
        time_diff = (current_time - last_time).total_seconds() / 60
        if time_diff < 10:
            is_short_frequency = True
    
    # 应用平衡机制
    score_details = scoring_engine.apply_balance_mechanisms(score_details, same_behavior_count, is_short_frequency, level)
    final_score = score_details["final_score"]
    
    # 生成行为记录
    behavior_record = scoring_engine.generate_behavior_record(
        selected_behavior, behavior_info, level, duration, mood, score_details, specific_time, feeling
    )
    behavior_record["energy_cost"] = final_energy_cost
    behavior_record["is_recovery"] = is_recovery
    
    # 更新用户数据
    user_data = scoring_engine.update_user_data(
        user_data, behavior_record, energy_cost_details, current_energy
    )
    
    # 保存用户数据
    save_user_data(user_data)
    
    # 显示结果
    combo_result = score_details["combo_result"]
    
    print(f"\n=== 行为记录成功！ ===")
    print(f"行为名称: {selected_behavior}")
    print(f"行为等级: {level}")
    print(f"时长: {duration} 分钟")
    print(f"心情: {mood}星 {MOOD_CONFIG[mood]['text']}")
    
    # 显示详细记录（如果有）
    if specific_time:
        print(f"具体时段: {specific_time}")
    if feeling:
        print(f"当时的感受: {feeling}")
    
    if level.startswith("R"):
        print(f"推测子级: {behavior_info['inferred_sublevel']}")
        print(f"心理锚点: {behavior_info['mental_anchor']}")
    else:
        # 从行为列表中获取类别
        behavior_category = behaviors[selected_behavior].get("category", "未分类")
        print(f"行为类别: {behavior_category}")
    
    print(f"\n=== 得分详情 ===")
    print(f"基础分: {score_details['base_score']:.2f} (等级基础分: {behavior_info['base_score_per_min']}/分钟)")
    print(f"动态系数: {score_details['dynamic_coefficient']:.2f}")
    print(f"  ├ 精力系数: {score_details['energy_coefficient']:.2f} (记录前精力: {current_energy:.1f})")
    print(f"  └ 连击系数: {score_details['combo_coefficient']:.2f} (连击: {combo_result['combo_count']})")
    print(f"开始奖励: {score_details['start_bonus_score']:.2f}")
    print(f"新手奖励: {score_details['novice_bonus']:.2f}")
    print(f"最终得分: {final_score:.2f}")
    
    print(f"\n=== 精力变化 ===")
    if is_recovery:
        print(f"基础恢复: {abs(energy_cost_details['base_energy_cost']):.2f} (等级恢复: {abs(behavior_info['energy_cost_per_min'])}/分钟)")
        print(f"最终恢复: {abs(final_energy_cost):.2f}")
        print(f"精力变化: +{abs(final_energy_cost):.2f}")
    else:
        print(f"基础消耗: {energy_cost_details['base_energy_cost']:.2f} (等级消耗: {behavior_info['energy_cost_per_min']}/分钟)")
        print(f"开始奖励: {energy_cost_details['start_bonus_energy']:.2f}")
        print(f"最终消耗: {final_energy_cost:.2f}")
        print(f"精力变化: -{final_energy_cost:.2f}")
    
    print(f"\n=== 当前状态 ===")
    print(f"当日剩余精力: {user_data['day_energy']:.1f}")
    print(f"当日得分: {user_data['day_score']:.2f}")
    print(f"总得分: {user_data['total_score']:.2f}")
    print(f"当日已记录行为: {user_data['today_behaviors_count']} 个")
    
    # 渐进惊喜系统
    if final_score >= 200:
        print("🎉 恭喜！触发'大师时刻'全屏庆祝！")
    elif final_score >= 100:
        print("✨ 恭喜！触发'高效时刻'特效！")
    elif final_score >= 50:
        print("🌟 恭喜！解锁小成就动画！")
    
    print("========================")
    
    # 生成行为可视化
    viz_engine = VisualizationEngine()
    viz_engine.show_behavior_feedback({
        "level": level,
        "duration": duration,
        "mood": mood,
        "final_score": final_score,
        "energy_consume": final_energy_cost
    })
    viz_engine.close()

if __name__ == "__main__":
    record_behavior()
