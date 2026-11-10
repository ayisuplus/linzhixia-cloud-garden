"""本轮图册修订记录；以 v1.2 为输入，保留旧版。"""
from pathlib import Path
import json, re, hashlib
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
REL = PKG.relative_to(ROOT).as_posix()
ATLAS = ROOT / '视频制作/第一幕关键帧图册-20261017-v1.3'
ATLAS.mkdir(exist_ok=True)
old = json.loads((ROOT / '视频制作/第一幕关键帧图册-20261017-v1.2/atlas.json').read_text(encoding='utf-8-sig'))
atlas = json.loads(json.dumps(old))
atlas['subtitle'] = '衣柜主动推荐、全屋忙碌与喊停后停在半途的三张新候选。17镜、90秒预算不变；实际静帧与待制作动态分别列明。'
atlas['source_manifest'] = REL + '/manifest.json'
atlas['story_script'] = '第一季/分镜/第一集-A-今天没有安排-智能镜与动态被子-v0.11.md'
shots = {s['id']: s for s in atlas['shots']}

def set_shot(suffix, filename, title, visible, missing, action, entry, exit, invariants, next_link):
    s = shots['E01-A-' + suffix]
    old_path = s['presentation']['path']
    for r in s['refs']:
        if r['path'] == old_path:
            r['role'] = '历史候选，仅追溯本轮之前的状态；不继承旧构图中的物件位置或界面状态'
    path = REL + '/' + filename
    s['title'] = title
    s['presentation'] = dict(path=path, role='action', visible=visible, missing=missing, show_as_main=True, status='本轮关键动作候选，待作者审阅')
    s['refs'].insert(0, dict(path=path, role='本轮关键状态主图；不是全部动作尚未发生的起始帧'))
    s.update(action=action, entry_state=entry, exit_state=exit, invariants=invariants, next_link=next_link)

set_shot('009', 'E01-A-009-衣柜主动推荐.png', '衣柜主动推荐搭配',
    '木柜左侧外露面板保留木纹，浮现暖色双眼、笑口与“搭配就绪”；桃粉上衣及青绿裙装向柜外递出，裙摆偏斜。右门长镜保留“昨晚预设／试穿预览”及云上花园中的同款穿搭人像。',
    '开门、表情亮起、衣架递出和裙摆摆动尚未制作。镜中鞋袜仍属推演细节；这不是实时换装，也不是普通镜面反射。',
    '柜门打开，侧壁木纹中亮出双眼和笑口，“搭配就绪”随之出现；实物衣架向柜外前移，把桃粉上衣与青绿裙装主动递给床上的知夏，裙摆轻摆后等待。镜内同时显示昨晚保存的试穿预览，背景为独立云上花园。知夏仍穿睡衣，不替她换装。',
    '衣柜尚未完成开门、显像与递衣。', '衣物伸出柜口、侧壁笑脸及保存预览保持，等待知夏回应。',
    ['原木柜、玉扣、服装颜色与刺绣保持', '侧壁表情融入木材，不加黑色屏幕或机械手', '镜中是保存预览，花园只存在于镜框内', '同一镜面虚拟人物不变成现实中的第二个人'],
    'A010知夏仍穿睡衣；A011衣物保持已递出的位置，只做催促小摆动，镜内预览在喊停前继续。')
shots['E01-A-009']['purpose'] = '让观众同时看见衣柜的表情、主动递衣与保存的搭配预览。'

