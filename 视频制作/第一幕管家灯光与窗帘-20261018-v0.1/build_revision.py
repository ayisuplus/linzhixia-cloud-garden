"""Build the approved house wake / return-to-sleep revision; no media service calls."""
import copy
import hashlib
import importlib.util
import json
import os
import struct
from html import escape as esc
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
MEDIA=HERE.relative_to(ROOT).as_posix()
ATLAS='视频制作/第一幕关键帧图册-20261018-v1.9'
ASSETS='视频制作/资产图册-20261018-v1.3'
PLAN='视频制作/第一幕Seedance2.5生成分组-20261018-v0.4'
SCRIPT='第一季/分镜/第一集-A-今天没有安排-管家灯光与窗帘-v0.16.md'
PRIOR='视频制作/第一幕关键帧图册-20261018-v1.8/atlas.json'
def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def write(path,value):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value.rstrip()+'\n',encoding='utf-8')
def dump(path,value): write(path,json.dumps(value,ensure_ascii=False,indent=2))
def url(path,folder): return quote(Path(os.path.relpath(ROOT/path,ROOT/folder)).as_posix(),safe='/.-_')
def stamp(s): return f'{int(s)//60:02}:{int(s)%60:02}'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj

architecture='中央主窗仍为单块连续玻璃、木质外框、原窗台和窗下墙；新增燕麦色遮光布帘与象牙色纱帘，隐藏双轨固定在外框上方，帘长至窗台下缘。开帘后收于外框两侧，避开衣柜旋臂和贴玻璃飞行路径；不改落地窗。右侧通廊入口另有隐藏式遮光卷帘，置于原木格门后，睡眠时降至地面阻断旁路日光，木格门保持原样。'
controller='全屋管家为无形协调层：执行既有手动闹钟预设；A006末检测坐起，A007先承托，A007-L展开灯光和开帘。检测醒来不等于她愿意起床。A013喊停只暂停主动催促，A015点头继续睡才取消本次晨起，不能据此永久修改其他闹钟。后台安防持续，不因熄灯停用。'
motion='贴窗镜保留微型追随波纹：摄影机在前沿稍后方同向同行，左后方水巷、右前方庭院持续同框；窗台向后掠过。双层帘在此镜已完全收开，不伸入相机线路。'
lighting={
 'L0':'熟睡：主窗双层帘与通廊卷帘闭合，所有室内照明关闭；只有帘缝漏光与极弱待机轮廓，窗外已是清晨。',
 'L1':'低光叫醒：主窗双层帘与通廊卷帘闭合，只有床边球灯低亮；衣柜灯、书桌灯与通廊灯不提前亮，无日光硬斑。',
 'L2':'全屋启动：先床边暖光，再衣柜局部灯、书桌层板灯；厚帘先开、纱帘后开，通廊卷帘随厚帘升起，露出原庭院；室外始终清晨。',
 'L3':'白昼服务：双层帘完全收于两侧、通廊卷帘已收顶，晨光主导，室内照明降为辅助；窗景按镜头保持庭院或水巷。',
 'L4':'喊停：主动语音和家具动作停止，设备提示可退；主窗帘与通廊卷帘仍开、水巷仍保持、基础照明不熄。',
 'L5':'同意再睡：取消本次唤醒，先恢复原庭院；纱帘先合、厚帘后合，通廊卷帘同时下降遮断侧光，书桌灯、衣柜灯及通廊灯依次熄，床边灯保留。',
 'L6':'相拥：主窗帘和通廊卷帘完成闭合、其他照明已熄，仅床边球灯柔和照着她和汤圆；设备提示退去。',
 'L7':'最后熄灯：床边球灯最后缓灭，保持暗室可读轮廓；无其他照明或设备提示重新亮起。'
}
meta=read(MEDIA+'/frames.json')
frames={f['key']:f for f in meta}
atlas=read(PRIOR);shots={s['id']:s for s in atlas['shots']}
atlas.update(subtitle='v1.9：全屋管家、闭帘暗室、分区唤醒与周末再睡；21镜115秒未测时预算。新图为候选，动态未制作。',story_script=SCRIPT,source_manifest=MEDIA+'/manifest.json')
atlas['production_guide'].update(path=PLAN+'/生成分组.html',label='04 视频生成镜头表 v0.4',summary='8批视频规划＋日历插镜；21镜115秒；暗室→苏醒→忙碌→同意再睡→最后熄灯。')

