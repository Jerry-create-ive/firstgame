#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
太行残雪 - Python 视觉小说游戏引擎

核心功能：
1. 场景管理
2. 对话系统
3. 选择分支
4. 状态管理
5. 结局判定
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Callable


class GameState:
    """游戏状态管理类"""
    
    def __init__(self):
        self.relation = 0  # 人际关系
        self.trust = 0      # 信任度
        self.guilt = 0      # 愧疚值
        self.flags = {}     # 标记字典
        
        # 结局阈值
        self.ENDING_THRESHOLD = {
            "good": 18,
            "neutral": 8
        }
    
    def update_stat(self, stat: str, value: int) -> None:
        """更新状态值"""
        if stat == "relation":
            self.relation += value
        elif stat == "trust":
            self.trust += value
        elif stat == "guilt":
            self.guilt += value
    
    def set_flag(self, flag_name: str, value: bool = True) -> None:
        """设置标记"""
        self.flags[flag_name] = value
    
    def get_total_score(self) -> int:
        """计算总分"""
        return self.relation + self.trust - self.guilt
    
    def determine_ending(self) -> str:
        """判定结局"""
        total = self.get_total_score()
        if total >= self.ENDING_THRESHOLD["good"]:
            return "good"
        elif total >= self.ENDING_THRESHOLD["neutral"]:
            return "neutral"
        else:
            return "bad"
    
    def get_stats_summary(self) -> str:
        """获取状态摘要"""
        return (
            f"📊 当前状态\n"
            f"  ├─ 人际关系: {self.relation}\n"
            f"  ├─ 信任度: {self.trust}\n"
            f"  └─ 愧疚值: {self.guilt}\n"
            f"  总分: {self.get_total_score()} (完美结局需 ≥18)"
        )


class Dialogue:
    """对话类"""
    
    def __init__(self, character: Optional[str], text: str):
        self.character = character
        self.text = text
    
    def display(self, delay: float = 0.03) -> None:
        """显示对话文本"""
        if self.character:
            print(f"\033[1;33m【{self.character}】\033[0m")
        
        # 逐字显示
        for char in self.text:
            print(char, end="", flush=True)
            time.sleep(delay)
        print("\n")


class Choice:
    """选择分支类"""
    
    def __init__(self, text: str, effects: Dict[str, int], next_scene: str, flag: Optional[str] = None):
        self.text = text
        self.effects = effects
        self.next_scene = next_scene
        self.flag = flag
    
    def apply_effects(self, state: GameState) -> None:
        """应用选择效果"""
        for stat, value in self.effects.items():
            state.update_stat(stat, value)
        
        if self.flag:
            state.set_flag(self.flag)


class Scene:
    """场景类"""
    
    def __init__(
        self,
        id: str,
        background: str,
        dialogues: List[Dialogue],
        choices: Optional[List[Choice]] = None
    ):
        self.id = id
        self.background = background
        self.dialogues = dialogues
        self.choices = choices or []
    
    def has_choices(self) -> bool:
        """是否有选择分支"""
        return len(self.choices) > 0