set_shot('011', 'E01-A-011-全屋忙碌-去支架.png', '全屋忙碌催醒',
    '知夏坐在床左侧略向前倾，双手攥近身被缘，困倦不耐；高枕仍在背后，汤圆留在枕边。腿边同一条被子抬起大片带表情的被缘，与双手位置分开；衣物探出柜口、裙摆偏斜，木侧壁有弯眼及“搭配就绪”。书桌椅已退出，日历立在桌上，两只拖鞋前后错开。整窗为连续水巷；荷叶托盘悬停承杯、杯身显示42°C，盘下无新增支架。',
    '仍是静态忙碌关键姿态，不能据此认定家具已运动。窗景转换、裙摆小摆、椅子退出、日历转向、拖鞋再次微调、被缘抬起及声音均待视频；镜面未展示，预览仍应保持。被缘显像带织纹，光滑液态质感弱于A010，过渡需动态衔接。',
    '在既有服务上继续叠加动作：A009递出的衣物轻摆提醒；被缘在腿边自主抬起，知夏烦躁地攥住另一处近身被缘，身体向前离开高枕。椅子稍退出书桌并朝她转，桌面日历朝她调整角度；拖鞋等不到她伸脚，再做一次小幅对位，形成前后错开状态。杯盘沿用A010的停点，完成把手朝向的调整后等待，不重新飞入。中央整扇窗统一换成有真实纵深的水巷。窗、衣柜、水杯最多三路短句叠加，其余家具以动作参与。她最后把目光落到日历。',
    '床已托高原枕，衣物已递出，杯盘已到手边，拖鞋曾并排等候。', '物件分别处于催促或微调姿态；她看到右侧书桌日历，预览与主动服务仍在。',
    ['床、柜、书桌等建筑布局保持，增加活动姿态而非随机垃圾', '知夏手攥近身被缘，显像抬起处在腿边，不能写成双手托起表情被子', '高枕不重复从低处升起；被面与整条被子连续，不另生宠物', '杯底贴荷叶盘、仅托盘悬停，盘下无新增支架', '镜面未展示不等于退出预览；整窗连续换景，不出现贴图边框', '最多三路可辨声音，其他家具用动作参与', '拖鞋二次调整解释从A008整齐到本镜错位，不瞬移'],
    'A012沿她看日历的视线切入；A013继承本镜所有物件位置，A014同机位呈现停在半途。')
shots['E01-A-011']['framing'] = '固定卧室全景，与A014匹配机位'
shots['E01-A-011']['purpose'] = '用不同方向和阶段的家居动作，把过度热心变成可见的忙乱。'
shots['E01-A-011']['trial_recommended'] = True

set_shot('014', 'E01-A-014-全屋停在半途-去支架.png', '全屋停在半途',
    '与A011相同全景中，衣物仍伸出柜口，椅子仍退出，拖鞋仍错开，被缘仍抬起；各件物品没有归位。知夏肩膀和手放松，汤圆留在枕边，高枕仍在。被缘保留收敛的侧眼与闭口表情，柜侧双眼变得低调且“搭配就绪”消失；荷叶盘仍悬停承杯，杯身读数消失，盘下无新增支架。整窗回到树、白墙和瓦顶的原庭院景象。',
    '这是喊停后立刻停在半途的状态，不是被角表情已完全淡出的结束帧。镜面未展示，不能声称已拍到普通反射；退出预览、表情进一步淡去和床的询问仍是视频计划。床头仍有暖亮，不能写成全屋完全灭光。',
    '承接A013已经生效的停止指令，切回与A011匹配的全景：衣物、椅子、拖鞋、抬起的被缘停留在各自动作半途，杯盘保持既有停点，先安静半拍。窗已恢复原园景，杯身读数消失、柜侧提示收敛；被缘短暂不好意思地闭口侧看，随后表情逐渐淡去。镜内预览按指令退出，但本机位不展示反射。高枕继续提供支撑，实体玉件仍在；床头轻亮一小段，床小声询问要不要铺回去。',
    'A013第一声停已中止动作；同一空间中的椅子、衣架、拖鞋和被缘留在中途。', '安静半拍后床轻声询问；物件保持未归位，等待她选择继续休息。',
    ['与A011同一机位和物件停点，不把房间瞬间收拾整齐', '被缘仍抬起、表情仍可见；后续淡去不冒称已在静帧完成', '高枕、玉璧、玉扣保留；床头可以轻亮，不等于重启全屋', '杯贴盘、托盘承重悬停，杯盘不凭空消失或落到新增桌子上', '普通镜面恢复是画外状态计划，本图不展示镜面', '窗的全部可见区域回到原园景'],
    'A015先由知夏点头并主动躺回，床再降低原枕，被缘让出她手臂活动空间；其他家具不自行重新忙碌。')
