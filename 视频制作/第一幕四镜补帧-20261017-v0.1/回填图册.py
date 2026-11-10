"""本次四镜补帧的文档回填；图片只读取，画布仅通过MCP另行同步。"""
import json, re, hashlib, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = Path(__file__).resolve().parent
OLD_ATLAS = ROOT / '视频制作/第一幕关键帧图册-20261017-v1.0/atlas.json'
NEW_ATLAS = ROOT / '视频制作/第一幕关键帧图册-20261017-v1.1/atlas.json'
OLD_SCRIPT = ROOT / '第一季/分镜/第一集-A-今天没有安排-智能镜与动态被子-v0.8.md'
NEW_SCRIPT = ROOT / '第一季/分镜/第一集-A-今天没有安排-智能镜与动态被子-v0.9.md'

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

manifest = json.loads((PACK/'manifest.json').read_text(encoding='utf-8-sig'))
descriptions = json.loads((PACK/'画面核对.json').read_text(encoding='utf-8-sig'))
atlas = json.loads(OLD_ATLAS.read_text(encoding='utf-8-sig'))
atlas['subtitle'] = '四处完整画面已补为待审候选；沿用16镜、90秒预算与既有母版。实际画面、动态计划及尚存连续性限制分别列明。'
atlas['source_manifest'] = (PACK/'manifest.json').relative_to(ROOT).as_posix()
atlas['story_script'] = NEW_SCRIPT.relative_to(ROOT).as_posix()
for frame in manifest['frames']:
    path = ROOT/frame['path']
    binary = path.read_bytes()
    frame['sha256'] = hashlib.sha256(binary).hexdigest()
    frame['width'], frame['height'] = struct.unpack('>II', binary[16:24])
    assert abs(frame['width']/frame['height']-16/9) < .003
    frame.update(descriptions[frame['id']])
    shot = next(s for s in atlas['shots'] if s['id'] == frame['id'])
    shot['presentation'] = {'path':frame['path'], 'role':frame['role'], 'visible':frame['visible'], 'missing':frame['missing'], 'show_as_main':True, 'status':'完整镜头候选，待作者审阅'}
    shot['refs'].insert(0, {'path':frame['path'], 'role':'本轮完整镜头指定状态候选；不可直接当作尚未发生动作的首帧'})
    shot['priority'] = 'trial' if shot.get('trial_recommended') else 'normal'
    if frame['id'] == 'E01-A-010':
        shot['invariants'] = [x.replace('完整人物与杯盘同框待补', '人物与杯盘保持同框，杯柄转向仍待动态调整') for x in shot['invariants']]
    if frame['id'] == 'E01-A-014':
        for ref in shot['refs']:
            ref['role'] = ref['role'].replace('本镜若要求镜面退出预览，须另外制作该状态', '此辅助图仍是预览态，退出后的普通镜面以本轮主图为准')
    if frame['id'] == 'E01-A-011':
        shot['invariants'].append('喊停前被角显像仍在；本机位镜面未展示，不能据此判定镜内预览已退出')
        shot['action'] = shot['action'].replace('中央全息园窗局部展开一幅小水巷实时景象，保留外围园景，像窗中多开了一扇借景窗。', '中央整扇园窗的所有可见玻璃区域统一切换为连贯的水巷景象；实体木框、窗棂与窗台不变。近处岸边植物、中景水面与建筑、远处拱桥形成自然纵深，透视和晨光与房间衔接，不出现画中画、发光边框或残留园景围边。')
        shot['exit_state'] = '整扇窗已呈现真实纵深的连续水巷景象，她的视线落到窗右书桌日历。'
        shot['invariants'].append('整个窗口连续换景，窗棂自然遮挡远景；无悬浮屏幕、发光描边或局部贴图')
    if frame['id'] == 'E01-A-015':
        shot['invariants'].append('伸手尚未接触汤圆，肩臂未被盖住；此帧不是已相拥结尾')
