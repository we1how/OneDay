from add_behavior import add_behavior
from record_behavior import record_behavior
from visualization_engine import VisualizationEngine

def main():
    """主程序入口"""
    print("=== Welcome to OneDay 时间管理系统 ===")
    
    while True:
        print("\n请选择要进入的界面：")
        print("1. 增加行为界面")
        print("2. 记录行为界面")
        print("3. 历史回顾系统")
        print("4. 退出系统")
        
        choice = input("请输入选项编号（1-4）: ")
        
        if choice == "1":
            print()
            add_behavior()
        elif choice == "2":
            print()
            record_behavior()
        elif choice == "3":
            print()
            # 显示历史回顾系统
            viz_engine = VisualizationEngine()
            viz_engine.show_historical_review()
            viz_engine.close()
        elif choice == "4":
            print("\n=== 感谢使用 OneDay 时间管理系统！ ===")
            break
        else:
            print("无效的选项，请重新输入！")

if __name__ == "__main__":
    main()