shots['E01-A-014']['framing'] = '固定卧室全景，与A011匹配机位'
shots['E01-A-014']['purpose'] = '用相同构图中尚未完成的姿势，表现家具确实听懂了停。'
shots['E01-A-014']['trial_recommended'] = True
for r in shots['E01-A-014']['refs']:
    if '智能镜云上花园' in r['path']:
        r['role'] = '历史预览造型参考；本轮A014镜面未展示，不可当成退出后的普通反射证据'
s = shots['E01-A-013']
s['action'] += ' 第一声停即冻结衣架、退出的椅子、再次微调的拖鞋与抬起的被缘；不得先归位再切A014。'
s['presentation']['missing'] += ' 旧喊停图未完整呈现本轮新增忙碌姿态，制作时需承接A011；本轮没有重画A013。'
s['invariants'].append('A011的抬被、递衣、椅子退出和拖鞋错位在第一声停后保持，接同机位A014')
s['refs'].append(dict(path=shots['E01-A-011']['presentation']['path'],role='仅继承喊停前物件位置与高枕状态，不复制表情和对白时刻'))
shots['E01-A-015']['entry_state'] += ' 抬起的被缘尚未自动整理，先随知夏的躺回动作退让。'
assert len(atlas['shots']) == 17 and sum(s['seconds'] for s in atlas['shots']) == 90
(ATLAS / 'atlas.json').write_text(json.dumps(atlas, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

script_old = ROOT / '第一季/分镜/第一集-A-今天没有安排-智能镜与动态被子-v0.10.md'
script = script_old.read_text(encoding='utf-8-sig').replace('v0.10','v0.11').replace('关键帧图册-20261017-v1.2','关键帧图册-20261017-v1.3')
script = script.replace('其余家具不因此增加脸或肢体。', '本轮作者授权衣柜侧壁增加表情及读数；其他家具按实际用途响应，不自动新增肢体。')
script = script.replace('A009沿用此候选；本轮另外补齐四处完整画面，动态限制仍按逐镜说明。', 'A009在此基础上新增侧壁表情、状态字与主动递衣；A011/A014用匹配全景呈现忙碌及停在半途，均为待审静帧。')
script = script.replace('本图显像区较隆起且光泽强，为待审方案。', 'A007/A010候选显像区较隆起且光泽强；A011/A014改为整片被缘抬起，显像带织纹，材质过渡待动态验证。')
script = script.replace('2026-10-17。沿用既有镜头编号', '2026-10-17。新增衣柜主动推荐、全屋忙碌及喊停后未归位三张候选。沿用既有镜头编号',1)
for suffix in ['009','011','014']:
    s = shots['E01-A-'+suffix]
    pattern = r'### E01-A-'+suffix+r'｜.*?(?=\n### |\Z)'
    old_section = re.search(pattern, script, re.S).group()
    time = old_section.splitlines()[0].split('｜')[-1]
    refs = '；'.join(f"[{Path(r['path']).name}](../../{r['path']})（{r['role']}）" for r in s['refs'])
    section = f"### {s['id']}｜{s['title']}｜{time}\n\n**当前画面：关键动作候选，待审。** {s['presentation']['visible']}\n\n**尚未体现：** {s['presentation']['missing']}\n\n**视频计划（未制作）：** {s['action']}\n\n**对白：**{s['dialogue']}\n\n**声音：**{s['sound']}\n\n**衔接：**{s['next_link']} {'；'.join(s['invariants'])}。\n\n**参考：**{refs}。\n"
    script = re.sub(pattern, lambda m:section, script, flags=re.S)
script = script.replace('被角若入镜，显像眼睛短暂睁圆，嘴闭上，抬起处停住；杯子和被子不再播报。', '被角若入镜，显像眼睛短暂睁圆，嘴闭上，抬起处停住；杯子和被子不再播报。第一声停即冻结衣物、椅子、再次微调的拖鞋和被缘的位置，不归位。旧喊停图未完整展示新增姿态，视频需继承A011，本轮未重画此镜。')
(ROOT / atlas['story_script']).write_text(script, encoding='utf-8')

for name in ['制作进度.md','创作速查卡.md','第一季/分镜/第一幕-当前制作总览.md']:
    p = ROOT / name
    txt = p.read_text(encoding='utf-8-sig').replace('关键帧图册-20261017-v1.2','关键帧图册-20261017-v1.3').replace('关键帧图册v1.2','关键帧图册v1.3').replace('v0.10','v0.11')
    txt = txt.replace('四处完整画面已补为待审候选，母版、17镜总览、起止状态与邻镜衔接同步更新；旧图保留。', '新增衣柜主动推荐、全屋忙碌及喊停后未归位三张候选；同步17镜状态与邻镜衔接，旧图保留。')
    txt = txt.replace('本轮补四镜静帧并同步图册与画布，未制作视频。', '本轮更新A009/A011/A014静帧并同步图册与画布，未制作视频。')
    txt = txt.replace('其他旧静帧的玉璧、枕头高度等连续性问题按v0.9逐镜说明处理。', '其他旧静帧的玉璧、枕头高度等连续性问题按v0.11逐镜说明处理。')
    if name.endswith('当前制作总览.md'):
        for suffix in ['009','011','013','014']:
            s = shots['E01-A-'+suffix]
            row = f"| {s['id']} | {s['title']} | {s['presentation']['status']} | {s['presentation']['missing']} |"
            txt = re.sub(r'\| E01-A-'+suffix+r' \|[^\n]*', lambda m:row, txt)
        txt = txt.replace('顶区是本总览与A001—A016四行顺序；','顶区是本总览与A001—A016四行顺序（含A008-PRE）；')
    intro = '\n本轮新增：衣柜木侧壁表情与“搭配就绪”，衣物主动递出；忙碌全景增加抬起的被缘、退出的椅子与再次微调的拖鞋。喊停全景沿用同一机位和物件位置，停在半途；三张均待作者审阅，动态尚未制作。\n'
    first = txt.find('\n')
    txt = txt[:first+1] + intro + txt[first+1:]
    p.write_text(txt, encoding='utf-8')

world = ROOT / '世界观/生活技术-晨起智能家居-当前设计-v0.2.md'
txt = world.read_text(encoding='utf-8-sig').replace('三拳喜剧按v0.9','三拳喜剧按v0.11')
txt = txt.replace('当前候选较隆起、像凝胶，立体嘴仍待审', 'A007/A010较光滑隆起；A011/A014为与整被连续的抬起被缘、带织纹显像，材质转换待动态验证')
txt = txt.replace('## 保留的未定问题', '## 2026-10-17 作者修订：可见的忙碌与响应\n\n衣柜侧壁保留木纹，在使用时浮现暖色双眼、笑口与“搭配就绪”，衣架主动把既定服装递出；镜内仍是昨晚保存的云上花园试穿。忙碌阶段由被缘自主抬起、衣物轻摆、椅子退出、日历朝向她、拖鞋再次小幅对位共同参与，不靠增加满屋语音。知夏可以攥近身被缘，但不托起显像区域。\n\n喊停立刻停止主动服务，家具保持未完成的物理姿态：衣物不收回、椅子不归位、拖鞋不重新并齐、被缘不瞬间摊平。表情和读数随后收敛，整窗回原园景；镜面退出预览为画外计划。托盘保持悬停承杯，不加木支架，也不让杯子离盘飞。床维持支撑，得到继续休息的回应后再降低枕头、重新铺被。\n\n[三张候选与制作记录](../视频制作/第一幕家居忙碌表演-20261017-v0.1/README.md)\n\n## 保留的未定问题')
world.write_text(txt, encoding='utf-8')
print('Updated atlas v1.3, script v0.11, current entrypoints and household design. 17 shots / 90 seconds budget.')
