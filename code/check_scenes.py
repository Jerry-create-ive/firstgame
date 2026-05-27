import re

# 读取index.html
with open('main/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取sceneBackgroundMap
start_idx = content.find('const sceneBackgroundMap = {')
end_idx = content.find('};', start_idx) + 2
map_content = content[start_idx:end_idx]

# 提取storyData
start_idx2 = content.find('const storyData = {')
end_idx2 = content.find('};', start_idx2) + 2
story_content = content[start_idx2:end_idx2]

# 提取所有场景名称
scene_pattern = r"'([^']+)':\s*{"
story_scenes = set(re.findall(scene_pattern, story_content))
map_scenes = set(re.findall(r"'([^']+)':\s*\d+", map_content))

print('=== 场景映射检查报告 ===')
print()

# 检查未在映射中定义的场景
missing = story_scenes - map_scenes
if missing:
    print('未在sceneBackgroundMap中定义的场景:')
    for scene in sorted(missing):
        print('   - ' + scene)
else:
    print('所有场景都已在sceneBackgroundMap中定义')

print()

# 统计各背景图使用次数
print('=== 背景图使用统计 ===')
bg_usage = {}
for match in re.findall(r"'([^']+)':\s*(\d+)", map_content):
    scene, bg_idx = match[0], int(match[1])
    if bg_idx not in bg_usage:
        bg_usage[bg_idx] = []
    bg_usage[bg_idx].append(scene)

for bg_idx in sorted(bg_usage.keys()):
    scenes = bg_usage[bg_idx]
    print('图片 ' + str(bg_idx + 1) + '.jpg (' + str(len(scenes)) + '个场景):')
    for scene in scenes:
        print('   - ' + scene)
    print()

# 检查是否有未使用的背景图
all_bgs = set(range(17))  # 0-16 对应 1-17.jpg
used_bgs = set(bg_usage.keys())
unused = all_bgs - used_bgs
if unused:
    print('未使用的背景图:')
    for bg_idx in sorted(unused):
        print('   - ' + str(bg_idx + 1) + '.jpg')
else:
    print('所有17张背景图都已使用')
