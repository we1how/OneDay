from data_manager import load_behaviors, save_behaviors, LEVEL_CONFIG

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
    
    # 保存行为信息
    behaviors[behavior_name] = {
        "name": behavior_name,
        "level": level,
        "category": category,
        "base_score": level_info["base_score"],
        "energy_cost": level_info["energy_cost"],
        "level_weight": level_info["level_weight"],
        "chain_weight": level_info["chain_weight"]
    }
    
    save_behaviors(behaviors)
    
    print(f"\n=== 行为添加成功！ ===")
    print(f"行为名称: {behavior_name}")
    print(f"等级: {level}")
    print(f"类别: {category}")
    print(f"基础得分: {level_info['base_score']}")
    print(f"精力消耗: {level_info['energy_cost']}")
    print(f"等级权重: {level_info['level_weight']}")
    print(f"连锁权重: {level_info['chain_weight']}")
    print("========================")

if __name__ == "__main__":
    add_behavior()
