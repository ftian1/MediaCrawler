#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
断点续传功能演示脚本
Checkpoint Resume Feature Demo Script

This script demonstrates how to use the checkpoint functionality.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.checkpoint import CheckpointManager


def demo_basic_usage():
    """基本使用演示"""
    print("=" * 60)
    print("断点续传功能演示 - 基本使用")
    print("Checkpoint Resume Demo - Basic Usage")
    print("=" * 60)
    
    # 创建checkpoint管理器
    manager = CheckpointManager("demo_checkpoint.json")
    
    # 1. 保存checkpoint
    print("\n1. 保存checkpoint...")
    manager.save_checkpoint(
        platform="xhs",
        crawler_type="search",
        keyword="Python教程",
        last_page=5,
        last_item_id="note_abc123"
    )
    print("   ✅ Checkpoint已保存")
    
    # 2. 加载checkpoint
    print("\n2. 加载checkpoint...")
    checkpoint = manager.load_checkpoint(
        platform="xhs",
        crawler_type="search",
        keyword="Python教程"
    )
    if checkpoint:
        print(f"   ✅ 找到checkpoint:")
        print(f"      - 平台: {checkpoint['platform']}")
        print(f"      - 关键词: {checkpoint['keyword']}")
        print(f"      - 最后页码: {checkpoint['last_page']}")
        print(f"      - 最后内容ID: {checkpoint['last_item_id']}")
    
    # 3. 清除checkpoint
    print("\n3. 清除checkpoint...")
    manager.clear_checkpoint(
        platform="xhs",
        crawler_type="search",
        keyword="Python教程"
    )
    print("   ✅ Checkpoint已清除")
    
    # 清理演示文件
    manager.clear_all_checkpoints()
    print("\n✅ 演示完成!\n")


def demo_multiple_keywords():
    """多关键词管理演示"""
    print("=" * 60)
    print("断点续传功能演示 - 多关键词管理")
    print("Checkpoint Resume Demo - Multiple Keywords")
    print("=" * 60)
    
    manager = CheckpointManager("demo_checkpoint.json")
    
    # 模拟多个关键词的爬取
    keywords = ["Python", "Java", "JavaScript", "Golang"]
    
    print("\n1. 保存多个关键词的checkpoint...")
    for i, keyword in enumerate(keywords, 1):
        manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword=keyword,
            last_page=i * 2,
            last_item_id=f"note_{keyword.lower()}_{i}"
        )
        print(f"   ✅ 保存: {keyword} (页码: {i * 2})")
    
    print("\n2. 查看所有checkpoint...")
    for keyword in keywords:
        checkpoint = manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword=keyword
        )
        if checkpoint:
            print(f"   📍 {keyword}: 页码={checkpoint['last_page']}, "
                  f"ID={checkpoint['last_item_id']}")
    
    print("\n3. 清除特定checkpoint...")
    manager.clear_checkpoint(
        platform="xhs",
        crawler_type="search",
        keyword="Java"
    )
    print("   ✅ 已清除: Java")
    
    print("\n4. 验证清除结果...")
    checkpoint = manager.load_checkpoint(
        platform="xhs",
        crawler_type="search",
        keyword="Java"
    )
    if checkpoint is None:
        print("   ✅ Java checkpoint已不存在")
    
    # 清理演示文件
    manager.clear_all_checkpoints()
    print("\n✅ 演示完成!\n")


def demo_resume_simulation():
    """模拟中断恢复场景"""
    print("=" * 60)
    print("断点续传功能演示 - 中断恢复模拟")
    print("Checkpoint Resume Demo - Resume Simulation")
    print("=" * 60)
    
    manager = CheckpointManager("demo_checkpoint.json")
    
    # 模拟爬取过程
    print("\n场景: 爬取'AI开发'关键词，目标100页")
    print("Scenario: Crawling 'AI开发' keyword, target 100 pages")
    
    # 第一次运行 - 爬到第30页时中断
    print("\n第一次运行 (Run 1):")
    print("  开始页: 1")
    print("  当前页: 1 -> 10 -> 20 -> 30")
    print("  ⚠️  在第30页时程序中断...")
    
    # 保存checkpoint
    manager.save_checkpoint(
        platform="xhs",
        crawler_type="search",
        keyword="AI开发",
        last_page=31,  # 下次从31页开始
        last_item_id="note_ai_030"
    )
    print("  ✅ Checkpoint已保存 (next_page: 31)")
    
    # 第二次运行 - 从checkpoint恢复
    print("\n第二次运行 (Run 2):")
    checkpoint = manager.load_checkpoint(
        platform="xhs",
        crawler_type="search",
        keyword="AI开发"
    )
    
    if checkpoint:
        resume_page = checkpoint['last_page']
        print(f"  ✅ 检测到checkpoint，从第{resume_page}页继续")
        print(f"  当前页: {resume_page} -> 40 -> 50 -> 60")
        print("  ⚠️  在第60页时再次中断...")
        
        # 更新checkpoint
        manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="AI开发",
            last_page=61,
            last_item_id="note_ai_060"
        )
        print("  ✅ Checkpoint已更新 (next_page: 61)")
    
    # 第三次运行 - 完成剩余部分
    print("\n第三次运行 (Run 3):")
    checkpoint = manager.load_checkpoint(
        platform="xhs",
        crawler_type="search",
        keyword="AI开发"
    )
    
    if checkpoint:
        resume_page = checkpoint['last_page']
        print(f"  ✅ 从第{resume_page}页继续")
        print(f"  当前页: {resume_page} -> 70 -> 80 -> 90 -> 100")
        print("  ✅ 爬取完成!")
        
        # 完成后清除checkpoint
        manager.clear_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="AI开发"
        )
        print("  ✅ Checkpoint已自动清除")
    
    # 清理演示文件
    manager.clear_all_checkpoints()
    print("\n✅ 演示完成!\n")
    
    print("总结:")
    print("  - 中断2次，共运行3次")
    print("  - 每次从上次中断位置继续")
    print("  - 完成后自动清除checkpoint")
    print("  - 避免了重复爬取1-60页的数据")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print(" MediaCrawler 断点续传功能演示")
    print(" Checkpoint Resume Feature Demo")
    print("=" * 60 + "\n")
    
    demos = [
        ("1", "基本使用", demo_basic_usage),
        ("2", "多关键词管理", demo_multiple_keywords),
        ("3", "中断恢复模拟", demo_resume_simulation),
        ("4", "运行全部演示", None),
        ("0", "退出", None),
    ]
    
    while True:
        print("\n请选择演示:")
        print("Please select a demo:")
        for num, desc, _ in demos:
            print(f"  {num}. {desc}")
        
        choice = input("\n请输入选项 (Enter choice): ").strip()
        
        if choice == "0":
            print("\n再见! Goodbye!\n")
            break
        elif choice == "1":
            demo_basic_usage()
        elif choice == "2":
            demo_multiple_keywords()
        elif choice == "3":
            demo_resume_simulation()
        elif choice == "4":
            demo_basic_usage()
            demo_multiple_keywords()
            demo_resume_simulation()
        else:
            print("\n❌ 无效选项，请重新选择")
            print("Invalid choice, please try again")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  演示已取消")
        print("Demo cancelled")
        # 清理可能存在的演示文件
        try:
            if os.path.exists("demo_checkpoint.json"):
                os.remove("demo_checkpoint.json")
        except:
            pass