def present(s,key):
    f=frames[key];old=s.get('presentation',{}).get('path')
    if old:
        for r in s['refs']:
            if r['path']==old:r['role']='历史姿态/布局参考；灯光和帘状态以新候选及本镜文字为准，不继承冲突的旧日照或窗景。'
    s['presentation']=dict(path=f['path'],role=f['role'],visible=f['visible'],missing=f['limits'],show_as_main=True,status='本轮灯光/窗帘候选，待作者审阅')
    s.setdefault('refs',[]).append(dict(path=f['path'],role=f['label']+'；'+f['limits']))

def newshot(sid,title,seconds,key,action,entry,exit_state,next_link):
    s=dict(id=sid,title=title,seconds=seconds,framing='匹配卧室全景，固定机位',purpose=title,refs=[],entry_state=entry,exit_state=exit_state,action=action,dialogue='无',sound='细微布料与室内环境声',invariants=[architecture,controller],next_link=next_link,priority='trial',trial_recommended=True)
    present(s,key);return s

opening=newshot('E01-A-000','闭帘暗室熟睡',4,'open','在暗室中先留一拍安静：知夏抱着汤圆侧卧，低枕承托、被子盖肩。双层帘闭合，家具尚未送出或活动。仅有帘缝漏光、钟面与汤圆极弱待机光；末尾闹钟提示响起，下一镜才开始亮床边灯。','清晨室外，室内昏暗但轮廓可读，主窗帘和通廊卷帘闭合，尚未响铃。','仍熟睡，闹钟刚开始响，家具还未启动。','切A001床头闹钟；床边灯从暗渐亮。')
atlas['shots'].insert(0,opening)
for sid,key in [('E01-A-001','clock'),('E01-A-002','sleep'),('E01-A-003','punch1'),('E01-A-004','punch2'),('E01-A-005','punch3'),('E01-A-006','sit'),('E01-A-007','support'),('E01-A-011','busy'),('E01-A-012','calendar'),('E01-A-014','stop'),('E01-A-015','return'),('E01-A-016','cuddle')]: present(shots[sid],key)
shots['E01-A-001']['action']='承接开场铃声，床边球灯只亮一个低暖光光池；圆闹钟从普通钟形伸出胖软手臂，拳头抬到准备位置。钟底始终落在桌面，末尾停一拍，还没打人。窗帘仍闭、其余灯不亮。'
shots['E01-A-001']['entry_state']='双层帘闭合，闹钟刚响，圆钟落在床头柜上，手臂未伸出，床边灯尚暗。'
shots['E01-A-006']['action']+=' 镜尾管家通过坐起状态确认她醒来，一次轻柔确认声；不新增头像或第二个播报角色。此时只亮床边灯，下一镜先承托，再展开全屋服务。'
shots['E01-A-006']['exit_state']+=' 管家确认坐起，晨间流程被触发；帘仍闭、只有低床边光。'
shots['E01-A-007']['next_link']='切A007-L全屋分区启动与开帘；随后才切拖鞋，人物仍在床上。'
shots['E01-A-006']['sound']='布料声、轻收臂声；镜尾一次轻柔坐起确认声。'
shots['E01-A-001']['sound']='承接开场轻柔闹铃、伸缩声；隔帘的弱鸟声。'
shots['E01-A-013']['sound']='第一声停立刻停止主动播报与踱步；保留自然环境底声，不到句末才停。'
shots['E01-A-013']['presentation']['missing']=shots['E01-A-013']['presentation']['missing'].replace('熄光与喊停声音','设备提示光退去与喊停声音')
shots['E01-A-007']['sound']='坐起确认后的轻承托声与床被短句；此处不再第二次检测醒来。'
startup=newshot('E01-A-007-L','全屋苏醒·分区亮灯与开帘',6,'wake_mid','0—1.5秒床边暖光稍升，衣柜局部灯、书桌层板灯先后亮起；通廊灯作弱辅助，不另播报。1.5—3.5秒厚帘向两侧收拢，通廊遮光卷帘同步升至隐藏盒；仍闭的纱帘柔化主窗晨光。3.5—6秒纱帘收开，通廊卷帘保持已收顶；原庭院完整显露，晨光铺上地板和被面；局部灯退为辅助亮度。衣柜仍闭、衣服未递出，杯盘未进入，椅子仍靠桌，拖鞋未走。','A006已确认坐起，A007已托背；双层帘闭合，只有床边灯亮。','双层帘全开、通廊卷帘收顶，原庭院可见，灯光完成过渡，家具送物尚未发生。','切A008-PRE拖鞋开始走；维持开帘晨光。')
startup['state_frames']=[{k:frames[key][k] for k in ('path','label','role','visible','limits')} for key in ['wake_mid','wake_end']]
startup['refs'].append(dict(path=frames['wake_end']['path'],role='开帘完成状态，原庭院；不能继承为窗户换景完成'))
atlas['shots'].insert(atlas['shots'].index(shots['E01-A-007'])+1,startup)
shots['E01-A-012'].update(title='周末，闹钟却开着',action='切书桌青瓷薄屏，清楚显示“周末”“今日无事／宜休沐”，下方“闹钟：已开启”及开启开关。她看清周末却忘关的闹钟状态，没有触屏；家具仍在催促，下一镜口头喊停。',dialogue='无；界面：“周末”“今日无事”“宜休沐”“闹钟：已开启”“暂停唤醒”。',exit_state='她意识到今天是周末，昨晚忘了关闹钟；界面仍是开启态。')
shots['E01-A-012']['invariants']=['周末、今日无事、宜休沐、闹钟已开启都要可读；开关此刻保持开启，不提前取消','不固定具体日期；周末是故事设定，不从制作日期推定','人物未触屏；只取消本次唤醒的动作发生在A015点头后','原画面精确文字用于剪辑插镜，实际视频文字后期稳定合成']
shots['E01-A-013'].update(dialogue='知夏：“停停停！别吵了！”',action='知夏抬起一只手掌喊停，第一声停立刻中止语音催促、踱步、衣架轻摆和椅子动作；各物件停在途中，不先归位。另一手留在被面，枕头仍托背；杯盘停稳承杯，读数和家具提示随后淡出。玉璧短弧确认后退去，它是提示光，不是房间照明。窗帘仍全开、窗仍水巷、基础照明保持；她低头缓一口气，下一镜才说忘关闹钟。',exit_state='催促停止、家具停住，但晨光和基础照明仍在，水巷保持；尚未进入再睡模式。')
shots['E01-A-014'].update(seconds=8,title='周末忘关闹钟·全屋等她决定',entry_state='刚喊停，家具与杯盘停在途中；窗帘仍开，窗内水巷和基础照明保持。',action='切与A011匹配的全景，保持衣架伸出、椅子拉出、拖鞋错位、杯盘承托。知夏缓下语气，低声自语“……周末。忘关闹钟了。”床停半拍，轻声问要不要铺回去。灯光暂时不变，窗帘不关，窗景仍水巷；让她选择是否继续休息。',dialogue='知夏：“……周末。忘关闹钟了。”\n床：“那……我再给你铺回去？”',exit_state='床问完，等待知夏确认；照明、开帘和水巷保持，家具不归位。',next_link='A015点头才取消本次晨起，恢复庭院并开始合帘。')
shots['E01-A-014']['invariants']=[architecture,'本镜只停催促，窗帘全开、水巷不变、基础照明不灭','衣柜臂仍伸出，杯盘仍停稳，枕头维持承托；不得一键归位','画面闭口为静态状态候选，完整自语和询问需动态口型/声音']
shots['E01-A-015']['action']='听到床询问，知夏困倦地点头，顺势向枕头靠回。管家据此取消本次晨起和本次闹钟重响；原枕随她躺下放低，被子让开手臂。窗景先恢复真实庭院，纱帘开始合拢、厚帘随后合拢，晨光逐步收窄；通廊入口遮光卷帘同步下降，阻断旁路日光，室外仍是同一清晨。书桌灯先熄、衣柜局部灯随后熄，通廊辅助光退下，床边球灯保留。她侧躺后伸手找汤圆，指尖尚未接触，被子尚未盖肩；衣柜臂、杯盘和椅子仍保持停点，不瞬间消失。'
shots['E01-A-015']['exit_state']='她躺回低枕伸手，汤圆仍在枕边；合帘已开始，局部灯逐步退下，床边灯仍亮。'
shots['E01-A-015']['next_link']='A016接汤圆自己靠回与盖肩，同时完成合帘；最后一盏床边灯留给A016-L。'
shots['E01-A-016']['action']='汤圆沿枕面靠回知夏怀里，她抱住它，被子绕过手臂盖到肩侧并落稳。主窗帘与通廊卷帘完成闭合，其他分区灯已熄；床头玉璧提示弧和被面表情淡去，显像区恢复织物。仅床边球灯留一小片暖光照着相拥轮廓，不能在本镜提前全部熄灭。衣柜伸出、椅子和杯盘仍停在原处。'
shots['E01-A-016']['exit_state']='她抱住汤圆安静休息，主窗双层帘与通廊卷帘闭合、其他灯已熄，床边灯仍亮。'
shots['E01-A-016']['next_link']='切A016-L匹配暗室全景，最后床边灯缓灭。'
ending=newshot('E01-A-016-L','最后一盏灯·陪她再睡',4,'final','承接相拥完成，固定全屋机位，主窗双层帘与通廊卷帘已经闭合。0—2秒最后一盏床边球灯缓缓熄灭，2—4秒留住暗室里相拥的轮廓与轻呼吸。所有设备提示停止主动发光；仅允许极弱待机与帘边漏光，不让屏幕重新照亮房间。衣柜臂与服装仍伸出，杯盘仍承杯、椅子仍拉出、鞋仍错位，不能恢复成开场整齐状态。','双层帘已合，其他灯已熄，只有床边灯亮；她已相拥睡下。','床边灯熄，暗室安静，安全承托与后台安防继续。','本段结束，后续剧情另接。')
atlas['shots'].append(ending)
shots={s['id']:s for s in atlas['shots']}
for s in atlas['shots']:
    sid=s['id']
    phase='L0' if sid=='E01-A-000' else 'L1' if sid in [f'E01-A-{i:03}' for i in range(1,8)] else 'L2' if sid=='E01-A-007-L' else 'L4' if sid in ['E01-A-013','E01-A-014'] else 'L5' if sid=='E01-A-015' else 'L6' if sid=='E01-A-016' else 'L7' if sid=='E01-A-016-L' else 'L3'
    s['light_phase']=phase;s['invariants']+=[architecture,lighting[phase]]
    s['entry_state']+=' 本镜推进所遵循的光线阶段（起始依前句，非已完成状态）：'+lighting[phase]
    if sid=='E01-A-010-W':s['invariants'].append(motion)
    if sid=='E01-A-013':s['presentation']['missing']+=' 旧图未补帘侧堆与新灯具位置；只作喊停姿态参考，不继承旧光线变化。'