class GameEngine:
    """游戏引擎主类"""
    
    def __init__(self):
        self.state = GameState()
        self.scenes: Dict[str, Scene] = {}
        self.current_scene_id = "start"
        self.is_running = True
        
    def add_scene(self, scene: Scene) -> None:
        """添加场景"""
        self.scenes[scene.id] = scene
    
    def load_scene(self, scene_id: str) -> Optional[Scene]:
        """加载场景"""
        return self.scenes.get(scene_id)
    
    def run_scene(self, scene_id: str) -> str:
        """运行场景"""
        scene = self.load_scene(scene_id)
        if not scene:
            print(f"❌ 场景 {scene_id} 不存在")
            return "ending"
        
        self.current_scene_id = scene_id
        
        # 显示场景背景提示
        print(f"\n" + "=" * 60)
        print(f"📍 {scene.id.replace('_', ' ')}")
        print("=" * 60)
        
        # 显示对话
        for dialogue in scene.dialogues:
            dialogue.display()
            input("按 Enter 继续...")
        
        # 处理选择
        if scene.has_choices():
            print("\n请选择：")
            for i, choice in enumerate(scene.choices, 1):
                print(f"  {i}. {choice.text}")
            
            while True:
                try:
                    selection = int(input("\n请输入选择序号: ")) - 1
                    if 0 <= selection < len(scene.choices):
                        choice = scene.choices[selection]
                        choice.apply_effects(self.state)
                        print("\n" + self.state.get_stats_summary())
                        return choice.next_scene
                    else:
                        print("❌ 请输入有效的序号")
                except ValueError:
                    print("❌ 请输入数字")
        
        # 没有选择，返回下一个场景
        return self.get_next_scene_id(scene_id)
    
    def get_next_scene_id(self, current_id: str) -> str:
        """获取下一个场景ID"""
        # 根据场景ID推断下一个场景
        if current_id == "start":
            return "intro"
        elif current_id == "intro":
            return "intro_2"
        elif current_id.endswith("_transition"):
            # 过渡场景后的下一章
            match = current_id.replace("_transition", "")
            if match == "ch1":
                return "ch2_1"
            elif match == "ch2":
                return "ch3_1"
            elif match == "ch3":
                return "ch4_1"
            elif match == "ch4":
                return "ch5_1"
            elif match == "ch5":
                return "ending"
            return "ending"
        elif "_transition" in current_id:
            # 特殊过渡场景
            base = current_id.split("_transition")[0]
            chapter = base.split("_")[0]
            next_chapter_num = int(chapter[2:]) + 1
            return f"ch{next_chapter_num}_1"
        elif "_" in current_id:
            parts = current_id.split("_")
            if len(parts) == 2:
                # 如 ch1_1 -> ch1_2
                try:
                    num = int(parts[1])
                    return f"{parts[0]}_{num + 1}"
                except:
                    pass
        return "ending"
    
    def run(self) -> None:
        """运行游戏"""
        print("""
╔══════════════════════════════════════════════════════╗
║                   太行残雪                           ║
║              十字岭反扫荡 · 1942                    ║
╚══════════════════════════════════════════════════════╝
        """)
        
        input("按 Enter 开始游戏...")
        
        current_scene = "start"
        
        while self.is_running and current_scene != "ending":
            current_scene = self.run_scene(current_scene)
            
            # 检查是否到达结局判定点
            if current_scene == "ending" or current_scene.startswith("ending_"):
                break
        
        # 结局判定与展示
        self.show_ending()
    
    def show_ending(self) -> None:
        """显示结局"""
        ending_type = self.state.determine_ending()
        
        endings = {
            "good": {
                "title": "🏆 青山永念，忠骨留芳",
                "text": """
漫天风雪慢慢停歇，炮火渐渐远去，十字岭群山静默无言。

你带着满身伤痕站在山岭之上，送别了一路庇护战士、心系家国的左权将军。

一路走来，你帮扶战友、守护百姓、危难之时挺身而出，将军的叮嘱、温暖、坚毅的模样深深刻进心底。

那些雨夜同行、岩洞分粮、生死相护的画面一遍遍在脑海浮现。

将军从未身居高位漠视士兵，始终把每一条生命、每一方百姓都扛在肩头。

往后漫长岁月，你带着将军未完成的心愿继续奔赴战场，守护山河故土。

每当回望这座埋葬忠魂的太行大山，泪水总会悄然滑落。

英雄长眠故土，精神永世不灭，这段生死相伴的烽火岁月，成为一生最滚烫、最动容的记忆。
                """
            },
            "neutral": {
                "title": "🌄 山河怅惘，心怀惋惜",
                "text": """
战役落幕，队伍顺利突围保全了有生力量，可敬的将领永远留在了这片山岭。

你按部就班走完整场突围之路，守好自身本分，见过战火残酷，见过军民同心，也见证了将星陨落的悲壮。

没有深刻的羁绊亏欠，也没有轰轰烈烈的挺身而出。

往后日子里，你时常想起左权沉稳的身影，想起绝境里不曾退缩的担当。

心中满是沉甸甸的惋惜与敬意。历史滚滚向前，先烈以身换来生机，你带着这份缅怀安稳前行。
                """
            },
            "bad": {
                "title": "💔 半生愧悔，夜夜难眠",
                "text": """
你侥幸从惨烈的突围中活了下来，可一路走来一次次犹豫、退缩、自顾自保，全都变成往后岁月里挥之不去的枷锁。

当初可以帮扶战友却冷眼旁观，可以救助百姓却转身离开，最后关头也没能鼓起勇气守护敬重的首长。

身边战友谈及将军的仁厚与壮烈，你只能默默闭口躲闪，不敢直视他们的眼睛。

历史不会因为个人选择更改分毫，将军依旧为国捐躯，部队依旧冲破封锁走向胜利。

只有你带着满心愧疚与遗憾度过余生。每到雨夜风起之时，太行山上的炮火与身影总会闯入梦境。

这份遗憾，终生都无法释然，成为你心中永远的痛。
                """
            }
        }
        
        ending = endings[ending_type]
        
        print("\n" + "=" * 60)
        print(ending["title"])
        print("=" * 60)
        print(ending["text"])
        print("\n" + self.state.get_stats_summary())
        print("\n🎉 游戏结束")


