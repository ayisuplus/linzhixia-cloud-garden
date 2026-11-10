"""Build the window/wardrobe revision from preserved source atlases. No media calls."""
import copy
import hashlib
import importlib.util
import json
import os
import struct
from html import escape as esc
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MEDIA = HERE.relative_to(ROOT).as_posix()
ATLAS = '视频制作/第一幕关键帧图册-20261017-v1.7'
ASSETS = '视频制作/资产图册-20261017-v1.1'
PLAN = '视频制作/第一幕Seedance2.5生成分组-20261017-v0.2'
SCRIPT = '第一季/分镜/第一集-A-今天没有安排-窗户飞行与衣柜递衣-v0.14.md'

def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))

def write(path, value):
    p = ROOT/path
    p.parent.mkdir(parents=True, exist_ok=True)
    value = value.replace('更新：2026-10-17。', '更新：2026-10-18。').replace('2026-10-17。新增E01-A-010-W', '2026-10-18。新增E01-A-010-W')
    p.write_text(value, encoding='utf-8')

def dump(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def url(path, folder):
    return quote(Path(os.path.relpath(ROOT/path, ROOT/folder)).as_posix(), safe='/.-_')

def stamp(s):
    return f'{int(s)//60:02}:{int(s)%60:02}'

# State frames are visual candidates, not evidence that the motion has been generated.
wardrobe = [
    dict(path=MEDIA+'/E01-A-009-01-固定臂预备位.png', label='01 柜内预备位', role='opening', visible='粉色上衣与青绿裙由刚性连接的衣架在柜内承托；镜面尚未显示试穿人物。', limits='开门后状态参考；柜门开启未展示。此帧直连块较粗，后两帧短连接较细，动态须统一同一部件尺寸，不能形变换机构。'),
    dict(path=MEDIA+'/E01-A-009-02-固定臂旋出.png', label='02 固定衣架旋出途中', role='action', visible='主衣架呈短直连接，服装有转向姿态，镜面未显示人物；无外围框。', limits='仅途中姿态参考，旋臂投影与终态接近，不是准确机械中间位；实际旋转路径、角度、门与衣摆避让未验证。'),
    dict(path=MEDIA+'/E01-A-009-03-固定臂停稳.png', label='03 固定衣架停稳展示', role='ending', visible='旋转臂直接连接肩形衣架，整套服装递出；镜内显示保存的云上花园试穿。', limits='裙夹内部连接藏在衣后，画面不证明隐蔽结构；停稳、衣摆惯性与预览亮起尚未动态制作。'),
]
window = [
    dict(path=MEDIA+'/E01-A-010-W-01-微型侧掠起始.png', label='01 微型尺度·贴面侧掠', role='opening', visible='极近木窗棂占据前景，窗面沿纵深延伸，原庭院在窗后局部可见。', limits='仅起始机位和状态；飞行与运动视差未制作，整扇窗不在此近景内。'),
    dict(path=MEDIA+'/E01-A-010-W-02-微型侧掠蔓延-锁景.png', label='02 贴面飞行·影像蔓延', role='action', visible='巨大近景木窗棂与纵深窗面保留，窗后庭院向水巷转换，变化前沿可见。', limits='按终态水巷修订的边界候选；视频仍需锁定同一底景逐步揭开，不能让已显露景物继续重绘。三帧不是实际飞行的三个位姿。'),
    dict(path=MEDIA+'/E01-A-010-W-03-微型侧掠完成.png', label='03 侧掠完成·即将切全景', role='ending', visible='贴面侧向机位下，可见窗区已换成水巷；近处木框保持实体。', limits='本近景看不到整窗，全部完成状态由下一镜A011全景交代；景观机位、桥和船细节仍需动态统一。'),
]
for frame in wardrobe+window:
    assert (ROOT/frame['path']).is_file(), frame['path']

atlas = read('视频制作/第一幕关键帧图册-20261017-v1.6/atlas.json')
atlas['subtitle'] = 'v1.7：补衣柜预备／旋出／停稳与窗户飞行换景三状态；18镜99秒预算，6批生成＋日历插镜。新图为待审候选，动态未制作。'
atlas['story_script'] = SCRIPT
atlas['source_manifest'] = MEDIA+'/manifest.json'
atlas['production_guide'] = dict(path=PLAN+'/生成分组.html', label='04 视频生成镜头表 v0.2', summary='衣柜8秒；送水→窗户换景→忙碌全景合计17秒；18镜99秒预算。')
shots = {s['id']:s for s in atlas['shots']}
w = shots['E01-A-009']
w.update(title='预备衣架旋出与试穿预览', seconds=8,
    framing='衣柜近景，轻微跟随挂杆；柜内结构与镜面同时可辨',
    purpose='看清昨晚选好的整套衣服怎样从预备位送到柜外，承托始终成立。',
    entry_state='整套衣服由固定于旋转臂的衣架在柜内预备位承托；镜内预览未亮，窗外仍为原庭院。',
    exit_state='旋转臂和刚性直连衣架整体递出并停稳，肩形部分承上衣、衣后连接的下层裙夹承裙腰；镜内云上花园预览亮起，窗外仍原庭院。',
    action='0—2秒柜门先让开通道，镜面所在右门板保持安全停靠；2—6秒柜体固定转轴带动旋转臂，经刚性短连接带动肩形衣架整体旋出，主衣架无挂钩、衣物外围无框。肩形部分承上衣，下层裙夹与同一衣架连接，连接藏在衣服后面，不靠上衣下摆承重。后排衣物与上层收纳不动。6—8秒整套机构减速停稳，衣摆轻晃，镜内亮起昨晚保存的云上花园试穿预览；知夏本人仍穿睡衣在床上。',
    next_link='切A010送水；衣服保持已递出状态，不二次旋出。窗仍原庭院，换景在A010之后。',
    state_frames=wardrobe, priority='trial', trial_recommended=True)
w['invariants'] = ['柜体固定转轴→旋转臂→刚性短连接→肩形衣架整体旋出；主衣架没有挂钩，没有外围框', '裙夹连接藏衣后，不能夹住上衣下摆承重', '右侧镜门不扫过旋转臂；转轴固定在柜体而非活动柜门', '粉色上衣和青绿裙的既定颜色、绣纹和款式不变', '镜中人物为保存预览，真实知夏仍穿睡衣在床上', '室外窗景保持原庭院，镜内云上花园独立于窗外']
w['presentation'] = dict(path=wardrobe[-1]['path'], role='ending', visible=wardrobe[-1]['visible'], missing='三状态图为候选；柜门开启过程、实际转角、衣摆避让与停稳节奏均待视频验证。', show_as_main=True, status='新增停稳状态候选，待作者审阅')
w['refs'] = [dict(path=f['path'], role=f['label']+'；'+f['limits']) for f in wardrobe] + [dict(path=r['path'],role='历史外观参考，仅保留服装、人物及木柜；不继承已否定的挂钩或外围框机构。') for r in w['refs']]
t = shots['E01-A-010']
t['action'] += ' 本镜窗外仍为原庭院，不提前换成水巷。'
t['next_link'] = '杯盘停妥后切A010-W贴窗飞行换景；画外人物、杯盘停点和衣柜伸出状态保持，不重复送水。'
t['invariants'] += ['原庭院保持到本镜结束，换景另由A010-W完成']
new = dict(id='E01-A-010-W', title='贴窗飞行·全息水巷蔓延', seconds=6,
    framing='微型飞行尺度，极近窗面，从侧边沿窗近乎平行掠行；巨大木窗棂擦过前景，结束硬切A011全屋广角',
    purpose='让观众看见窗景从庭院变成水巷的过程，随后用全景交代房间已改变。',
    presentation=dict(path=window[1]['path'], role='action', visible=window[1]['visible'], missing='飞行轨迹、变化速度与视差未制作；发光过渡为候选，最终应克制，不变成传送门。', show_as_main=True, status='新增换景过程候选，待作者审阅'),
    refs=[dict(path=f['path'],role=f['label']+'；'+f['limits']) for f in window] + [dict(path=shots['E01-A-011']['presentation']['path'],role='下一镜全屋广角和已完成水巷参考；不复制其机位作为贴窗首帧')],
    state_frames=window,
    entry_state='A010送水完成，杯盘停妥；窗外仍原庭院。镜头进入微型飞行尺度，极近左侧窗面，镜轴几乎平行窗面，近处窗框巨大。',
    exit_state='整窗换成连续水巷，近景木窗棂仍为实体，摄影机减速；下一镜直接切全屋忙碌广角。',
    action='0—1秒观众仿佛跟着微型飞机来到窗侧，摄影机极近窗面侧掠，近木窗棂巨大并越出画框；镜轴近乎平行窗面，窗口沿纵深伸向远方，不能回到站在房间里斜看整窗的机位。1—4.5秒沿窗持续向前飞行，木棂掠过前景，全息变化沿窗面随行展开，已变水巷与未变庭院的边界保留在斜向视野中。木材不变形、不消失，不穿玻璃或窗框。4.5—6秒飞行减速，可见窗区完成换景；直接切A011广角揭示整扇窗已经完成。三张关键状态不等于飞行视频，需另执行轨迹、近远视差和速度曲线。',
    dialogue='无新增对白；窗的晨间播报留到A011。', sound='原鸟声连续；水声渐清晰，画外拖鞋踱步不断。不加飞机引擎声。',
    invariants=['摄影机模拟飞行，不新增实体飞机或无人机道具', '不穿过玻璃、木窗棂或实体墙；不进入另一个空间', '原庭院→水巷单向展开，只发生一次', '过渡边界持续在画面可见区域，不完全落到摄影机背后', '窗框窗棂及室内陈设不变，景象在各窗区连续', '杯盘、衣杆和人物保持上一镜状态；拖鞋画外持续踱步'],
    next_link='直接硬切A011既有全屋广角；整窗水巷已经完成，不再重新变一次；杯盘仍在A010停点。', priority='trial', trial_recommended=True)
atlas['shots'].insert(atlas['shots'].index(t)+1,new)
wide = shots['E01-A-011']
wide['entry_state'] += ' A010-W已经完成整窗水巷换景。'
wide['action'] = wide['action'].replace('中央整扇窗统一换成有真实纵深的水巷。','中央整扇窗保持A010-W已完成的连续水巷，直接承接窗镜，不再重复换景。')
wide['invariants'] += ['窗景在上一镜已完成，广角只呈现结果；与窗镜统一景观要素']
wide['presentation']['missing'] += ' 与本轮A009夹架细部及A010-W窗景机位需统一，旧广角不作为这两项修正已完成的证据。'
for sid in ['E01-A-011','E01-A-014']:
    s=shots[sid]
    for field in ['action','entry_state','exit_state','next_link']:
        s[field]=s[field].replace('转杆承托的衣物','刚性直连衣架承托的衣物').replace('衣架仍挂在杆端','衣架与旋转臂直接固定连接').replace('衣架仍挂于杆端','刚性直连衣架仍由旋转臂固定承托，保持伸出位置').replace('衣架挂杆','刚性直连衣架')
    s['invariants']=[x for x in s['invariants'] if not any(term in x for term in ['衣架钩','挂在杆','挂于杆'])]+['A009固定转轴、旋转臂与无钩直连衣架保持同一结构；无外围框']
    s['presentation']['missing']+=' 旧全景的挂钩细部尚未重画，视频须继承本轮固定直连衣架，不沿用旧挂钩。'
    for ref in s['refs']:
        if 'A-009' in ref['path']:
            ref['role']='历史服装与木柜外观参考，不继承挂钩；机构以本轮固定直连衣架候选为准。'
    s['refs'].append(dict(path=wardrobe[-1]['path'],role='当前固定直连衣架机构，覆盖旧全景挂钩细部；候选待审。'))
shots = {s['id']:s for s in atlas['shots']}
assert len(shots)==18 and sum(s['seconds'] for s in shots.values())==99

# Full current action script, preserving every prior shot's metadata and references.
md=['# 第一集A段：今天没有安排｜窗户飞行与衣柜递衣 v0.14','',
    '2026-10-17。新增E01-A-010-W，保留原17个镜头ID；A009从5秒调整为8秒。18镜、99秒是未测时预算；新图为候选，正式视频未制作。', '',
    f'[关键帧图册v1.7](../../{ATLAS}/关键帧图册.html) · [生成镜头表](../../{PLAN}/生成分组.html) · [完整生成及核对记录](../../{MEDIA}/README.md)', '',
    '## 连续性', '',
    'A009递衣→A010送水→A010-W窗户飞行换景→A011全屋忙碌。镜中云上花园独立于窗外水巷；真正知夏始终在床上穿睡衣。喊停后A014整窗恢复原庭院，衣物、杯盘与高枕保持承托。拖鞋脚步从A008-PRE延续到A013第一声停。', '',
    '不新增实体飞行器。图像状态、视频计划及作者采用分别记录；旧图的玉璧、枕头、被面材质等限制继续有效。', '', '## 18镜动作稿']
cursor=0
for s in atlas['shots']:
    end=cursor+s['seconds']; p=s['presentation']
    md += ['',f"### {s['id']}｜{s['title']}｜{stamp(cursor)}—{stamp(end)}（{s['seconds']}秒）",'',f"**当前画面：{p['status']}。** {p['visible']}",'',f"**尚未体现：** {p['missing']}",'',f"**起始：** {s['entry_state']}",'',f"**视频计划（未制作）：** {s['action']}",'',f"**结束：** {s['exit_state']}",'',f"**对白：** {s['dialogue']}",'',f"**声音：** {s['sound']}",'',f"**衔接：** {s['next_link']}",'', '**保持：** '+'；'.join(s['invariants']),'','**参考：**']
    md += [f"- [{Path(r['path']).name}](../../{r['path']})：{r['role']}" for r in s['refs']]
    cursor=end
write(SCRIPT,'\n'.join(md)+'\n')

plan=read('视频制作/第一幕Seedance2.5生成分组-20261017-v0.1/plan.json')
plan.update(atlas_source=ATLAS+'/atlas.json',story_script=SCRIPT, status='planned_not_submitted_not_dynamically_tested')
plan['spec_note']='沿用上一版作者选择与规格记录；本轮未现场核验端点。提交前核验模型、参考槽位和可选时长。'
g4=next(u for u in plan['units'] if u['id']=='G04')
g4.update(requested_seconds=10,title='预备衣架旋出与镜中试穿', staging=w['action'],safe_cut='同组衣架递出并停稳、预览亮起后切送水；不在柜门扫过或衣物擦碰时硬剪。',continuity='固定柜体转轴，肩架连接下层夹架，衣物不弹射；右镜门让开运动空间，窗外保持原庭院。',reference_strategy='依次用预备位、旋出、停稳三张候选约束机构状态；开门过程需视频补足，终态图不能当首帧。',fallback='先做柜门避让与旋杆递衣；若镜内人像干扰机构，预览独立合成。夹架被遮挡时用结构依据，不允许让裙子悬浮。')
g4['why']='按作者修订，衣架经刚性短连接直接固定于旋转臂，整套旋出；无挂钩或外围框。独立拍摄便于检查固定点和衣物避让。'
g4['continuity']='柜体转轴→旋转臂→刚性短连接→肩形衣架；下层裙夹连接藏衣后，无主衣架挂钩、无外围框；右镜门让开，窗外保持庭院。'
g5=next(u for u in plan['units'] if u['id']=='G05')
g5.update(requested_seconds=19,title='送水、贴窗换景与全屋忙碌',shot_ids=['E01-A-010','E01-A-010-W','E01-A-011'],why='送水停点建立后，窗户飞行换景直接切全屋广角，避免重复送水与换景。17秒成片含三种机位，动态可行性尚未验证。',staging='5秒床侧送水、转柄并停妥→6秒贴窗飞行和影像展开→6秒全屋忙碌广角。'+new['action'],safe_cut='送水停妥后切窗；整窗水巷完成后直接切A011。广角末知夏看日历，再接I01。',continuity='A010仍原庭院；A010-W只换一次；A011水巷保持。杯盘停点、衣柜伸出状态和高枕跨切镜不变；拖鞋脚步不断。',reference_strategy='A010人物和杯盘参考＋窗户三状态＋A011全景；A009停稳图补充夹架细部。三状态为状态参考，不是冻结机位的视频轨迹。',fallback='若长段多机位不稳，拆为送水5秒／窗户6秒／全景6秒，分别申请7／8／8秒，新增4秒余量、成片仍17秒；窗户变化也可用锁定窗框的遮罩合成并另作相机运动。不得把室内物件一并溶解。')
cursor=0
for u in plan['units']:
    u['timeline_start']=cursor
    u['edit_seconds']=sum(shots[s]['seconds'] for s in u['shot_ids'])
    cursor+=u['edit_seconds'];u['timeline_end']=cursor
    time=u['head_handle'];u['beats']=[]
    for sid in u['shot_ids']:
        s=shots[sid]
        u['beats'].append(dict(shot_id=sid,start=time,end=time+s['seconds'],title=s['title'],image=s['presentation']['path'],image_role=s['presentation']['role']))
        time+=s['seconds']
    if u['requested_seconds']:
        assert time+u['tail_handle']==u['requested_seconds']<=plan['max_seconds']
assert [sid for u in plan['units'] for sid in u['shot_ids']]==list(shots)
assert cursor==99
dump(PLAN+'/plan.json',plan)
intro='6次AI生成＋1个日历剪辑插镜；18镜、99秒成片预算。106秒AI原片＋4秒插镜，去11秒余量。尚未提交视频、未测对白时长。'
rules=[plan['spec_note'],'原有三拳29秒与喊停至相拥25秒预算保留，所有长段稳定性均待验证。','G04衣柜8秒成片/10秒申请；G05送水→换景→全景17秒成片/19秒申请。','同批允许明确切镜；G05最后直接切全景，禁止换景重启或杯盘二次飞入。','人物、服装配色、发夹、玉璧、高枕、杯盘停点与衣架支撑跨镜保持。','每批使用独立完整提示词，不引用聊天省略执行内容；无任务ID、无假生成结果。','声音遵循动作稿；脚步跨窗镜持续，A013第一声停骤止。新图候选不自动升级为作者采用。']
pmd=['# 第一幕 · Seedance 2.5生成分组 v0.2','',intro,'','## 共同执行口径','']+['- '+r for r in rules]+['','| 单元 | 镜头 | 成片区间 | 成片/申请 |','|---|---|---|---|']
html=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>晨起视频生成镜头表 v0.2</title><style>body{margin:0;background:#f5f1e8;color:#293f38;font:16px/1.7 system-ui,"Microsoft YaHei"}main{max-width:1200px;margin:auto;padding:32px}article{background:#fffdf8;padding:24px;margin:28px 0;border:1px solid #d9d8cb;border-radius:12px}a{color:#376a59}.strip{display:flex;gap:14px;flex-wrap:wrap}.strip a{width:210px}img{width:100%}pre{white-space:pre-wrap;font:inherit}nav{display:flex;gap:18px;flex-wrap:wrap}small{color:#6f756e}</style><main><h1>晨起 · 视频生成镜头表 v0.2</h1>',f'<p>{esc(intro)}</p><p><a href="{url(ATLAS+"/关键帧图册.html",PLAN)}">关键帧图册v1.7</a> · <a href="生成分组.md">交接文档</a></p><ul>'+''.join('<li>'+esc(r)+'</li>' for r in rules)+'</ul><nav>'+''.join(f'<a href="#{u["id"]}">{u["id"]} · {u["edit_seconds"]}秒</a>' for u in plan['units'])+'</nav>']
for u in plan['units']:
    pmd.append(f"| {u['id']} {u['title']} | {'、'.join(u['shot_ids'])} | {stamp(u['timeline_start'])}—{stamp(u['timeline_end'])} | {u['edit_seconds']}秒 / {u['requested_seconds'] or '剪辑'} |")
for u in plan['units']:
    pmd+=['',f"## {u['id']} · {u['title']}",'',u['why']]
    html.append(f'<article id="{u["id"]}"><small>{u["id"]} · {stamp(u["timeline_start"])}—{stamp(u["timeline_end"])} · 成片{u["edit_seconds"]}秒 / 申请{u["requested_seconds"] or "剪辑"}</small><h2>{esc(u["title"])}</h2><p>{esc(u["why"])}</p><div class="strip">')
    for b in u['beats']:
        pmd.append(f"- {b['start']:g}—{b['end']:g}秒：{b['shot_id']} {b['title']}")
        html.append(f'<a href="{url(ATLAS+"/关键帧图册.html",PLAN)}#{b["shot_id"]}"><img src="{url(b["image"],PLAN)}" alt="{esc(b["title"])}">{b["shot_id"]} · {b["start"]:g}—{b["end"]:g}s</a>')
    html.append('</div>')
    for key,label in [('staging','调度'),('safe_cut','安全剪点'),('continuity','连续性'),('reference_strategy','参考用途'),('fallback','失败拆法')]:
        pmd+=['',f'**{label}：** {u[key]}']
        html.append(f'<h3>{label}</h3><p>{esc(u[key])}</p>')
    # Complete prompts are expanded from every assigned shot; no dangling "same as above".
    prompt='横屏16:9，新中式写实治愈。延续指定人物、服装配色、房间布局和道具。不得新增人物、文字水印、飞机或额外肢体。\n'+u['staging']+'\n'+u['continuity']+'\n'
    for b in u['beats']:
        s=shots[b['shot_id']]
        prompt+=f"\n{b['start']:g}—{b['end']:g}秒 {s['id']}：{s['framing']}。起始：{s['entry_state']} 动作：{s['action']} 结束：{s['exit_state']} 对白：{s['dialogue']} 声音：{s['sound']} 保持：{'；'.join(s['invariants'])}。\n"
    prompt+='\n前后余量只延续当前状态，不重复对白或动作。不同机位允许明确切镜。无额外配乐，保留环境声以便后期连续剪辑。'
    if u['requested_seconds']:
        write(PLAN+f"/prompt-{u['id']}.txt",prompt+'\n')
        pmd+=['','**完整执行提示词：**','',prompt]
        html.append(f'<details><summary>完整执行提示词</summary><pre>{esc(prompt)}</pre></details>')
    html.append('</article>')
html.append('</main></html>')
write(PLAN+'/生成分组.md','\n'.join(pmd)+'\n');write(PLAN+'/生成分组.html',''.join(html))
dump(ATLAS+'/atlas.json',atlas)

# Provenance is completed from the actual output paths and prompt files, never invented task IDs.
provenance=read(MEDIA+'/generation-inputs.json')
frames=[]
for f in wardrobe+window:
    b=(ROOT/f['path']).read_bytes()
    assert b[:8]==b'\x89PNG\r\n\x1a\n'
    width,height=struct.unpack('>II',b[16:24])
    frames.append(dict(**f,status='候选待作者审阅',sha256=hashlib.sha256(b).hexdigest(),dimensions=[width,height],generation=provenance[Path(f['path']).name]))
dump(MEDIA+'/manifest.json',dict(date='2026-10-18',started_on='2026-10-17',method='built-in imagegen',video_produced=False,frames=frames,prior_atlas='视频制作/第一幕关键帧图册-20261017-v1.6/atlas.json'))
assets=read('视频制作/资产图册-20261017-v1.0/assets.json')
assets['title']='未来女孩林知夏 · 资产图册 v1.1'
assets['scope']+=' 本轮追加衣柜机构与窗户换景六张状态候选；不改变旧素材采用状态。'
for i,f in enumerate(frames):
    assets['assets'].append(dict(id=f'E01-STATE-20261017-{i+1:02}',name=f['label'],category='晨起衣柜与窗户状态候选',version='20261017-v0.1',status=f['status'],path=f['path'],role=f['visible'],limits=f['limits'],source=MEDIA+'/manifest.json',related=[dict(path=MEDIA+'/README.md',role='生成记录及审阅限制')]))
dump(ASSETS+'/assets.json',assets)
asset_builder=load_module('asset_builder','.agents/skills/linzhixia-production/scripts/build_asset_atlas.py')
write(ASSETS+'/资产图册.html',asset_builder.build(ROOT,assets,ROOT/ASSETS/'资产图册.html'))
builder=load_module('atlas_builder','.agents/skills/linzhixia-keyframe-atlas/scripts/build_atlas.py')
stats=builder.validate(atlas,ROOT)
write(ATLAS+'/关键帧图册.html',builder.render(atlas,ROOT,ROOT/ATLAS/'关键帧图册.html',stats))
dump(ATLAS+'/validation.json',dict(valid=True,**stats,video_generated=False))
dump(PLAN+'/validation.json',dict(valid=True,shots=len(shots),units=7,ai_generations=6,edit_seconds=99,ai_raw_seconds=sum(u['requested_seconds'] or 0 for u in plan['units']),handles_seconds=11,video_generated=False))

overview=['# 第一幕晨起：当前制作总览','',
    '更新：2026-10-17。18镜、99秒预算；新补六张衣柜／窗户状态候选。正式视频、配音与测时预演未制作。','',
    f'[资产图册v1.1](../../{ASSETS}/资产图册.html) · [关键帧图册v1.7](../../{ATLAS}/关键帧图册.html) · [视频生成镜头表v0.2](../../{PLAN}/生成分组.html)','',
    f'[完整动作稿v0.14]({Path(SCRIPT).name}) · [家居当前设计](../../世界观/生活技术-晨起智能家居-当前设计-v0.2.md) · [本轮补帧与核对](../../{MEDIA}/README.md)','',
    '## 本轮变化','',
    '- A009保留ID，5秒扩为8秒：预备衣架→旋出→停稳并亮起镜内预览。新图是候选，机构动态待验证。',
    '- 新增E01-A-010-W，6秒：A010送水完成后贴窗飞行换景，结束直接切A011全屋广角。摄影机模拟飞行，不新增实体飞机。',
    '- A011保持已经完成的水巷，不再重复换景；A014喊停后仍恢复庭院。人物、衣服、杯盘停点与高枕保持。',
    '- 图册直接显示两个镜头的三状态图；同机位状态图不是飞行轨迹。',
    '- 生成计划仍为6批＋日历插镜，G04申请10秒、G05申请19秒；端点参数与动态可行性待提交前核实。','',
    '## 18镜实际状态','', '| 镜头 | 内容 | 秒数 | 图像状态 | 尚缺 |','|---|---|---:|---|---|']
overview += [f"| {s['id']} | {s['title']} | {s['seconds']} | {s['presentation']['status']} | {s['presentation']['missing']} |" for s in atlas['shots']]
overview += ['','## 下一步','', '先审衣柜固定点、门与衣物避让，以及窗户变化边界与景观衔接，再按批次准备视频。其余旧帧的玉璧、枕头高度、被面材质问题继续保留，不因新增六图宣称整幕已连续性验收。','',
    '## 后续段落与归档','', '整集仍按约17分40秒的七段提案开发；A段增加9秒，整集总预算待重排，不能直接声称仍精确17:40。B—G维持宿舍联系、旧舞鞋寄修、飞越云城、检查修复、试穿与展示的方向，未扩展制作。','',
    'ToonFlow仅保留历史归档，不回填新图；原创媒体留项目。旧图册v1.6、动作稿v0.13和生成计划v0.1保留，现行入口以上方链接为准。','']
write('第一季/分镜/第一幕-当前制作总览.md','\n'.join(overview))
entry=f'[资产图册v1.1]({ASSETS}/资产图册.html) · [关键帧图册v1.7]({ATLAS}/关键帧图册.html) · [视频生成镜头表v0.2]({PLAN}/生成分组.html)'
progress=f'''# 《未来女孩林知夏》制作进度

更新：2026-10-17。本轮补衣柜递衣三状态与窗户飞行换景三状态，均为待作者审阅候选。晨起18镜、99秒预算；正式视频、配音、测时预演尚未制作。

当前流程：**资产图册 → 关键帧图册 → 视频生成镜头表**。不另建人工维护资产表，不强制ToonFlow回填。入口使用项目内linzhixia-production技能。

{entry}

## 本轮完成

- 衣柜A009：保留镜头ID，增加到8秒。固定衣架预备位→柜门避让→旋转臂连同衣架整体送出→缓停展示；无主衣架挂钩、无外围框。镜内云上花园与窗外庭院分开。
- 窗户E01-A-010-W：新增6秒，位于A010送水与A011忙碌全景之间。贴窗飞行，全息水巷沿窗蔓延，结尾直接切全景；不新增实体飞机。
- A011水巷只呈现结果，不重复换景；A014喊停后恢复庭院。旧镜头编号及历史素材保留。
- 六张状态候选已进入关键帧图册v1.7与资产图册v1.1；动作稿v0.14和生成计划v0.2同步。画面可见事实、候选限制与未制作动作分别列出。
- 仍按选定Seedance 2.5编排6批生成＋1个日历插镜。G04为8秒成片/10秒申请，G05送水→换景→全景为17秒成片/19秒申请；总106秒AI原片＋4秒插镜，去11秒余量得99秒。实际可选时长与参考槽位须提交前现场核实，本轮未调用视频模型。

## 从这里继续

| 用途 | 当前入口 |
|---|---|
| 18镜状态与下一步 | [当前制作总览](第一季/分镜/第一幕-当前制作总览.md) |
| 实际候选与审阅限制 | [本轮补帧记录]({MEDIA}/README.md) |
| 动作、对白、起止与衔接 | [晨起v0.14]({SCRIPT}) |
| 智能家居当前方案 | [家居当前设计](世界观/生活技术-晨起智能家居-当前设计-v0.2.md) |
| 人物与采用素材 | [人物一致性修复](视频制作/人物一致性修复-20261013-v1.0/README.md)、[发夹母版](人物/知夏-晨起发夹母版-20261017.md) |
| 整集与后续 | [整体分镜与分段发布](第一季/分镜/第一集-整体分镜与分段发布-v0.1.md) |
| 世界与创作规则 | [世界观索引](世界观总索引.md)、[创作速查卡](创作速查卡.md) |
| 生成工具安装与认证记录 | [项目工具](tools/media/README.md) |

## 当前边界

横屏16:9。99秒是未测时预算；原整集17:40提案需随A段增加9秒重新测算，其余段落未改。新图未经作者逐张采用；衣柜机械避让、窗户飞行与变化视差、对白节奏均未动态验证。旧帧的玉璧、枕头高度和被面材质等缺口继续有效。

## 保存与工作台

三项交付物是制作入口，后期沿用达芬奇；ToonFlow旧画布已可恢复归档。Git保存文本、图册数据、提示词及校验记录，媒体按既有规则忽略并保存在项目目录，需随项目另行备份。旧图册v1.6、动作稿v0.13、生成计划v0.1均保留。

此前逐日历史见[整理前历史](制作进度-整理前历史-20261017.md)，历史中的“当前”仅适用于当时。
'''
write('制作进度.md',progress)
card=(ROOT/'创作速查卡.md').read_text(encoding='utf-8-sig')
long_rules=card[card.index('## 〇、主题定案'):]
write('创作速查卡.md',f'''# 《未来女孩林知夏》创作速查卡

当前流程：资产图册 → 关键帧图册 → 视频生成镜头表。项目内linzhixia-production为入口；ToonFlow不再必经。

{entry}

更新：2026-10-17。晨起18镜99秒预算，动作稿[v0.14]({SCRIPT})。新增窗户贴窗飞行换景，A010送水后接A010-W，结束直接切A011全景；衣柜A009扩为8秒，预备／旋出／停稳三状态。六张新图候选待审，正式动态未制作。原整集17:40预算待随本轮增加9秒重排。

保持当前人物、服装配色、奶油色蝴蝶结母版；床承托、被子动态材质、杯贴荷叶盘、汤圆无嘴含混说话等规则不变。镜内云上花园独立于窗外水巷。窗镜不新增实体飞行物。

详见[制作总览](第一季/分镜/第一幕-当前制作总览.md)与[家居设计](世界观/生活技术-晨起智能家居-当前设计-v0.2.md)。旧帧局部连续性限制仍有效，候选不自动升级采用。历史记录保留在[整理前历史](创作速查卡-整理前历史-20261017.md)。

'''+long_rules)
print(json.dumps(dict(atlas=ATLAS,assets=len(assets['assets']),**stats),ensure_ascii=False))