for m in atlas['masters']:
    if m['id']=='M-08':m['limits']+=' 新增帘轨与帘长改依M-09，原图无帘状态不再完整。'
atlas['masters'].append(dict(id='M-09',title='双层窗帘与开场暗室',path=frames['open']['path'],role=architecture,status='作者认可设计方向，图像候选待审',limits='开场家具未送出，不能拿此整齐状态当结尾；结尾保留停点与承托。'))
assert len(shots)==21 and sum(s['seconds'] for s in shots.values())==115

# Save actual image provenance, all new candidates, and the three deliverables.
provenance=read(MEDIA+'/generation-inputs.json');manifest=[]
for f in meta:
    b=(ROOT/f['path']).read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n'
    manifest.append(dict(**f,dimensions=list(struct.unpack('>II',b[16:24])),sha256=hashlib.sha256(b).hexdigest(),generation=provenance[Path(f['path']).name],status='候选待作者审阅'))
history=[dict(path=MEDIA+'/'+name,**entry) for name,entry in provenance.items() if entry['status'].startswith(('rejected','superseded'))]
dump(MEDIA+'/manifest.json',dict(date='2026-10-18',frames=manifest,history=history,video_produced=False,prior_atlas=PRIOR))
assets=read('视频制作/资产图册-20261018-v1.2/assets.json');assets['title']='未来女孩林知夏 · 资产图册 v1.3';assets['scope']+=' 新增管家灯光/窗帘及周末状态候选；旧图保留，旧光线按当前阶段覆盖。'
for i,f in enumerate(manifest,1):assets['assets'].append(dict(id=f'E01-LIGHT-20261018-{i:02}',name=f['label'],category='管家灯光与窗帘候选',version='20261018-v0.1',status=f['status'],path=f['path'],role=f['visible'],limits=f['limits'],source=MEDIA+'/manifest.json',related=[dict(path=MEDIA+'/README.md',role='生成与核对记录')]))
dump(ASSETS+'/assets.json',assets)
ab=module('asset_builder','.agents/skills/linzhixia-production/scripts/build_asset_atlas.py');write(ASSETS+'/资产图册.html',ab.build(ROOT,assets,ROOT/ASSETS/'资产图册.html'))
dump(ATLAS+'/atlas.json',atlas)
md=['# 第一集A段：今天没有安排｜管家灯光与窗帘 v0.16','','2026-10-18。21镜115秒预算，未测时、未制作正式视频。新增A000、A007-L、A016-L；A014由6秒扩为8秒，保留旧18镜ID。','',f'[图册v1.9](../../{ATLAS}/关键帧图册.html) · [生成镜头表v0.4](../../{PLAN}/生成分组.html) · [生成核对](../../{MEDIA}/README.md)','',controller,'',architecture,'',motion,'','## 光线与窗帘状态','']+[f'- {k}：{v}' for k,v in lighting.items()]
cursor=0
for s in atlas['shots']:
    end=cursor+s['seconds'];p=s['presentation']
    md+=['',f"## {s['id']}｜{s['title']}｜{stamp(cursor)}—{stamp(end)}（{s['seconds']}秒）",'',f"**画面：{p['status']}。** {p['visible']}",'',f"**限制：** {p['missing']}",'',f"**起始：** {s['entry_state']}",'',f"**视频计划（未制作）：** {s['action']}",'',f"**结束：** {s['exit_state']}",'',f"**对白：** {s['dialogue']}",'',f"**声音：** {s['sound']}",'',f"**衔接：** {s['next_link']}",'','**保持：** '+'；'.join(s['invariants']),'','**参考：**']
    md+=[f"- [{Path(r['path']).name}](../../{r['path']})：{r['role']}" for r in s['refs']];cursor=end
