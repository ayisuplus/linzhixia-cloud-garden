from pathlib import Path
import json,re,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent;rel=P.relative_to(R).as_posix()
O=R/'视频制作/第一幕关键帧图册-20261017-v1.5';O.mkdir(exist_ok=True)
a=json.loads((R/'视频制作/第一幕关键帧图册-20261017-v1.4/atlas.json').read_text(encoding='utf-8'))
a['subtitle']='在v1.4连续动作基础上细化A012智能日历：时辰刻度、感应图标、开启开关及暂停入口。17镜、90秒预算不变，静态界面待审。'
a['source_manifest']=rel+'/manifest.json';a['story_script']='第一季/分镜/第一集-A-今天没有安排-智能镜与动态被子-v0.13.md'
s=next(s for s in a['shots'] if s['id']=='E01-A-012');old=s['presentation']['path']
s['presentation'].update(path=rel+'/E01-A-012-智能日历.png',visible='青瓷薄屏保留“今日无事／宜休沐”；左上日出刻度标“卯时”，右上叶片感应图标；下方“早起出门：已开启”配琥珀色开启开关，下面是“暂停唤醒”入口。底座左端短灯条亮起，界面带淡雅山水亭阁与花枝。',missing='静帧体现可操作界面，不能证明已感应或可触控。灯条响应、开关切换与视频文字稳定性待制作；本镜无人触屏，晨起开关仍开启。“卯时”为本轮界面候选，不另锁定整集时间线。',status='智能日历界面候选，待作者审阅')
s['refs'].insert(0,dict(path=s['presentation']['path'],role='新版日历界面主图；开关为开启状态，暂停入口未触发'))
for ref in s['refs'][1:]:ref['role']='历史界面／修改来源，不复制旧版排版作为当前界面'
s['action']='切到书桌青瓷薄屏。知夏看过来时，木底座短灯条轻亮一次，晨起控制条稍亮后稳定。主文字“今日无事／宜休沐”和“早起出门：已开启”保持清楚，开启开关与暂停入口说明它可被操作。她没有触屏，也没有按下暂停；背景拖鞋仍在走，下一镜由她口头喊停。'
s['dialogue']='无；主信息：“今日无事”“宜休沐”“早起出门：已开启”；附属标签：“卯时”“暂停唤醒”'
s['invariants']+=['本镜开关保持开启，暂停入口未触发；不提前终止晨起服务','主文案优先于装饰与刻度，感应灯不持续闪烁','近景是界面母版；A011/A014远景小屏仅参考设备位置，视频中需统一显示内容']
(O/'atlas.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=R/'第一季/分镜/第一集-A-今天没有安排-智能镜与动态被子-v0.12.md';txt=p.read_text(encoding='utf-8').replace('v0.12','v0.13').replace('关键帧图册-20261017-v1.4','关键帧图册-20261017-v1.5')
pattern=r'### E01-A-012｜.*?(?=\n### |\Z)';oldsection=re.search(pattern,txt,re.S).group();heading=oldsection.splitlines()[0]
refs='；'.join(f"[{Path(v['path']).name}](../../{v['path']})（{v['role']}）" for v in s['refs'])
section=f"{heading}\n\n**当前画面：智能日历界面候选。** {s['presentation']['visible']}\n\n**尚未体现：** {s['presentation']['missing']}\n\n**视频计划（未制作）：** {s['action']}\n\n**对白：**{s['dialogue']}\n\n**声音：**{s['sound']}\n\n**衔接：**{s['next_link']} {'；'.join(s['invariants'])}。\n\n**参考：**{refs}。\n"
txt=re.sub(pattern,lambda _:section,txt,flags=re.S);txt=txt.replace('## 本轮规则','本轮追加A012智能日历界面：时辰刻度、感应图标、晨起开关与暂停入口。仍未制作视频。\n\n## 本轮规则',1)
(R/a['story_script']).write_text(txt,encoding='utf-8')
intro='本轮追加：A012日历增加时辰刻度、感应图标、晨起开启开关与暂停入口；“今日无事／宜休沐”仍为主信息。候选待审，动态未制作。'
for name in ['制作进度.md','创作速查卡.md','第一季/分镜/第一幕-当前制作总览.md']:
 p=R/name;t=p.read_text(encoding='utf-8').replace('关键帧图册-20261017-v1.4','关键帧图册-20261017-v1.5').replace('关键帧图册v1.4','关键帧图册v1.5').replace('v0.12','v0.13')
 pos=t.find('\n');t=t[:pos+1]+'\n'+intro+'\n'+t[pos+1:]
 if name.endswith('当前制作总览.md'):
  row=f"| E01-A-012 | 今日无事，宜休沐 | 智能日历界面候选 | {s['presentation']['missing']} |"
  t=re.sub(r'\| E01-A-012 \|[^\n]*',lambda _:row,t)
 p.write_text(t,encoding='utf-8')
p=R/'世界观/生活技术-晨起智能家居-当前设计-v0.2.md';t=p.read_text(encoding='utf-8').replace('按v0.12','按v0.13')
t=t.replace('## 保留的未定问题','## 日历的智能表现（本轮候选）\n\n青瓷薄屏保留古雅主文案，以时辰刻度、叶片感应图标、琥珀色晨起开关和未触发的“暂停唤醒”入口表达可交互能力；底座短灯条在看向它时轻亮一次。A012开关仍开启，她未触屏，A013才口头喊停。淡雅园林界面属于显示内容，不改变房间空间。响应及触控尚未动态验证。\n\n## 保留的未定问题')
p.write_text(t,encoding='utf-8')
f=P/'E01-A-012-智能日历.png';m=dict(date='2026-10-17',method='built-in imagegen',status='候选，待作者审阅',video_produced=False,prior_sources='视频制作/第一幕步履与旋杆衣柜-20261017-v0.1/manifest.json',id='E01-A-012',path=s['presentation']['path'],source='C:/Users/36322/.codex/generated_images/01a13a12-c15f-7431-88a9-5ceeb49cb3b0/exec-ccf40883-8d3c-4111-bd3c-722818294419.png',references=[old],prompt='prompt.txt',dimensions=list(Image.open(f).size),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),visible=s['presentation']['visible'],missing=s['presentation']['missing'])
(P/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('A012 updated; other frames unchanged. 17 shots / 90 seconds budget.')
