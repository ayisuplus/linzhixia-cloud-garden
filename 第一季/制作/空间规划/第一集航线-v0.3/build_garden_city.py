"""Floating garden corridor v0.3. Local geometric previs, no generated movie."""
import bpy, math, random, json, ast, argparse, sys, hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--render',default='all');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root).resolve();OUT=ROOT/'视频制作/第一集浮空园城-20261022-v0.3';OUT.mkdir(exist_ok=True,parents=True)
SOURCE=ROOT/'视频制作/第一集航线空间-20261022-v0.2/episode1-delivery-corridor-v02.blend'
old=json.loads((SOURCE.parent/'route-layout.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene;random.seed(103)
for c in list(bpy.data.collections):
    if c.name.startswith('V02_'):
        for o in list(c.objects):bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
helper=ROOT/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py'
names={'section','group','box','ell','rod','surf','slab','roof','tree','road','railing','area'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
COL={};G=None
mn={'wood':'Warm timber / reference-derived family','floor':'Honey timber floor','wall':'Warm mineral plaster','stone':'Warm gray garden stone','green':'Garden leaves','sage':'Sage bedding','cream':'Ivory cloth','roof':'Gray clay roof','brass':'Muted brass','ink':'School ink timber','paper':'School paper plaster','gray':'School gray stone','inkleaf':'School ink vegetation','inkwater':'School monochrome water','water':'Longzhou water','cloud':'Cloud support proxy'}
M={k:bpy.data.materials[v] for k,v in mn.items()}
def mat(n,c):
    m=bpy.data.materials.new('V03 '+n);m.diffuse_color=(*c,1);m.use_nodes=True;b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=.83;return m
for k,c in {'cloudhard':(.68,.75,.73),'cloudsoft':(.85,.88,.83),'grass':(.27,.37,.23),'sand':(.57,.54,.43),'route':(.9,.30,.045),'mistfar':(.73,.79,.78)}.items():M[k]=mat(k,c)
# Remove the inherited single opaque gray world; open sky remains below the floating edges too.
S.world.use_nodes=True;S.world.node_tree.nodes.clear();bg=S.world.node_tree.nodes.new('ShaderNodeBackground');bg.inputs['Color'].default_value=(.40,.61,.80,1);bg.inputs['Strength'].default_value=.7;wo=S.world.node_tree.nodes.new('ShaderNodeOutputWorld');S.world.node_tree.links.new(bg.outputs[0],wo.inputs['Surface'])
S.world.color=(.54,.65,.73)
for o in S.objects:
    if o.type=='LIGHT' and o.data.type=='SUN':o.data.energy=2.2;o.rotation_euler=(.35,-.6,-.55)

flight=old['flight_points'][:6]+[[-1290,925,54],[-1235,885,49],[-1215,865,47],[-1213,842,47],[-1190,842,47],[-1120,815,55],[-1050,760,66],[-990,705,62],[-945,665,55],[-945,635,55],[-920,610,55],[-895,610,55],[-890,625,55],[-850,615,57],[-790,590,57],[-680,505,48],[-570,405,42],[-450,320,34],[-335,220,26],[-300,110,21],[-260,30,12],[-225,0,6],[-225,13.5,6],[-180,13.5,6],[-145,23,8],[-105,27,8],[-70,13.5,8],[-25,13.5,5],[14,14,3],[10.8,15.5,1.132],[10.8,18.5,1.132]]
raw_walk=[[-1371,950.2,42],[-1371,944.5,42],[-1320,920,42],[-1250,880,42],[-1220,830,42],[-1170,815,42],[-1150,780,42],[-1140,680,24],[-1050,680,24],[-900,700,24],[-900,520,18],[-830,460,18],[-670,460,18],[-600,380,8],[-480,330,8],[-480,180,0],[-300,180,0],[-300,-15,0],[-30,-15,0],[-30,10.1,0]]
walk=[]
for i,pt in enumerate(raw_walk):
    q=Vector(pt)
    if 1<i<len(raw_walk)-1:
        pre=q+(Vector(raw_walk[i-1])-q).normalized()*6;post=q+(Vector(raw_walk[i+1])-q).normalized()*6;pre.z=q.z;post.z=q.z;walk.extend([list(pre),pt,list(post)])
    else:walk.append(pt)
walk+=old['walk_points'][old['walk_points'].index([-30,10.1,0])+1:]
def length(pts):return sum((Vector(b)-Vector(a)).length for a,b in zip(pts,pts[1:]))
def distline(x,y,pts):
    best=1e9
    for aa,bb in zip(pts,pts[1:]):
        a,b=Vector(aa),Vector(bb);d=b-a;t=max(0,min(1,((x-a.x)*d.x+(y-a.y)*d.y)/max(.0001,d.x*d.x+d.y*d.y)));q=a+t*d;best=min(best,math.hypot(x-q.x,y-q.y))
    return best
platforms=[];blocks=[]
def cloudbank(n,cx,cy,z,rx,ry,depth=10,ink=False):
    """A shallow lenticular load-bearing cloud material, not rock and not ordinary mist."""
    count=64;verts=[];phase=random.random()*6
    rings=[(1,0),(.99,-depth*.24),(.87,-depth*.7),(.55,-depth),(0.07,-depth*1.1)]
    for factor,dz in rings:
        for i in range(count):
            t=i*math.tau/count;r=1+.18*math.sin(3*t+phase)+.09*math.sin(7*t-phase)
            verts.append((cx+rx*r*factor*math.cos(t),cy+ry*r*factor*math.sin(t),z+dz))
    faces=[tuple(range(count))]
    for j in range(len(rings)-1):
        for i in range(count):faces.append((j*count+i,(j+1)*count+i,(j+1)*count+(i+1)%count,j*count+(i+1)%count))
    faces.append(tuple(reversed(range((len(rings)-1)*count,len(rings)*count))))
    o=surf(n+' structural cloud',verts,faces,'gray' if ink else 'cloudhard');o['material_role']='Load-bearing cloud material; antigravity remains unspecified'
    for f in o.data.polygons[1:]:f.use_smooth=True
    # Garden top fits inside the actual bank, keeps a pale soft margin visible.
    top=[(cx,cy,z+.035)]+[(cx+rx*.86*(1+.04*math.sin(3*i*math.tau/count))*math.cos(i*math.tau/count),cy+ry*.86*(1+.04*math.sin(3*i*math.tau/count))*math.sin(i*math.tau/count),z+.035) for i in range(count)]
    surf(n+' garden surface',top,[(0,i+1,(i+1)%count+1) for i in range(count)],'gray' if ink else 'grass')
    platforms.append({'name':n,'center':[cx,cy,z],'radii':[rx,ry],'depth':depth})
    return o
def water(n,x,y,z,rx,ry,ink=False):
    vs=[(x+rx*math.cos(i*math.tau/64),y+ry*math.sin(i*math.tau/64),z) for i in range(64)];surf(n,vs,[tuple(range(64))],'inkwater' if ink else 'water',False)
def pavilion(n,x,y,z,w=14,d=10,h=5,ink=False):
    key='ink' if ink else 'wood';slab(n+' stone terrace',x-w/2-1,y-d/2-1,x+w/2+1,y+d/2+1,z,'gray' if ink else 'stone',.45)
    for xx in [-w/2,w/2]:
        for yy in [-d/2,d/2]:rod(n+' column',(x+xx,y+yy,z),(x+xx,y+yy,z+h),.25,key)
    roof(n+' tiled roof',x-w/2-1.2,y-d/2-1.2,x+w/2+1.2,y+d/2+1.2,z+h,'ink' if ink else 'roof')
def courtyard(n,x,y,z,w=34,d=25,ink=False):
    key='paper' if ink else 'wall';stone='gray' if ink else 'stone'
    slab(n+' apron',x-w/2-3,y-d/2-3,x+w/2+3,y+d/2+3,z,stone,.5)
    for dx,dy,ww,dd in [(-w/2,0,6,d),(w/2,0,6,d),(0,d/2,w,7)]:
        o=box(n+' wing',(x+dx,y+dy,z+3),(ww,dd,6),key,.08);blocks.append({'name':o.name,'center':list(o.location),'size':[ww,dd,6],'district':G.name});roof(n+' roof',x+dx-ww/2-.6,y+dy-dd/2-.6,x+dx+ww/2+.6,y+dy+dd/2+.6,z+6,'ink' if ink else 'roof')
    water(n+' courtyard pool',x,y,z+.025,w*.22,d*.17,ink);tree(n+' asymmetrical court tree',x-w*.23,y-d*.15,z,9,'inkleaf' if ink else 'green','ink' if ink else 'wood')
def gallery(n,pts,width=5,ink=False):
    road(n+' deck',pts,width,'gray' if ink else 'stone')
    for aa,bb in zip(pts,pts[1:]):
        a,b=Vector(aa),Vector(bb);dv=b-a;side=Vector((-dv.y,dv.x,0)).normalized();num=max(1,math.ceil(dv.length/9))
        for i in range(num):
            v=a.lerp(b,(i+.5)/num);seg=dv.length/num
            # Roof axis follows each bridge segment; shallow pitched sectional strip.
            ends=[a.lerp(b,i/num),a.lerp(b,(i+1)/num)];vs=[]
            for e in ends:
                vs.extend([e+side*(width/2+.65)+Vector((0,0,4.2)),e+Vector((0,0,5.2)),e-side*(width/2+.65)+Vector((0,0,4.2))])
            surf(n+' folded roof',vs,[(0,3,4,1),(1,4,5,2)],'ink' if ink else 'roof')
            for s in [-1,1]:
                q=ends[0]+side*s*(width/2-.25);rod(n+' gallery post',q,q+Vector((0,0,4.3)),.15,'ink' if ink else 'wood')
def curve(n,pts,r,key,physical=False):
    cv=bpy.data.curves.new(n,'CURVE');cv.dimensions='3D';sp=cv.splines.new('POLY');sp.points.add(len(pts)-1)
    for q,pt in zip(sp.points,pts):q.co=(*pt,1)
    cv.bevel_depth=r;cv.bevel_resolution=2;cv.materials.append(M[key]);o=bpy.data.objects.new(n,cv);G.objects.link(o);o['physical']=physical;return o

section('V03_CLOUD_STRUCTURE')
# No common rectangle, no rock cones, no road piers extending to a ground plane.
cloudbank('School cloud shore',-1340,970,35.7,220,148,13,True)
cloudbank('School gate garden',-1200,859,41.7,75,61,9,True)
cloudbank('Upper hanging garden',-780,760,58,154,110,8)
cloudbank('Middle courtyard garden',-655,600,23,175,102,10)
cloudbank('West shaded garden',-1030,500,-15,155,105,10)
cloudbank('Lower eastern garden',-365,325,4,115,105,8)
cloudbank('Lower western garden',-520,150,-8,140,96,9)
cloudbank('Water lane cloud bank',-150,20,-3.5,220,62,8)
# The entire route is a usable connected city. Cloud ribbons carry the pedestrian spine.
section('V03_WALKING_CONNECTIONS')
split=walk.index([-30,10.1,0]);road('Cross district walking spine',walk[1:split+1],8,'stone');road('Home lane connection',[[-30,-15,0],[-30,10.1,0]],3,'stone')
for x,y,z in walk[1:split]:slab('Spine corner seam',x-.25,y-.25,x+.25,y+.25,z,'stone',.25)
for i,(aa,bb) in enumerate(zip(walk[1:split],walk[2:split+1])):
    a0,b0=Vector(aa),Vector(bb);dv=b0-a0;side=Vector((-dv.y,dv.x,0)).normalized()*5.4
    # ribbon below the deck; open sky still visible on both sides
    surf('Load-bearing cloud ribbon', [a0+side-Vector((0,0,.3)),a0-side-Vector((0,0,.3)),b0-side-Vector((0,0,.3)),b0+side-Vector((0,0,.3)),a0-Vector((0,0,4)),b0-Vector((0,0,4))],[(0,3,2,1),(0,4,5,3),(1,2,5,4),(0,1,4),(2,3,5)],'cloudhard')
    # Handrails are simplified continuous lines; detailed supports belong to the next pass.
    for s in [-1,1]:curve('Spine edge handrail',[list(a0+side.normalized()*s*3.9+Vector((0,0,1))),list(b0+side.normalized()*s*3.9+Vector((0,0,1)))],.08,'wood')

section('V03_LEARNING_GARDENS')
for x,y,z in [(-1290,999,35.8),(-1180,894,41.8)]:courtyard('Learning garden',x,y,z,40,28,True)
gallery('School waterside corridor',[[-1363,946,42],[-1300,946,42],[-1250,902,42],[-1230,875,42]],5,True)
for x,y in [(-1400,1030),(-1320,1050),(-1270,985),(-1250,920),(-1170,879),(-1190,877)]:tree('Ink cloud garden tree',x,y,42,random.uniform(10,17),'inkleaf','ink')
# A real garden screen blocks a distant pavilion, while the parcel turns past its end.
box('Reveal A garden screen',(-1203,859,47.5),(.65,22,11),'paper',.12)
roof('Reveal A screen coping',-1204,847,-1202,871,53.1,'ink')
pavilion('School exit rest pavilion',-1223,850,42,10,9,5,True)

section('V03_WATER_SEQUENCE')
for i,(x,y,z,rx,ry) in enumerate([(-1070,805,45,60,45),(-1025,755,23,58,43),(-980,705,0,54,40)]):
    cloudbank('Cascade garden '+str(i),x,y,z-.4,rx+10,ry+10,7,ink=i==0);water('Catchment basin '+str(i),x,y,z,rx,ry,ink=i==0)
    pavilion('Water listening pavilion '+str(i),x-56,y+12,z+.15,12,8,5,i==0)
    if i<2:
        # Narrow sheet meets the following catchment, not an endless fall onto homes.
        surf('Cascade falling water '+str(i),[(x-8,y-ry*.7,z),(x+8,y-ry*.7,z),(x+45+8,y-50+10,z-22),(x+45-8,y-50+10,z-22)],[(0,1,2,3)],'water',False)
    curve('Catchment rim '+str(i),[(x+rx*math.cos(t*math.tau/64),y+ry*math.sin(t*math.tau/64),z+.15) for t in range(65)],.35,'stone')
curve('Return-water service conduit candidate',[[-980,705,-3],[-1025,755,-3],[-1070,805,42]],.5,'cloudhard')
# Sparse ordinary mist ONLY at the waterfall and below far edges.
fog=bpy.data.materials.new('V03 ordinary water mist');fog.use_nodes=True;fog.node_tree.nodes.clear();v=fog.node_tree.nodes.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=.007;v.inputs['Color'].default_value=(.78,.82,.83,1);nd=fog.node_tree.nodes.new('ShaderNodeOutputMaterial');fog.node_tree.links.new(v.outputs['Volume'],nd.inputs['Volume']);M['fog']=fog
fogob=box('Ordinary mist beside cascade',(-1035,756,42),(84,72,36),'fog',0,False);fogob.display_type='WIRE'

section('V03_GARDEN_ROOMS')
cloudbank('Moon corridor garden',-920,638,48,62,48,7)
water('Moon corridor shallow pool',-942,647,48.12,22,17)
box('Reveal B garden screen',(-910,639,55),(.7,34,14),'wall',.15)
roof('Reveal B screen coping',-911,621,-909,657,62.1)
gallery('Moon corridor',[[-953,622,48],[-944,609,48],[-915,602,48]],4)
tree('Near screen canopy',-913,655,48,14)
# Landmark recurs in skyline, side view and through the later bridge opening.
pavilion('Cloud observatory landmark',-810,678,58,23,18,8)
pavilion('Cloud observatory upper',-810,678,68,15,12,6)
for n,x,y,z in [('Upper east court',-715,775,58),('Upper west court',-835,785,58),('Middle dwelling court',-630,610,23),('Lower east court',-345,350,4),('Lower west court',-545,175,-8),('West quiet court',-1050,520,-15)]:courtyard(n,x,y,z)
gallery('Hanging garden connecting bridge',[[-900,700,24],[-875,735,40],[-860,755,50],[-855,760,58]],5)
gallery('East layered garden bridge',[[-705,715,58],[-665,690,48],[-625,660,42],[-620,635,23]],5)
gallery('Lower borrowed-view bridge',[[-450,330,8],[-410,355,6],[-385,355,4]],5)
gallery('West garden access',[[-1140,680,24],[-1160,610,8],[-1145,550,-15],[-1110,520,-15]],5)
gallery('Lower west access',[[-480,180,0],[-500,195,-8],[-510,190,-8]],5)
gallery('Middle garden access',[[-670,460,18],[-630,500,23],[-620,550,23]],5)
# Planters/paths follow each individual garden, never a rectangular city block grid.
for bank in platforms[:8]:
    cx,cy,z=bank['center'];rx,ry=bank['radii'];ink='School' in bank['name']
    for i in range(22):
        t=i*2.399;rr=random.uniform(.48,.75);x=cx+math.cos(t)*rx*rr;y=cy+math.sin(t)*ry*rr
        if distline(x,y,flight)<14 or distline(x,y,walk)<12:continue
        tree('Cloud garden tree',x,y,z+.1,random.uniform(9,17),'inkleaf' if ink else 'green','ink' if ink else 'wood')
    pts=[(cx+rx*.74*math.cos(i*math.tau/40),cy+ry*.74*math.sin(i*math.tau/40),z+.1) for i in range(41)]
    road('Garden winding path',pts,2.5,'gray' if ink else 'stone')
    # Soft lip hangs down in long lateral lobes instead of a soil/rock island.
    for i in range(18):
        t=i*math.tau/18+.2;x=cx+rx*.9*math.cos(t);y=cy+ry*.9*math.sin(t)
        if distline(x,y,walk)<rx*.20+7:continue
        ell('Cloud material soft edge',(x,y,z-3),(rx*random.uniform(.10,.19),ry*random.uniform(.10,.19),random.uniform(2,5)),'cloudsoft')
    for i in range(7):
        t=i*math.tau/7+.6;x=cx+rx*.48*math.cos(t);y=cy+ry*.48*math.sin(t)
        if distline(x,y,flight)<26 or distline(x,y,walk)<28:continue
        if bank['name']=='Water lane cloud bank':continue
        courtyard('Garden neighbourhood',x,y,z+.15,24,17,ink)

section('V03_CANAL_NEIGHBOURHOOD')
canal=[[-340,30,0],[-285,30,0],[-240,13.5,0],[-170,13.5,0],[-140,27,0],[-95,27,0],[-70,13.5,0],[-22,13.5,0]]
def canal_strip(name,offset,width,z,key,physical=True):
    vs=[]
    for i,pt in enumerate(canal):
        d=Vector(canal[min(i+1,len(canal)-1)])-Vector(canal[max(i-1,0)]);side=Vector((-d.y,d.x,0)).normalized();q=Vector(pt)+side*offset;q.z=z;vs.extend([q-side*width/2,q+side*width/2])
    return surf(name,vs,[(2*i,2*i+2,2*i+3,2*i+1) for i in range(len(canal)-1)],key,physical)
canal_strip('Curving canal basin',0,6.5,-.8,'stone');canal_strip('Curving canal water',0,5.4,-.48,'water',False)
canal_strip('South waterside lane',-4.6,3.5,0,'stone');canal_strip('North waterside lane',5.1,3.5,0,'stone')
for i,x in enumerate([-300,-255,-160,-108,-60]):
    for y in [-4,39]:
        if distline(x,y,walk)<12:continue
        w=14;d=9;h=4.5+(i%2)*1.5;o=box('Canal house',(x,y,h/2),(w,d,h),'wall',.04);blocks.append({'name':o.name,'center':list(o.location),'size':[w,d,h],'district':G.name});roof('Canal house roof',x-8,y-5.5,x+8,y+5.5,h)
        tree('Canal courtyard tree',x+10,y,0,8)
box('Reveal C white wall',(-210,0,5),(.5,20,10),'wall',.08);roof('Reveal C coping',-211,-11,-209,11,10)
gallery('Canal long gallery',[[-200,25,0],[-165,25,0],[-140,37,0],[-95,37,0]],3.5)
for x,y in [(-280,30),(-130,27)]:road('Canal neighbour bridge',[[x,y-6.5,0],[x,y+6.5,0]],3,'stone')
# Lower-level sky and remote cloud banks are staging surroundings, not traversable structures.
section('V03_DISTANT_CLOUDS')
for x,y,z,rx,ry in [(-1500,1320,-125,410,190),(-800,1150,-170,380,170),(-300,750,-180,330,130),(300,280,-150,280,130),(-900,-250,-155,430,180)]:
    o=box('Distant ordinary cloud proxy',(x,y,z),(rx*2,ry*2,18),'fog',0,False);o.display_type='WIRE'

section('V03_FRAME_OPENINGS')
for name,location,radius,key in [('Reveal A garden screen',(-1203,852,47),2.5,'ink'),('Reveal B garden screen',(-910,630,55),3.0,'wood'),('Reveal C white wall',(-210,-4,5),2.3,'wood')]:
    wall=bpy.data.objects[name];bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=3,location=location,rotation=(0,math.pi/2,0));cutter=bpy.context.object;mod=wall.modifiers.new('Real circular garden opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;bpy.context.view_layer.objects.active=wall;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    x,y,z=location;curve('Moon window trim',[(x-.36,y+radius*math.cos(i*math.tau/64),z+radius*math.sin(i*math.tau/64)) for i in range(65)],.12,key)
section('V03_ROUTE_GUIDES');guide=curve('Parcel route guide',flight,.65,'route');guide.hide_render=True;guide.show_in_front=True
section('V03_CAMERAS');cameras={}
specs=[
('V03-OV','云隙与层叠园城',(-1650,-1360,1080),(-730,580,12),43,'C-G01—06'),
('V03-SIDE','侧看云岸：城下留空',(-1520,0,120),(-800,660,35),40,'C-G04'),
('V03-A0','廊墙收景',(-1215,865,47),(-1070,805,50),35,'C-G03'),
('V03-AM','转角中段：墙端与远景',(-1213,842,47),(-1070,805,50),35,'C-G03/G04'),
('V03-A1','转过墙端，露出叠水',(-1190,842,47),(-1070,805,50),35,'C-G03/G04'),
('V03-B0','近墙藏住上层水榭',(-945,635,55),(-810,678,68),35,'C-G04'),
('V03-BM','绕墙中段：局部露出',(-924,614,55),(-810,678,68),35,'C-G04'),
('V03-B1','绕墙后，水榭与悬廊展开',(-890,625,55),(-810,678,68),35,'C-G04'),
('V03-WATER','同一水脉：从上池落入下庭',(-1130,695,60),(-1040,770,25),35,'C-G04'),
('V03-MID','经过上层庭院的下方',(-750,490,48),(-810,678,68),30,'C-G04'),
('V03-C0','水巷墙端收住去路',(-225,0,6),(10.8,18.5,3),35,'C-G05'),
('V03-CM','转入水巷的墙边',(-225,13.5,6),(10.8,18.5,3),35,'C-G05'),
('V03-C1','转入水巷，看到两岸住家',(-180,13.5,6),(10.8,18.5,3),35,'C-G05'),
('V03-C2','越过弯岸，半园桥与作坊显露',(-70,13.5,8),(10.8,18.5,3),35,'C-G05/G06'),
('V03-HOME','落回熟悉的桥与作坊',(28,-20,22),(-5,17,2),32,'C-G05/G06')]
for cid,title,pos,target,lens,shots in specs:
    d=bpy.data.cameras.new(cid);d.lens=lens;d.clip_start=.1;d.clip_end=6000;o=bpy.data.objects.new(cid+' '+title,d);G.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();cameras[cid]=o
for o in list(S.objects):
    if o.name.startswith('Middle garden access gallery post') and distline(o.location.x,o.location.y,walk)<3:bpy.data.objects.remove(o,do_unlink=True)
for i,o in enumerate(S.objects):
    if o.type=='MESH' and any(c.name.startswith('V03_') for c in o.users_collection) and o.dimensions.z<.7 and any(m and m.name in ['Warm gray garden stone','School gray stone'] for m in o.data.materials):
        mod=o.modifiers.new('V03 separate coincident deck surfaces','DISPLACE');mod.direction='Z';mod.mid_level=0;mod.strength=.004+(i%37)*.0003
S.camera=cameras['V03-OV'];S.frame_start=1;S.frame_end=1;S.frame_set(1);S['episode_scope']='v0.3 floating garden spatial candidate. Three geometric reveal pairs. Not final art or timed film.'
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=24;S.cycles.use_denoising=True;S.cycles.max_bounces=4;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':ar.spaces.active.clip_end=6000;ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.shading.type='SOLID'
data={'version':'v0.3','status':'Floating garden spatial candidate, author review pending','source':old['source'],'source_sha256':old['source_sha256'],'previous_source':str(SOURCE.relative_to(ROOT)),'previous_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'school_translation_m':old['school_translation_m'],'flight_distance_m':length(flight),'walking_route_distance_m':length(walk),'flight_points':flight,'walk_points':walk,'blocks':blocks,'platforms':platforms,'cameras':[dict(id=c,title=t,position=p,target=v,lens_mm=l,shots=s) for c,t,p,v,l,s in specs],'reveal_pairs':[{'id':'A','before':'V03-A0','after':'V03-A1','target':[-1070,805,50],'screen':'Reveal A garden screen'},{'id':'B','before':'V03-B0','after':'V03-B1','target':[-810,678,68],'screen':'Reveal B garden screen'},{'id':'C','before':'V03-C0','after':'V03-C1','target':[10.8,18.5,3],'screen':'Reveal C white wall'}],'limits':['Cloud material is structural; ordinary mist is visual only. Antigravity mechanics unspecified.','Original interiors remain; surroundings and inferred dimensions are candidates.','Gardens and secondary sloped galleries are staging masses, not accessibility or engineering certification.','No timing, film animation, final vegetation or water simulation.','Sightline evidence concerns selected landmarks, not every pixel or a continuous camera path.']}
(OUT/'route-layout.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');tx=bpy.data.texts.new('V03_CURRENT_SCOPE');tx.write(json.dumps(data,ensure_ascii=False,indent=2))
for tx in bpy.data.texts:
    if tx.name=='V02_CURRENT_SCOPE':tx.name='ARCHIVE_V02_SCOPE'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'episode1-floating-garden-v03.blend'))
ids=list(cameras) if a.render=='all' else ([] if a.render=='none' else a.render.split(','))
for cid in ids:
    S.camera=cameras[cid];S.render.filepath=str(OUT/(cid+'.png'));bpy.ops.render.render(write_still=True)
print('GARDEN_CITY_BUILD_OK',len(S.objects),length(flight),flush=True)
