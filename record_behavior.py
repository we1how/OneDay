from data_manager import (
    load_behaviors, load_user_data, save_user_data,
    LEVEL_CONFIG, GLOBAL_CONFIG, reset_daily_data_if_needed
)
from datetime import datetime

def record_behavior():
    """记录行为界面"""
    print("=== 记录行为界面 ===")
    
    # 加载行为和用户数据
    behaviors = load_behaviors()
    user_data = load_user_data()
    
    # 重置当日数据（如果需要）
    user_data = reset_daily_data_if_needed(user_data)
    
    # 如果没有行为，提示用户先添加行为
    if not behaviors:
        print("当前没有任何行为，请先使用增加行为功能添加行为！")
        return
    
    # 输入等级
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
    
    # 输入行为时长
    while True:
        try:
            duration = int(input("请输入行为时长（分钟）: "))
            if duration <= 0:
                print("时长必须大于0，请重新输入！")
                continue
            break
        except ValueError:
            print("无效的输入，请输入数字！")
    
    # 获取行为信息
    behavior_info = level_behaviors[selected_behavior]
    
    # 计算得分和精力消耗
    # 得分公式 = 基础得分 / per_time * 时长
    score = (behavior_info["base_score"] / GLOBAL_CONFIG["per_time"]) * duration
    energy_cost = (behavior_info["energy_cost"] / GLOBAL_CONFIG["per_time"]) * duration
    
    # 更新用户数据
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 创建行为记录
    behavior_record = {
        "name": selected_behavior,
        "level": level,
        "category": behavior_info["category"],
        "start_time": current_time,
        "end_time": current_time,  # 简化处理，仅记录当前时间
        "date": today,
        "behavior_score": score,
        "mood_score": 0,  # 暂时默认为0
        "duration": duration,
        "energy_cost": energy_cost
    }
    
    # 更新用户数据
    user_data["behavior_list"].append(behavior_record)
    user_data["behavior_day_list"].append(behavior_record)
    user_data["total_score"] += score
    user_data["day_score"] += score
    user_data["day_energy"] -= energy_cost
    user_data["day_energy_cost"] += energy_cost
    
    # 保存用户数据
    save_user_data(user_data)
    
    # 显示结果
    print(f"\n=== 行为记录成功！ ===")
    print(f"行为名称: {selected_behavior}")
    print(f"等级: {level}")
    print(f"时长: {duration} 分钟")
    print(f"获得得分: {score:.2f}")
    print(f"消耗精力: {energy_cost:.2f}")
    print(f"\n当前状态：")
    print(f"总得分: {user_data['total_score']:.2f}")
    print(f"当日得分: {user_data['day_score']:.2f}")
    print(f"当日剩余精力: {user_data['day_energy']:.2f}")
    print(f"总精力: {user_data['total_energy']:.2f}")
    print("========================")

if __name__ == "__main__":
    record_behavior()
