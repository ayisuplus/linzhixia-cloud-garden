"""One-time migration from preserved v1.9/v0.4; never regenerates media."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def create(name,data):
    with (HERE/name).open('x',encoding='utf-8') as f: f.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

atlas=read('视频制作/第一幕关键帧图册-20261018-v1.9/atlas.json')
old=read('视频制作/第一幕Seedance2.5生成分组-20261018-v0.4/plan.json')
architecture=next(x for x in atlas['shots'][0]['invariants'] if x.startswith('中央主窗仍'))
atlas.pop('production_guide',None)
atlas.update(title='今天没有安排 · 分镜与生成',subtitle='v2.0：分镜图册与生成执行共用镜头资料。21镜115秒预算不变，候选与图像限制沿用v1.9；本轮整理未新增媒体或提交生成。',asset_atlas='视频制作/资产图册-20261018-v1.3/资产图册.html',scene_context='新中式、写实治愈的卧室，故事时间为周末清晨。人物、服装及配色沿用当前母版；身份、空间、结构与状态参考按用途继承。'+architecture)
notes={
'000':('先留一拍熟睡的安静，末尾才响铃。','床在画面左侧；主窗和右通廊遮光均关闭。'),
'001':('圆钟伸出胖软手臂，停在准备位置，还不接触她。','钟底落在床头柜；低亮床灯在近旁。'),
'002':('知夏抱着汤圆熟睡，呼吸与被褥微动。','知夏、汤圆、已伸臂闹钟同侧关系明确。'),
'003':('轻碰额角后仍不愿醒，抱紧翻身，把汤圆举到脸前；汤圆半睁眼偷看。','钟拳从床柜侧进入，汤圆随后挡在女孩与钟之间。'),
'004':('第二拳落在汤圆身上；她嫌烦，汤圆含混抗议。','保持原侧机位与接触位置，汤圆无嘴，不加口型。'),
'005':('她放低汤圆，抢在第三拳落下前按钟。','一手按钟，另一手扶汤圆；床品承重，不悬空。'),
'006':('松开按键后坐起，又困倦地垂下肩膀；镜尾才检测坐起。','汤圆移到原枕旁，双手回被面；帘仍闭。'),
'007':('原枕抬高托背，被面局部显像并催醒。','高枕接住身体，被子显像区属于整被；汤圆在枕边。'),
'007-L':('她还困着，房间开始热心服务；亮灯与开帘依次展开。','固定全景看清主窗与通廊；衣柜、杯盘、椅子尚未送物。'),
'008-PRE':('空拖鞋小步走向床沿，显出主动照料的趣味。','镜头贴地跟在后侧，抵床沿微抬；女孩仍在床上。'),
'008':('拖鞋到床边后继续短距离踱步催促。','鞋与地面持续接触，保持沿床边的路线。'),
'009':('柜门让开后，刚性直连衣架整体旋出，减速停稳，衣摆轻晃。','柜体转轴、旋臂与肩架连续连接；镜中云上花园独立于窗外庭院。'),
'010':('杯盘送近，她转开脸不接，托盘停在手边等候。','杯底始终贴荷叶盘，知夏仍靠高枕。'),
'010-W':('窗面变化前沿向前铺开，相机追上后与其同行。','左后方已是水巷，右前方仍是庭院；窗台向后掠过，玻璃不形变。'),
'011':('家具都想帮忙，各自小动作叠成忙乱；她转眼看日历。','与喊停全景匹配；衣服已出、杯盘已到、窗已是水巷，不重复启动。'),
'012':('停留足够时间看清周末与闹钟开启的反差，她没有触屏。','书桌薄屏特写；界面背景不作为真实窗景依据。'),
'013':('抬一只手喊停，第一声停就制止催促，随后缓口气。','另一手留被面，枕头仍托背，杯盘与家具保持停点。'),
'014':('她意识到周末忘关闹钟；床轻声问，要不要再铺回去。','与忙碌全景匹配；灯、开帘、水巷保持，家具不归位。'),
'015':('困倦点头后躺回，伸手找汤圆；尚未触到它。','原枕随身体降低，被子让开手臂，窗帘和通廊卷帘开始闭合。'),
'016':('汤圆自己靠回，她抱住它，被子绕过手臂盖肩。','枕面完成靠回，双层帘与通廊卷帘闭合；只有床灯仍亮。'),
'016-L':('床灯最后缓灭，留一拍相拥呼吸。','衣柜仍伸出、杯盘承杯、鞋错位；不能恢复开场的整齐状态。')}
for s in atlas['shots']:
    phase=s['entry_state'].split(' 本镜推进所遵循的光线阶段（起始依前句，非已完成状态）：')
    s['entry_state']=phase[0]
    light=phase[1] if len(phase)>1 else '按起止状态保持光线。'
    s['invariants']=[x for x in s['invariants'] if x != architecture and x != light and not x.startswith('全屋管家为无形协调层：')]
    if not s['invariants']: s['invariants']=['人物、空间和道具延续共同母版；只改变本镜明确描述的状态。']
    performance,space=notes[s['id'].removeprefix('E01-A-')]
    checks=['起止承接、人物朝向与手的任务连续','动作时长与对白停顿需实测']
    if s.get('state_frames'): checks.append('状态帧之间的路径、接触与相机运动成立')
    if s['light_phase'] in ['L0','L2','L5','L6','L7']: checks.append('主窗与通廊入光有关闭依据，床灯最后熄灭')
    s['direction']=dict(performance=performance,space=space,lighting=light,checks=checks)
for s in atlas['shots']:
    if s['id']=='E01-A-000': s['purpose']='先建立安静暗室，为全屋启动和结尾再睡形成呼应。'
    if s['id']=='E01-A-007-L': s['purpose']='让观众看懂，坐起触发了管家统一协调的灯光与开帘服务。'
    if s['id']=='E01-A-012': s['purpose']='让周末与仍开启的闹钟同框，解释这场忙碌源于忘关闹钟。'
    if s['id']=='E01-A-016-L': s['purpose']='最后一盏床灯熄灭，把过度热心的忙碌落回陪伴。'
plan={k:v for k,v in old.items() if k!='units'}
plan.update(schema_version=2,atlas_source=HERE.relative_to(ROOT).as_posix()+'/atlas.json')
keys=['id','title','shot_ids','method','head_handle','tail_handle','why','reference_strategy','safe_cut','fallback']
plan['units']=[dict(**{k:u[k] for k in keys},runs=[]) for u in old['units']]
create('atlas.json',atlas);create('plan.json',plan)
print('Created canonical atlas and batch plan; old versions unchanged.')
