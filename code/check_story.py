#!/usr/bin/env python3
import re

# 读取文件
with open(r'd:\demooo\code\main\templates\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取所有场景ID（在storyData对象中）
story_data_start = content.find('const storyData = {')
story_data_end = content.find('};', story_data_start) + 2
story_data_content = content[story_data_start:story_data_end]

# 提取场景ID
scene_pattern = r"(\w+):\s*\{[^}]*\}"
scenes = re.findall(scene_pattern, story_data_content)

# 提取所有next指向
next_pattern = r"next:\s*['\"](\w+)['\"]"
nexts = re.findall(next_pattern, story_data_content)

# 找出缺失的场景
missing = [n for n in nexts if n not in scenes]

print('=' * 60)
print('剧情数据检查报告')
print('=' * 60)
print('场景总数:', len(scenes))
print('next指向总数:', len(nexts))
print()

if missing:
    print('缺失的场景（存在next指向但场景未定义）:')
    for m in missing:
        print('  -', m)
else:
    print('所有next指向都有对应的场景定义')

print()
print('=' * 60)