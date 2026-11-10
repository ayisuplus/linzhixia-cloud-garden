"""Read the saved scene, check a proposed walking corridor, and draw an exact-coordinate plan."""
import bpy, argparse, sys, json, math
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.root).resolve()/'视频制作/知夏卧室三维空间-20261022-v0.1'
bpy.ops.wm.open_mainfile(filepath=str(out/'zhixia-bedroom-v01.blend'))
s=bpy.context.scene;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
route=[(0,-.7),(1.9,-.3),(2.7,.8),(3.8,1.2),(3.6,3.2),(3.6,5.7),(2.4,5.7)]
hits=[];samples=0
for a,b in zip(route,route[1:]):
    length=math.dist(a,b)
    for i in range(math.ceil(length/.10)+1):
        t=i/math.ceil(length/.10);x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1]);samples+=1
        for z in [.2,.9,1.65]:
            for k in range(24):
                v=Vector((math.cos(k*math.tau/24),math.sin(k*math.tau/24),0))
                hit,loc,n,idx,obj,m=s.ray_cast(dg,Vector((x,y,z)),v,distance=.25)
                if hit:hits.append({'xy':[round(x,3),round(y,3)],'z':z,'object':obj.name})
report={'route_xy_m':route,'spacing_m_max':.1,'sample_positions':samples,'radial_probe_m':.25,'directions':24,'heights_m':[.2,.9,1.65],'hits':hits,'scope':'Discrete horizontal rays only; not continuous actor collision, navigation or accessibility certification','saved_camera_count':len([o for o in s.objects if o.type=='CAMERA']),'object_count':len(s.objects)}
(out/'walk-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
def xy(x,y):return (80+(x+3.3)*75,90+(9-y)*75)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="880" height="1080" viewBox="0 0 880 1080"><style>text{font-family:Microsoft YaHei, sans-serif;fill:#30483d;font-size:16px}</style><rect width="880" height="1080" fill="#f8f5ed"/><text x="50" y="38" font-size="26">知夏卧室 · 空间与机位 v0.1</text><text x="50" y="65">尺寸为建模假设｜正上方示意，不是拆墙渲染｜单位：米</text>']
def rect(x1,y1,x2,y2,color,label=''):
    x,y=xy(x1,y2);w=(x2-x1)*75;h=(y2-y1)*75
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#777465"/>')
    if label:svg.append(f'<text x="{x+7}" y="{y+22}">{label}</text>')
rect(-3,2.6,3.1,8.6,'#dbe3cb','窗外庭院');rect(3.1,-3,4.8,5.3,'#ddd8cb','通廊')
rect(-3,-3,3,2.4,'#eadbc6','卧室 6.0 × 5.4（暂定）')
rect(-2.8,-1.7,-.4,.12,'#a6b49c','床 / 西侧床头')
rect(-2.922,1.45,-1.86,2.28,'#b3946e','衣柜')
rect(.875,1.33,2.425,2.01,'#bd9f77','书桌')
rect(-1.63,2.32,1.63,2.48,'#99c8cb')
for x,y in [(-.7,4.7),(-2.2,7)]:
    px,py=xy(x,y);svg.append(f'<circle cx="{px}" cy="{py}" r="40" fill="#9eaf7d"/><text x="{px-16}" y="{py+5}">树</text>')
pts=' '.join(f'{xy(x,y)[0]},{xy(x,y)[1]}' for x,y in route);svg.append(f'<polyline points="{pts}" fill="none" stroke="#b76b37" stroke-width="4" stroke-dasharray="8 5"/>')
for obj in s.objects:
    if obj.type!='CAMERA' or obj.name.startswith('PATH'):continue
    x,y=xy(obj.location.x,obj.location.y);d=obj.rotation_euler.to_matrix()@Vector((0,0,-1));ex,ey=xy(obj.location.x+d.x*.6,obj.location.y+d.y*.6)
    svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#347b87"/><line x1="{x}" y1="{y}" x2="{ex}" y2="{ey}" stroke="#347b87" stroke-width="3"/><text x="{x+9}" y="{y-8}">{obj.name[:3]}</text>')
svg.append('<text x="50" y="1030">橙虚线：拟定通行路线；蓝点：实际保存机位。视角细节见配套渲染。</text></svg>')
(out/'plan.svg').write_text(''.join(svg),encoding='utf8')
print(json.dumps({'walk_probe_hits':len(hits),'samples':samples,'objects':len(s.objects)},ensure_ascii=False))
