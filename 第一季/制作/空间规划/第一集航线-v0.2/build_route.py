"""Expand the episode into a kilometre-scale delivery corridor. Preserve v0.1 unchanged."""
import bpy,math,json,sys,argparse,random,ast,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--render',default='all');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root).resolve();OUT=ROOT/'视频制作/第一集航线空间-20261022-v0.2';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'视频制作/第一集三维场景与道路-20261022-v0.1/episode1-connected-sets-v01.blend'
old=json.loads((SOURCE.parent/'episode-layout.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene;random.seed(22102)
S['episode_scope']='CURRENT v0.2: kilometre-scale delivery corridor; previous adjacent campus layout rejected'
for tx in list(bpy.data.texts):
    if tx.name=='EPISODE_SCOPE_README':tx.name='ARCHIVE_v01_SUPERSEDED_SCOPE'
# Reuse geometry primitives only; do not execute the old builder or mutate v0.1.
helper=ROOT/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py'
names={'section','group','box','ell','rod','surf','slab','roof','table','bench','tree','railing','road','area'}
defs=[n for n in ast.parse(helper.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in names]
exec(compile(ast.Module(body=defs,type_ignores=[]),str(helper),'exec'))
COL={};G=None
material_names={'wood':'Warm timber / reference-derived family','floor':'Honey timber floor','wall':'Warm mineral plaster','stone':'Warm gray garden stone','green':'Garden leaves','sage':'Sage bedding','cream':'Ivory cloth','roof':'Gray clay roof','brass':'Muted brass','ceramic':'Ivory ceramic','glass':'Single continuous clear pane','ink':'School ink timber','paper':'School paper plaster','gray':'School gray stone','inkleaf':'School ink vegetation','inkwater':'School monochrome water','water':'Longzhou water','cloud':'Cloud support proxy'}
M={k:bpy.data.materials[v] for k,v in material_names.items()}
def flatmat(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.85;return m
for k,c in {'blockcream':(.56,.52,.43),'blockclay':(.42,.30,.23),'blockgreen':(.28,.36,.27),'ground':(.25,.30,.22),'route':(.9,.30,.045)}.items():M[k]=flatmat('V02 '+k,c)
SHIFT=Vector((-1350,900,36))
school_collections={'E01_SCHOOL_GROUND','E01_DORM','E01_DANCE_HALL'}
for o in list(S.objects):
    if any(c.name in school_collections for c in o.users_collection):o.location+=SHIFT
    if o.type=='CAMERA' and any(o.name.startswith(k) for k in ['E01-SCHOOL','E01-DORM','E01-SEND','E01-DANCE','E01-STAGE']):o.location+=SHIFT;o.data.clip_end=6000
# The former adjacent-campus ramp and misleading short flight are superseded only in this new copy.
remove_prefixes=('School exit walk','Terraced long ramp','Ramp turning landing','Ramp stone pier','Ramp east garden base')
for o in list(S.objects):
    if o.name.startswith(remove_prefixes) or o.name.startswith('PATH_parcel_technical') or o.name.startswith('E01-ROAD') or o.name.startswith('Cloud support mass proxy'):bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.collections['E01_FLIGHT_PROXY'].objects:
    if o.animation_data:o.animation_data_clear()
carrier=bpy.data.objects['Same carrier ROOT placeholder'];carrier.location=Vector(old['routes']['parcel']['points'][0])+SHIFT;carrier.rotation_euler=(0,0,0)
for o in bpy.data.collections['E01_FLIGHT_PROXY'].objects:o.hide_render=True
for o in S.objects:
    if o.type=='CAMERA':o.data.clip_end=6000

# Real distances in metres, explicitly a staging hypothesis rather than an adopted map.
school_path=[list(Vector(q)+SHIFT) for q in old['routes']['parcel']['points'][:6]]
flight=school_path+[
    [-1260,925,62],[-1195,870,63],[-1120,820,63], # adjacent learning courts / school edge
    [-1050,760,66],[-990,705,62],                 # water and mist transition corridor
    [-900,640,59],[-790,590,57],[-680,505,48],    # upper garden city
    [-570,405,42],[-450,320,34],[-335,220,26],    # overlapping courtyard blocks
    [-300,110,21],[-240,35,17],[-180,13.5,13],   # residential water lane
    [-70,13.5,8],[-25,13.5,5], [14,14,3],
    [10.8,15.5,1.132],[10.8,18.5,1.132]]
walk=[[-1371,950.2,42],[-1371,944.5,42],[-1320,850,42],[-1170,850,42],[-1090,820,36],[-1140,780,36],[-1140,680,24],[-1050,680,24],[-900,700,24],[-900,520,18],[-670,520,18],[-670,330,8],[-450,330,8],[-450,180,0],[-300,180,0],[-300,-15,0],[-30,-15,0],[-30,10.1,0],[5.8,10.1,0],[5.8,9.1,0],[8,9.1,0],[8,17.9,0],[2.2,17.9,0],[2.2,21,0]]
# Flatten the long road turns so a descending strip does not cut through the previous deck.
raw_walk=walk;split=raw_walk.index([-30,10.1,0]);main=[]
for i,pt in enumerate(raw_walk[:split+1]):
    q=Vector(pt)
    if 1<i<split and (q-Vector(raw_walk[i-1])).length>20 and (Vector(raw_walk[i+1])-q).length>20:
        before=q+(Vector(raw_walk[i-1])-q).normalized()*7;after=q+(Vector(raw_walk[i+1])-q).normalized()*7;before.z=q.z;after.z=q.z;main.extend([list(before),pt,list(after)])
    else:main.append(pt)
walk=main+raw_walk[split+1:]
def nearest(x,y,pts):
    best=1e9;point=None
    for av,bv in zip(pts,pts[1:]):
        av,bv=Vector(av),Vector(bv);d=bv-av;den=d.x*d.x+d.y*d.y;t=max(0,min(1,((x-av.x)*d.x+(y-av.y)*d.y)/den)) if den else 0;q=av+d*t;dist=math.hypot(x-q.x,y-q.y)
        if dist<best:best=dist;point=q
    return point
def distline(x,y,pts):
    best=1e9
    for av,bv in zip(pts,pts[1:]):
        av,bv=Vector(av),Vector(bv);d=bv-av;den=d.x*d.x+d.y*d.y;t=max(0,min(1,((x-av.x)*d.x+(y-av.y)*d.y)/den)) if den else 0
        q=av+d*t;best=min(best,math.hypot(x-q.x,y-q.y))
    return best
def length(pts):return sum((Vector(b)-Vector(a)).length for a,b in zip(pts,pts[1:]))

section('V02_REGIONAL_GROUND')
# Base board below the complete route, with district platforms and visible topographic steps.
slab('Regional ground proxy',-1580,-130,170,1180,-4,'ground',10)
slab('Monochrome school landscape',-1550,800,-1160,1160,36,'gray',8)
# Local campus roads extend from the already built school platform.
road('Campus approach',main[1:3],8,'gray')
road('Regional access road',main[2:],8,'stone')
road('Home lane connection',[[-30,-15,0],[-30,10.1,0]],3,'stone')
for i,(av,bv) in enumerate(zip(main[2:],main[3:])):
    av,bv=Vector(av),Vector(bv);d=bv-av
    for j in range(1,max(2,math.ceil(d.length/35))):
        q=av.lerp(bv,j/max(2,math.ceil(d.length/35)))
        if q.z>1:box('Road support proxy',(q.x,q.y,(q.z-4-.18)/2),(2,2,q.z+4-.18),'stone',0)
for x,y,z in raw_walk[2:split]:slab('Road junction',x-.5,y-.5,x+.5,y+.5,z,'stone',.25)

section('V02_SCHOOL_LEARNING_COURTS')
blocks=[]
def block(n,x,y,z,w,d,h,key,ink=False):
    o=box(n,(x,y,z+h/2),(w,d,h),key,.12);o['blockout']=True;blocks.append({'name':o.name,'center':[x,y,z+h/2],'size':[w,d,h],'district':G.name})
    box(n+' roof cap',(x,y,z+h+.18),(w+.6,d+.6,.36),'ink' if ink else 'roof',.05)
    slab(n+' terrace',x-w/2-3,y-d/2-3,x+w/2+3,y+d/2+3,z,'gray' if ink else 'stone',max(.4,z+4))
    return o
# Two courtyards along C-G03, deliberately basic masses with open courts and galleries.
for ci,(cx,cy,z) in enumerate([(-1260,975,42),(-1160,925,40)]):
    slab('Learning court floor',cx-48,cy-38,cx+48,cy+38,z,'gray',1)
    for dx,dy,w,d,h in [(-38,0,14,64,8),(38,0,14,64,10),(0,31,65,14,9)]:block('Learning court '+str(ci),cx+dx,cy+dy,z,w,d,h,'paper',True)
    slab('Learning court water',cx-15,cy-10,cx+15,cy+14,z+.02,'inkwater',.03)
    road('Learning court access',[[cx,cy-38,z],[cx,850,42]],4,'gray')
for x,y,z in [(-1480,1000,36),(-1450,1080,36),(-1300,1090,36),(-1170,1070,36)]:
    block('Ink hillside proxy',x,y,z,55,45,random.uniform(30,65),'gray',True)

section('V02_BOUNDARY_CASCADE')
# Three separated water terraces beside the flight corridor. No flight through solid falls.
for i,(x,y,z) in enumerate([(-1070,785,43),(-1040,750,30),(-1010,715,17)]):
    slab('Boundary water terrace',x-28,y-20,x+28,y+20,z,'gray' if i==0 else 'stone',z+4)
    box('Boundary water plane',(x,y,z+.08),(54,38,.06),'inkwater' if i==0 else 'water',0,False)
    if i<2:surf('Boundary sheet fall',[(x-22,y-20.1,z+.1),(x+22,y-20.1,z+.1),(x+52,y-35.1,z-12.9),(x+8,y-35.1,z-12.9)],[(0,1,2,3)],'water',False)
# Translucent fog volume is a reversible visual interface, not a portal mechanism.
fog=bpy.data.materials.new('Boundary neutral mist candidate');fog.use_nodes=True;fog.node_tree.nodes.clear();v=fog.node_tree.nodes.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.018;v.inputs['Color'].default_value=(.7,.7,.7,1);outnode=fog.node_tree.nodes.new('ShaderNodeOutputMaterial');fog.node_tree.links.new(v.outputs['Volume'],outnode.inputs['Volume']);M['fog']=fog
fogobj=box('Boundary mist candidate',(-1030,754,51),(130,110,44),'fog',0,False);fogobj.display_type='WIRE'

section('V02_CITY_BLOCKS')
# Districts flank the actual flight and walking routes. No decorative empty corridor.
districts=[('Upper garden quarter',-880,655,440,320,20,16,34),('Mid terrace quarter',-620,440,460,360,10,10,26),('Lower garden quarter',-390,235,380,320,0,7,18)]
for title,cx,cy,ww,dd,z,hmin,hmax in districts:
    section('V02_'+title.replace(' ','_'))
    for ix in range(int(ww/38)):
        for iy in range(int(dd/38)):
            x=cx-ww/2+ix*38+random.uniform(-4,4);y=cy-dd/2+iy*38+random.uniform(-4,4)
            if distline(x,y,flight)<32 or distline(x,y,walk)<29:continue
            w=random.uniform(15,25);d=random.uniform(15,26);h=random.uniform(hmin,hmax)
            if any(abs(x-bx)<w/2+31 and abs(y-by)<d/2+23 for bx,by in [(-1070,785),(-1040,750),(-1010,715)]):continue
            if min(abs(y-(cy-85)),abs(y-(cy+85)))<d/2+6:continue
            if any(abs(x-b['center'][0])<(w+b['size'][0])/2+7 and abs(y-b['center'][1])<(d+b['size'][1])/2+7 for b in blocks):continue
            block(title+' mass',x,y,z,w,d,h,random.choice(['blockcream','blockclay','blockgreen']))
            if (ix+iy)%4==0:tree('Court tree proxy',x+w/2+1.5,y,z,4)
    # Local streets cross each quarter, extending the main access road into the block fabric.
    for yy in [cy-85,cy+85]:
        streetz=nearest(cx,yy,walk).z
        road(title+' cross street',[[cx-ww/2-25,yy,streetz],[cx+ww/2+25,yy,streetz]],2.4,'stone')

section('V02_WATER_LANE_APPROACH')
slab('Extended canal basin',-340,10.8,-22,16.2,-.8,'stone',.4)
box('Extended canal water',(-181,13.5,-.48),(318,5.4,.055),'water',0,False)
road('Extended south quay',[[-340,8.9,0],[-22,8.9,0]],3.5,'stone')
road('Extended north quay',[[-340,18.6,0],[-22,18.6,0]],3.5,'stone')
for side in [-1,1]:
    for i,x in enumerate(range(-330,-30,24)):
        y=-2 if side<0 else 32
        if distline(x,y,flight)<11 or distline(x,y,walk)<11:continue
        block('Water lane house mass',x,y,0,random.uniform(9,16),random.uniform(8,12),random.uniform(4,9),'blockcream')
for x in [-280,-130]:road('Neighbour water bridge',[[x,7,0],[x,20,0]],3,'stone')

section('V02_ROUTE_GUIDES')
cv=bpy.data.curves.new('Parcel route metres','CURVE');cv.dimensions='3D';sp=cv.splines.new('POLY');sp.points.add(len(flight)-1)
for q,pt in zip(sp.points,flight):q.co=(*pt,1)
curve=bpy.data.objects.new('DELIVERY_ROUTE full journey — not timed animation',cv);G.objects.link(curve);curve.show_in_front=True;curve.color=(1,.25,.02,1);curve.hide_render=True
cv.bevel_depth=.35;cv.bevel_resolution=0;cv.materials.append(M['route'])
guide=curve.copy();guide.data=cv.copy();guide.name='Route overview render guide';G.objects.link(guide);guide.hide_render=True;guide['physical']=False
stops=[('01 宿舍寄件',flight[0]),('02 学院外缘',flight[6]),('03 水墨边界',flight[9]),('04 上层园城',flight[12]),('05 中层街区',flight[15]),('06 水巷入口',flight[19]),('07 两岸住家',flight[-3]),('08 作坊收件',flight[-1])]
for label,pos in stops:
    e=bpy.data.objects.new(label,None);G.objects.link(e);e.location=pos;e.empty_display_type='SPHERE';e.empty_display_size=3;e.show_in_front=True

section('V02_ROUTE_CAMERAS');cameras={}
specs=[
('V02-OV','整条寄送航线总览',(780,-1450,1750),(-700,510,15),43,'C-G01—C-G06'),
('V02-SCHOOL','学校与相邻学习庭院',(-1540,760,140),(-1280,960,48),35,'C-G02/G03'),
('V02-EDGE','沿学院外缘离开',(-1310,835,76),(-1170,915,47),30,'C-G03'),
('V02-BOUNDARY','叠水与薄雾边界',(-1160,620,125),(-1030,760,35),36,'C-G04'),
('V02-UPPER','雾后上层园城',(-1050,545,115),(-820,640,34),32,'C-G04'),
('V02-MIDDLE','穿过中段街区',(-760,295,94),(-550,420,28),32,'C-G04'),
('V02-LOWER','层叠街区向水巷下降',(-515,80,80),(-320,210,17),32,'C-G04/G05'),
('V02-CANAL','长水巷与住宅体块',(-270,-44,35),(-85,16,5),35,'C-G05'),
('V02-ARRIVE','抵达住家与对岸作坊',(28,-20,22),(-5,17,2),32,'C-G05/G06')]
for cid,title,pos,target,lens,shots in specs:
    d=bpy.data.cameras.new(cid);d.lens=lens;d.clip_start=.1;d.clip_end=6000;o=bpy.data.objects.new(cid+'_'+title,d);G.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cameras[cid]=o
S.camera=cameras['V02-OV'];S.frame_start=1;S.frame_end=1;S.frame_set(1)
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.cycles.use_denoising=True;S.cycles.max_bounces=4;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
S.world.color=(.5,.5,.5)
# Large-scene ray precision exposes coplanar deck intersections as black patches.
# Separate thin stone surfaces by 3-16.8 mm with reversible modifiers; source meshes stay intact.
for i,o in enumerate(S.objects):
    if o.type=='MESH' and o.dimensions.z<.7 and any(m and m.name in ['Warm gray garden stone','School gray stone'] for m in o.data.materials):
        mod=o.modifiers.new('V02 separate coincident stone surfaces','DISPLACE');mod.direction='Z';mod.mid_level=0;mod.strength=.003+(i%47)*.0003;o['surface_separation_m']=mod.strength
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':ar.spaces.active.clip_end=6000;ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.shading.type='SOLID'
data={'version':'v0.2','status':'Expanded delivery corridor candidate; old adjacent campus rejected','source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'school_translation_m':list(SHIFT),'direct_distance_m':(Vector(flight[0])-Vector(flight[-1])).length,'flight_distance_m':length(flight),'walking_route_distance_m':length(walk),'flight_points':flight,'walk_points':walk,'stops':[{'label':n,'point':q} for n,q in stops],'blocks':blocks,'cameras':[{'id':c,'title':t,'position':p,'target':v,'lens_mm':l,'shots':s} for c,t,p,v,l,s in specs],'limits':['Distances are proposed scene scale, not adopted world geography','Building masses are placeholders; no final architecture or game assets','Fog is a visual candidate, not a teleportation decision','Route has no approved timing; full delivery is not compressed into former 10-second test','Road branch interiors and full character navigation are not validated']}
(OUT/'route-layout.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
tx=bpy.data.texts.new('V02_CURRENT_SCOPE');tx.write(json.dumps({k:v for k,v in data.items() if k!='blocks'},ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'episode1-delivery-corridor-v02.blend'))
ids=list(cameras) if a.render=='all' else ([] if a.render=='none' else a.render.split(','))
for cid in ids:
    S.camera=cameras[cid];guide.hide_render=cid!='V02-OV';S.render.filepath=str(OUT/(cid+'.png'));bpy.ops.render.render(write_still=True)
print('ROUTE_BUILD_OK',json.dumps({'blocks':len(blocks),'flight_m':length(flight),'walk_m':length(walk)}),flush=True)
