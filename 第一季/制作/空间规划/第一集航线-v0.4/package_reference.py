"""Versioned reference-readability review. Images are actual Blender renders."""
from pathlib import Path
import argparse,json,hashlib,html
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();out=root/'视频制作/第一集浮空园城-20261022-v0.4';old=root/'视频制作/第一集浮空园城-20261022-v0.3'
d=json.loads((out/'route-layout.json').read_text(encoding='utf8'));c=json.loads((out/'route-checks.json').read_text(encoding='utf8'))
assert all(v['pass'] for v in c['routes'].values()) and all(v['pass'] for v in c['docks']) and c['source_unchanged']
assert not c['preserved_scene_objects']['unexpected_changes'] and not c['camera_transform_changes'] and c['v03_route_and_camera_data_unchanged']
assert all(v['screen_transition_pass'] for v in c['reveals'])
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
comparisons=[('B1','云岸、树冠与水榭','云岸的硬边被软边包裹；树冠有叶丛和轮廓，灰瓦、木梁、栏杆与远处住宅门窗可辨。'),('WATER','瀑布与收水池','旧斜面改成溢水口、垂直水帘和落水白沫；水面有细波纹。'),('C1','水巷两岸建筑','补齐山墙、檐口、门窗与水面细波，减轻空盒和纯色面片的误读。')]
cards=[]
for suffix,title,desc in comparisons:
    before=Image.open(old/('V03-'+suffix+'.png'));after=Image.open(out/('V04-'+suffix+'.png'));assert before.size==after.size==(1280,720)
    sheet=Image.new('RGB',(1600,530),'#eee9de');dr=ImageDraw.Draw(sheet);sheet.paste(before.resize((800,450)),(0,0));sheet.paste(after.resize((800,450)),(800,0));dr.text((18,463),'v0.3 · 已认可的空间草模',font=font,fill='#28443d');dr.text((818,463),'v0.4 · 参考用途美术轻修',font=font,fill='#28443d');sheet.save(out/('compare-'+suffix+'.jpg'),quality=94)
    cards.append(f'<section><h2>{title}</h2><p>{desc}</p><img src="compare-{suffix}.jpg"><div class="links"><a href="V04-{suffix}.png">查看新版原尺寸净图</a></div></section>')
seq=Image.new('RGB',(1920,410),'#eee9de');dr=ImageDraw.Draw(seq)
for i,s in enumerate(['B0','BM','B1']):
    im=Image.open(out/('V04-'+s+'.png'));seq.paste(im.resize((640,360)),(i*640,0));dr.text((i*640+15,372),['遮住主景，月窗借见侧景','墙边露出水榭一角','水榭、云岸与廊桥展开'][i],font=small,fill='#28443d')
