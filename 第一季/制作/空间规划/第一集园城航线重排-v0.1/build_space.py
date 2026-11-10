"""Route-facing neighbourhoods and gates; all changes are a new candidate."""
import bpy, sys, argparse, ast, json, math, random, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root);OUT=ROOT/'视频制作/第一集园城航线重排-20261023-v0.1';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'视频制作/第一集园城设计-20261023-v0.1/garden-city-flight-58s-v03.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene;S.frame_set(1)
layout=json.loads((ROOT/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text(encoding='utf8'))
for path,names in [(ROOT/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py',{'section','group','box','ell','rod','surf','slab','road'}),(ROOT/'第一季/制作/空间规划/第一集园城设计-v0.1/build_design.py',{'linecurve','curved_roof','hall','pine','rocks','courtyard','center'})]:
    exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'))
COL={};G=None;added_courts=[];roof_count=0;random.seed(231023)
mn={'wood':'Warm timber / reference-derived family','wall':'Warm mineral plaster','stone':'Warm gray garden stone','green':'Garden leaves','roof':'Gray clay roof','ink':'School ink timber','paper':'School paper plaster','gray':'School gray stone','inkleaf':'School ink vegetation','water':'Longzhou water','inkwater':'School monochrome water'}
M={k:bpy.data.materials[v] for k,v in mn.items()}
gate_specs=[('A',(-1203,852,47),-30,2.5),('B',(-910,630,55),-35,3),('C',(-210,-4,5),0,2.3)]
transformed=[]
for label,xyz,deg,r in gate_specs:
    if deg==0:continue
    pivot=Vector(xyz);mat=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(deg),4,'Z')@Matrix.Translation(-pivot)
    for o in list(S.objects):
        if o.hide_render:continue
        own=o.name.startswith(('Reveal '+label,'Moon '+label))
        if o.name.startswith('Moon window trim') and (center(o)-pivot).length<1:own=True
        if own:o.matrix_world=mat@o.matrix_world;transformed.append(o.name)

# Gate approach and departure are a shared straight segment, not a U-turn to a side-facing aperture.
nodes=[list(layout['flight_points'][0]),[-1399.9,945.7,43.132],[-1396,945.7,45.7],[-1390,944.5,49],[-1372,934,53],[-1320,911,52]]
labels={'start':0,'exit':3}
for label,xyz,deg,r in gate_specs[:2]:
    if label=='B':nodes += [[-1100,793,58],[-1045,745,67]]
    v=np.array([math.cos(math.radians(deg)),math.sin(math.radians(deg)),0.]);c=np.array(xyz)
    nodes.append(list(c-v*65));labels['gate'+label]=len(nodes);nodes.append(list(c));nodes.append(list(c+v*(35 if label=='A' else 65)))
    if label=='A':nodes.append(list(c+v*80+np.array([0,0,11])))
nodes += [[-760,578,43],[-650,567,39],[-535,465,31],[-410,355,25],[-350,260,21],[-305,145,17],[-277,35,12],[-250,-4,5]]
labels['gateC']=len(nodes);nodes += [[-210,-4,5],[-185,-4,5],[-155,17,3],[-130,27,1.2],[-112,27,.45],[-96,26,.45],[-70,13.5,.45],[-30,13.5,.45],[-12,13.5,.45],[-3,13.5,1.4],[7,13.5,2.4],[10.8,16,2],[10.8,18.5,1.132]]
labels.update(skim=len(nodes)-9,lift=len(nodes)-5,end=len(nodes)-1)
route=np.array(nodes)
def near_route(x,y,r):
    q=np.array([x,y]);u=route[:-1,:2];d=route[1:,:2]-u;t=np.clip(np.sum((q-u)*d,axis=1)/np.maximum(np.sum(d*d,axis=1),1e-9),0,1)
    return float(np.min(np.linalg.norm(q-u-d*t[:,None],axis=1)))<r

def near_flight_volume(x,y,z,r,height=15):
    q=np.array([x,y]);u=route[:-1,:2];d=route[1:,:2]-u;t=np.clip(np.sum((q-u)*d,axis=1)/np.maximum(np.sum(d*d,axis=1),1e-9),0,1)
    xy=np.linalg.norm(q-u-d*t[:,None],axis=1);zz=route[:-1,2]+(route[1:,2]-route[:-1,2])*t
    return bool(np.any((xy<r)&(zz<z+height+7)&(zz>z-2)))

bpy.context.view_layer.update()
def bounds(o):
    vs=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(q[i] for q in vs) for i in range(3)]+[max(q[i] for q in vs) for i in range(3)]
obstacles=[]
for o in S.objects:
    if o.hide_render or o.type not in {'MESH','CURVE'}:continue
    if any(t in c.name for c in o.users_collection for t in ['CLOUD','FLIGHT','QUADROTOR','ROUTE_GUIDES']):continue
    b=bounds(o)
    if 'water' in o.name.lower() or 'pond' in o.name.lower() or 'pool' in o.name.lower() or 'basin' in o.name.lower():
        obstacles.append((b,True));continue
    if o.get('physical',True):obstacles.append((b,False))
occupied=[];districts=[]
def overlap(a,b,pad=0):return a[0]<b[2]+pad and a[2]>b[0]-pad and a[1]<b[3]+pad and a[3]>b[1]-pad
def clear_rect(x,y,z,w,d,pad=2):
    rect=(x-w/2,y-d/2,x+w/2,y+d/2)
    if any(abs(z-zz)<20 and overlap(rect,rr,pad) for rr,zz in occupied):return False
    for b,water in obstacles:
        if b[5]<z+(0 if water else .8) or b[2]>z+19:continue
        if overlap(rect,(b[0],b[1],b[3],b[4]),pad):return False
    return True

section('REPLAN_V01_NEIGHBOURHOODS')
# Each complete compound has lanes on all sides; offset rows avoid a ruler-straight city grid.
for bi,bank in enumerate(layout['platforms'][:7]):
    cx,cy,z=bank['center'];rx,ry=bank['radii'];z+=.2;ink=bi<2;count=0
    for row in range(900):
        for col in range(1):
            x=cx+random.uniform(-rx*.87,rx*.87);y=cy+random.uniform(-ry*.85,ry*.85)
            w=random.choice([22,26,30]);d=random.choice([19,22,25])
            if any(((xx-cx)/rx)**2+((yy-cy)/ry)**2>.90**2 for xx in [x-w/2-2,x+w/2+2] for yy in [y-d/2-3,y+d/2+3]):continue
            if near_flight_volume(x,y,z,math.hypot(w,d)/2+10) or not clear_rect(x,y,z,w+3,d+8):continue
            n=f'Replan {bi:02} compound {count:02}';courtyard(n,x,y,z,w,d,ink)
            for o in list(G.objects):
                if o.name.startswith(n+' court pine'):
                    o.location.x-=w*.26
                elif o.name.startswith(n+' court rock'):
                    o.location.x-=w*.18;o.location.y+=3-d*.32
            # A low opposite wing makes a legible lane-facing enclosure, with a generous entry gap.
            if count%3!=1:hall(n+' east wing',x+w/2-3,y+1,z,6,d-11,4.2,ink)
            # Footways form a connected mesh between the compounds; homes do not float on empty lawns.
            stone='gray' if ink else 'stone'
            road(n+' perimeter walk',[(x-w/2-3,y-d/2-4,z+.1),(x+w/2+3,y-d/2-4,z+.1),(x+w/2+3,y+d/2+3,z+.1)],3,stone)
            occupied.append(((x-w/2-2,y-d/2-5,x+w/2+3,y+d/2+3),z));count+=1
    districts.append({'name':bank['name'],'new_compounds':count})

# Low, irregular planting groups close the leftover blank lawns while keeping actual air corridors open.
section('REPLAN_V01_GARDEN_MASSES');groves=[]
for bi,bank in enumerate(layout['platforms'][:7]):
    cx,cy,z=bank['center'];rx,ry=bank['radii'];z+=.22;ink=bi<2
    for k in range(220):
        x=cx+random.uniform(-rx*.87,rx*.87);y=cy+random.uniform(-ry*.87,ry*.87)
        if ((x-cx)/rx)**2+((y-cy)/ry)**2>.88**2 or near_flight_volume(x,y,z,14) or not clear_rect(x,y,z,10,10,1):continue
        h=random.uniform(7,13);pine(f'Replan grove {bi}-{k}',x,y,z,h,ink)
        for j in range(3):
            ell('Replan low shrub',(x+random.uniform(-3,3),y+random.uniform(-3,3),z+.9),(2.1,1.7,.95),'inkleaf' if ink else 'green')
        if k%3==0:rocks('Replan grove rock',x+3,y-2,z,.8,ink)
        occupied.append(((x-5,y-5,x+5,y+5),z));groves.append([x,y,z,h])

# Canal facades are closer-spaced, but the bend and low flight keep their full open water width.
section('REPLAN_V01_CANAL_STREET');canal=[]
for side,y in [(-1,-20),(1,48)]:
    for k,x in enumerate(range(-305,-24,22)):
        z=0.;w=15+(k%3)*2;d=9
        if near_route(x,y,14) or not clear_rect(x,y,z,w+3,d+3,2):continue
        hall('Replan canal house',x,y,z,w,d,5.5+(k%3)*.9)
        road('Replan canal frontage',[(x-w/2-2,y-side*7,z+.12),(x+w/2+2,y-side*7,z+.12)],3,'stone')
        pine('Replan canal tree',x+w/2+3,y,z,7)
        occupied.append(((x-w/2-2,y-7,x+w/2+3,y+7),z));canal.append([x,y,z,w,d])

report={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'gates':[{'id':'gate'+l,'center':c,'normal':[math.cos(math.radians(d)),math.sin(math.radians(d)),0],'radius':r} for l,c,d,r in gate_specs],'gate_objects_rotated':transformed,'nodes':nodes,'labels':labels,'districts':districts,'new_compounds':added_courts,'new_groves':groves,'new_canal_houses':canal,'palette_changed':False,'status':'candidate; route and visual review pending'}
(OUT/'space-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=lambda x:x.item()),encoding='utf8')
S['replan_court_planting_refined']=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'garden-city-space-v01.blend'))
print('SPACE_READY',districts,'groves',len(groves),'canal',len(canal),flush=True)
