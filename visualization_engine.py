#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化引擎模块
根据TimeScore V4.0可视化系统文档实现CLI可视化功能
包含仪表盘、时间轴、热力图、分布图和RPG元素
"""

from termcolor import colored
from datetime import datetime, timedelta
import json
from storage_engine import StorageEngine

class VisualizationEngine:
    """可视化引擎类，负责生成各种CLI可视化输出"""
    
    def __init__(self):
        """初始化可视化引擎"""
        self.storage = StorageEngine()
    
    def close(self):
        """关闭数据库连接"""
        self.storage.close()
    
    def get_star_rating(self, mood):
        """根据心情值生成星级评分"""
        full_star = "★"
        empty_star = "☆"
        return full_star * mood + empty_star * (5 - mood)
    
    def generate_dashboard(self, user_data, today_records):
        """生成仪表盘概览"""
        print("\n" + "="*50)
        print(colored("仪表盘概览", "cyan", attrs=["bold"]))
        print("="*50)
        
        # 计算当日总积分
        today_total_score = sum(record["final_score"] for record in today_records)
        
        # 计算平均心情
        if today_records:
            avg_mood = sum(record["mood"] for record in today_records) / len(today_records)
            avg_mood = round(avg_mood)
        else:
            avg_mood = 3
        
        # 计算效率比（如果有精力消耗数据）
        total_energy_cost = sum(abs(record["energy_consume"]) for record in today_records)
        if total_energy_cost > 0:
            efficiency = today_total_score / total_energy_cost
        else:
            efficiency = 0
        
        # 显示仪表盘卡片
        print("┌──────────────┐ ┌──────────────┐")
        print(f"│总积分: {today_total_score:.1f} │ │效率: {efficiency:.1f}/点 │")
        print("└──────────────┘ └──────────────┘")
        print("┌──────────────┐ ┌──────────────┐")
        print(f"│连击: {user_data['combo_count']}次  │ │心情: {self.get_star_rating(avg_mood)} │")
        print("└──────────────┘ └──────────────┘")
    
    def generate_timeline(self, records):
        """生成多维时间轴"""
        print("\n" + "="*50)
        print(colored("时间轴", "cyan", attrs=["bold"]))
        print("="*50)
        
        if not records:
            print("今日暂无行为记录")
            return
        
        # 按时间排序
        sorted_records = sorted(records, key=lambda x: x["start_ts"])
        
        for record in sorted_records:
            # 格式化时间
            start_time = datetime.fromtimestamp(record["start_ts"]).strftime("%H:%M")
            end_time = datetime.fromtimestamp(record["end_ts"]).strftime("%H:%M")
            
            # 等级颜色
            level_color_map = {
                "S": "green",
                "A": "blue",
                "B": "yellow",
                "C": "magenta",
                "D": "red",
                "R": "cyan"
            }
            level_color = level_color_map.get(record["level"], "white")
            
            # 生成进度条
            bar_length = min(20, int(record["duration"] / 5))  # 每5分钟一个字符
            bar = "■" * bar_length
            
            # 生成星级
            star_rating = self.get_star_rating(record["mood"])
            
            # 显示记录
            print(f"{start_time}-{end_time} [{colored(bar, level_color)}] {record['level']}级 "
                  f"积分:{record['final_score']:.0f} 精力:{record['energy_consume']:+.1f} "
                  f"心情:{star_rating}")
    
    def generate_heatmap(self, days=30):
        """生成热力图"""
        print("\n" + "="*50)
        print(colored("热力图", "cyan", attrs=["bold"]))
        print("="*50)
        
        # 获取过去days天的日期
        today = datetime.now().date()
        dates = [today - timedelta(days=i) for i in range(days-1, -1, -1)]
        
        # 获取每日总积分
        daily_scores = {}
        for date in dates:
            # 计算当天的时间戳范围
            start_ts = int(datetime.combine(date, datetime.min.time()).timestamp())
            end_ts = int(datetime.combine(date, datetime.max.time()).timestamp())
            
            # 查询当天的所有记录
            self.storage.cursor.execute(
                "SELECT SUM(final_score) FROM core_behavior WHERE start_ts BETWEEN ? AND ?",
                (start_ts, end_ts)
            )
            result = self.storage.cursor.fetchone()[0]
            daily_scores[date] = result or 0
        
        # 显示月份
        print(f"{today.strftime('%b %Y')}")
        print("S M T W T F S")
        
        # 生成热力图网格
        week = []
        for date in dates:
            day = date.day
            score = daily_scores[date]
            
            # 根据分数确定颜色
            if score < 50:
                color = "red"
                char = "□"
            elif score < 100:
                color = "yellow"
                char = "■"
            elif score < 200:
                color = "green"
                char = "■"
            else:
                color = "green"
                char = "■■"
            
            week.append(colored(f"{day:2d}{char}", color))
            
            # 每周换行
            if date.weekday() == 6:  # 周日
                print(" ".join(week))
                week = []
        
        # 打印剩余的
        if week:
            print(" ".join(week))
    
    def generate_distribution(self, records):
        """生成数据洞察/分布图"""
        print("\n" + "="*50)
        print(colored("数据洞察/分布图", "cyan", attrs=["bold"]))
        print("="*50)
        
        if not records:
            print("暂无数据可分析")
            return
        
        # 等级分布
        level_counts = {}
        total_records = len(records)
        
        for record in records:
            level = record["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print("等级分布:")
        for level in sorted(level_counts.keys()):
            count = level_counts[level]
            percentage = (count / total_records) * 100
            bar_length = int(percentage / 5)  # 每5%一个字符
            bar = "■" * bar_length
            print(f"{level}: {bar} ({percentage:.1f}%)")
        
        # 周趋势（简化版）
        print("\n周趋势:")
        # 这里简化处理，只显示当日数据
        today_total = sum(record["final_score"] for record in records)
        print(f"今日: {today_total:.0f}分")
    
    def generate_rpg_elements(self, user_data, total_score):
        """生成RPG/游戏化反馈"""
        print("\n" + "="*50)
        print(colored("RPG元素", "cyan", attrs=["bold"]))
        print("="*50)
        
        # 计算等级（每1000分升一级）
        level = int(total_score / 1000) + 1
        xp = total_score % 1000
        
        # 生成XP进度条
        xp_bar_length = 8
        filled_bars = int((xp / 1000) * xp_bar_length)
        xp_bar = "■" * filled_bars + "□" * (xp_bar_length - filled_bars)
        
        # 计算属性
        # 专注：基于S/A比例
        if user_data['today_behaviors_count'] > 0:
            positive_behaviors = sum(1 for record in user_data['behavior_day_list'] 
                                   if record['level'] in ['S', 'A'])
            focus_level = min(5, int((positive_behaviors / user_data['today_behaviors_count']) * 5) + 1)
        else:
            focus_level = 1
        
        # 恢复：基于R级使用
        recovery_count = sum(1 for record in user_data['behavior_day_list'] 
                           if record['level'] == 'R')
        recovery_level = min(5, recovery_count + 1)
        
        # 耐力：基于精力剩余
        endurance_level = min(5, int(user_data['day_energy'] / 20) + 1)
        
        # 显示RPG信息
        print(f"角色: 时间大师 Lv.{level}")
        print(f"XP: [{xp_bar}] {xp}/1000")
        print("属性:")
        print(f"- 专注: Lv.{focus_level} ({'■' * focus_level})")
        print(f"- 恢复: Lv.{recovery_level} ({'■' * recovery_level})")
        print(f"- 耐力: Lv.{endurance_level} ({'■' * endurance_level})")
        
        # 装备（基于连击数）
        if user_data['combo_count'] >= 3:
            print("装备: 连击剑 (解锁于3连击)")
        elif user_data['combo_count'] >= 1:
            print("装备: 入门装备")
        else:
            print("装备: 无")
    
    def generate_behavior_visualization(self, behavior_record):
        """生成单次行为的可视化反馈"""
        print("\n" + "="*50)
        print(colored("行为可视化", "cyan", attrs=["bold"]))
        print("="*50)
        
        # 等级颜色
        level_color_map = {
            "S": "green",
            "A": "blue",
            "B": "yellow",
            "C": "magenta",
            "D": "red",
            "R": "cyan"
        }
        level_color = level_color_map.get(behavior_record["level"], "white")
        
        # 显示行为基本信息
        print(f"行为等级: {colored(behavior_record['level'], level_color)}")
        print(f"持续时长: {behavior_record['duration']}分钟")
        print(f"心情评分: {self.get_star_rating(behavior_record['mood'])}")
        print(f"最终得分: {behavior_record['final_score']:.2f}")
        print(f"精力变化: {behavior_record['energy_consume']:+.1f}")
        
        # 生成进度条
        max_score = 200  # 假设最大得分为200
        bar_length = min(30, int((behavior_record['final_score'] / max_score) * 30))
        bar = "■" * bar_length + "□" * (30 - bar_length)
        
        print(f"\n得分进度: [{colored(bar, level_color)}] {behavior_record['final_score']:.0f}/{max_score}")
        
        # 生成AI洞察（简单规则）
        if behavior_record['final_score'] >= 100:
            print("\n💡 AI洞察: 高效的行为！继续保持这个状态。")
        elif behavior_record['final_score'] >= 50:
            print("\n💡 AI洞察: 良好的表现，继续努力。")
        elif behavior_record['final_score'] < 0:
            print("\n💡 AI洞察: 建议调整行为，恢复精力。")
    
    def show_historical_review(self):
        """显示历史回顾系统"""
        print("\n" + "="*60)
        print(colored("历史回顾系统", "cyan", attrs=["bold", "underline"]))
        print("="*60)
        
        # 加载用户数据
        user_data = {
            "combo_count": self.storage.get_user_state()["combo_count"],
            "day_energy": self.storage.get_user_state()["current_energy"],
            "today_behaviors_count": self.storage.get_user_state()["today_behavior_count"],
            "behavior_day_list": self.storage.get_today_records()
        }
        
        # 获取今日记录
        today_records = self.storage.get_today_records()
        
        # 获取总得分
        total_score = self.storage.get_total_score()
        
        # 显示完整视图
        self.generate_dashboard(user_data, today_records)
        self.generate_timeline(today_records)
        self.generate_heatmap()
        self.generate_distribution(today_records)
        self.generate_rpg_elements(user_data, total_score)
        
        print("\n" + "="*60)
        print("历史回顾完成")
        print("="*60)
    
    def show_behavior_feedback(self, behavior_record):
        """显示单次行为的反馈"""
        self.generate_behavior_visualization(behavior_record)
    
    def generate_summary_json(self, user_data, records):
        """生成总结JSON"""
        today_total_score = sum(record["final_score"] for record in records)
        
        if records:
            avg_mood = sum(record["mood"] for record in records) / len(records)
            avg_mood = round(avg_mood)
        else:
            avg_mood = 3
        
        summary = {
            "today_total_score": today_total_score,
            "combo_count": user_data["combo_count"],
            "avg_mood": avg_mood,
            "behavior_count": len(records),
            "current_energy": user_data["day_energy"]
        }
        
        return json.dumps(summary, ensure_ascii=False, indent=2)