seq.save(out/'reveal-sequence.jpg',quality=94)
limits='本轮是参考场景的类别与材质提示，不是最终美术，也不是完整视频。云质仍保留简化承托核心；局部草地、远景与支路继续简化。没有提交视频生成模型，不能把人工看懂等同于模型已经正确理解。'
css='body{margin:0;background:#eee9de;color:#28443d;font:17px/1.8 system-ui,"Microsoft YaHei"}main{max-width:1360px;margin:auto;padding:40px}h1{font-size:42px;line-height:1.3}h2{margin-top:44px}img{width:100%;display:block;border-radius:5px}nav,.links{display:flex;gap:22px;flex-wrap:wrap;margin:18px 0}a{color:#915638}.note{background:#dce4d8;border-left:5px solid #71927d;padding:20px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}@media(max-width:700px){main{padding:16px}.grid{display:block}}'
body='<p>未来女孩林知夏 / REFERENCE ART v0.4</p><h1>把空间说明白，把质感留给成片</h1><p>作者已认可v0.3的空间机制。本轮只打磨容易被视频模型误读的形状与材质：树、云、水、墙、瓦、木，仍是同一套相机和航线。</p><nav><a href="episode1-floating-garden-v04.blend">新版Blender工程</a><a href="README.md">参考职责与制作说明</a><a href="route-checks.json">几何复核</a></nav><img src="V04-B1.png"><p class="note">所有独立PNG都是无文字、无路线标记的Blender净图。下面对照图只用于审阅，不作为视频模型的画面输入。</p>'
body+=''.join(cards)+'<h2>原来的遮挡机制继续成立</h2><img src="reveal-sequence.jpg"><p>同一35mm焦距、同一主地标；旧相机位置和航线数组保持不变。屋顶轮廓细化后重新检查三组屏墙揭示。</p><h2>原半园与浮空关系</h2><div class="grid"><div><img src="V04-HOME.png"><p>原卧室、半园与对岸作坊保持。原房间内部网格未改。</p></div><div><img src="V04-SIDE.png"><p>实体承托与柔软云边分开，保留层与层之间的天空。</p></div></div>'
body+=f'<h2>交给视频模型时的参考职责</h2><p>Blender参考负责空间、尺度、机位、遮挡和后续飞行路径；现有场景美术参考负责最终新中式写实治愈质感，人物与载具采用素材另行约束身份。学院外景保持水墨黑白，半园保留既有白墙、灰瓦、木色与植物色族。</p><p>可进一步细化叶片、云絮、瓦片、水波和墙木纹理；应保留云城悬空、两岸分设、同一地标和转角揭示。剩余简化体块不代表要求成片继承低模游戏风。</p><p class="note">{limits}</p><p>本轮包裹路径{c["routes"]["parcel"]["samples"]}点与步行主线{c["routes"]["regional_walk"]["samples"]}点离散检查通过，原2557个房间/学院网格数量与预期变换保持；未替代连续碰撞或动态镜头验收。七张机位净图只验证本轮外观，未制作新动画。</p>'
(out/'review.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>长洲 · 视频参考美术轻修 v0.4</title><style>'+css+'</style><main>'+body+'</main></html>',encoding='utf8')
readme=f'''# 长洲首集参考场景 · 美术轻修 v0.4

作者已认可v0.3空间机制。本轮目标是降低视频参考中的类别误读，做到可读即可，不扩建成游戏级资产。

[审阅页](review.html) · [Blender工程](episode1-floating-garden-v04.blend)

## 实际变化

- 云：原硬云边外围增加有疏密的柔软体积边缘，保留承托核心与层间空隙。软边指结构云质的外观，普通瀑布水雾另有图层；反重力机制不在本轮设计。
- 树：新增外景球状树冠换成不规则内部叶团＋叶片轮廓，保留树的位置与主枝。学院使用原黑白叶色；庭院沿用原植物色族。
- 建筑：新外景填补{d['appearance_changes']['gables']}处山墙，增门窗与木框，强化瓦屋顶坡度、屋脊和檐木；双层水榭加木栏。原室内及已采用角色、服装不变。
- 水：两处斜水板退出渲染，增加沿实际云岸边缘的溢水口、垂直跌水、接水白沫及水面细波。跌入下池，非地面道路。仍为几何与材质表达，没有流体模拟。
- 木、瓦、石、白墙和水用不同粗糙度与细微法线起伏区分；不重新指定项目主辅配色。

## 参考职责

本工程以及后续由它渲染的参考视频约束：位置、尺度、高差、飞行方向、镜头和遮挡。保留学校到半园的跨区距离、云城悬浮、两岸分设、月窗与转角揭示、同一水榭地标。

最终视频的质感沿现有《半园-云上园居-两岸分设概念01》与《山水书院-宿舍水庭舞院总景01》等对应美术方向；它们是美术依据，不能用来重排已认可的三维布局。现行采用状态仍以项目图册/进度为准，未把历史探索稿自动升为采用。

允许视频模型细化云絮、叶片、瓦片、木纹、水流及光影。剩余简化面不指定低模游戏风；结构云质不解释为岩石浮岛或水泥平台；瀑布不解释为坡道；人物/载具身份不从代理体块推断，须用对应采用资产。

净图是`V04-*.png`，没有路线标记或说明文字。`compare-*.jpg`及`reveal-sequence.jpg`含审阅标签，只供人看，不用于直接图生视频。完整逐镜提交输入与模型参数仍在实际执行时按项目流程冻结；本轮没有上传、云端生成、Meshy调用或视频模型理解测试。

## 复核与边界

原v0.3文件SHA256不变；航线、步行路线、15个相机数据与实际位置/焦距保持。包裹{c['routes']['parcel']['samples']}个离散位置、步行主线{c['routes']['regional_walk']['samples']}个离散位置无本次检测发现的障碍或地面缺口；三组屏墙中心射线仍完成遮挡→越墙。2557个原房间/学院网格数量与预期变换保持。属于离散几何复核，非完整连续碰撞或视频验收。

保留15个原机位，本轮输出7个重点机位的1280×720净图；frame_end=1，未制作新的定时航拍视频。生成脚本保存在`第一季/制作/空间规划/第一集航线-v0.4`，直接在v0.3上叠加可复现外观修改，不重跑旧城市规划。

{limits}

原创成果留项目，旧版保留。Git保存工程、脚本与数据，PNG/JPG按项目规则本地保存，需随项目另行备份。
'''
(out/'README.md').write_text(readme,encoding='utf8')
ad=json.loads((root/'视频制作/资产图册-20261022-v1.7/assets.json').read_text(encoding='utf8'));f='视频制作/第一集浮空园城-20261022-v0.4/'
for item in ad['assets']:
    if item['id']=='SCENE-E01-DELIVERY-CORRIDOR-3D':
        item.update(name='第一集浮空园城｜视频参考美术轻修',version='v0.4',status='v0.3空间机制作者认可；v0.4参考美术轻修待审',path=f+'V04-B1.png',role='保持已认可布局，强化云、树、水与建筑的类别识别，服务后续视频控制参考',limits=limits,source=f+'README.md')
        item['related']=[{'path':f+'review.html','role':'同机位前后对照与参考职责'},{'path':f+'episode1-floating-garden-v04.blend','role':'当前美术轻修工程'},{'path':f+'V04-WATER.png','role':'垂直跌水净图'},{'path':'视频制作/第一集浮空园城-20261022-v0.3/review.html','role':'已获认可的空间机制历史稿'}]
ad['title']='未来女孩林知夏 · 资产图册 v1.8';ad['scope']+=' 作者认可v0.3空间机制；本版新增v0.4参考美术轻修，沿用航线资产ID。'
atlas=root/'视频制作/资产图册-20261022-v1.8';atlas.mkdir(exist_ok=True);(atlas/'assets.json').write_text(json.dumps(ad,ensure_ascii=False,indent=2),encoding='utf8')
manifest={'artifact':'episode1-floating-garden-v04','files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir()) if p.suffix in ['.blend','.json','.html','.png','.jpg','.md'] and p.name!='delivery-manifest.json'],'downstream_video_model_tested':False}
(out/'delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');print('REFERENCE_PACKAGE_OK',len(ad['assets']))
