import logging
import traceback
from django.shortcuts import render
from django.http import JsonResponse
import json

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

# 节点评价文案
NODE_EVALUATIONS = {
    1: {
        'positive': '雨夜之中，你伸出援手。善良的种子，在泥泞中生根发芽。',
        'neutral': '你选择了稳妥之路，既保护了自己，也尽到了职责。',
        'negative': '军令如山，但人心更重。那一刻的催促，或许会成为心中的刺。'
    },
    2: {
        'positive': '半块干粮，一份希望。你把生的机会留给了更需要的人。',
        'neutral': '平分口粮，不偏不倚。乱世之中，这已是难得的公平。',
        'negative': '战争面前，自保无可厚非。只是那份干粮的重量，是否会压在心头？'
    },
    3: {
        'positive': '百姓是根，军队是叶。你用行动诠释了什么是人民子弟兵。',
        'neutral': '服从命令是天职，但百姓的安危，始终牵动着你的心。',
        'negative': '鸣枪引敌，虽属无奈。只是那些未能救下的面孔，是否会时常浮现？'
    },
    4: {
        'positive': '明察秋毫，识破诡计。你的谨慎，守护了整个队伍的安全。',
        'neutral': '将甄别之责交予首长，既尽职守，也显谦逊。',
        'negative': '轻信于人，险些酿成大祸。战争之中，信任需要代价。'
    },
    5: {
        'positive': '加固绳索，排除隐患。你的细致，让战友们安全通过险地。',
        'neutral': '快速通过，虽有惊险，却也体现了军人的决断。',
        'negative': '全面排查，稳妥至上。只是时间，往往是战争中最奢侈的东西。'
    },
    6: {
        'positive': '留下掩护，断后阻击。你选择了危险，把生的希望留给战友。',
        'neutral': '全员突围，共进退。这份凝聚力，是战胜强敌的关键。',
        'negative': '托付农户，虽属无奈。只是那些伤员的命运，是否会让你牵挂？'
    },
    7: {
        'positive': '主动请战，勇担断后。真正的勇士，敢于直面炮火与死亡。',
        'neutral': '居中护卫，坚守职责。首长的安全，就是你的使命。',
        'negative': '申请先行，人之常情。只是回望战场时，心中是否会有波澜？'
    },
    8: {
        'positive': '劝说撤离，情深义重。你用勇气直面首长，用智慧守护英雄。',
        'neutral': '誓死陪伴，同生共死。这份忠诚，感天动地。',
        'negative': '护送他人，职责所在。只是那最后的时刻，你不在他身边。'
    },
    9: {
        'positive': '舍身掩护，英雄本色。你用血肉之躯，诠释了什么是担当。',
        'neutral': '大声警报，提醒战友。你的呼喊，或许能挽救更多生命。',
        'negative': '本能躲避，人之天性。只是那一幕，会成为永远的遗憾。'
    },
    10: {
        'positive': '振臂高呼，冲锋在前。将军的精神，在你身上得到传承。',
        'neutral': '肃穆送别，含泪前行。带着将军的遗志，继续战斗。',
        'negative': '沉默跟随，心如止水。只是那无声的背影，是否承载着太多沉重？'
    }
}


def index(request):
    """首页视图，返回游戏主页面"""
    try:
        logger.info('用户访问首页')
        return render(request, 'index.html')
    except Exception as e:
        logger.error(f'首页加载失败: {str(e)}')
        logger.error(traceback.format_exc())
        return JsonResponse({'error': '首页加载失败'}, status=500)


def calculate_spirit(request):
    """
    计算精神值变化的API接口
    
    POST参数:
    - node: 当前节点编号 (1-10)
    - influence: 选择的影响值 (正数=担当, 负数=退缩)
    - current_spirit: 当前精神值
    """
    if request.method != 'POST':
        logger.warning(f'calculate_spirit接口收到非POST请求: {request.method}')
        return JsonResponse({'error': '只支持POST请求'}, status=400)

    try:
        # 解析请求数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f'请求体JSON解析失败: {str(e)}')
            return JsonResponse({'error': '请求体格式错误，需要JSON格式'}, status=400)

        # 验证必要参数
        required_params = ['node', 'influence', 'current_spirit']
        for param in required_params:
            if param not in data:
                logger.error(f'缺少必要参数: {param}')
                return JsonResponse({'error': f'缺少必要参数: {param}'}, status=400)

        # 转换并验证参数类型
        try:
            node = int(data.get('node', 0))
            influence = int(data.get('influence', 0))
            current_spirit = int(data.get('current_spirit', 0))
        except ValueError as e:
            logger.error(f'参数类型转换失败: {str(e)}')
            return JsonResponse({'error': '参数类型错误，需要整数'}, status=400)

        # 验证节点编号范围
        if node < 1 or node > 10:
            logger.error(f'无效的节点编号: {node}')
            return JsonResponse({'error': '无效的节点编号，范围应为1-10'}, status=400)

        # 获取节点权重
        weight = NODE_WEIGHTS.get(node, 1)

        # 计算变化值
        change = influence * weight

        # 关键节点额外加成 (节点7-10选择挺身而出)
        if node >= 7 and influence > 0:
            change += 2
            logger.debug(f'关键节点{node}额外加成，变化值变为: {change}')

        # 更新精神值
        new_spirit = current_spirit + change

        # 获取节点评价
        evaluation = get_node_evaluation(node, influence)

        # 记录日志
        logger.info(f'精神值计算完成 - 节点:{node}, 影响值:{influence}, '
                    f'权重:{weight}, 变化值:{change}, 新精神值:{new_spirit}')

        return JsonResponse({
            'success': True,
            'node': node,
            'influence': influence,
            'weight': weight,
            'change': change,
            'new_spirit': new_spirit,
            'evaluation': evaluation
        })

    except Exception as e:
        logger.error(f'calculate_spirit接口异常: {str(e)}')
        logger.error(traceback.format_exc())
        return JsonResponse({'error': '服务器内部错误'}, status=500)


