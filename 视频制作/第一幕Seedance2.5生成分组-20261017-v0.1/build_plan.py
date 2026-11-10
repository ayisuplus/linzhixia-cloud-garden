"""Build this scene's generation handoff; no media or remote jobs are created."""
import importlib.util
import json
import os
from html import escape as e
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / '视频制作/第一幕关键帧图册-20261017-v1.5/atlas.json'
NEW = ROOT / '视频制作/第一幕关键帧图册-20261017-v1.6'
SOURCE = 'https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5'
atlas = json.loads(OLD.read_text(encoding='utf-8-sig'))
shots = {s['id']: s for s in atlas['shots']}

def unit(uid, title, nums, seconds, why, staging, cut, locks, refs, fallback):
    return dict(id=uid,title=title,shot_ids=['E01-A-'+n for n in nums.split()],requested_seconds=seconds,
                method='edit_existing_image' if uid=='I01' else 'seedance2.5',why=why,staging=staging,
                safe_cut=cut,continuity=locks,reference_strategy=refs,fallback=fallback)

units = [
 unit('G01','三拳叫醒','001 002 003 004 005',30,
 '闹钟、知夏、汤圆在同一床侧完成一条因果链，优先放在同一次生成。29秒成片只留1秒余量，是高风险长段试做方案。',
 '钟的近景切床侧中近景，再以同侧机位看清第一拳、翻身举汤圆、第二拳和第三拳蓄势。允许明确切镜，不要求29秒一镜到底。第三拳未击中就被知夏按住。',
 '段末知夏手掌已按住钟顶，汤圆落在床被上仍受另一只手扶住；钟臂仍在外。下一段才回收钟臂与坐起。不要截在拳头接触、软壳压缩、翻身或汤圆悬空交接中。',
 '钟不离开床头柜；第二拳打软壳不打屏幕；汤圆无嘴，眼神从困到委屈；知夏奶油色折面蝴蝶结、青绿发带、睡衣不变。',
 '身份发夹母版+床侧空间；A003/A004为接触状态，A005为终态。A001图已伸手，只作钟的结构参考，不能直接当作尚未伸手的首帧。',
 '若三次拳序或对白串台，在A003末拆成16秒和13秒成片（申请18/15秒）。剪点必须是翻身完成、汤圆已稳稳挡脸、拳已收回；用前段实际合格末帧衔接，不在接触中硬剪。'),
 unit('G02','坐起与床被响应','006 007',13,
 '同一人物由按钟过渡到坐起，床和被子响应，适合合并。接G01后总长40秒，不能维持现有时长直接合为一批。',
 '承接按钟姿态，钟臂回收后知夏松开钟顶，借床面坐起；知夏松开对汤圆的扶持，它始终接触床品，自行挪到原枕旁；她确认它落稳后双手落被上，后续升枕不得挤压汤圆。原枕头升起托背，床说“坐稳啦”；被角抬起转为平滑显像态并催醒。',
 '待知夏坐稳、枕头承托成立、被角显像后再切到地面。不能在身体失去承托或被角半变形时接独立段。',
 '托背枕到喊停后仍保持高度，直到知夏点头躺回才降低。玉璧保留；被子和床分工；汤圆停在枕旁。',
 '优先前段合格末帧+A006坐姿和A007托背显像图；旧图缺少玉璧的地方按床母版补足，不能整张当起始状态。',
 '若床与被子同时变形失控，按A006坐稳时切成5+6秒；无需先补两套重复图。'),
 unit('G03','贴地跟随到床边踱步','008-PRE 008',7,
 '两镜是同一路线同一对拖鞋，合成一个连续低机位运动。与人脸、衣柜分开可减少微观视角跳回正常尺度的风险。',
 '镜头贴地从两只空拖鞋后侧跟行，抵达床沿外侧后轻转向，跟着它们沿床边走、折返。PRE的2秒与A008的3秒是节拍，不强加切镜。',
 '结束时仍在踱步，趁迈步切出；可切画面但不能安排停步等穿鞋。后面的画外脚步继续，直到A013第一声“停”。',
 '拖鞋不长脚、不加脸、没有人穿；花纹与数量固定；床边路线避开床腿。沿床边而非钻进床底后消失。',
 'PRE作为途中构图参考，A008作为床边迈步/转弯参考；不是静止到位的首尾帧。',
 '若跟拍转向困难，可在床腿短暂遮挡画面时切镜，仍保留完整行走路线与连续脚步声。'),
 unit('G04','旋杆递衣与镜中试穿','009',7,
 '旋转挂衣杆和镜内虚拟人是一个独立技术展示，建议单独生成，便于重试而不重做整屋。此处是风险选择，不是模型禁止与别镜同批。',
 '衣柜近景，门让开，竖向转轴带横杆转出，选定衣服始终挂在杆上。侧壁笑脸/搭配就绪响应；镜内显现保存的试穿预览与云上花园。',
 '衣服递出后仍挂在杆上，镜内预览已稳定，再切床侧送水。不要在衣架穿杆或转轴遮挡关系不明时截断。',
 '镜中人仅是预览，不能走出镜子；真实知夏在床上穿睡衣。粉色上衣与青绿裙不换色；衣架钩有支点；柜门与杆避让。',
 'A009主约束柜内机构，镜子参考约束华丽虚拟背景。标“昨晚预设/试穿预览”，小字必要时后期叠加，不能以错误文字冒充完成。',
 '若机构与虚拟换景互相干扰，先完成旋杆送衣，镜内背景在后期固定合成；不靠衣服凭空漂浮避开机构问题。'),
 unit('G05','送水回避到全屋闹腾','010 011',13,
 '先表现知夏拒绝水，再切全景叠加家居声音；人物坐姿和杯盘位置有直接衔接，适合同批。',
 '床侧中近景：荷叶托盘托着杯子靠近，杯柄转向知夏，她转脸不接。托盘在可接取处停住。明确切全屋广角：衣杆保持G04已转出的角度、挂衣轻摆，椅子拉开、被角说话、拖鞋仍踱步，结尾知夏看日历；不能再次完整转杆递衣。',
 '以知夏看向日历切至I01，随后从日历切回喊停。两处切镜不要求复现完全相同的嘴型，但人物始终坐着，忙碌状态不能提前解除。',
 '杯底贴托盘，杯盘在两机位中是同一停点；A010图杯柄未转好须在视频完成。A011全窗水巷；镜面离画；最多三种家具声音争先，脚步另外保留。',
 'A010作回避动作参考，A011锁定全屋状态和下一段喊停前布局；A009补旋杆结构。被角显像要统一，不能自动从光滑面跳回普通织纹脸。',
 '若从近景切全景导致杯盘瞬移，拆5+6秒；取前段实际末帧记录停点，再按相同坐姿/道具位置制作全景。'),
 unit('I01','日历插镜：今日无事，宜休沐','012',None,
 '优先用现有界面图剪辑4秒，以保住阅读与字形；不是因为模型绝对不能写字。它也是忙碌全景与喊停之间的天然转场。',
 '轻微推近或保持镜头，让“今日无事／宜休沐”可读，保留“早起出门：已开启”。按动作稿补底座灯条轻闪与控制条短亮，使用后期局部光效层，文字与开启状态保持固定；纯静帧推近本身不算完成这些响应。',
 '从知夏视线切入，读完再切回她开口。此时没有触屏，也不切换晨起开关。',
 '画面只占4秒；脚步和家具催促声继续在画外，不因插镜安静下来。服务直到下一段首声“停”才停止。',
 '仅用当前A012智能日历图；小幅推近避免裁掉“已开启”与主文案。',
 '若坚持全AI，可另做6秒日历镜头取4秒，并用原界面做跟踪覆盖保字；文字验证单独验收。'),
 unit('G06','喊停、发愣、重新相拥','013 014 015 016',27,
 '四镜构成一条情绪和身体动作链，合为25秒成片更容易保留“吵闹骤停到安静”的节奏，但多人/多物互动仍需试验。',
 '头部1秒余量仍是忙碌状态，不提前刹停。进入保留内容后知夏举手喊停；第一声“停”响起的同一时点，鞋、旋杆、椅子及被缘停止动作，脚步与重复催促声停止，完整命令后提示逐渐熄下。明确切匹配全景，房间停在半途，床问“那……我再给你铺回去？”；她点头主动躺回、枕头降低，被子退让；汤圆自己靠来，她抱住，被子盖肩，最后留1–2秒安静。',
 '段末相拥已稳、脸露出、被子表情淡回，保持自然呼吸。备用拆点在床问完且知夏尚未点头时；不要截在倒下、枕头降低、汤圆移交或被子越过手臂中。',
 '喊停不是一键收拾房间：椅子仍拉出、衣杆衣服在外、鞋错位停住。杯盘不坠落，枕头不提前塌。A014全窗回园景。汤圆无嘴，情绪变化；所有旧图缺失的玉璧沿用母版。',
 'A011锁定忙碌输入，A014锁定停在半途；A013只取表演，不复制旧靠枕和道具布局。A015只取伸手尚未接触，A016只取相拥终态。',
 '若四镜动作遗漏，按A014结束拆13+12秒成片（申请15/14秒）。前段床问完，后段从点头起；沿用前段合格末帧与房间状态表。')
]

