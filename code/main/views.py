from django.shortcuts import render
from django.http import JsonResponse
import json

# 节点权重配置
NODE_WEIGHTS = {
    1: 1, 2: 1.5, 3: 1.5, 4: 1, 5: 1,
    6: 2, 7: 2.5, 8: 3, 9: 3.5, 10: 4
}

# 结局判定阈值
ENDING_THRESHOLDS = {
    'good': 15,
    'neutral': -5
}

def index(request):
    return render(request, 'index.html')

def calculate_spirit(request):
    """
    计算精神值变化的API接口
    POST参数:
    - node: 当前节点编号 (1-10)
    - influence: 选择的影响值 (正数=担当, 负数=退缩)
    - current_spirit: 当前精神值
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            node = int(data.get('node', 0))
            influence = int(data.get('influence', 0))
            current_spirit = int(data.get('current_spirit', 0))
            
            if node < 1 or node > 10:
                return JsonResponse({'error': '无效的节点编号'}, status=400)
            
            # 获取节点权重
            weight = NODE_WEIGHTS.get(node, 1)
            
            # 计算变化值
            change = influence * weight
            
            # 关键节点额外加成 (节点7-10选择挺身而出)
            if node >= 7 and influence > 0:
                change += 2
            
            # 更新精神值
            new_spirit = current_spirit + change
            
            return JsonResponse({
                'success': True,
                'node': node,
                'influence': influence,
                'weight': weight,
                'change': change,
                'new_spirit': new_spirit
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '只支持POST请求'}, status=400)

def determine_ending(request):
    """
    判定结局的API接口
    POST参数:
    - spirit: 最终精神值
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            spirit = int(data.get('spirit', 0))
            
            # 判定结局
            if spirit >= ENDING_THRESHOLDS['good']:
                ending = {
                    'type': 'good',
                    'title': '结局一：青山永念',
                    'description': '你带着满身伤痕站在山岭之上，送别了左权将军。回望突围之路，每一次善意与担当都让你收获了真挚情谊。将军的精神万古长青，这段烽火记忆成为你一生最珍贵的念想。',
                    'image_index': 14
                }
            elif spirit >= ENDING_THRESHOLDS['neutral']:
                ending = {
                    'type': 'neutral',
                    'title': '结局二：山河怅惘',
                    'description': '你恪守本分，做好了警卫员的职责。经历了战火的残酷与将星陨落的悲壮，心中满是沉甸甸的惋惜与敬意。',
                    'image_index': 15
                }
            else:
                ending = {
                    'type': 'bad',
                    'title': '结局三：半生愧悔',
                    'description': '你侥幸存活，可一路走来的退缩与犹豫成了终生的枷锁。每到雨夜，太行山上的身影便会闯入梦境，这份遗憾如影随形。',
                    'image_index': 16
                }
            
            return JsonResponse({'success': True, 'ending': ending})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': '只支持POST请求'}, status=400)

def get_game_config(request):
    """
    获取游戏配置的API接口
    返回节点权重、结局阈值等配置信息
    """
    config = {
        'node_weights': NODE_WEIGHTS,
        'ending_thresholds': ENDING_THRESHOLDS,
        'total_nodes': 10,
        'max_spirit': 5 * 4 + 4 * 2,
        'min_spirit': -4 * 3.5
    }
    return JsonResponse({'success': True, 'config': config})
