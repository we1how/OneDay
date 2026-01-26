#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
积分兑换系统模块（V5.0）
实现TimeScore积分兑换系统的核心逻辑，包括新增心愿、兑换心愿等功能
"""

from storage_engine import StorageEngine
from datetime import datetime

class ExchangeSystem:
    """积分兑换系统"""
    
    def __init__(self):
        """初始化积分兑换系统"""
        self.storage = StorageEngine()
        self.MIN_COST = 100  # 心愿积分成本下限
    
    def close(self):
        """关闭数据库连接"""
        self.storage.close()
    
    def show_exchange_menu(self):
        """显示积分兑换主菜单"""
        print("\n" + "="*60)
        print("积分兑换中心")
        print("="*60)
        
        # 获取当前总积分
        total_score = self.storage.get_total_score()
        print(f"当前总积分: {total_score:.1f}")
        
        # 获取待兑换心愿数量
        pending_wishes = self.storage.get_pending_wishes()
        available_count = sum(1 for wish in pending_wishes if total_score >= wish["cost"])
        
        print("\n请选择操作：")
        print("1. 新增心愿")
        print(f"2. 兑换心愿 (可用: {available_count})")
        print("0. 返回主菜单")
        
        return input("请输入选项编号: ")
    
    def add_wish(self):
        """新增心愿"""
        print("\n" + "="*60)
        print("新增心愿")
        print("="*60)
        
        # 获取当前总积分，用于AI建议
        total_score = self.storage.get_total_score()
        
        # 获取心愿名称
        while True:
            name = input("请输入心愿名称（限50字）: ").strip()
            if name and len(name) <= 50:
                break
            print("心愿名称不能为空且不能超过50字，请重新输入！")
        
        # 获取所需积分
        while True:
            cost_input = input(f"请输入所需积分（最小值: {self.MIN_COST}）: ").strip()
            try:
                cost = int(cost_input)
                if cost >= self.MIN_COST:
                    break
                print(f"所需积分不能低于{self.MIN_COST}，请重新输入！")
            except ValueError:
                print("请输入有效的整数！")
        
        # AI成本建议
        average_daily_score = self._calculate_average_daily_score()
        if average_daily_score > 0:
            suggested_cost = int(average_daily_score * 30)  # 建议30天的积分
            print(f"\n💡 AI建议：基于您的日均积分（{average_daily_score:.1f}），建议心愿积分设置在 {suggested_cost} - {suggested_cost * 10} 之间")
        
        # 确认添加
        confirm = input(f"\n确认添加心愿「{name}」，所需积分：{cost}？(y/n): ").strip().lower()
        if confirm != "y":
            print("\n已取消添加心愿")
            return
        
        # 添加心愿到数据库
        wish_id = self.storage.add_wish(name, cost)
        if wish_id:
            print(f"\n✅ 心愿添加成功！ID: {wish_id}")
            self._show_wish_details(wish_id)
        else:
            print("\n❌ 心愿添加失败，请重试！")
    
    def redeem_wish(self):
        """兑换心愿"""
        print("\n" + "="*60)
        print("兑换心愿")
        print("="*60)
        
        # 获取当前总积分
        total_score = self.storage.get_total_score()
        
        # 获取待兑换心愿
        pending_wishes = self.storage.get_pending_wishes()
        
        if not pending_wishes:
            print("\n您还没有添加任何心愿，请先添加心愿！")
            return
        
        # 更新所有心愿的进度
        self.storage.update_all_wishes_progress(total_score)
        
        # 重新获取更新后的心愿
        pending_wishes = self.storage.get_pending_wishes()
        
        # 显示心愿列表
        print("\n心愿列表：")
        print("-"*60)
        for wish in pending_wishes:
            # 生成进度条
            progress = min(1.0, wish["progress"])
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = "■" * filled_length + "□" * (bar_length - filled_length)
            
            # 计算进度百分比
            progress_percent = progress * 100
            
            # 积分是否足够
            if total_score >= wish["cost"]:
                status = "✓ 积分够"
            else:
                status = f"✗ 需{wish['cost'] - total_score:.1f}积分"
            
            print(f"{wish['id']}. {wish['name']} - {wish['cost']}分 [{bar}] {progress_percent:.0f}% {status}")
        
        # 选择要兑换的心愿
        while True:
            wish_id_input = input("\n请输入要兑换的心愿ID（0返回）: ").strip()
            if wish_id_input == "0":
                return
            
            try:
                wish_id = int(wish_id_input)
                # 检查心愿是否存在
                wish = self.storage.get_wish_by_id(wish_id)
                if wish:
                    break
                print("无效的心愿ID，请重新输入！")
            except ValueError:
                print("请输入有效的整数！")
        
        # 检查积分是否足够
        if total_score < wish["cost"]:
            print(f"\n❌ 积分不足！需要 {wish['cost']} 积分，当前只有 {total_score:.1f} 积分")
            print("继续努力积累积分吧！")
            return
        
        # 确认兑换
        confirm = input(f"\n确认兑换心愿「{wish['name']}」，消耗 {wish['cost']} 积分？(y/n): ").strip().lower()
        if confirm != "y":
            print("\n已取消兑换")
            return
        
        # 执行兑换
        if self.storage.redeem_wish(wish_id):
            # 兑换成功，触发庆祝
            print("\n🎉 兑换成功！")
            print(f"恭喜您实现了心愿：{wish['name']}")
            print(f"剩余积分: {total_score - wish['cost']:.1f}")
            print("\n✨ 继续努力积累积分，实现更多心愿吧！")
        else:
            print("\n❌ 兑换失败，请重试！")
    
    def _calculate_average_daily_score(self):
        """计算日均积分"""
        # 获取所有行为记录
        # 注意：这里简化处理，实际应该按天统计
        # 由于当前storage_engine没有提供按天统计的方法，我们只返回0
        return 0
    
    def _show_wish_details(self, wish_id):
        """显示心愿详情"""
        wish = self.storage.get_wish_by_id(wish_id)
        if wish:
            print(f"\n心愿详情：")
            print(f"ID: {wish['id']}")
            print(f"名称: {wish['name']}")
            print(f"所需积分: {wish['cost']}")
            print(f"状态: {wish['status']}")
            print(f"创建时间: {datetime.fromtimestamp(wish['created_at']).strftime('%Y-%m-%d %H:%M:%S')}")
    
    def run(self):
        """运行积分兑换系统"""
        while True:
            choice = self.show_exchange_menu()
            
            if choice == "1":
                self.add_wish()
            elif choice == "2":
                self.redeem_wish()
            elif choice == "0":
                break
            else:
                print("无效的选项，请重新输入！")

# 测试代码
if __name__ == "__main__":
    exchange = ExchangeSystem()
    exchange.run()
    exchange.close()