cursor=0
for u in units:
    u['timeline_start']=cursor
    u['edit_seconds']=sum(shots[s]['seconds'] for s in u['shot_ids'])
    cursor+=u['edit_seconds']; u['timeline_end']=cursor
    u['head_handle']=0.5 if u['id']=='G01' else (1 if u['requested_seconds'] else 0)
    u['tail_handle']=u['head_handle']
    t=u['head_handle']; u['beats']=[]
    for sid in u['shot_ids']:
        s=shots[sid]
        u['beats'].append(dict(shot_id=sid,start=t,end=t+s['seconds'],title=s['title'],image=s['presentation']['path'],image_role=s['presentation']['role']))
        t+=s['seconds']
    if u['requested_seconds']:
        assert t+u['tail_handle']==u['requested_seconds']<=30
assert [s for u in units for s in u['shot_ids']]==list(shots)
assert cursor==sum(s['seconds'] for s in shots.values())==90

plan=dict(schema_version=1,status='production_proposal_not_dynamically_tested',model='Seedance 2.5',max_seconds=30,
          aspect_ratio='16:9',atlas_source=OLD.relative_to(ROOT).as_posix(),story_script=atlas['story_script'],
          official_source=SOURCE,verified_on='2026-10-17',video_generated=False,units=units)