def create_game() -> GameEngine:
    """创建游戏实例"""
    engine = GameEngine()
    
    # ========== 序章 ==========
    engine.add_scene(Scene(
        id="start",
        background="bg_start",
        dialogues=[
            Dialogue(None, "1942年5月，华北日军集结数万兵力，对太行抗日根据地发动疯狂大「扫荡」。"),
            Dialogue(None, "铁蹄踏遍山野，炮火撕裂晴空，根据地军民陷入空前险境。"),
            Dialogue(None, "八路军总部机关被迫连夜转移，向着山势险峻、易守难攻的十字岭深山突围。"),
            Dialogue(None, "连日阴雨裹挟着山间寒气，冷雨浇透了军装，泥泞的山路每一步都举步维艰。"),
            Dialogue(None, "远方断断续续的枪炮声如同催命鼓点，始终盘旋在山林上空。"),
            Dialogue(None, "队伍不敢有半分停歇，数千干部、战士、随行百姓相互搀扶，在漆黑的山野里艰难前行。"),
            Dialogue(None, "左权副总参谋长骑马走在队伍中段，时而勒住缰绳清点人数，时而低声叮嘱身边战士照看伤员。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="intro",
        background="bg_intro",
        dialogues=[
            Dialogue(None, "我作为贴身警卫员陈怀安，寸步不离守在左权首长身侧。"),
            Dialogue(None, "手心攥出冷汗，紧绷的神经从入夜起就未曾放松。"),
            Dialogue(None, "今年我刚满十九岁，出身贫苦农家，三年前参了军，承蒙首长厚爱，调至他身边担任警卫员。"),
            Dialogue(None, "这两年多来，我亲眼见证了他如何运筹帷幄，如何关爱士兵，那份沉稳与仁爱，早已深深烙印在我心底。"),
            Dialogue(None, "此刻，我望着首长坚毅的侧脸，只盼着能护他周全，平安度过这场劫难。"),
        ]
    ))
    
    # ========== 第一章：雨夜急撤 ==========
    engine.add_scene(Scene(
        id="intro_2",
        background="bg_intro_2",
        dialogues=[
            Dialogue(None, "冷雨斜斜地打在枝叶上，汇成水流顺着帽檐往下淌，浸湿了脖颈。"),
            Dialogue(None, "脚下的黄泥路被雨水泡得软烂，踩上去噗嗤作响，稍不留意就会脚下打滑。"),
            Dialogue(None, "队伍呈长蛇状在密林间蜿蜒前行，没人高声说话，唯有杂乱的脚步声、粗重的喘息声。"),
            Dialogue(None, "左权翻身下马，徒步走了一段路。山路狭窄湿滑，马匹行进艰难，他不愿因坐骑拖累队伍速度。"),
            Dialogue("左权", "放慢步速，但绝对不能停，日军机械化部队机动性强，一旦原地滞留，后果不堪设想。"),
            Dialogue("左权", "多留意队伍后方，新兵和体力弱的战士重点照看。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch1_1",
        background="bg_ch1_1",
        dialogues=[
            Dialogue(None, "我紧跟在首长身后，目光下意识扫向队伍末尾。夜色浓重，林间能见度极低。"),
            Dialogue(None, "就在这时，一阵压抑的痛呼隐隐传来——新兵牛娃正扶着树干，单脚踮地，身体止不住地晃动。"),
            Dialogue(None, "牛娃入伍不过半年，还是个半大孩子，平日里干活勤快，性子腼腆。"),
            Dialogue(None, "此刻他裤脚沾满泥浆，右侧脚腕明显肿胀，额头上布满冷汗，嘴唇咬得发白。"),
            Dialogue(None, "他拼尽全力想要跟上大部队的节奏，可受伤的脚踝根本不听使唤，短短片刻，就和主力队伍拉开了一大段距离。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch1_2",
        background="bg_ch1_2",
        dialogues=[
            Dialogue(None, "后方的枪炮声似乎又近了几分，隐约还能听见日军吆喝喊话的声音，追兵正在步步紧逼。"),
            Dialogue(None, "前方队伍依旧在向前行进，没人注意到这个掉队的新兵。"),
            Dialogue(None, "我站在原地，看着孤立无援的牛娃，心中开始权衡当下的选择。"),
        ],
        choices=[
            Choice(
                text="立刻停下，留下来搀扶牛娃一同赶路",
                effects={"relation": 2, "trust": 1},
                next_scene="ch1_4a",
                flag="help_niuwa"
            ),
            Choice(
                text="先赶回前方汇报首长，请求派人折返接应",
                effects={"trust": 2},
                next_scene="ch1_4b",
                flag="report_niuwa"
            ),
            Choice(
                text="催促牛娃咬牙跟上，不能拖累整体突围进度",
                effects={"relation": -2, "guilt": 1},
                next_scene="ch1_4c",
                flag="ignore_niuwa"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch1_4a",
        background="bg_ch1_4a",
        dialogues=[
            Dialogue("牛娃", "谢...谢谢班长！"),
            Dialogue(None, "我快步上前扶住他，架着他的胳膊一步步前行。"),
            Dialogue(None, "他小声告诉我，今天是他第一次经历实战，刚才在泥泞中不慎扭伤了脚。"),
            Dialogue("牛娃", "我...我不想拖大家后腿..."),
            Dialogue("陈怀安", "别说傻话，咱们八路军从不丢下一个战友。"),
            Dialogue(None, "牛娃重重地点点头，目光里满是感激。从那以后，他看我的眼神都带着一份特殊的信赖。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch1_4b",
        background="bg_ch1_4b",
        dialogues=[
            Dialogue(None, "我简单安抚牛娃后，快步跑到左权身边说明情况。"),
            Dialogue("左权", "做得好，怀安。遇事冷静，思虑周全。"),
            Dialogue(None, "他当即安排两名体力尚可的战士折返接应，又嘱咐道：「告诉牛娃，别着急，我们不会丢下任何一个同志。」"),
            Dialogue(None, "那一刻，我感受到首长话语中的温度，也明白了什么叫做真正的爱兵如子。"),
            Dialogue(None, "此后左权安排任务时，确实更愿意将协调、侦查类工作托付给我。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch1_4c",
        background="bg_ch1_4c",
        dialogues=[
            Dialogue("陈怀安", "快点跟上，别耽误大部队！"),
            Dialogue(None, "牛娃面露难堪，嘴唇动了动想说什么，最终还是咬紧牙关，强忍着剧痛硬撑前行。"),
            Dialogue(None, "他的身影在雨幕中越来越小，我不敢回头，只听见身后传来他压抑的痛哼声。"),
            Dialogue(None, "军令如山，我只能继续向前，但心底却莫名地有些沉重。"),
            Dialogue(None, "从那以后，牛娃见到我总是刻意避开，那份疏远，成了我心中难以言说的疙瘩。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch1_transition",
        background="bg_ch1_transition",
        dialogues=[
            Dialogue(None, "队伍继续在雨夜山林中穿行。雨势渐渐小了些，但山间寒风愈发刺骨，吹得人浑身发抖。"),
            Dialogue(None, "一路上不断有战士互相提醒脚下路况，有人捡起路边的枯枝当作拐杖，帮扶着身边体力不支的同伴。"),
            Dialogue(None, "左权始终走在队伍中段，时不时停下脚步，挨个询问伤员的身体状况。"),
            Dialogue(None, "约莫两个小时后，前方探路的侦查兵传来消息：前方山腰处有一处天然岩洞，可以临时躲避风雨。"),
        ]
    ))
    
    # ========== 第二章：岩洞暂歇 ==========
    engine.add_scene(Scene(
        id="ch2_1",
        background="bg_ch2_1",
        dialogues=[
            Dialogue(None, "众人相互扶持着攀上陡坡，陆续走进了那座依山而建的天然岩洞。"),
            Dialogue(None, "岩洞内壁粗糙干燥，隔绝了外界的风雨，昏暗的天光从洞口照进来，勉强能看清洞内景象。"),
            Dialogue(None, "战士们纷纷靠墙坐下，揉着酸痛的腿脚，解开湿透的绑带处理伤口。"),
            Dialogue(None, "岩洞内侧的角落，几名重伤员躺在干草上，其中排长老周伤势最重。"),
            Dialogue(None, "他在之前的阻击战中被子弹擦伤胸腹，此刻正发着高烧，脸颊通红，呼吸急促微弱。"),
            Dialogue(None, "随行的卫生员翻遍了药包，药品早已耗尽，只能用干净的布条简单包扎伤口，束手无策。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_2",
        background="bg_ch2_2",
        dialogues=[
            Dialogue(None, "一路奔袭，所有人随身携带的干粮基本都已吃光。"),
            Dialogue(None, "我伸手摸向胸口贴身存放的布包，里面还剩下最后一块拳头大小的杂粮干粮——这是我出发前特意留下的。"),
            Dialogue(None, "岩洞之内，饥饿与疲惫笼罩着每一个人。"),
            Dialogue("卫生员", "没有吃食补充体力，他这身子怕是撑不了太久。"),
            Dialogue(None, "周围的战士纷纷看向彼此，所有人都空空如也，谁也拿不出多余的粮食。"),
            Dialogue(None, "我低头看着怀中温热的杂粮干粮，握着干粮的手迟迟没有松开。"),
        ],
        choices=[
            Choice(
                text="全部让出，喂给重伤排长补充体力",
                effects={"relation": 3, "trust": 2},
                next_scene="ch2_3a",
                flag="share_all_food"
            ),
            Choice(
                text="分出一半口粮，自己留一半维持护卫体力",
                effects={},
                next_scene="ch2_3b",
                flag="share_half_food"
            ),
            Choice(
                text="自己悄悄收好，保留体力保护首长安全",
                effects={"relation": -3, "guilt": 2},
                next_scene="ch2_3c",
                flag="keep_food"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_3a",
        background="bg_ch2_3a",
        dialogues=[
            Dialogue(None, "我将整块干粮掰碎，一点点喂到老周口中。"),
            Dialogue(None, "老周艰难地睁开眼睛，嘴唇动了动，想说什么却没力气出声，只是眼中泛起了泪光。"),
            Dialogue(None, "周围的战士看在眼里，纷纷投来敬佩的目光。"),
            Dialogue(None, "左权将军恰好走进来，看到这一幕，对我投来赞许的目光。"),
            Dialogue("左权", "怀安，做得对。我们八路军，就是要互相扶持。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_3b",
        background="bg_ch2_3b",
        dialogues=[
            Dialogue(None, "我将干粮掰成两半，一半递给了老周，另一半自己留着。"),
            Dialogue("老周", "谢谢。"),
            Dialogue(None, "这是最稳妥的选择，既照顾了伤员，也保证了自己有足够的体力继续护卫任务。"),
            Dialogue(None, "没有人特别注意到这个举动，一切都显得那么自然。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_3c",
        background="bg_ch2_3c",
        dialogues=[
            Dialogue(None, "我悄悄将干粮藏进怀里，假装什么都没有发生。"),
            Dialogue(None, "作为警卫员，保护首长的安全是第一位的，我需要保持体力。"),
            Dialogue(None, "但我能感觉到身旁几名战士投来的异样目光，那是一种无声的谴责。"),
            Dialogue(None, "老周的呼吸越来越微弱，卫生员急得直搓手，却毫无办法。"),
            Dialogue(None, "我不敢抬头，只能假装整理装备，可心底那份沉甸甸的愧疚，却怎么也挥之不去。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_transition",
        background="bg_ch2_transition",
        dialogues=[
            Dialogue(None, "口粮的事情尘埃落定，洞内的气氛恢复平和。"),
            Dialogue(None, "大家利用这短暂的休整时间，整理装备、擦拭枪械，低声交流着接下来的突围路线。"),
            Dialogue(None, "左权借着天光，摊开简易的手绘地图，和几名干部低声研讨局势，眉头始终紧锁。"),
            Dialogue(None, "就在这时，洞口传来急促的脚步声，侦查班班长披着一身泥水快步冲了进来。"),
            Dialogue("侦查班长", "首长，山下李家庄还有不少村民没来得及转移，日军已经进村搜查了！"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_5",
        background="bg_ch2_5",
        dialogues=[
            Dialogue(None, "消息一出，洞内瞬间陷入一片沉寂。"),
            Dialogue(None, "一边是被困的无辜百姓，一边是隐蔽休整的总部机关。"),
            Dialogue(None, "若是贸然下山救人，极有可能暴露岩洞位置，引来大批日军围剿；可若是坐视不理..."),
            Dialogue(None, "左权站起身，走到洞口望向山下村落的方向，面色沉重。他看向身边众人，没有立刻下达命令。"),
            Dialogue(None, "结合此前一路上众人的相处状态，身边战友的态度也隐隐不同。"),
        ],
        choices=[
            Choice(
                text="主动向首长请命，带队下山掩护村民进山避险",
                effects={"relation": 3, "trust": 2},
                next_scene="ch2_6a",
                flag="rescue_villagers"
            ),
            Choice(
                text="服从原地待命命令，坚守岩洞护卫机关人员",
                effects={"guilt": 1},
                next_scene="ch2_6b",
                flag="stay_defend"
            ),
            Choice(
                text="建议远距离鸣枪，引开日军不去正面接触",
                effects={"trust": 1},
                next_scene="ch2_6c",
                flag="divert_japanese"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_6a",
        background="bg_ch2_6a",
        dialogues=[
            Dialogue(None, "我主动请命，愿意同行的战友纷纷响应。"),
            Dialogue(None, "我们趁着夜色悄悄摸下山去，村民们惊恐地蜷缩在地道里，看到我们来了，眼中都燃起了希望。"),
            Dialogue("大娘", "八路军同志，你们可算来了！"),
            Dialogue(None, "我们迅速将村民转移至深山隐蔽处，大娘记着这份恩情，悄悄告诉我一条只有本地人才知道的隐秘小路。"),
            Dialogue(None, "她说这条路上有一处日军没发现的天然隘口，可以避开前方的埋伏。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_6b",
        background="bg_ch2_6b",
        dialogues=[
            Dialogue(None, "我选择严守军令，站在岩洞门口警戒。"),
            Dialogue(None, "山下隐约传来几声妇女的哭喊，刺得人心头发紧。"),
            Dialogue(None, "我握紧手中的枪，目光死死盯着山下的方向，却什么也做不了。"),
            Dialogue(None, "职责所在，我必须保护首长和机关人员的安全，但那份无力感却沉甸甸地压在心头。"),
            Dialogue(None, "村民最终自行躲避，我心中留下难以释怀的遗憾，这份愧疚，在往后的日子里时常浮现。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_6c",
        background="bg_ch2_6c",
        dialogues=[
            Dialogue(None, "我的提议被左权采纳，战士们绕至远处鸣枪。"),
            Dialogue(None, "清脆的枪声在山谷间回荡，日军果然被吸引了过去，朝着枪声响起的方向追去。"),
            Dialogue("侦查班长", "小子，脑子挺活泛！"),
            Dialogue(None, "他十分认可我的智谋，之后遇到复杂情况时，总会主动询问我的意见。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch2_5_transition",
        background="bg_ch2_5_transition",
        dialogues=[
            Dialogue(None, "按照选择执行完毕后，山下的危机暂时解除。"),
            Dialogue(None, "左权见外界风险降低，当即下令全员整队出发。"),
            Dialogue(None, "众人背起行囊、搀扶着伤员，有序地走出岩洞，继续向十字岭深处行进。"),
            Dialogue(None, "此时雨完全停歇，山间起了浓雾，白茫茫的雾气笼罩着整片山林。"),
        ]
    ))
    
    # ========== 第三章：山路涉险 ==========
    engine.add_scene(Scene(
        id="ch3_1",
        background="bg_ch3_1",
        dialogues=[
            Dialogue(None, "山间小路蜿蜒曲折，两侧林木茂密，怪石嶙峋。浓雾之中，每走一步都要格外小心。"),
            Dialogue(None, "侦查班派出数名尖兵在前方百米外探路，每隔一段距离就传回安全信号。"),
            Dialogue(None, "队伍行进了大约半个时辰，前方的尖兵突然停下脚步。"),
            Dialogue(None, "我陪着左权走上前查看，只见雾气当中，迎面走来一个衣衫褴褛、头发散乱的陌生人。"),
            Dialogue("陌生人", "别开枪！我是附近村子的逃难百姓！我知道前面山路的情况，日军在前面设了关卡！"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_3",
        background="bg_ch3_3",
        dialogues=[
            Dialogue(None, "此人言辞恳切，可眼下局势复杂，日军时常派出伪装成百姓的探子刺探情报。"),
            Dialogue(None, "再加上浓雾遮挡视线，根本无法判断对方的真实身份。"),
            Dialogue(None, "那人站在原地，眼神飘忽不定，等待着我们的回应。"),
            Dialogue(None, "周围的战士纷纷举起枪械，警惕地盯着他。"),
        ],
        choices=[
            Choice(
                text="严格盘问细节，核对村落、敌军动向信息",
                effects={"trust": 2},
                next_scene="ch3_4a",
                flag="strict_question"
            ),
            Choice(
                text="心生怜悯，不加盘问直接放其离开",
                effects={"relation": -2, "guilt": 2},
                next_scene="ch3_4b",
                flag="release_stranger"
            ),
            Choice(
                text="直接押送到左权首长面前统一甄别",
                effects={"trust": 1},
                next_scene="ch3_4c",
                flag="escort_to_leader"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_4a",
        background="bg_ch3_4a",
        dialogues=[
            Dialogue("陈怀安", "你是哪个村子的？村里有几口井？村东头那棵老槐树有多粗？"),
            Dialogue(None, "那人支支吾吾，回答得漏洞百出。"),
            Dialogue(None, "在我的追问下，他终于露出了马脚——他说的那个村子，根本就没有老槐树！"),
            Dialogue(None, "原来他是日军派来的探子！我们及时识破了阴谋，避免了队伍陷入伏击。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_4b",
        background="bg_ch3_4b",
        dialogues=[
            Dialogue(None, "我心生怜悯，觉得他不过是个普通百姓，便挥挥手让他走了。"),
            Dialogue(None, "没想到此人果然是日军探子，他跑下山后不久，队伍就遭到了日军的伏击。"),
            Dialogue(None, "枪声突然响起，队伍陷入一片混乱，虽然最终击退了敌人，但还是有几名战士受了伤。"),
            Dialogue(None, "看着战友们包扎伤口时痛苦的表情，我心中充满了懊悔。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_4c",
        background="bg_ch3_4c",
        dialogues=[
            Dialogue(None, "我将人带到左权面前，首长仔细打量了那人一番，然后问了几个看似无关紧要的问题。"),
            Dialogue("左权", "你说你是逃难的，那你身上为什么没有一点干粮的味道？"),
            Dialogue(None, "那人脸色一变，支支吾吾说不出话来。"),
            Dialogue("左权", "怀安做得对，遇事不擅作主张。"),
            Dialogue(None, "在将军面前，任何伪装都无所遁形。那人被揭穿后，终于承认了自己的身份。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_3_transition",
        background="bg_ch3_3_transition",
        dialogues=[
            Dialogue(None, "隐患清除，队伍重新整队前行。经过探子一事，所有人的警惕性提到了最高。"),
            Dialogue(None, "又前行数百米，前方出现一处陡峭的山壁斜坡，一段危险的绳索桥横亘在眼前。"),
            Dialogue("战士", "首长，这段山路的防护绳索多处松动！"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_6",
        background="bg_ch3_6",
        dialogues=[
            Dialogue(None, "我凑上前看去，粗麻绳被雨水浸泡后沉重打滑，几处绑定的位置确实岌岌可危。"),
            Dialogue(None, "身后的追兵随时可能追来，原地停留越久风险越高；可若是贸然通行，后果同样不堪设想。"),
            Dialogue(None, "战士们都停下脚步，看向左权，等待指令。"),
        ],
        choices=[
            Choice(
                text="停下脚步，立刻动手加固危险路段绳索",
                effects={"relation": 2, "trust": 1},
                next_scene="ch3_7a",
                flag="reinforce_rope"
            ),
            Choice(
                text="提醒众人小心，催促队伍快速通过",
                effects={"guilt": 1},
                next_scene="ch3_7b",
                flag="rush_through"
            ),
            Choice(
                text="先行通知前方队伍停下，统一排查路况",
                effects={"trust": 2},
                next_scene="ch3_7c",
                flag="halt_and_check"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_7a",
        background="bg_ch3_7a",
        dialogues=[
            Dialogue(None, "我招呼几名战士一起动手加固绳索。"),
            Dialogue(None, "我们用随身携带的铁丝和木棍将松动的木桩重新固定，确保每一根绳索都牢固可靠。"),
            Dialogue(None, "老周虽然还很虚弱，但也挣扎着坐起来，帮我们传递工具。"),
            Dialogue(None, "经过半个时辰的努力，路段终于稳固了。后续的伤员和百姓通过时，都安全无恙。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_7b",
        background="bg_ch3_7b",
        dialogues=[
            Dialogue(None, "我大声提醒大家小心，队伍加快速度通过。"),
            Dialogue(None, "大部分人都平安到达了对岸，可就在最后一名战士快要到达时，一根绳索突然断裂！"),
            Dialogue(None, "他脚下打滑，身体瞬间失去平衡，朝着山涧坠去！"),
            Dialogue(None, "幸好旁边的战友眼疾手快，一把抓住了他的胳膊，众人合力将他拉了上来。"),
            Dialogue(None, "所有人都惊出一身冷汗，我更是心有余悸。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_7c",
        background="bg_ch3_7c",
        dialogues=[
            Dialogue(None, "我迅速跑到队伍前方，通知所有人停下。"),
            Dialogue(None, "我们仔细排查了整条路段，不仅加固了绳索，还清理了路面松动的碎石。"),
            Dialogue(None, "谨慎行事，才能确保所有人的安全。"),
            Dialogue("左权", "怀安考虑得很周全。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch3_6_transition",
        background="bg_ch3_6_transition",
        dialogues=[
            Dialogue(None, "险坡路段顺利通过，队伍终于抵达十字岭中段区域。"),
            Dialogue(None, "此处地势开阔一些，林木相对稀疏，可也正因如此，我们彻底暴露在了日军的炮火射程之内。"),
            Dialogue(None, "天际传来沉闷的轰鸣声，日军主力终于追上来了。"),
        ]
    ))
    
    # ========== 第四章：炮火连天 ==========
    engine.add_scene(Scene(
        id="ch4_1",
        background="bg_ch4_1",
        dialogues=[
            Dialogue(None, "炮弹呼啸着划破浓雾，接二连三地落在队伍周边。"),
            Dialogue(None, "「轰隆！轰隆！」巨响震得地面微微颤抖，碎石、泥土混杂着断枝四处飞溅。"),
            Dialogue(None, "战士们立刻就地卧倒，躲避炮火袭击。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_2",
        background="bg_ch4_2",
        dialogues=[
            Dialogue(None, "炮火稍歇，队伍重新集结。清点人数时发现，又有几名战士挂了彩。"),
            Dialogue(None, "队伍里的重伤员已经有十几名，他们无法快速奔走。"),
            Dialogue(None, "若是带着他们突围，速度会大幅减慢；若是留下他们，无异于让他们送死。"),
            Dialogue(None, "所有人都陷入了两难。左权看着伤员们痛苦的表情，眉头紧锁，一言不发。"),
        ],
        choices=[
            Choice(
                text="留下几名战士一同就地隐蔽，掩护伤员暂避",
                effects={"relation": 2},
                next_scene="ch4_3a",
                flag="stay_with_wounded"
            ),
            Choice(
                text="全员咬紧牙关，带着伤员强行一同突围",
                effects={"relation": 3, "trust": 2},
                next_scene="ch4_3b",
                flag="carry_wounded"
            ),
            Choice(
                text="把伤员托付给深山隐秘农户，轻装快速撤离",
                effects={"guilt": 2},
                next_scene="ch4_3c",
                flag="entrust_wounded"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_3a",
        background="bg_ch4_3a",
        dialogues=[
            Dialogue(None, "我主动站出来，带领几名战士留下。"),
            Dialogue(None, "我们将伤员安置在一处隐蔽的山洞里，用树枝和茅草把洞口伪装好。"),
            Dialogue("老周", "小兄弟，谢谢你..."),
            Dialogue("陈怀安", "排长，好好养伤，我们会尽快回来接你们。"),
            Dialogue(None, "我们轮流警戒，等待大部队安全撤离后再想办法跟上。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_3b",
        background="bg_ch4_3b",
        dialogues=[
            Dialogue(None, "没有人放弃伤员，我们用简易担架轮流抬着重伤的战友，相互搀扶着继续前进。"),
            Dialogue(None, "牛娃虽然脚伤还没好利索，却也主动帮着抬担架；卫生员背着沉重的药箱，一路小跑跟在队伍旁边。"),
            Dialogue(None, "没有人抱怨，没有人退缩，战友情谊在这一刻达到了顶峰。"),
            Dialogue(None, "左权走在队伍最后，时不时回头看看伤员，眼神里满是欣慰。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_3c",
        background="bg_ch4_3c",
        dialogues=[
            Dialogue(None, "我们将伤员托付给了深山里的农户。"),
            Dialogue("大娘", "同志们放心，我一定会好好照顾他们。"),
            Dialogue(None, "虽然减轻了负担，但每个人的心里都沉甸甸的。"),
            Dialogue(None, "不知道这些战友们能否平安度过这场劫难，也许我们再也没有机会相见了。"),
            Dialogue(None, "队伍继续前进，身后传来伤员们微弱的告别声，我不敢回头，生怕泪水会忍不住流下来。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_2_transition",
        background="bg_ch4_2_transition",
        dialogues=[
            Dialogue(None, "伤员安置妥当，队伍继续向十字岭主峰进发。"),
            Dialogue(None, "日军的炮火越来越近，层层包围圈不断收缩，突围的通道越来越狭窄。"),
            Dialogue(None, "左权根据战局变化，迅速调整部署，准备组织精锐力量组成断后小队。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_4",
        background="bg_ch4_4",
        dialogues=[
            Dialogue("左权", "同志们，现在需要有人留下来断后，掩护大部队撤离。"),
            Dialogue("左权", "这是一项危险的任务，愿意留下的同志请出列。"),
            Dialogue(None, "他的目光扫过每一个人，最后落在我的身上。"),
            Dialogue(None, "结合此前的选择，身边战友的态度也各不相同。"),
        ],
        choices=[
            Choice(
                text="主动请缨留下来断后，阻拦追兵掩护大部队",
                effects={"relation": 3, "trust": 3},
                next_scene="ch4_5a",
                flag="volunteer_rearguard"
            ),
            Choice(
                text="服从调配，跟随首长居中护卫机关人员",
                effects={"trust": 1},
                next_scene="ch4_5b",
                flag="follow_leader"
            ),
            Choice(
                text="借口身体疲累，申请跟随前路队伍先行转移",
                effects={"relation": -3, "guilt": 3},
                next_scene="ch4_5c",
                flag="avoid_rearguard"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_5a",
        background="bg_ch4_5a",
        dialogues=[
            Dialogue("陈怀安", "我留下！"),
            Dialogue(None, "「我也留下来！」「算我一个！」看到我主动请命，几名战友也纷纷站了出来。"),
            Dialogue(None, "我们紧握手中的武器，准备迎接即将到来的恶战。"),
            Dialogue("左权", "怀安，保重。"),
            Dialogue(None, "身后，大部队正在向十字岭方向撤退，我们这些留下来断后的战士，将用自己的血肉之躯，为他们争取宝贵的时间。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_5b",
        background="bg_ch4_5b",
        dialogues=[
            Dialogue("左权", "好，怀安，你跟在我身边。"),
            Dialogue(None, "我紧紧跟随着首长，警惕地观察着四周，确保他的安全。"),
            Dialogue(None, "这是我的职责，也是我的使命。"),
            Dialogue(None, "断后的战友们已经就位，远处传来了激烈的枪声。"),
            Dialogue("左权", "告诉同志们，加快速度，一定要安全突围！"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_5c",
        background="bg_ch4_5c",
        dialogues=[
            Dialogue("陈怀安", "首长，我...我有点累了，想跟着前路队伍先走一步。"),
            Dialogue(None, "说完这句话，我感觉脸上火辣辣的。"),
            Dialogue(None, "左权看了我一眼，没有说什么，只是点了点头。"),
            Dialogue(None, "我转身跟着前路队伍走了，身后传来激烈的枪声，那是断后的战友们在与日军殊死搏斗。"),
            Dialogue(None, "我不敢回头，只能加快脚步，可那份沉甸甸的愧疚，却怎么也甩不掉。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch4_4_transition",
        background="bg_ch4_4_transition",
        dialogues=[
            Dialogue(None, "部队抵达十字岭核心区域，日军已经完成合围，大规模总攻正式打响。"),
            Dialogue(None, "枪林弹雨笼罩着整个山岭，突围通道被死死封锁。"),
            Dialogue(None, "左权毅然决定留在最高处指挥断后，不肯独自先行撤离。"),
        ]
    ))
    
    # ========== 第五章：生死绝境 ==========
    engine.add_scene(Scene(
        id="ch5_1",
        background="bg_ch5_1",
        dialogues=[
            Dialogue(None, "他站在山岭最高处，手持望远镜观察着战局，身边只有几名警卫员陪着他。"),
            Dialogue(None, "为了掩护机关干部、伤员和百姓全部冲出包围圈，他选择了最危险的位置。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_2",
        background="bg_ch5_2",
        dialogues=[
            Dialogue(None, "看着首长坚定的背影，我的心里五味杂陈。"),
            Dialogue(None, "一路朝夕相处，他对我的关怀、信任，一幕幕浮现在眼前。"),
            Dialogue(None, "现在，他要独自面对最危险的局面。"),
        ],
        choices=[
            Choice(
                text="含泪极力劝说首长立刻跟着主力突围保命",
                effects={"trust": 1},
                next_scene="ch5_3a",
                flag="persuade_leader"
            ),
            Choice(
                text="默默持枪站立，誓死留在首长身边一同坚守",
                effects={"relation": 3, "trust": 2},
                next_scene="ch5_3b",
                flag="stay_with_leader"
            ),
            Choice(
                text="听从命令，护送其他干部先行冲出封锁线",
                effects={"guilt": 1},
                next_scene="ch5_3c",
                flag="escort_others"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_3a",
        background="bg_ch5_3a",
        dialogues=[
            Dialogue("陈怀安", "首长！您不能留下！太危险了！"),
            Dialogue("左权", "怀安，你的心意我明白。"),
            Dialogue("左权", "但我是这里的最高指挥官，我必须留下。告诉同志们，一定要把百姓和伤员安全送出去！"),
            Dialogue(None, "他的声音坚定有力，不容置疑。我知道，劝说已经没用了，他早已下定了决心。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_3b",
        background="bg_ch5_3b",
        dialogues=[
            Dialogue(None, "我没有说话，只是默默走到首长身边，持枪站立。"),
            Dialogue("左权", "好样的，怀安！有你在，我很安心。"),
            Dialogue(None, "我们并肩站在山岭最高处，看着山下如潮水般涌来的日军。"),
            Dialogue(None, "炮火越来越猛烈，炮弹不断在我们身边爆炸。"),
            Dialogue(None, "我紧紧握着枪，随时准备应对任何突发情况。能陪首长走完最后一程，是我作为警卫员的荣幸。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_3c",
        background="bg_ch5_3c",
        dialogues=[
            Dialogue(None, "我服从命令，护送着几位机关干部向山下突围。"),
            Dialogue(None, "走了几步，我忍不住回头望去，左权将军的身影依然屹立在山顶，指挥着最后的战斗。"),
            Dialogue(None, "阳光透过硝烟照在他身上，仿佛给他镀上了一层金色的光辉。"),
            Dialogue(None, "我只能在心里默默祈祷，希望首长能够平安。但我知道，这个愿望，可能很难实现了。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_2_transition",
        background="bg_ch5_2_transition",
        dialogues=[
            Dialogue(None, "炮火愈发猛烈，日军的进攻一浪高过一浪。"),
            Dialogue(None, "突然，一枚炮弹拖着长长的尾焰，正朝着指挥位置飞速袭来。"),
            Dialogue(None, "危险就在眼前，时间仿佛凝固了。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_4",
        background="bg_ch5_4",
        dialogues=[
            Dialogue(None, "周围的战士们都愣住了，没人来得及做出反应。"),
            Dialogue(None, "我的大脑一片空白，身体却本能地做出了反应。"),
        ],
        choices=[
            Choice(
                text="不顾一切纵身扑上前，试图掩护首长",
                effects={"relation": 2, "trust": 2},
                next_scene="ch5_5a",
                flag="shield_leader"
            ),
            Choice(
                text="大声嘶吼警报，招呼周围所有人迅速卧倒",
                effects={"trust": 1},
                next_scene="ch5_5b",
                flag="alert_everyone"
            ),
            Choice(
                text="本能俯身躲避冲击，保全自身性命",
                effects={"guilt": 3},
                next_scene="ch5_5c",
                flag="self_protect"
            )
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_5a",
        background="bg_ch5_5a",
        dialogues=[
            Dialogue(None, "我不顾一切地扑向左权将军，但炮弹的速度太快了。"),
            Dialogue(None, "巨大的冲击波将我掀翻在地，我感到一阵剧痛，眼前渐渐模糊。"),
            Dialogue(None, "在失去意识的最后一刻，我看到了将军倒下的身影..."),
            Dialogue(None, "那一刻，时间仿佛停止了。我用尽最后一丝力气想要爬过去，却怎么也动不了。"),
            Dialogue(None, "泪水混合着血水从眼角滑落，我知道，我没能保护好首长。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_5b",
        background="bg_ch5_5b",
        dialogues=[
            Dialogue("陈怀安", "卧倒！"),
            Dialogue(None, "周围的战士们纷纷扑倒在地，减少了伤亡。"),
            Dialogue(None, "但那枚炮弹还是落在了指挥位置...巨大的爆炸声响起，火光冲天。"),
            Dialogue(None, "我挣扎着爬起来，看向指挥位置，只看到一片浓烟和碎石。"),
            Dialogue(None, "首长...首长他...我的喉咙像是被堵住了，一句话也说不出来。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_5c",
        background="bg_ch5_5c",
        dialogues=[
            Dialogue(None, "强烈的求生本能让我下意识地俯身躲避。"),
            Dialogue(None, "爆炸过后，我缓缓抬起头，看到的却是将军倒在血泊中的身影。"),
            Dialogue(None, "那一刻，无尽的悔恨如同潮水般将我淹没。"),
            Dialogue(None, "我明明可以冲上去保护他的，可我却选择了保全自己。"),
            Dialogue(None, "首长平时对我那么好，关键时刻我却退缩了。这份愧疚，注定要伴随我一生。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_4_transition",
        background="bg_ch5_4_transition",
        dialogues=[
            Dialogue(None, "左权将军不幸中弹，壮烈牺牲。"),
            Dialogue(None, "残存的众人强忍悲痛，围在将军身边，默默敬礼。"),
            Dialogue(None, "炮火还在继续，日军还在进攻，但所有人都知道，必须抓紧最后的机会冲破封锁。"),
        ]
    ))
    
    engine.add_scene(Scene(
        id="ch5_6",
        background="bg_ch5_6",
        dialogues=[
            Dialogue(None, "将军用他的生命为我们争取了时间，我们不能辜负他的牺牲。"),
        ],
        choices=[
            Choice(
                text="强忍悲痛，带头鼓舞战友士气，全力冲锋突围",
                effects={"relation": 2},
                next_scene="ending",
                flag="lead_charge"
            ),
            Choice(
                text="停下脚步，肃穆低头送别将军，久久不愿离去",
                effects={"trust": 1},
                next_scene="ending",
                flag="farewell_leader"
            ),
            Choice(
                text="压抑心绪，沉默跟随队伍，沉默冲出山岭",
                effects={},
                next_scene="ending",
                flag="silent_escape"
            )
        ]
    ))
    
    return engine


if __name__ == "__main__":
    game = create_game()
    game.run()
