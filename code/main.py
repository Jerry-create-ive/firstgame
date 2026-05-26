#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太行残雪 - Python 视觉小说游戏

运行方式:
    python main.py

游戏背景:
    1942年5月，华北日军对太行抗日根据地发动大扫荡，
    八路军总部机关被迫向十字岭突围。你将扮演警卫员陈怀安，
    在血与火的考验中做出抉择，书写属于你的战争记忆。

三种结局:
    🏆 完美结局 - 青山永念，忠骨留芳 (总分 ≥ 18)
    🌄 普通结局 - 山河怅惘，心怀惋惜 (总分 8-17)
    💔 遗憾结局 - 半生愧悔，夜夜难眠 (总分 < 8)
"""

import sys
import os

def run_game():
    """运行游戏"""
    from game_engine import create_game
    
    print("""
╔══════════════════════════════════════════════════════╗
║                   太行残雪                           ║
║              十字岭反扫荡 · 1942                    ║
╚══════════════════════════════════════════════════════╝

故事背景:
    1942年5月，华北日军集结数万兵力，对太行抗日根据地
    发动疯狂大「扫荡」。八路军总部机关被迫向十字岭突围，
    你作为左权将军的贴身警卫员，将在这场生死考验中
    做出一个个艰难的抉择...

游戏提示:
    - 按 Enter 键继续对话
    - 在选择时输入数字序号进行选择
    - 你的选择将影响最终结局
    
开始游戏? (Y/N)
    """)
    
    choice = input("> ").strip().upper()
    if choice == "Y":
        game = create_game()
        game.run()
    else:
        print("👋 下次再见！")


def show_help():
    """显示帮助信息"""
    help_text = """
📖 游戏帮助

基本操作:
    - 阅读对话后按 Enter 继续
    - 遇到选择时输入数字序号 (1, 2, 3)
    - 你的选择会影响角色状态和最终结局

状态系统:
    • 人际关系: 帮助战友、保护百姓时增加
    • 信任度:    正确决策、听从命令时增加
    • 愧疚值:    冷漠对待他人、自私选择时增加

结局判定:
    总分 = 人际关系 + 信任度 - 愧疚值
    
    🏆 完美结局: 总分 ≥ 18
    🌄 普通结局: 8 ≤ 总分 < 18  
    💔 遗憾结局: 总分 < 8

文件结构:
    ├── main.py        # 游戏入口
    ├── game_engine.py # 游戏引擎核心
    └── scripts/       # 开发工具目录
        ├── text_extractor.py   # 文本提取器
        ├── story_builder.py    # 剧情构建器
        └── stats_analyzer.py   # 状态分析器

运行方式:
    python main.py     # 启动游戏
    python scripts/text_extractor.py   # 提取对话
    python scripts/stats_analyzer.py   # 分析状态
    """
    print(help_text)


if __name__ == "__main__":
    # 检查参数
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_help()
    else:
        run_game()
