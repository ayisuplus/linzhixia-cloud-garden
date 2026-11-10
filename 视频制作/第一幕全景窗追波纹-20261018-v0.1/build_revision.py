"""Build v1.8 from preserved v1.7; no generation or browser calls."""
import hashlib
import importlib.util
import json
import os
import struct
from pathlib import Path
from html import escape as esc
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MEDIA = HERE.relative_to(ROOT).as_posix()
ATLAS = '视频制作/第一幕关键帧图册-20261018-v1.8'
ASSETS = '视频制作/资产图册-20261018-v1.2'
PLAN = '视频制作/第一幕Seedance2.5生成分组-20261018-v0.3'
SCRIPT = '第一季/分镜/第一集-A-今天没有安排-全景窗追波纹-v0.15.md'
PRIOR = '视频制作/第一幕关键帧图册-20261017-v1.7/atlas.json'

def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def write(path, value):
    p=ROOT/path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(value, encoding='utf-8')
def dump(path, value): write(path, json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def url(path, folder): return quote(Path(os.path.relpath(ROOT/path, ROOT/folder)).as_posix(), safe='/.-_')
def stamp(s): return f'{int(s)//60:02}:{int(s)%60:02}'
def module(name, path):
    spec=importlib.util.spec_from_file_location(name, ROOT/path)
    obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj

architecture='中央主窗为单块连续玻璃，保留原木质外框、原窗台高度和窗下实体墙；去掉内部横竖窗格、花格和分扇把手，不改成落地窗；右侧通廊门格栅不改。'
motion='摄影机模拟微型飞机贴着窗面追随波纹前沿；前沿在镜头前方一点，保持在画面中央偏右。摄影机和波纹沿窗同向前进，窗台木纹和近处边缘明显向后掠过，不能用固定机位只移动波纹替代飞行。'
window=[
    dict(path=MEDIA+'/E01-A-010-W-01-全景窗起始.png', label='01 全景玻璃·起步追波', role='opening', visible='无内窗格的连续玻璃、近处木质外框与窗台，窗后全为原庭院。', limits='起步前状态候选；波纹尚未启动。静帧不证明镜头已在飞行。'),
    dict(path=MEDIA+'/E01-A-010-W-02-追随波纹.png', label='02 追随前沿·新旧景共存', role='action', visible='左侧水巷已显露，右侧白墙庭院尚未变化，中间窄波纹划出交界；近左外框退出构图，窗台保留近景尺度。', limits='明确变化状态与途中构图；中、末帧使用相同构图锁景，不代表摄影机停住，也不是已标定的三个相机位姿。波纹略亮，动态可减弱。'),
    dict(path=MEDIA+'/E01-A-010-W-03-换景完成.png', label='03 波纹扫完·水巷完成', role='ending', visible='可见玻璃内为连续水巷，波纹消退；中间帧已显露的桥、船与左岸大体保持。', limits='中段机位的完成状态参考；实际末段仍须继续移动相机后减速。近景到全景的精确视差与景物投影未标定。'),
]
wide_frames=[
    dict(path=MEDIA+'/E01-A-011-全景窗忙碌.png', label='A011 全景窗·忙碌结果', role='action', visible='忙碌房间中央窗无内部花格，整窗呈现水巷；人物前倾攥被、杯读数与被缘张口状态保留。', limits='本轮只修主窗；衣架挂钩小细部仍是历史图，须继承A009固定直连结构。旧枕头、玉件、被面材质限制继续有效。'),
    dict(path=MEDIA+'/E01-A-014-全景窗喊停.png', label='A014 全景窗·喊停复原', role='action', visible='同一无内窗格主窗恢复白墙庭院；人物闭眼、杯读数消失，被缘表情收敛，衣物与杯盘保持伸出和承托。', limits='保留历史衣架挂钩细部限制；喊停动态和窗景复原过程未制作。窗外枝叶与近景不构成几何一致性证明。'),
]
atlas=read(PRIOR)
atlas.update(subtitle='v1.8：全景玻璃与微型追波纹飞行；新增5张候选，18镜99秒预算不变。静帧、动作计划及动态验收分别记录。', story_script=SCRIPT, source_manifest=MEDIA+'/manifest.json')
atlas['production_guide'].update(path=PLAN+'/生成分组.html', label='04 视频生成镜头表 v0.3')
shots={s['id']:s for s in atlas['shots']}
s=shots['E01-A-010-W']
s.update(title='贴窗追波纹·水巷展开', framing='微型尺度贴玻璃沿窗前飞，视线略朝向玻璃；追随前方的变化波纹，木窗台作为高速近景参照，末尾硬切A011全景。',
    purpose='以追随波纹的飞行同时展示尺度、速度和新旧窗景转换。',
    entry_state='A010送水已完成，窗内仍全为原庭院；从主窗左侧进入微型贴面机位，木质外框局部巨大，玻璃连续无内窗格。',
    exit_state='波纹扫过最后可见窗区并消退，整窗水巷完成，摄影机减速后硬切A011。',
    action='0—1秒贴着窗台从左端向右端起步，原庭院保持；波纹先在稍前方启动，摄影机加速追上。1—4.5秒摄影机处于波纹前沿稍后方，与其同向近似同速前进，边界保持中央偏右；左侧后方已展开水巷，右侧前方仍是原庭院，两种景象持续同时可见。视线略朝玻璃，不能平行到只看见一条边。窗台木纹向后掠过，近处外框退出画面，远端外框逐渐接近；玻璃及外框不形变。4.5—6秒波纹扫完最后窗区并消退，摄影机仍向前滑行后减速，短留完整水巷，直接切A011广角。中末静帧锁同一底景便于比较，不允许据此把实际运动冻结。',
    invariants=[architecture, motion, '摄影机模拟微型飞机飞行，不新增实体飞机道具；不穿玻璃、窗台或外框', '变化只在玻璃显示区发生，木材、窗下墙、人物与室内物件不随之变形或溶解', '波纹后方为已变水巷，波纹前方为原庭院，单向一次扫完；禁止左右反转和重复启动', '桥、船、建筑在已显露区域固定，随统一相机产生视点变化，不逐帧重画或漂移', '杯盘停点、衣柜递出和人物状态沿用A010；拖鞋画外持续踱步'],
    state_frames=window)
s['presentation'].update(path=window[1]['path'], visible=window[1]['visible'], missing=window[1]['limits']+' 追波纹的实际速度、视差与首尾机位仍待动态验证。', status='全景窗追波纹候选，待作者审阅')
s['refs']=[dict(path=f['path'],role=f['label']+'；'+f['limits']) for f in window]+[dict(path=wide_frames[0]['path'],role='下一镜全景与主窗结构；近远视点需动态统一')]
for sid,f in zip(['E01-A-011','E01-A-014'], wide_frames):
    shot=shots[sid]
    old=shot['presentation']['path']
    shot['presentation'].update(path=f['path'],visible=f['visible'],missing=f['limits'],status='主窗修订候选，待作者审阅')
    shot['refs']=[r for r in shot['refs'] if r['path']!=old]+[dict(path=old,role='历史布局和动作参考；内部窗格已退出当前设计，不作为窗结构依据'),dict(path=f['path'],role=f['label']+'；'+f['limits'])]
    shot['entry_state']+=' '+architecture
    shot['action']+=' 主窗全程保持连续玻璃及原外框窗台，不出现内窗格。'
    shot['invariants']=[x.replace('整窗连续换景，不出现贴图边框','整窗连续显示已完成的水巷，不再次换景，不出现贴图边框') for x in shot['invariants']]+[architecture]
for shot in atlas['shots']:
    if shot['id'] not in ['E01-A-010-W','E01-A-011','E01-A-014']:
        shot['invariants'].append('如中央主窗入画，统一沿用M-08连续玻璃外框结构；历史参考中的内部窗格不继承。')
        shot['presentation']['missing']+=' 如旧画面包含中央主窗内窗格，属于待统一历史细节，本轮未逐镜重绘。'
for m in atlas['masters']:
    if m['id']=='M-02': m['limits']+=' 中央窗内部花格已废弃，主窗结构改依M-08；右侧通廊门格栅仍保留。'
atlas['masters'].append(dict(id='M-08',title='主窗连续玻璃与木框窗台',path=wide_frames[0]['path'],role=architecture,status='作者同意结构方向，图像候选待审',limits='只约束主窗结构；不以本图替代人物和衣柜母版，不将水巷套到换景前。'))

provenance=read(MEDIA+'/generation-inputs.json')
frames=[]
for f in window+wide_frames:
    b=(ROOT/f['path']).read_bytes(); assert b[:8]==b'\x89PNG\r\n\x1a\n'
    frames.append(dict(**f,status='候选待作者审阅',sha256=hashlib.sha256(b).hexdigest(),dimensions=list(struct.unpack('>II',b[16:24])),generation=provenance[Path(f['path']).name]))
dump(MEDIA+'/manifest.json',dict(date='2026-10-18',method='built-in imagegen',video_produced=False,frames=frames,prior_atlas=PRIOR))
assets=read('视频制作/资产图册-20261017-v1.1/assets.json')
assets.update(title='未来女孩林知夏 · 资产图册 v1.2')
assets['scope']+=' 2026-10-18追加5张全景窗候选；保留旧图并标明窗结构已替代。'
old_window=next(s for s in read(PRIOR)['shots'] if s['id']=='E01-A-010-W')
old_window_paths={f['path'] for f in old_window['state_frames']}
for a in assets['assets']:
    if a['path'] in old_window_paths:
        a['status']='历史候选，窗结构已替代'
        a['limits']+=' 内部花格不再采用，当前依据为全景玻璃追波纹候选。'
for i,f in enumerate(frames,1):
    assets['assets'].append(dict(id=f'E01-WINDOW-20261018-{i:02}',name=f['label'],category='全景窗追波纹候选',version='20261018-v0.1',status=f['status'],path=f['path'],role=f['visible'],limits=f['limits'],source=MEDIA+'/manifest.json',related=[dict(path=MEDIA+'/README.md',role='生成与视觉核对记录')]))
dump(ASSETS+'/assets.json',assets)
ab=module('asset_builder','.agents/skills/linzhixia-production/scripts/build_asset_atlas.py')
write(ASSETS+'/资产图册.html',ab.build(ROOT,assets,ROOT/ASSETS/'资产图册.html'))
dump(ATLAS+'/atlas.json',atlas)
kb=module('keyframe_builder','.agents/skills/linzhixia-keyframe-atlas/scripts/build_atlas.py')

# Render the full action script, keeping each stable shot ID and dialogue.
md=['# 第一集A段：今天没有安排｜全景窗追波纹 v0.15','','2026-10-18。18镜99秒预算不变。本轮5张图为候选；正式视频未制作。', '',f'[关键帧图册v1.8](../../{ATLAS}/关键帧图册.html) · [生成镜头表](../../{PLAN}/生成分组.html) · [生成与核对记录](../../{MEDIA}/README.md)','',architecture,'',motion,'','中间帧明确新旧景与波纹同框；中末帧锁景不等于相机静止。窗面合成与相机路径分开控制后再结合，不能用平面滑动代替真实近远视差。','']
cursor=0
for s in atlas['shots']:
    end=cursor+s['seconds']; p=s['presentation']
    md += [f"## {s['id']}｜{s['title']}｜{stamp(cursor)}—{stamp(end)}（{s['seconds']}秒）",'',f"**当前画面：{p['status']}。** {p['visible']}",'',f"**尚未体现：** {p['missing']}",'',f"**起始：** {s['entry_state']}",'',f"**视频计划（未制作）：** {s['action']}",'',f"**结束：** {s['exit_state']}",'',f"**对白：** {s['dialogue']}",'',f"**声音：** {s['sound']}",'',f"**衔接：** {s['next_link']}",'','**保持：** '+'；'.join(s['invariants']),'','**参考：**']
    md += [f"- [{Path(r['path']).name}](../../{r['path']})：{r['role']}" for r in s['refs']]+['']
    cursor=end
write(SCRIPT,'\n'.join(md).rstrip()+'\n')

plan=read('视频制作/第一幕Seedance2.5生成分组-20261017-v0.2/plan.json')
plan.update(atlas_source=ATLAS+'/atlas.json',story_script=SCRIPT,status='planned_not_submitted_not_dynamically_tested')
g5=next(u for u in plan['units'] if u['id']=='G05')
g5.update(title='送水、贴窗追波纹与全屋忙碌',staging='含片头余量的G05原片时间：1—6秒送水，6—12秒贴窗追波纹，12—18秒全屋全景；0—1秒与18—19秒为余量。以下0—6秒仅是窗镜内部相对时间，原片执行时整体加6秒，禁止在送水段提前换景：'+shots['E01-A-010-W']['action'],reference_strategy='新主窗三状态＋A011新全景，原A010只约束人物和杯盘。中、末帧是同机位换景状态，实际相机路径仍前进，不能当成静止视频。',continuity=architecture+' '+motion+' A010原庭院，A010-W只换一次，A011水巷保持；衣柜、杯盘和人物状态保持。',fallback='优先把相机沿窗路径和玻璃内的景象揭示分别控制，再用同一视点合成。先固定窗几何、窗台纹理和玻璃遮罩，再锁庭院/水巷两层及跟随相机的变化前沿；补足真实视差，不用一张图平移冒充飞行。若多机位长段不稳，可拆送水5秒/窗户6秒/全景6秒，申请7/8/8秒，额外4秒余量需另记，本计划仍未提交。')
for u in plan['units']:
    if architecture not in u['continuity']: u['continuity']+=' '+architecture
    for b in u['beats']:
        s=shots[b['shot_id']]; b.update(title=s['title'],image=s['presentation']['path'],image_role=s['presentation']['role'])
dump(PLAN+'/plan.json',plan)

intro='6次AI生成＋1个日历剪辑插镜；18镜、99秒成片预算。106秒AI原片＋4秒插镜，去11秒余量。尚未提交视频、未测对白时长。'
rules=[architecture,motion,plan['spec_note'],'原有三拳29秒与喊停至相拥25秒预算保留，所有长段稳定性均待验证。','G04衣柜8秒成片/10秒申请；G05送水→换景→全景17秒成片/19秒申请。','同批允许明确切镜；G05最后直接切全景，禁止换景重启或杯盘二次飞入。','人物、服装配色、发夹、玉璧、高枕、杯盘停点与衣架支撑跨镜保持。','每批使用独立完整提示词，不引用聊天省略执行内容；无任务ID、无假生成结果。','声音遵循动作稿；脚步跨窗镜持续，A013第一声停骤止。新图候选不自动升级为作者采用。']
pmd=['# 第一幕 · Seedance 2.5生成分组 v0.3','',intro,'','## 共同执行口径','']+['- '+r for r in rules]+['','| 单元 | 镜头 | 成片区间 | 成片/申请 |','|---|---|---|---|']
html=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>晨起视频生成镜头表 v0.3</title><style>body{margin:0;background:#f5f1e8;color:#293f38;font:16px/1.7 system-ui,"Microsoft YaHei"}main{max-width:1200px;margin:auto;padding:32px}article{background:#fffdf8;padding:24px;margin:28px 0;border:1px solid #d9d8cb;border-radius:12px}a{color:#376a59}.strip{display:flex;gap:14px;flex-wrap:wrap}.strip a{width:210px}img{width:100%}pre{white-space:pre-wrap;font:inherit}nav{display:flex;gap:18px;flex-wrap:wrap}small{color:#6f756e}</style><main><h1>晨起 · 视频生成镜头表 v0.3</h1>',f'<p>{esc(intro)}</p><p><a href="{url(ATLAS+"/关键帧图册.html",PLAN)}">关键帧图册v1.8</a> · <a href="生成分组.md">交接文档</a></p><ul>'+''.join('<li>'+esc(r)+'</li>' for r in rules)+'</ul><nav>'+''.join(f'<a href="#{u["id"]}">{u["id"]} · {u["edit_seconds"]}秒</a>' for u in plan['units'])+'</nav>']
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
        prompt+=f"\n{b['start']:g}—{b['end']:g}秒 {s['id']}：{s['framing']}。动作内秒数均相对此镜起点，需加本段起始秒数，不得重置整批时间。起始：{s['entry_state']} 动作：{s['action']} 结束：{s['exit_state']} 对白：{s['dialogue']} 声音：{s['sound']} 保持：{'；'.join(s['invariants'])}。\n"
    prompt+='\n前后余量只延续当前状态，不重复对白或动作。不同机位允许明确切镜。无额外配乐，保留环境声以便后期连续剪辑。'
    if u['requested_seconds']:
        write(PLAN+f"/prompt-{u['id']}.txt",prompt+'\n')
        pmd+=['','**完整执行提示词：**','',prompt]
        html.append(f'<details><summary>完整执行提示词</summary><pre>{esc(prompt)}</pre></details>')
    html.append('</article>')
html.append('</main></html>')
write(PLAN+'/生成分组.md','\n'.join(pmd)+'\n');write(PLAN+'/生成分组.html',''.join(html))


overview=['# 第一幕晨起：当前制作总览','','2026-10-18。18镜99秒预算不变；本轮全景窗5张候选，正式动态未制作。','',f'[资产图册v1.2](../../{ASSETS}/资产图册.html) · [关键帧图册v1.8](../../{ATLAS}/关键帧图册.html) · [视频生成镜头表v0.3](../../{PLAN}/生成分组.html)','',f'[完整动作稿v0.15]({Path(SCRIPT).name}) · [本轮图像及核对](../../{MEDIA}/README.md)','',architecture,'',motion,'','旧衣柜三状态继续沿用，主窗三状态更新；A011/A014两张全景同步结构。旧图的衣架挂钩、枕头、玉件、被面材质及未重画镜头内窗格仍须统一。','','| 镜头 | 内容 | 秒数 | 图像状态 | 尚缺 |','|---|---|---:|---|---|']
overview += [f"| {s['id']} | {s['title']} | {s['seconds']} | {s['presentation']['status']} | {s['presentation']['missing']} |" for s in atlas['shots']]
overview += ['','原整集17:40为历史预算，须随此前A段增加9秒重排。旧版本、原素材与稳定ID保留。新候选不自动变为作者采用。','']
write('第一季/分镜/第一幕-当前制作总览.md','\n'.join(overview))
stats=kb.validate(atlas,ROOT)
write(ATLAS+'/关键帧图册.html',kb.render(atlas,ROOT,ROOT/ATLAS/'关键帧图册.html',stats))
dump(ATLAS+'/validation.json',dict(valid=True,**stats,video_generated=False))
print(json.dumps(dict(atlas=ATLAS,assets=len(assets['assets']),new_frames=len(frames),**stats),ensure_ascii=False))
