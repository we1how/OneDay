from data_manager import load_behaviors, LEVEL_CONFIG, add_behavior_to_db

def add_behavior():
    """增加行为界面"""
    print("=== 增加行为界面 ===")
    
    # 加载现有行为
    behaviors = load_behaviors()
    
    # 输入行为等级
    while True:
        level = input("请输入行为习惯等级（S/A/B/C/D）: ").upper()
        if level in LEVEL_CONFIG:
            break
        print("无效的等级，请重新输入！")
    
    # 输入行为名称
    while True:
        behavior_name = input("请输入行为习惯名称: ").strip()
        if not behavior_name:
            print("行为名称不能为空，请重新输入！")
            continue
        if behavior_name in behaviors:
            print("该行为已存在，请重新输入！")
            continue
        break
    
    # 输入行为类别（可选）
    category = input("请输入行为类别（可选）: ").strip() or "未分类"
    
    # 自动填充等级相关信息
    level_info = LEVEL_CONFIG[level]
    
    # 保存行为信息到数据库
    success = add_behavior_to_db(
        behavior_name, level, category,
        level_info["base_score_per_min"], level_info["energy_cost_per_min"]
    )
    
    if success:
        print(f"\n=== 行为添加成功！ ===")
        print(f"行为名称: {behavior_name}")
        print(f"等级: {level}")
        print(f"类别: {category}")
        print(f"基础得分/分钟: {level_info['base_score_per_min']}")
        print(f"精力消耗/分钟: {level_info['energy_cost_per_min']}")
        print(f"心理锚点: {level_info['mental_anchor']}")
        print(f"适用行为举例: {level_info['example']}")
        print("========================")
    else:
        print(f"\n=== 行为添加失败！ ===")
        print("该行为可能已存在或数据库操作失败。")
        print("========================")

if __name__ == "__main__":
    add_behavior()