write(PACK/'manifest.json', json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
write(NEW_ATLAS, json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')

script = OLD_SCRIPT.read_text(encoding='utf-8-sig')
script = script.replace('智能镜与动态被子 v0.8','智能镜与动态被子 v0.9',1)
script = script.replace('2026-10-17。继承v0.7镜头编号与16镜/90秒预算。按最新作者决定加入智能镜试衣、床被分工与被子材质变化。2张新候选，尚无视频。','2026-10-17。继承v0.8的16镜编号、动作与90秒预算。本轮补A010、A011、A014、A015四张完整画面候选，并修复A011被角表情连续性；全部待作者审阅，尚无视频。')
script = script.replace('第一幕关键帧图册-20261017-v1.0','第一幕关键帧图册-20261017-v1.1')
script = script.replace('该候选只替换A009镜内背景，其余缺帧与动态限制不变。','A009沿用此候选；本轮另外补齐四处完整画面，动态限制仍按逐镜说明。')
script = script.replace('四镜仍缺完整画面（A010/A011/A014/A015）；其他静帧的局部连续性限制按各镜明示。','四镜完整画面已补为候选（A010/A011/A014/A015）；其他静帧的局部连续性限制按各镜明示，不能理解为所有镜头已经连续性验收。')
for frame in manifest['frames']:
    pattern = r'(### '+re.escape(frame['id'])+r'｜.*?)(?=\n### |\Z)'
    match = re.search(pattern, script, re.S)
    section = match.group(1)
    section = re.sub(r'\*\*当前画面：.*?(?=\n\n\*\*尚未体现)', '**当前画面：完整镜头候选，待作者审阅。** '+frame['visible'], section, count=1, flags=re.S)
    section = re.sub(r'\*\*尚未体现：\*\*.*?(?=\n\n\*\*视频计划)', '**尚未体现：** '+frame['missing'], section, count=1, flags=re.S)
    image_ref = f"[{Path(frame['path']).name}](../../{frame['path']})（本轮完整指定状态候选；不是动作首帧）；"
    section = section.replace('**参考：**','**参考：**'+image_ref,1)
    if frame['id']=='E01-A-010':
        section=section.replace('新图只参考杯形、釉色及读数。正式镜头须有知夏回避反应同框，','本轮新图已含回避反应同框，用作关键动作状态。道具辅助图只参考杯形、釉色及读数，')
    if frame['id']=='E01-A-011':
        section=section.replace('中央全息园窗局部展开一幅小水巷实时景象，保留外围园景，像窗中多开了一扇借景窗。','中央整扇园窗的所有可见玻璃区域统一切换为连贯的水巷景象；实体木框、窗棂与窗台不变。近处岸边植物、中景水面与建筑、远处拱桥形成自然纵深，透视和晨光与房间衔接，不出现画中画、发光边框或残留园景围边。')
        section=section.replace('水巷画面属于窗内局部仿真，实体窗框和原房间不动；没有穿越到室外或换场。','水巷景象填满整个窗口，所有窗棂后的视景连续，像真实窗外空间；实体窗框和原房间不动，没有穿越到室外或切换房间。')
    if frame['id']=='E01-A-014':
        section=section.replace('旧全景只提供布局，正式画面需继承本轮枕头和柜口衣架状态。','本轮全景已补高靠枕、玉件、柜口服装与普通镜面，旧全景降为布局辅助。')
        section=section.replace('本镜若要求镜面退出预览，须另外制作该状态','此辅助图仍是预览态，退出后的普通镜面以本轮主图为准')
    script = script[:match.start()]+section+script[match.end():]
write(NEW_SCRIPT, script)

for name in ['制作进度.md','创作速查卡.md','第一季/分镜/第一幕-当前制作总览.md']:
    p=ROOT/name
    text=p.read_text(encoding='utf-8-sig')
    text=text.replace('第一幕关键帧图册-20261017-v1.0','第一幕关键帧图册-20261017-v1.1').replace('智能镜与动态被子-v0.8.md','智能镜与动态被子-v0.9.md').replace('晨起v0.8','晨起v0.9').replace('完整动作稿v0.8','完整动作稿v0.9').replace('[v0.8]','[v0.9]')
    text=text.replace('**关键帧图册已精修（2026-10-17）：** 母版、16镜总览、帧用途、起止状态和相邻镜衔接已整理；配色与原图保持。','**关键帧图册v1.1（2026-10-17）：** 四处完整画面已补为待审候选，母版、16镜总览、起止状态与邻镜衔接同步更新；旧图保留。')
    text=text.replace('仍有候选、四镜完整画面缺口和动态待验证项。','四镜完整画面已补为候选，仍有局部连续性限制和动态待验证项。')
    text=text.replace('A010、A011、A014、A015缺完整画面；其他镜的局部连续性限制保留在逐镜说明中。','A010、A011、A014、A015已补完整画面候选；其他镜的局部连续性限制保留在逐镜说明中。')
    text=text.replace('本轮只整理文档与画布，不再生图。','本轮补四镜静帧并同步图册与画布，未制作视频。')
    text=text.replace('四镜缺完整画面，全部正式动态待制作；','四镜完整画面已补为待审候选，全部正式动态待制作；')
    text=text.replace('A010送水、A011窗内水巷与人物反应、A014喊停后全景、A015躺回伸手，这四镜缺完整画面。现有静帧的玉璧、枕头高度等连续性问题按v0.8逐镜说明处理。','A010送水、A011窗内水巷与人物反应、A014喊停后全景、A015躺回伸手，这四镜已补完整候选。A011补回了喊停前仍应存在的被角显像。其他旧静帧的玉璧、枕头高度等连续性问题按v0.9逐镜说明处理。')
    text=text.replace('缺完整画面的镜头用文字卡占位。','四处原缺帧位置已放入新图，原文字卡保留为右侧镜头说明。')
    for frame in manifest['frames']:
        sid=frame['id']; title=next(s['title'] for s in atlas['shots'] if s['id']==sid)
        text=re.sub(r'^\| '+re.escape(sid)+r' \|.*$',f"| {sid} | {title} | 完整指定状态候选，待审 | {frame['missing']} |",text,flags=re.M)
    write(p,text)

readme=['# 晨起四镜补帧','', '2026-10-17。四处缺口已补成完整静帧候选，尚待作者审阅；不代表动态成立。旧图与历史图册保留。', '', '[新版关键帧图册](../第一幕关键帧图册-20261017-v1.1/关键帧图册.html) · [动作稿v0.9](../../第一季/分镜/第一集-A-今天没有安排-智能镜与动态被子-v0.9.md)', '']
for f in manifest['frames']:
    readme += ['## '+f['id'], '', '!['+f['id']+']('+Path(f['path']).name+')','',f['visible'],'','限制：'+f['missing'],'']
readme += ['提示词、实际参考、源文件、尺寸与SHA256见 manifest.json。A011初版漏掉被角显像；补回后，作者指出局部方框像贴图，现按整窗真实纵深换景修订。两版局部视景保留为历史。PNG按项目既有规则留本地，Git记录文档与来源，迁移时须连同媒体复制。','']
write(PACK/'README.md','\n'.join(readme))
print(json.dumps({'updated_shots':[f['id'] for f in manifest['frames']],'atlas':str(NEW_ATLAS),'script':str(NEW_SCRIPT)},ensure_ascii=False))
