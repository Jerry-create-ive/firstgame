#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剧情构建器 - 可视化剧情结构并生成脚本

功能：
1. 可视化剧情流程图
2. 生成新场景脚本
3. 检查剧情连接
4. 生成状态变化报告
"""

import os
import json
from typing import Dict, List, Any, Optional


class StoryBuilder:
    """剧情构建器"""
    
    def __init__(self):
        self.scenes = {}
        self.connections = []
        self.stats_effects = {}
    
    def load_from_script(self, script_path: str = "script.rpy") -> None:
        """从脚本文件加载场景信息"""
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")
        
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取标签和跳转
        import re
        
        # 提取所有标签
        label_pattern = r"label (\w+):"
        labels = re.findall(label_pattern, content)
        
        # 提取所有跳转
        jump_pattern = r"jump (\w+)"
        jumps = re.findall(jump_pattern, content)
        
        # 提取选择分支
        menu_pattern = r'menu:\s*(".*?")\s*:\s*\n\s*\$?\s*(\w+)\s*[+-]=\s*\d+\s*\n\s*jump (\w+)'
        matches = re.findall(menu_pattern, content, re.DOTALL)
        
        for label in labels:
            self.scenes[label] = {
                "id": label,
                "type": self._guess_scene_type(label),
                "connections": []
            }
        
        for jump in jumps:
            if jump in self.scenes:
                self.connections.append({"from": "unknown", "to": jump})
        
        print(f"✅ 已加载 {len(self.scenes)} 个场景")
    
    def _guess_scene_type(self, label: str) -> str:
        """猜测场景类型"""
        if label.startswith("intro"):
            return "序章"
        elif label.startswith("ch"):
            match = label.split("_")[0]
            return f"第{match[2]}章"
        elif label.startswith("ending"):
            return "结局"
        elif "transition" in label:
            return "过渡"
        return "场景"
    
    def add_scene(
        self,
        scene_id: str,
        chapter: str = "",
        description: str = "",
        choices: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """添加新场景"""
        self.scenes[scene_id] = {
            "id": scene_id,
            "chapter": chapter,
            "description": description,
            "choices": choices or []
        }
        print(f"✅ 添加场景: {scene_id}")
    
    def add_connection(self, from_scene: str, to_scene: str, condition: str = "") -> None:
        """添加场景连接"""
        if from_scene in self.scenes and to_scene in self.scenes:
            self.connections.append({
                "from": from_scene,
                "to": to_scene,
                "condition": condition
            })
            print(f"✅ 添加连接: {from_scene} -> {to_scene}")
    
    def generate_script(self, scene_id: str) -> str:
        """生成单个场景的脚本代码"""
        scene = self.scenes.get(scene_id)
        if not scene:
            return f"# 场景 {scene_id} 不存在"
        
        script = f'label {scene_id}:\n'
        script += f'    scene bg_{scene_id} with fade\n'
        
        if scene.get("description"):
            script += f'    "{scene["description"]}"\n'
        
        if scene.get("choices"):
            script += '    menu:\n'
            for choice in scene["choices"]:
                effect = ""
                if choice.get("effect"):
                    effects = []
                    for stat, value in choice["effect"].items():
                        sign = "+=" if value > 0 else "-="
                        effects.append(f"${stat} {sign} {abs(value)}")
                    effect = "\n".join([f"            {e}" for e in effects])
                
                script += f'        "{choice["text"]}":\n'
                if effect:
                    script += effect + "\n"
                script += f'            jump {choice["next"]}\n'
        
        else:
            next_scene = self._get_next_scene(scene_id)
            if next_scene:
                script += f'    jump {next_scene}\n'
        
        return script
    
    def _get_next_scene(self, scene_id: str) -> Optional[str]:
        """获取下一个场景"""
        for conn in self.connections:
            if conn["from"] == scene_id:
                return conn["to"]
        return None
    
    def visualize_structure(self) -> str:
        """生成可视化的剧情结构"""
        lines = ["剧情结构图", "=" * 40]
        
        # 按章节分组
        chapters = {}
        for scene_id, scene in self.scenes.items():
            chapter = scene.get("chapter", "其他")
            if chapter not in chapters:
                chapters[chapter] = []
            chapters[chapter].append(scene_id)
        
        for chapter, scenes in sorted(chapters.items()):
            lines.append(f"\n📖 {chapter}")
            lines.append("-" * 20)
            
            for scene in scenes:
                next_scenes = [c["to"] for c in self.connections if c["from"] == scene]
                if next_scenes:
                    lines.append(f"  • {scene} -> {', '.join(next_scenes)}")
                else:
                    lines.append(f"  • {scene}")
        
        return "\n".join(lines)
    
    def check_connections(self) -> List[str]:
        """检查场景连接是否完整"""
        errors = []
        
        for scene_id in self.scenes:
            # 跳过结局场景
            if scene_id.startswith("ending"):
                continue
            
            has_connection = any(c["from"] == scene_id for c in self.connections)
            if not has_connection:
                errors.append(f"⚠️ 场景 {scene_id} 没有跳转目标")
        
        # 检查是否有孤立场景
        all_targets = set(c["to"] for c in self.connections)
        for scene_id in self.scenes:
            if scene_id != "start" and scene_id not in all_targets:
                errors.append(f"⚠️ 场景 {scene_id} 无法被访问")
        
        return errors


if __name__ == "__main__":
    builder = StoryBuilder()
    builder.load_from_script()
    
    # 显示结构
    print(builder.visualize_structure())
    
    # 检查连接
    errors = builder.check_connections()
    if errors:
        print("\n🔍 连接检查结果:")
        for error in errors:
            print(error)
    else:
        print("\n✅ 所有场景连接正常")