(HERE/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def stamp(s): return f'{int(s)//60:02}:{int(s)%60:02}'
intro='采用6次AI生成＋1个日历剪辑插镜，保留17个镜头ID与90秒成片预算。同一生成批次可以包含明确切镜，不等于一镜到底。时长和切点是制作提案，未生成视频、未测对白时长，也未证明长段一定更稳定。'
rules=[
 '官方确认Seedance 2.5单次最长30秒并支持多镜头叙事；复杂物理运动与多主体互动仍有改进空间。下述哪些段合并/拆开是本项目判断，不是官方限制。',
 '硬限制：按现有预算A001—A007共40秒、A006—A011共32秒，均不能原速完整塞入单次30秒。不要机械切成0—30/30—60/60—90：30秒落在坐起衔接，60秒落在看日历前的忙碌表演。',
 '建议分开：贴地拖鞋、旋杆镜中试穿、文字日历。原因分别是尺度与运动轴、真实人和虚拟人边界、字形可控性。技术上可尝试同批切镜；分开能降低一次失败重做整段的成本。',
 '段内时间码含头余量：G01前后各0.5秒，其余AI段前后各1秒；余量只延续当前状态，不重复台词、出拳或转杆。成片取中间预算部分。97秒AI原片＋4秒剪辑插镜＝101秒素材预算，去11秒余量得90秒；并非把余量加进剧情。',
 '申请时长是目标，实际入口的可选时长/引用方式需提交前确认。若只能选固定档，选择足够覆盖内容且不超过30秒的档位并重算余量，绝不拉长空镜凑满30秒。',
 '时间码约束节奏而非模型逐帧保证。先测对白，再检查生成结果：若对白/动作超出预算，明确修订剪辑预算或启用拆段方案，不用加速吞词或截掉接触动作。',
 '参考图按身份、空间、动作、终态分工，缩略序列不是逐张首帧。先选最必要的参考，不把17张整包塞进每一批。当前钟未伸手、翻身挡脸等起始/过渡状态尚未有完整对应静帧；先明确输入模式，只有出现实际歧义再补关键帧。',
 '先试高风险G01，再试G06；通过后制作G02/G03/G04/G05和日历插镜。叙事顺序始终按下表。分批制作时复用合格片尾与状态记录，不以旧图的不一致覆盖新动态。',
 '统一知夏、汤圆、床与被子声线；各段禁止自行加互相冲突的配乐。跨段环境声和拖鞋节拍在剪辑中连续铺设：A008-PRE开始脚步，A009—A012继续画外踱步，A013第一声“停”骤止。床后续问话发生在安静后。',
 'A011与A014尽量锁同一广角机位。跨段继承杯盘停点、衣架挂杆、椅子位置、枕头高度、玉璧、发夹与睡衣；停止后保留承托和未收拾姿态。图册现有局部缺口仍有效，本次分组不等于修好了图片或完成动态验收。'
]
md=['# 第一幕 · Seedance 2.5生成分组 v0.1','',intro,'',f'规格核对：[Seed官方介绍（2026-07-31）]({SOURCE})；核对日期2026-10-17。','',
    '| 单元 | 镜头 | 成片区间 | 成片/申请 | 组织方式 |','|---|---|---|---|---|']
for u in units:
    md.append(f"| {u['id']} {u['title']} | {'、'.join(s.replace('E01-','') for s in u['shot_ids'])} | {stamp(u['timeline_start'])}—{stamp(u['timeline_end'])} | {u['edit_seconds']}秒 / {str(u['requested_seconds'])+'秒' if u['requested_seconds'] else '剪辑4秒'} | {'独立插镜' if u['id']=='I01' else '同批生成'} |")
md+=['','## 共同执行口径','']+[f'- {r}' for r in rules]
for u in units:
    md+=['',f"## {u['id']} · {u['title']}",'',u['why'],'',f"段内参考节拍（生成素材本地时间，已含头余量）：" ]
    md += [f"- {b['start']:g}—{b['end']:g}秒：{b['shot_id']} {b['title']}" for b in u['beats']]
    for key,label in [('staging','调度'),('safe_cut','剪点与交接'),('continuity','状态锁定'),('reference_strategy','参考用途'),('fallback','失败后的拆法')]:
        md+=['',f'**{label}：** {u[key]}']
md+=['','## 验证范围','', '结构校验：17镜按序且仅出现一次、90秒故事预算、6段生成时长均不超过30秒、11秒余量独立核算、图片文件与链接存在。静态角色/道具缺口保留；所有合并可行性、实际时长、画面稳定性及声线一致性尚待真实试片。','']
(HERE/'生成分组.md').write_text('\n'.join(md),encoding='utf-8')

def url(path): return quote(os.path.relpath(ROOT/path,HERE).replace('\\','/'),safe='/.-_')
atlaspath=NEW.relative_to(ROOT).as_posix()+'/关键帧图册.html'
style='body{margin:0;background:#f5f1e8;color:#293f38;font:16px/1.7 system-ui,"Microsoft YaHei"}main{max-width:1240px;margin:auto;padding:35px 28px}h1{font-size:40px;line-height:1.25}h2{font-size:27px}a{color:#2b6457}nav{position:sticky;top:0;background:#f5f1efef;padding:12px;z-index:3;display:flex;gap:22px;flex-wrap:wrap}.card{background:#fffdf8;border:1px solid #d9d8cb;border-radius:14px;padding:26px;margin:30px 0;scroll-margin-top:80px}.meta{color:#9d6547;font-weight:700}.strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:13px}.thumb{color:inherit;text-decoration:none;font-size:13px}.thumb img{display:block;width:100%;aspect-ratio:16/9;object-fit:contain;background:#e8e6dc}.facts{display:grid;grid-template-columns:1fr 1fr;gap:0 26px}.notice{padding:20px;border-left:4px solid #9d6547;background:#eee9dc}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #d9d8cb;text-align:left}small{color:#69746d}details{margin:18px 0}summary{cursor:pointer;font-weight:bold}@media(max-width:750px){.facts{display:block}h1{font-size:30px}.tablewrap{overflow:auto}main{padding:20px 15px}}'
html=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',f'<title>第一幕 · Seedance 2.5生成分组</title><style>{style}</style><body><main>', '<small>LIN ZHIXIA · GENERATION PLAN · 16:9</small><h1>把连续表演放在一起<br>把难控制的展示单独做</h1>',f'<p>{e(intro)}</p><p><a href="{url(atlaspath)}">返回关键帧图册v1.6</a> · <a href="生成分组.md">完整交接文档</a> · <a href="plan.json">结构化计划</a></p>', '<nav>'+''.join(f'<a href="#{u["id"]}">{u["id"]} · {u["edit_seconds"]}秒</a>' for u in units)+'</nav>', '<div class="notice">最适合尝试的长段：三拳叫醒29秒、喊停到相拥25秒。日历保留4秒剪辑插镜。所有动态均未验证，已有图片不自动等于该段首帧。</div>', '<div class="tablewrap"><table><tr><th>单元</th><th>故事区间</th><th>成片</th><th>申请生成</th></tr>']
for u in units:
    html.append(f'<tr><td><a href="#{u["id"]}">{u["id"]} {e(u["title"])}</a></td><td>{stamp(u["timeline_start"])}—{stamp(u["timeline_end"])}</td><td>{u["edit_seconds"]}秒</td><td>{str(u["requested_seconds"])+"秒" if u["requested_seconds"] else "不调用模型"}</td></tr>')
html+=['</table></div><details><summary>分组原则、声音连续性与时长口径</summary><ul>'+''.join('<li>'+e(r)+'</li>' for r in rules)+f'</ul><p><a href="{SOURCE}">Seed官方规格来源</a> · 2026-10-17核对</p></details>']
for u in units:
    html += [f'<article class="card" id="{u["id"]}"><div class="meta">{u["id"]} · 成片{u["edit_seconds"]}秒 · {stamp(u["timeline_start"])}—{stamp(u["timeline_end"])}</div><h2>{e(u["title"])}</h2><p>{e(u["why"])}</p><div class="strip">']
    for b in u['beats']:
        html.append(f'<a class="thumb" href="{url(atlaspath)}#{b["shot_id"]}"><img loading="lazy" src="{url(b["image"])}" alt="{e(b["title"])}"><strong>{b["shot_id"]} · {b["start"]:g}—{b["end"]:g}s</strong><br>{e(b["title"])}</a>')
    html+=['</div><small>上方为本批素材内时间（含头余量）；缩略图是现有状态参考，并非逐镜首帧。</small><div class="facts">']
    for key,label in [('staging','段内调度'),('safe_cut','安全剪点'),('continuity','连续状态'),('reference_strategy','参考图分工')]:
        html.append(f'<div><h3>{label}</h3><p>{e(u[key])}</p></div>')
    html += [f'</div><div class="notice"><b>失败后怎么拆：</b>{e(u["fallback"])}</div></article>']
html+=['<p>未调用视频模型；时长、节奏及镜头衔接均待真实试片。原图、镜头编号与动作稿v0.13保留。</p></main></body></html>']
(HERE/'生成分组.html').write_text(''.join(html),encoding='utf-8')
NEW.mkdir(exist_ok=True)
atlas['subtitle']='v1.6增加Seedance 2.5生成分组入口：6次AI生成＋1个日历插镜；17镜90秒故事预算及v1.5图片不变。动态未验证。'
atlas['production_guide']=dict(path=(HERE/'生成分组.html').relative_to(ROOT).as_posix(),label='04 Seedance 2.5生成分组',summary=intro)
(NEW/'atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('atlas_builder',ROOT/'.agents/skills/linzhixia-keyframe-atlas/scripts/build_atlas.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
stats=module.validate(atlas,ROOT)
(NEW/'关键帧图册.html').write_text(module.render(atlas,ROOT,NEW/'关键帧图册.html',stats),encoding='utf-8')
result=dict(valid=True,shots=len(shots),units=len(units),ai_generations=6,edit_seconds=cursor,ai_raw_seconds=sum(u['requested_seconds'] or 0 for u in units),handles_seconds=11,video_generated=False)
(HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
