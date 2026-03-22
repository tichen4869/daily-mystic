"""每日玄学 - 云端版（多用户，生辰存浏览器）"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify

import cnlunar

app = Flask(__name__)

# ─── 天干地支 & 五行映射 ───

TIAN_GAN = "甲乙丙丁戊己庚辛壬癸"
DI_ZHI = "子丑寅卯辰巳午未申酉戌亥"

GAN_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}
ZHI_WUXING = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

WUXING_COLOR = {
    "金": ["白色", "银色"], "木": ["绿色", "青色"],
    "水": ["黑色", "深蓝"], "火": ["红色", "紫色"], "土": ["黄色", "棕色"],
}
WUXING_SHENG = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}
WUXING_KE = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}
WUXING_SHENG_BY = {"水": "金", "木": "水", "火": "木", "土": "火", "金": "土"}

CAISHEN_MAP = {
    "甲": "东北", "乙": "东方", "丙": "西南", "丁": "西方",
    "戊": "北方", "己": "南方", "庚": "东南", "辛": "南方",
    "壬": "南方", "癸": "东南",
}

SHICHEN_TIME = {
    "子": "23:00-01:00", "丑": "01:00-03:00", "寅": "03:00-05:00",
    "卯": "05:00-07:00", "辰": "07:00-09:00", "巳": "09:00-11:00",
    "午": "11:00-13:00", "未": "13:00-15:00", "申": "15:00-17:00",
    "酉": "17:00-19:00", "戌": "19:00-21:00", "亥": "21:00-23:00",
}

YI_JI_TRANSLATE = {
    "祭祀": "祭拜祖先", "祈福": "许愿求福", "求嗣": "备孕求子",
    "开光": "饰品开光", "塑绘": "画画手工", "沐浴": "洗澡SPA",
    "出行": "出门旅行", "嫁娶": "结婚", "裁衣": "买衣做衣",
    "安床": "搬床换床", "开市": "开业开张", "立券": "签合同",
    "交易": "买卖交易", "纳财": "收钱理财", "入宅": "搬家入住",
    "移徙": "搬家", "修造": "装修", "动土": "破土动工",
    "纳采": "提亲订婚", "解除": "打扫清理", "入学": "入学报名",
    "会亲友": "聚会社交", "栽种": "种花种菜", "取渔": "钓鱼",
    "安葬": "下葬", "破土": "动工挖地", "冠带": "穿戴打扮",
    "上梁": "房屋封顶", "竖柱": "立柱搭架", "放水": "排水通渠",
    "纳畜": "买宠物", "修饰垣墙": "修墙装修", "平治道涂": "整理环境",
    "伐木": "砍树清理", "畋猎": "户外冒险", "酝酿": "酿酒策划",
    "结网": "社交拓展", "扫舍": "打扫房间", "置产": "买房买地",
    "恤孤茕": "做慈善", "覃恩": "做善事", "宴会": "聚餐",
    "求医疗病": "看病体检", "整容": "美容护肤", "剃头": "理发",
    "整手足甲": "美甲", "作灶": "装修厨房", "习艺": "学习新技能",
    "齐醮": "祈祷", "斋醮": "祈祷", "酬神": "还愿感恩",
    "出火": "搬灶台", "安香": "安放香炉", "订盟": "结盟签约",
    "捕捉": "猎取", "经络": "织网编织",
}

NAYIN = [
    "海中金", "海中金", "炉中火", "炉中火", "大林木", "大林木",
    "路旁土", "路旁土", "剑锋金", "剑锋金", "山头火", "山头火",
    "涧下水", "涧下水", "城头土", "城头土", "白蜡金", "白蜡金",
    "杨柳木", "杨柳木", "泉中水", "泉中水", "屋上土", "屋上土",
    "霹雳火", "霹雳火", "松柏木", "松柏木", "长流水", "长流水",
    "沙中金", "沙中金", "山下火", "山下火", "平地木", "平地木",
    "壁上土", "壁上土", "金箔金", "金箔金", "覆灯火", "覆灯火",
    "天河水", "天河水", "大驿土", "大驿土", "钗钏金", "钗钏金",
    "桑柘木", "桑柘木", "大溪水", "大溪水", "沙中土", "沙中土",
    "天上火", "天上火", "石榴木", "石榴木", "大海水", "大海水",
]

# 日干基础性格
GAN_BASE = {
    "甲": "如参天大树，正直刚毅",
    "乙": "如花草藤蔓，柔韧灵活",
    "丙": "如太阳烈火，热情奔放",
    "丁": "如烛火星光，温暖细腻",
    "戊": "如高山大地，厚重稳健",
    "己": "如田园沃土，温和务实",
    "庚": "如刀剑精铁，果断刚强",
    "辛": "如珠玉宝石，精致敏锐",
    "壬": "如江河大海，智慧深沉",
    "癸": "如雨露清泉，聪慧内敛",
}

# 身强/身弱补充特质
STRENGTH_TRAIT = {
    "强": "精力充沛，主见强，有时过于坚持己见",
    "弱": "心思细腻，善于察言观色，适合借助外力成事",
}

# 五行偏旺的性格倾向
WX_DOMINANT_TRAIT = {
    "金": "做事果断利落，重规则讲原则",
    "木": "富有同情心，追求成长和突破",
    "水": "思维活跃，善于变通，人缘好",
    "火": "行动力强，热心肠，容易冲动",
    "土": "踏实可靠，重信守诺，偏保守",
}

# 五行缺失的提醒
WX_LACK_TRAIT = {
    "金": "决断力不足，可多听果断之人的建议",
    "木": "有时缺乏耐心，可多接触自然放松身心",
    "水": "灵活性欠缺，可多拓宽社交圈",
    "火": "行动力偏弱，需要外界推动力",
    "土": "安全感不够，可多培养稳定的生活节奏",
}

# 月令季节对性格的影响
SEASON_TRAIT = {
    "春": "内心向阳，喜欢新事物，有开拓精神",
    "夏": "性格明快，表达欲强，感染力足",
    "秋": "内心沉稳，审美在线，有品味追求",
    "冬": "思虑深远，低调内敛，后劲十足",
}

MONTH_SEASON = {
    "寅": "春", "卯": "春", "辰": "春",
    "巳": "夏", "午": "夏", "未": "夏",
    "申": "秋", "酉": "秋", "戌": "秋",
    "亥": "冬", "子": "冬", "丑": "冬",
}

def build_trait(day_gan, is_strong, wuxing_count, month_zhi):
    """根据日干+强弱+五行分布+月令生成定制性格描述"""
    parts = []

    # 1. 日干基础
    parts.append(GAN_BASE[day_gan])

    # 2. 季节影响
    season = MONTH_SEASON.get(month_zhi, "春")
    parts.append(SEASON_TRAIT[season])

    # 3. 身强/弱特质
    parts.append(STRENGTH_TRAIT["强" if is_strong else "弱"])

    # 4. 最旺的五行（除日主本身）
    day_wx = GAN_WUXING[day_gan]
    others = {k: v for k, v in wuxing_count.items() if k != day_wx}
    if others:
        dominant = max(others, key=others.get)
        if others[dominant] >= 2:
            parts.append(WX_DOMINANT_TRAIT[dominant])

    # 5. 缺失的五行
    lacks = [k for k, v in wuxing_count.items() if v == 0]
    if lacks:
        parts.append(WX_LACK_TRAIT[lacks[0]])

    return "。".join(parts)


# ─── 计算函数 ───

def year_ganzhi(year):
    return TIAN_GAN[(year - 4) % 10] + DI_ZHI[(year - 4) % 12]

def month_ganzhi(year, month):
    yg_idx = (year - 4) % 10
    mg_idx = ((yg_idx % 5) * 2 + (month - 1)) % 10
    mz_idx = (month + 1) % 12
    return TIAN_GAN[mg_idx] + DI_ZHI[mz_idx]

def day_ganzhi_from_date(dt):
    base = datetime(1900, 1, 1)
    delta = (dt.replace(hour=0, minute=0, second=0) - base).days
    offset = (delta + 10) % 60
    return TIAN_GAN[offset % 10] + DI_ZHI[offset % 12]

def hour_ganzhi(day_gan, hour):
    zhi_idx = ((hour + 1) % 24) // 2
    dg_idx = TIAN_GAN.index(day_gan)
    hg_idx = ((dg_idx % 5) * 2 + zhi_idx) % 10
    return TIAN_GAN[hg_idx] + DI_ZHI[zhi_idx]

def calc_bazi(dt):
    """使用 cnlunar 计算八字（正确处理节气）"""
    a = cnlunar.Lunar(dt, godType="8char")
    return a.year8Char, a.month8Char, a.day8Char, a.twohour8Char

def bazi_wuxing(bazi):
    count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for p in bazi:
        count[GAN_WUXING[p[0]]] += 1
        count[ZHI_WUXING[p[1]]] += 1
    return count

# 月支对应的当令五行（月令）
YUELING = {
    "寅": "木", "卯": "木",  # 春
    "巳": "火", "午": "火",  # 夏
    "申": "金", "酉": "金",  # 秋
    "亥": "水", "子": "水",  # 冬
    "辰": "土", "未": "土", "戌": "土", "丑": "土",  # 四季土
}

def analyze_bazi(bazi):
    day_gan = bazi[2][0]
    day_wx = GAN_WUXING[day_gan]
    yg_idx = TIAN_GAN.index(bazi[0][0])
    yz_idx = DI_ZHI.index(bazi[0][1])
    gz60 = next(i for i in range(60) if i % 10 == yg_idx and i % 12 == yz_idx)
    nayin = NAYIN[gz60]
    wc = bazi_wuxing(bazi)
    sheng_me = WUXING_SHENG_BY[day_wx]

    # 月令判断：月支的五行是否帮身
    month_zhi = bazi[1][1]
    month_wx = YUELING.get(month_zhi, "土")
    month_helps = (month_wx == day_wx or month_wx == sheng_me)

    # 计算帮身力量（同类+生我），加月令权重
    help_score = wc[day_wx] + wc[sheng_me]
    hurt_score = sum(wc[x] for x in wc if x != day_wx and x != sheng_me)

    # 月令得令 +2 分权重（月令是八字中最重要的因素）
    if month_helps:
        help_score += 2
    else:
        hurt_score += 2

    is_strong = help_score > hurt_score

    if is_strong:
        xi, yong = WUXING_KE[day_wx], WUXING_SHENG[day_wx]
        ji = [day_wx, sheng_me]
        sd = "身强"
    else:
        xi, yong = sheng_me, day_wx
        # 身弱忌：克我、泄我、耗我
        ke_me = [k for k, v in WUXING_KE.items() if v == day_wx]  # 谁克我
        ji = list(set([WUXING_SHENG[day_wx], WUXING_KE[day_wx]] +
                      [x for x in wc if x != day_wx and x != sheng_me]))
        # 简化：忌 = 食伤(泄) + 财(耗) + 官杀(克) = 除了同类和印之外的
        ji = [x for x in ["金","木","水","火","土"] if x != day_wx and x != sheng_me]
        sd = "身弱"

    trait = build_trait(day_gan, is_strong, wc, month_zhi)

    return {
        "ming": f"{nayin}命", "rizhu": f"{day_gan}{day_wx}",
        "qiangruo": sd, "xingge": trait,
        "xi": [xi, yong], "ji": ji,
    }

# 近义词合并（保留前面的）
SYNONYMS = {
    "做慈善": "做善事",
    "做好事": "做善事",
    "施恩、做善事": "做善事",
    "结婚": "结婚",
    "结婚姻": "结婚",
    "搬家入住": "搬家",
    "搬家": "搬家",
    "看病、体检": "看病",
    "看病": "看病",
    "做法事": "祈祷",
    "做法事、祈祷": "祈祷",
    "装修房屋": "装修",
    "装修": "装修",
    "破土动工": "动工挖地",
    "动工挖地": "动工挖地",
    "学习新技能": "学习进修",
    "学习、进修": "学习进修",
    "入学、报名": "学习进修",
    "提亲、订婚": "订婚",
    "合八字": "订婚",
}

def translate(items):
    result = []
    seen = set()
    for x in items:
        modern = YI_JI_TRANSLATE.get(x, x)
        # 合并近义词
        canonical = SYNONYMS.get(modern, modern)
        if canonical not in seen:
            seen.add(canonical)
            result.append(canonical)
    return result

SHICHEN_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def get_lucky_hours(a, xi_list=None):
    """从 cnlunar 的吉凶列表提取吉时，按与喜用神匹配度排序"""
    try:
        lucky_list = a.get_twohourLuckyList()
    except Exception:
        return ["卯时(05:00-07:00)", "巳时(09:00-11:00)"]

    xi_list = xi_list or []
    items = []
    for i, status in enumerate(lucky_list[:12]):
        if status == "吉":
            zhi = SHICHEN_NAMES[i]
            zhi_wx = ZHI_WUXING[zhi]
            # 吉时中与喜用神匹配的排在前面
            score = 2 if zhi_wx in xi_list else 1
            items.append((score, f"{zhi}时({SHICHEN_TIME[zhi]})"))

    items.sort(key=lambda x: -x[0])
    result = [x[1] for x in items]
    return result[:4] if result else ["卯时(05:00-07:00)"]

def get_daily(target):
    a = cnlunar.Lunar(target, godType="8char")
    gz = day_ganzhi_from_date(target)
    wx = GAN_WUXING[gz[0]]
    yi_raw = translate(a.goodThing[:8]) if a.goodThing else ["诸事不宜"]
    ji_raw = translate(a.badThing[:8]) if a.badThing else ["百无禁忌"]

    # 去重（翻译后意思相同的只保留一个）
    yi = list(dict.fromkeys(yi_raw))[:6]
    ji = list(dict.fromkeys(ji_raw))[:6]

    conflict = list(set(yi) & set(ji))
    jishi = get_lucky_hours(a)
    return {
        "lunar": f"{a.lunarMonthCn}{a.lunarDayCn}",
        "gz": gz, "wx": wx,
        "yi": yi, "ji": ji, "jishi": jishi,
        "caishen": CAISHEN_MAP.get(gz[0], "南方"),
        "conflict": conflict,
    }

def get_advice(bazi, daily, analysis):
    day_wx = daily["wx"]
    xi_wx = analysis["xi"][0]
    colors = WUXING_COLOR[xi_wx]
    outfit = f"{colors[0]}或{colors[1]}系"
    icons = {"up": "😊", "down": "😢", "neutral": "😐"}

    if day_wx in analysis["xi"]:
        msg = f"今日{day_wx}气当令，合你喜用，运势上扬"
        level = "up"
    elif day_wx in analysis["ji"]:
        msg = f"今日{day_wx}气偏旺，非你所喜，宜守不宜攻"
        level = "down"
    else:
        msg = f"今日{day_wx}气平稳，顺势而为即可"
        level = "neutral"

    wx_num = {"金": "4、9", "木": "3、8", "水": "1、6", "火": "2、7", "土": "5、0"}
    return {
        "outfit": outfit, "msg": msg, "level": level,
        "icon": icons[level], "lucky_num": wx_num.get(xi_wx, "8"),
    }


# ─── API ───

@app.route("/api/fortune")
def api_fortune():
    """核心 API：传入生辰和目标日期，返回所有数据"""
    birth = request.args.get("birth", "")
    date = request.args.get("date", "")

    try:
        birth_dt = datetime.strptime(birth, "%Y/%m/%d/%H:%M")
    except Exception:
        birth_dt = None

    try:
        target = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    except Exception:
        target = datetime.now()

    daily = get_daily(target)

    result = {
        "date_solar": target.strftime("%Y.%m.%d"),
        "date_iso": target.strftime("%Y-%m-%d"),
        "lunar": daily["lunar"],
        "gz": daily["gz"],
        "wx": daily["wx"],
        "yi": daily["yi"],
        "ji": daily["ji"],
        "jishi": daily["jishi"],
        "caishen": daily["caishen"],
    }

    if birth_dt:
        bazi = calc_bazi(birth_dt)
        analysis = analyze_bazi(bazi)
        advice = get_advice(bazi, daily, analysis)

        # 根据八字解决宜忌冲突
        if daily["conflict"]:
            day_wx = daily["wx"]
            xi = analysis["xi"]
            ji_wx = analysis["ji"]
            for item in daily["conflict"]:
                # 当日五行合喜用 → 这件事今天对你有利 → 留在宜
                # 当日五行合忌神 → 这件事今天对你不利 → 留在忌
                if day_wx in xi:
                    result["ji"] = [x for x in result["ji"] if x != item]
                elif day_wx in ji_wx:
                    result["yi"] = [x for x in result["yi"] if x != item]
                else:
                    # 中性日：看这件事本身偏动还是偏静
                    # 偏动的事（出行、交易、开业等）在中性日归宜
                    active_words = ["出门", "旅行", "交易", "买卖", "开业", "开张", "搬家",
                                    "结婚", "签合同", "入职", "聚会", "社交"]
                    is_active = any(w in item for w in active_words)
                    if is_active:
                        result["ji"] = [x for x in result["ji"] if x != item]
                    else:
                        result["yi"] = [x for x in result["yi"] if x != item]

        # 重新按喜用神排序吉时
        a = cnlunar.Lunar(target, godType="8char")
        result["jishi"] = get_lucky_hours(a, analysis["xi"])
        result.update({
            "bazi": list(bazi),
            "ming": analysis["ming"],
            "rizhu": analysis["rizhu"],
            "qiangruo": analysis["qiangruo"],
            "xingge": analysis["xingge"],
            "xi": analysis["xi"],
            "ji_wx": analysis["ji"],
            "luck_level": advice["level"],
            "luck_icon": advice["icon"],
            "luck_msg": advice["msg"],
            "outfit": advice["outfit"],
            "lucky_num": advice["lucky_num"],
        })
        # 五行主题色
        wx_theme = {
            "金": ["#C4A44A", "rgba(196,164,74,0.06)"],
            "木": ["#7A9E6B", "rgba(122,158,107,0.06)"],
            "水": ["#6B9AB5", "rgba(107,154,181,0.06)"],
            "火": ["#C47A5A", "rgba(196,122,90,0.06)"],
            "土": ["#B5A06B", "rgba(181,160,107,0.06)"],
        }
        t = wx_theme.get(daily["wx"], wx_theme["土"])
        result["particle_color"] = t[0]
        result["glow_color"] = t[1]

    return jsonify(result)


@app.route("/api/voice")
def api_voice():
    """返回语音播报文本"""
    birth = request.args.get("birth", "")
    date = request.args.get("date", "")

    try:
        birth_dt = datetime.strptime(birth, "%Y/%m/%d/%H:%M")
    except Exception:
        return jsonify({"text": "请先设置你的生辰"})

    try:
        target = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    except Exception:
        target = datetime.now()

    daily = get_daily(target)
    bazi = calc_bazi(birth_dt)
    analysis = analyze_bazi(bazi)
    advice = get_advice(bazi, daily, analysis)

    # 根据运势级别用不同语气
    if advice["level"] == "up":
        opening = "早安呀！今天运势不错哦。"
        closing = "总之今天很适合行动，加油！"
    elif advice["level"] == "down":
        opening = "早安。今天能量稍弱，别着急。"
        closing = "稳一点就好，明天会更好的。"
    else:
        opening = "早安。今天运势平平稳稳的。"
        closing = "顺其自然就好，祝你今天开心。"

    yi_str = '、'.join(daily['yi'][:3])
    ji_str = '、'.join(daily['ji'][:3])

    text = (
        f"{opening}"
        f"今天是农历{daily['lunar']}，{advice['msg']}。"
        f"穿搭的话，今天穿{advice['outfit']}会比较旺。"
        f"财神方位在{daily['caishen']}。"
        f"适合做的事呢，有{yi_str}。"
        f"不太建议{ji_str}。"
        f"{closing}"
    )

    return jsonify({"text": text})


@app.route("/api/speak")
def api_speak():
    """生成语音 MP3（用 Google Translate TTS）"""
    import urllib.request
    import tempfile

    birth = request.args.get("birth", "")
    date = request.args.get("date", "")

    try:
        birth_dt = datetime.strptime(birth, "%Y/%m/%d/%H:%M")
    except Exception:
        return "missing birth", 400

    try:
        target = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    except Exception:
        target = datetime.now()

    daily = get_daily(target)
    bazi = calc_bazi(birth_dt)
    analysis = analyze_bazi(bazi)
    advice = get_advice(bazi, daily, analysis)

    if advice["level"] == "up":
        opening = "早安呀！今天运势不错哦。"
        closing = "总之今天很适合行动，加油！"
    elif advice["level"] == "down":
        opening = "早安。今天能量稍弱，别着急。"
        closing = "稳一点就好，明天会更好的。"
    else:
        opening = "早安。今天运势平平稳稳的。"
        closing = "顺其自然就好，祝你今天开心。"

    yi_str = '、'.join(daily['yi'][:3])
    ji_str = '、'.join(daily['ji'][:3])

    text = (
        f"{opening}"
        f"今天是农历{daily['lunar']}，{advice['msg']}。"
        f"穿搭的话，今天穿{advice['outfit']}会比较旺。"
        f"财神方位在{daily['caishen']}。"
        f"适合做的事呢，有{yi_str}。"
        f"不太建议{ji_str}。"
        f"{closing}"
    )

    # 尝试 edge-tts（本地），失败则用 gTTS
    try:
        import asyncio
        import edge_tts
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        async def gen():
            c = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural", rate="+5%")
            await c.save(tmp.name)
        asyncio.run(gen())
        from flask import send_file
        return send_file(tmp.name, mimetype="audio/mpeg")
    except Exception:
        pass

    # 回退：Google Translate TTS（分段，每段 200 字以内）
    import io
    chunks = [text[i:i+200] for i in range(0, len(text), 200)]
    audio_data = io.BytesIO()
    for chunk in chunks:
        encoded = urllib.parse.quote(chunk)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=zh-CN&q={encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                audio_data.write(r.read())
        except Exception:
            pass

    audio_data.seek(0)
    from flask import send_file
    return send_file(audio_data, mimetype="audio/mpeg")


STATS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.json")

def load_stats():
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH) as f:
            return json.load(f)
    return {"total_visits": 0, "unique_users": 0, "users": [], "visits": []}

def save_stats(stats):
    with open(STATS_PATH, "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


@app.route("/api/ping")
def api_ping():
    """每次打开页面记录一次访问"""
    stats = load_stats()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    device = "mobile" if "Mobile" in ua else "desktop"
    stats["total_visits"] += 1
    # 按 IP 去重统计独立用户
    known_ips = [u.get("ip") for u in stats["users"]]
    if ip not in known_ips:
        stats["unique_users"] += 1
        stats["users"].append({
            "ip": ip, "device": device,
            "first_visit": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    save_stats(stats)
    return jsonify({"ok": True})


@app.route("/api/register")
def api_register():
    """用户设置生辰时记录（=部署/使用）"""
    stats = load_stats()
    name = request.args.get("name", "匿名")
    birth = request.args.get("birth", "")
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = request.headers.get("User-Agent", "")
    device = "mobile" if "Mobile" in ua else "desktop"

    # 更新用户信息
    found = False
    for u in stats["users"]:
        if u.get("ip") == ip:
            u["name"] = name
            u["birth"] = birth
            u["device"] = device
            u["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            found = True
            break
    if not found:
        stats["unique_users"] += 1
        stats["users"].append({
            "ip": ip, "name": name, "birth": birth, "device": device,
            "first_visit": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    save_stats(stats)
    return jsonify({"ok": True})


@app.route("/api/stats")
def api_stats():
    """查看统计数据"""
    stats = load_stats()
    return jsonify({
        "total_visits": stats["total_visits"],
        "unique_users": stats["unique_users"],
        "users": [{
            "name": u.get("name", "匿名"),
            "device": u.get("device", ""),
            "first_visit": u.get("first_visit", ""),
            "last_active": u.get("last_active", u.get("first_visit", "")),
        } for u in stats["users"]]
    })


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/static/sw.js")
def service_worker():
    return app.send_static_file("sw.js")




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
