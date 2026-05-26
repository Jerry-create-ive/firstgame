#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态分析器 - 分析和优化游戏状态系统

功能：
1. 分析每个选择对状态的影响
2. 计算达成各结局的难度
3. 生成状态影响热力图
4. 提供平衡建议
"""

import re
from typing import Dict, List, Tuple, Any


class StatsAnalyzer:
    """状态系统分析器"""
    
    def __init__(self):
        self.choices = []
        self.stats = {"relation": 0, "trust": 0, "guilt": 0}
        self.ending_thresholds = {"good": 18, "neutral": 8}
    
    def analyze_script(self, script_path: str = "script.rpy") -> None:
        """分析脚本中的状态变化"""
        import os
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")
        
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取所有选择及其效果
        menu_pattern = r'menu:\s*((?:\s*".*?":\s*\n\s*(?:\$\w+\s*[+-]=\s*\d+\s*\n)*\s*jump\s+\w+\s*\n?)+)'
        matches = re.findall(menu_pattern, content, re.DOTALL)
        
        for match in matches:
            option_pattern = r'"([^"]+)"\s*:\s*\n((?:\s*\$\w+\s*[+-]=\s*\d+\s*\n)*)\s*jump\s+(\w+)'
            options = re.findall(option_pattern, match)
            
            for text, effects_str, next_label in options:
                effects = {}
                
                # 提取状态变化
                effect_pattern = r'\$(\w+)\s*([+-]=)\s*(\d+)'
                effect_matches = re.findall(effect_pattern, effects_str)
                
                for stat, op, value in effect_matches:
                    if stat not in self.stats:
                        self.stats[stat] = 0
                    
                    val = int(value)
                    if op == "+=":
                        effects[stat] = val
                    else:
                        effects[stat] = -val
                
                self.choices.append({
                    "text": text.strip(),
                    "effects": effects,
                    "next": next_label
                })
        
        print(f"✅ 已分析 {len(self.choices)} 个选择")
    
    def calculate_balance(self) -> Dict[str, Any]:
        """计算选择的平衡性"""
        results = {
            "avg_effects": {},
            "max_effects": {},
            "min_effects": {},
            "good_path_difficulty": 0,
            "bad_path_difficulty": 0
        }
        
        for stat in self.stats:
            effects = [c["effects"].get(stat, 0) for c in self.choices]
            results["avg_effects"][stat] = sum(effects) / len(effects) if effects else 0
            results["max_effects"][stat] = max(effects) if effects else 0
            results["min_effects"][stat] = min(effects) if effects else 0
        
        # 计算达成各结局需要的选择数量
        good_choices = [c for c in self.choices if sum(c["effects"].values()) > 0]
        bad_choices = [c for c in self.choices if sum(c["effects"].values()) < 0]
        
        results["good_path_difficulty"] = len(good_choices)
        results["bad_path_difficulty"] = len(bad_choices)
        
        return results
    
    def predict_endings(self, choice_indices: List[int]) -> str:
        """根据选择预测结局"""
        total = 0
        
        for idx in choice_indices:
            if idx < len(self.choices):
                choice = self.choices[idx]
                total += sum(choice["effects"].values())
        
        if total >= self.ending_thresholds["good"]:
            return "good"
        elif total >= self.ending_thresholds["neutral"]:
            return "neutral"
        else:
            return "bad"
    
    def generate_heatmap(self) -> str:
        """生成状态影响热力图"""
        lines = ["状态影响热力图", "=" * 40]
        
        for i, choice in enumerate(self.choices, 1):
            effects = choice["effects"]
            total_effect = sum(effects.values())
            
            # 根据效果值确定颜色
            if total_effect >= 4:
                color = "🟢"
            elif total_effect >= 1:
                color = "🟡"
            elif total_effect >= -2:
                color = "🟠"
            else:
                color = "🔴"
            
            effects_str = ", ".join([f"{k}: {v:+d}" for k, v in effects.items()])
            lines.append(f"{color} 选择{i}: {choice['text'][:30]}... [{effects_str}]")
        
        return "\n".join(lines)
    
    def get_balance_suggestions(self) -> List[str]:
        """获取平衡调整建议"""
        suggestions = []
        balance = self.calculate_balance()
        
        # 检查关系值分布
        if balance["max_effects"].get("relation", 0) > 5:
            suggestions.append("⚠️ 建议降低最大关系值增加量，避免数值膨胀")
        
        if balance["min_effects"].get("relation", 0) < -3:
            suggestions.append("⚠️ 建议减少关系值惩罚，避免玩家受挫")
        
        # 检查愧疚值
        if balance["max_effects"].get("guilt", 0) > 0:
            suggestions.append("⚠️ 愧疚值不应增加，需要检查逻辑")
        
        # 检查结局难度
        if balance["good_path_difficulty"] < 3:
            suggestions.append("⚠️ 完美结局太容易达成，建议增加挑战")
        
        if balance["bad_path_difficulty"] > len(self.choices) // 2:
            suggestions.append("⚠️ 坏结局太容易达成，建议调整选择效果")
        
        if not suggestions:
            suggestions.append("✅ 状态系统平衡良好")
        
        return suggestions


if __name__ == "__main__":
    analyzer = StatsAnalyzer()
    analyzer.analyze_script()
    
    print("📊 状态平衡分析:")
    balance = analyzer.calculate_balance()
    print(f"  • 平均效果: {balance['avg_effects']}")
    print(f"  • 最大效果: {balance['max_effects']}")
    print(f"  • 最小效果: {balance['min_effects']}")
    print(f"  • 好结局难度: 需要 {balance['good_path_difficulty']} 个正向选择")
    print(f"  • 坏结局难度: 需要 {balance['bad_path_difficulty']} 个负向选择")
    
    print("\n" + analyzer.generate_heatmap())
    
    print("\n💡 平衡建议:")
    for suggestion in analyzer.get_balance_suggestions():
        print(f"  {suggestion}")
