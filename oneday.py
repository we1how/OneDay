# 行为等级定义
grade_levels = {
    "S": {"points_per_15min": 10, "energy_cost": 10},
    "A": {"points_per_15min": 5, "energy_cost": 5},
    "B": {"points_per_15min": 0, "energy_cost": 0},
    "C": {"points_per_15min": -5, "energy_cost": 5},
    "D": {"points_per_15min": -5, "energy_cost": 10}
}

# 行为定义
activities = {
    "reading": {"grade": "A"},
    "play_game": {"grade": "C"},
    "coding": {"grade": "S"}
}

# 初始化变量
total_energy = 100
total_score = 0
per_time = 15  # 每十五分钟结算

print("Welcome to OneDay Program!")
print("Available activities:", list(activities.keys()))
print("Grade levels:", list(grade_levels.keys()))

while True:
    # 请输入你做了什么，以及时长：
    user_activity = input("Please enter what you did: ")
    if user_activity not in activities:
        print("Invalid activity, please try again")
        continue
    
    try:
        activity_duration = int(input("Please enter duration (minutes): "))
    except ValueError:
        print("Please enter a valid number")
        continue
    
    # 获取行为等级
    activity_grade = activities[user_activity]["grade"]
    
    # 计算分数和消耗
    points = grade_levels[activity_grade]["points_per_15min"] * (activity_duration / per_time)
    energy_cost = grade_levels[activity_grade]["energy_cost"] * (activity_duration / per_time)
    
    # 更新总精力值和总分数
    total_energy = total_energy - energy_cost
    total_score = total_score + points
    
    print(f"\nActivity: {user_activity}, Grade: {activity_grade}, Duration: {activity_duration} minutes")
    print(f"Points gained: {points}")
    print(f"Energy consumed: {energy_cost}")
    print(f"Current total energy: {total_energy}")
    print(f"Current total score: {total_score}")
    
    # 询问是否继续
    continue_choice = input("\nContinue? (yes/no): ")
    if continue_choice != "yes":
        break

print("\nProgram ended!")