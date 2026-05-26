#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剧情文本提取器 - 从 script.rpy 中提取对话文本

功能：
1. 提取所有对话文本
2. 提取角色名称
3. 提取选择分支
4. 导出为 JSON/CSV 格式
5. 支持翻译工作流
"""

import re
import json
import csv
import os
from typing import Dict, List, Tuple, Any


class TextExtractor:
    """剧情文本提取器"""
    
    def __init__(self, script_path: str = "script.rpy"):
        self.script_path = script_path
        self.dialogues = []
        self.choices = []
        self.characters = set()
        self.labels = []
    
    def extract(self) -> None:
        """提取所有文本数据"""
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"脚本文件不存在: {self.script_path}")
        
        with open(self.script_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        current_label = None
        current_character = None
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 提取标签
            if line.startswith("label "):
                match = re.match(r"label (\w+):", line)
                if match:
                    current_label = match.group(1)
                    self.labels.append({"name": current_label, "line": i})
                    current_character = None
                continue
            
            # 提取角色对话（带引号）
            if line.startswith('"') and line.endswith('"'):
                dialogue = line[1:-1]
                self.dialogues.append({
                    "label": current_label,
                    "character": current_character,
                    "text": dialogue,
                    "line": i
                })
                continue
            
            # 提取角色名称（如 character "对话"）
            if ' "' in line and line.endswith('"'):
                parts = line.split(' "', 1)
                if len(parts) == 2:
                    char_name = parts[0].strip()
                    dialogue = parts[1][:-1]
                    self.characters.add(char_name)
                    current_character = char_name
                    self.dialogues.append({
                        "label": current_label,
                        "character": char_name,
                        "text": dialogue,
                        "line": i
                    })
                continue
            
            # 提取选择分支
            if line.startswith('menu:'):
                self._extract_choices(lines[i:], current_label, i)
    
    def _extract_choices(self, lines: List[str], label: str, start_line: int) -> None:
        """从当前位置提取选择分支"""
        choices = []
        for j, line in enumerate(lines):
            line = line.strip()
            
            # 检测选项
            if line.startswith('"') and ':' in line:
                match = re.match(r'"([^"]+)"\s*:', line)
                if match:
                    choices.append({
                        "text": match.group(1),
                        "line": start_line + j + 1
                    })
            
            # 检测跳转
            elif line.startswith('jump '):
                if choices:
                    self.choices.append({
                        "label": label,
                        "choices": choices,
                        "start_line": start_line
                    })
                break
    
    def export_to_json(self, output_file: str = "dialogues.json") -> None:
        """导出为 JSON 格式"""
        data = {
            "characters": sorted(list(self.characters)),
            "labels": [l["name"] for l in self.labels],
            "dialogues": self.dialogues,
            "choices": self.choices
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已导出到 {output_file}")
    
    def export_to_csv(self, output_file: str = "dialogues.csv") -> None:
        """导出对话为 CSV 格式"""
        with open(output_file, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["标签", "角色", "对话", "行号"])
            
            for d in self.dialogues:
                writer.writerow([d["label"], d["character"] or "", d["text"], d["line"]])
        
        print(f"✅ 已导出到 {output_file}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取提取统计信息"""
        return {
            "total_dialogues": len(self.dialogues),
            "total_characters": len(self.characters),
            "total_labels": len(self.labels),
            "total_choices": len(self.choices),
            "characters": sorted(list(self.characters))
        }


if __name__ == "__main__":
    extractor = TextExtractor()
    extractor.extract()
    
    stats = extractor.get_stats()
    
    print("📊 提取统计:")
    print(f"  • 对话数量: {stats['total_dialogues']}")
    print(f"  • 角色数量: {stats['total_characters']}")
    print(f"  • 标签数量: {stats['total_labels']}")
    print(f"  • 选择分支: {stats['total_choices']}")
    print(f"  • 角色列表: {', '.join(stats['characters'])}")
    
    # 导出文件
    extractor.export_to_json()
    extractor.export_to_csv()
