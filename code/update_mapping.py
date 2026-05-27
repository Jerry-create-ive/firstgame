# 更新场景背景映射为严格按剧情顺序
import re

# 读取index.html
with open('main/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 新的映射方案：每个图片对应一个主要剧情节点
new_map = {
    # 1.jpg - 序章/开始
    'start': 0,
    
    # 2.jpg - 第一章：雨夜急撤
    'chapter1_1': 1,
    'chapter1_2': 1,
    'chapter1_3': 1,
    'chapter1_4': 1,
    
    # 3.jpg - 第一章抉择
    'node1_1': 2,
    'node1_2': 2,
    'node1_3': 2,
    'transition1_1': 2,
    
    # 4.jpg - 第二章：岩洞暂歇
    'transition1_2': 3,
    'chapter2_1': 3,
    'chapter2_2': 3,
    'chapter2_3': 3,
    
    # 5.jpg - 第二章抉择（口粮）
    'chapter2_4': 4,
    'node2_1': 4,
    'node2_2': 4,
    'node2_3': 4,
    
    # 6.jpg - 第二章续：民心取舍
    'transition2_1': 5,
    'chapter2_5': 5,
    'chapter2_6': 5,
    'node3_1': 5,
    'node3_2': 5,
    'node3_3': 5,
    
    # 7.jpg - 第三章：情报危机
    'transition3_1': 6,
    'chapter3_1': 6,
    'chapter3_2': 6,
    'chapter3_3': 6,
    'node4_1': 6,
    'node4_2': 6,
    'node4_3': 6,
    
    # 8.jpg - 第三章续：险坡危索
    'transition4_1': 7,
    'chapter3_4': 7,
    'chapter3_5': 7,
    'node5_1': 7,
    'node5_2': 7,
    'node5_3': 7,
    
    # 9.jpg - 第四章：炮火连天
    'transition5_1': 8,
    'chapter4_1': 8,
    'chapter4_2': 8,
    'node6_1': 8,
    'node6_2': 8,
    'node6_3': 8,
    
    # 10.jpg - 第四章续：勇担断后
    'transition6_1': 9,
    'chapter4_3': 9,
    'node7_1': 9,
    'node7_2': 9,
    'node7_3': 9,
    
    # 11.jpg - 第五章：生死绝境
    'transition7_1': 10,
    'chapter5_1': 10,
    'chapter5_2': 10,
    'node8_1': 10,
    'node8_2': 10,
    'node8_3': 10,
    
    # 12.jpg - 第五章续：刹那生死
    'transition8_1': 11,
    'chapter5_3': 11,
    'node9_1': 11,
    'node9_2': 11,
    'node9_3': 11,
    
    # 13.jpg - 将星陨落
    'transition9_1': 12,
    
    # 14.jpg - 终章
    'chapter_end': 13,
    
    # 15.jpg - 结局1
    'node10_1': 14,
    
    # 16.jpg - 结局2
    'node10_2': 15,
    
    # 17.jpg - 结局3
    'node10_3': 16,
}

# 生成新的映射字符串
map_str = 'const sceneBackgroundMap = {\n'
items = []
for scene, idx in new_map.items():
    items.append(f"            '{scene}': {idx}")
map_str += ',\n'.join(items)
map_str += '\n        };'

# 替换原有映射
old_start = content.find('const sceneBackgroundMap = {')
old_end = content.find('};', old_start) + 2
new_content = content[:old_start] + map_str + content[old_end:]

# 写入文件
with open('main/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('场景映射已更新为按剧情顺序严格对应')
print()
print('新的映射关系：')
for i in range(17):
    scenes = [s for s, idx in new_map.items() if idx == i]
    if scenes:
        print(f'📷 {i+1}.jpg -> {", ".join(scenes[:3])}{"..." if len(scenes) > 3 else ""}')