def get_node_evaluation(node, influence):
    """
    根据节点和影响值获取评价文案
    
    Args:
        node: 节点编号 (1-10)
        influence: 影响值 (正数=担当, 负数=退缩, 0=中立)
    
    Returns:
        str: 评价文案
    """
    try:
        evaluations = NODE_EVALUATIONS.get(node, {})

        if influence > 0:
            return evaluations.get('positive', '你的选择，值得肯定。')
        elif influence < 0:
            return evaluations.get('negative', '每一个选择，都有它的代价。')
        else:
            return evaluations.get('neutral', '中庸之道，亦是一种智慧。')
    except Exception as e:
        logger.error(f'获取节点评价失败: {str(e)}')
        return '评价获取失败'


def determine_ending(request):
    """
    判定结局的API接口
    
    POST参数:
    - spirit: 最终精神值
    """
    if request.method != 'POST':
        logger.warning(f'determine_ending接口收到非POST请求: {request.method}')
        return JsonResponse({'error': '只支持POST请求'}, status=400)

    try:
        # 解析请求数据
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f'请求体JSON解析失败: {str(e)}')
            return JsonResponse({'error': '请求体格式错误，需要JSON格式'}, status=400)

        # 验证必要参数
        if 'spirit' not in data:
            logger.error('缺少必要参数: spirit')
            return JsonResponse({'error': '缺少必要参数: spirit'}, status=400)

        # 转换并验证参数类型
        try:
            spirit = int(data.get('spirit', 0))
        except ValueError as e:
            logger.error(f'spirit参数类型转换失败: {str(e)}')
            return JsonResponse({'error': 'spirit参数类型错误，需要整数'}, status=400)

        # 判定结局
        if spirit >= ENDING_THRESHOLDS['good']:
            ending = {
                'type': 'good',
                'title': '结局一：青山永念',
                'description': '你带着满身伤痕站在山岭之上，送别了左权将军。回望突围之路，每一次善意与担当都让你收获了真挚情谊。将军的精神万古长青，这段烽火记忆成为你一生最珍贵的念想。',
                'image_index': 14,
                'final_comment': '勇者无惧，仁者无敌。你用一次次的选择证明，平凡人也能铸就伟大。青山有幸埋忠骨，将军精神永存！'
            }
        elif spirit >= ENDING_THRESHOLDS['neutral']:
            ending = {
                'type': 'neutral',
                'title': '结局二：山河怅惘',
                'description': '你恪守本分，做好了警卫员的职责。经历了战火的残酷与将星陨落的悲壮，心中满是沉甸甸的惋惜与敬意。',
                'image_index': 15,
                'final_comment': '恪尽职守，无愧于心。你的选择或许不够耀眼，但每一步都走得踏实。山河依旧，英雄永存心中。'
            }
        else:
            ending = {
                'type': 'bad',
                'title': '结局三：半生愧悔',
                'description': '你侥幸存活，可一路走来的退缩与犹豫成了终生的枷锁。每到雨夜，太行山上的身影便会闯入梦境，这份遗憾如影随形。',
                'image_index': 16,
                'final_comment': '战争残酷，生存不易。只是有些选择，一旦做出，便再也无法回头。愿来生，能有勇气面对每一个抉择。'
            }

        # 记录日志
        logger.info(f'结局判定完成 - 精神值:{spirit}, 结局类型:{ending["type"]}, 结局标题:{ending["title"]}')

        return JsonResponse({'success': True, 'ending': ending})

    except Exception as e:
        logger.error(f'determine_ending接口异常: {str(e)}')
        logger.error(traceback.format_exc())
        return JsonResponse({'error': '服务器内部错误'}, status=500)


def get_game_config(request):
    """
    获取游戏配置的API接口
    返回节点权重、结局阈值等配置信息
    """
    try:
        config = {
            'node_weights': NODE_WEIGHTS,
            'ending_thresholds': ENDING_THRESHOLDS,
            'total_nodes': 10,
            'max_spirit': 5 * 4 + 4 * 2,
            'min_spirit': -4 * 3.5
        }
        logger.info('游戏配置获取成功')
        return JsonResponse({'success': True, 'config': config})
    except Exception as e:
        logger.error(f'获取游戏配置失败: {str(e)}')
        logger.error(traceback.format_exc())
        return JsonResponse({'error': '获取配置失败'}, status=500)