write(SCRIPT,'\n'.join(md))

plan=read('视频制作/第一幕Seedance2.5生成分组-20261018-v0.3/plan.json')
plan.update(atlas_source=ATLAS+'/atlas.json',story_script=SCRIPT,status='planned_not_submitted_not_dynamically_tested')
byid={u['id']:u for u in plan['units']}
g00=copy.deepcopy(byid['G02']);g00.update(id='G00',title='暗室开场',shot_ids=['E01-A-000'],head_handle=1,tail_handle=1)
byid['G02'].update(title='坐起确认、承托与全屋苏醒',shot_ids=['E01-A-006','E01-A-007','E01-A-007-L'])
byid['G06'].update(title='喊停与发现周末',shot_ids=['E01-A-013','E01-A-014'])
g07=copy.deepcopy(byid['G06']);g07.update(id='G07',title='合帘、相拥与最后熄灯',shot_ids=['E01-A-015','E01-A-016','E01-A-016-L'])
plan['units']=[g00]+[u for u in plan['units']]+[g07]
cursor=0
for u in plan['units']:
    sids=u['shot_ids'];edit=sum(shots[s]['seconds'] for s in sids)
    u.update(timeline_start=cursor,edit_seconds=edit,timeline_end=cursor+edit);cursor+=edit
    u['requested_seconds']=None if u['method']=='edit_existing_image' else edit+u['head_handle']+u['tail_handle']
    u['staging']='按以下逐镜顺序执行，各镜动作中秒数均为镜内相对时间，需加该镜在本批的起点：'+'；'.join(sids)
    u['continuity']=controller+' '+architecture+' '+(' '.join(dict.fromkeys(lighting[shots[s]['light_phase']] for s in sids)))
    u['reference_strategy']='以本批各镜新候选约束当前光线与窗帘，历史图只取未被覆盖的身份、结构和动作。动作终态不可直接当首帧；全屋管家无实体头像。'
    u['why']='按动作及光线因果分组，保留镜头ID；预算未经实测，端点时长选项与参考槽位提交前核实。'
    u['safe_cut']='在本批最后一个镜头的结束状态成立后切出，保持光线、窗帘、承托和家具停点，不截断接触过程。'
    u['fallback']='如多动作不稳定，按所列镜头安全结束状态拆分；新增请求及余量另记，不吞动作或对白凑时长。'
    if u['id']=='G05':u['fallback']+=' 贴窗换景仍优先分别控制相机路径和窗面显影后按统一视点合成，窗帘堆不得挡路径。'
    pos=u['head_handle'];u['beats']=[]
    for sid in sids:
        s=shots[sid];u['beats'].append(dict(shot_id=sid,start=pos,end=pos+s['seconds'],title=s['title'],image=s['presentation']['path'],image_role=s['presentation']['role']));pos+=s['seconds']
dump(PLAN+'/plan.json',plan)

intro='8次AI生成＋1个日历剪辑插镜；21镜、115秒成片预算。126秒AI原片＋4秒插镜，去15秒余量。尚未提交视频、未测对白时长。'
rules=[controller,architecture,motion,plan['spec_note'],'三拳段29秒预算保留；新增开场4秒、全屋启动6秒、最后熄灯4秒，A014增加2秒。','A006末确认醒来，A007先托背，A007-L开帘见庭院；A010-W才换水巷。','A013喊停不熄灯，A014保留水巷；A015点头后取消本次唤醒、回庭院、合帘关分区灯，A016-L床灯最后熄。','窗帘与灯光按当前阶段覆盖旧帧；旧全景挂钩不得覆盖A009刚性直连机构。','人物、服装配色、发夹、玉璧、承托和家具停点跨镜保持。','每批提示词完整展开，未提交视频；端点时长与参考槽位须现场核实。','对白、脚步和提示声遵循动作稿；候选不自动升级为作者采用。']
pmd=['# 第一幕 · Seedance 2.5生成分组 v0.4','',intro,'','## 共同执行口径','']+['- '+r for r in rules]+['','| 单元 | 镜头 | 成片区间 | 成片/申请 |','|---|---|---|---|']
html=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>晨起视频生成镜头表 v0.4</title><style>body{margin:0;background:#f5f1e8;color:#293f38;font:16px/1.7 system-ui,"Microsoft YaHei"}main{max-width:1200px;margin:auto;padding:32px}article{background:#fffdf8;padding:24px;margin:28px 0;border:1px solid #d9d8cb;border-radius:12px}a{color:#376a59}.strip{display:flex;gap:14px;flex-wrap:wrap}.strip a{width:210px}img{width:100%}pre{white-space:pre-wrap;font:inherit}nav{display:flex;gap:18px;flex-wrap:wrap}small{color:#6f756e}</style><main><h1>晨起 · 视频生成镜头表 v0.4</h1>',f'<p>{esc(intro)}</p><p><a href="{url(ATLAS+"/关键帧图册.html",PLAN)}">关键帧图册v1.9</a> · <a href="生成分组.md">交接文档</a></p><ul>'+''.join('<li>'+esc(r)+'</li>' for r in rules)+'</ul><nav>'+''.join(f'<a href="#{u["id"]}">{u["id"]} · {u["edit_seconds"]}秒</a>' for u in plan['units'])+'</nav>']
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

kb=module('keyframe_builder','.agents/skills/linzhixia-keyframe-atlas/scripts/build_atlas.py');stats=kb.validate(atlas,ROOT)
write(ATLAS+'/关键帧图册.html',kb.render(atlas,ROOT,ROOT/ATLAS/'关键帧图册.html',stats));dump(ATLAS+'/validation.json',dict(valid=True,**stats,video_generated=False))
pb=module('plan_validator','.agents/skills/linzhixia-production/scripts/validate_generation_plan.py');dump(PLAN+'/validation.json',pb.validate(ROOT,plan))
overview=['# 第一幕晨起：当前制作总览','','2026-10-18。21镜115秒未测时预算，正式视频与声音未制作。','',f'[资产图册v1.3](../../{ASSETS}/资产图册.html) · [关键帧图册v1.9](../../{ATLAS}/关键帧图册.html) · [视频镜头表v0.4](../../{PLAN}/生成分组.html)','',f'[动作稿v0.16]({Path(SCRIPT).name}) · [本轮图像与核对](../../{MEDIA}/README.md)','',controller,'',architecture,'','| 镜头 | 内容 | 秒数 | 光线阶段 | 实际画面限制 |','|---|---|---:|---|---|']
overview += [f"| {s['id']} | {s['title']} | {s['seconds']} | {s['light_phase']} | {s['presentation']['missing']} |" for s in atlas['shots']]
overview+=['','本轮较99秒增加16秒；相对原90秒增加25秒。原整集17:40预算须另重排，不声称仍精确成立。保留历版与稳定ID；候选不等于作者采用、动态验证或成片。']
write('第一季/分镜/第一幕-当前制作总览.md','\n'.join(overview))
print(json.dumps(dict(**stats,new_frames=len(meta),assets=len(assets['assets'])),ensure_ascii=False))
