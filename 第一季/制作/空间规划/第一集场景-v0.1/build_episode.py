"""Episode 1 connected set candidate. Explicit project root. Original bedroom remains untouched."""
import bpy, math, json, sys, argparse, random, hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--render',default='all');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root).resolve();OUT=ROOT/'视频制作/第一集三维场景与道路-20261022-v0.1';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'视频制作/知夏卧室三维空间-20261022-v0.1/zhixia-bedroom-v01.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene
S['episode_scope']='A-G spatial candidate, not adopted final art or game environment'
random.seed(26)
for o in list(S.objects):
    if o.type=='LIGHT' and o.data.type=='SUN':bpy.data.objects.remove(o,do_unlink=True)
for c in list(S.collection.children):c.name='HOME_'+c.name
COL={};G=None
def section(name):
    global G
    print('BUILD_SECTION',name,flush=True)
    c=bpy.data.collections.new(name);S.collection.children.link(c);COL[name]=c;G=c
def group(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    G.objects.link(o);return o
def mat(n,c,rough=.7,metal=0,noise=False):
    m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    if noise:
        ns=m.node_tree.nodes;ls=m.node_tree.links;t=ns.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=5;b=ns.new('ShaderNodeBump');b.inputs['Strength'].default_value=.15;b.inputs['Distance'].default_value=.035;ls.new(t.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs[0],bs.inputs['Normal'])
    return m
M={'wood':bpy.data.materials['Warm timber / reference-derived family'],'floor':bpy.data.materials['Honey timber floor'],'wall':bpy.data.materials['Warm mineral plaster'],'stone':bpy.data.materials['Warm gray garden stone'],'green':bpy.data.materials['Garden leaves'],'sage':bpy.data.materials['Sage bedding'],'cream':bpy.data.materials['Ivory cloth'],'roof':bpy.data.materials['Gray clay roof'],'brass':bpy.data.materials['Muted brass'],'ceramic':bpy.data.materials['Ivory ceramic'],'glass':bpy.data.materials['Single continuous clear pane']}
M.update({'ink':mat('School ink timber',(.065,.065,.065)),'paper':mat('School paper plaster',(.71,.71,.71),noise=True),'gray':mat('School gray stone',(.36,.36,.36),noise=True),'inkleaf':mat('School ink vegetation',(.14,.14,.14)),'inkwater':mat('School monochrome water',(.27,.27,.27),.14,.35),'water':mat('Longzhou water',(.09,.28,.25),.17,.30),'apricot':mat('Dorm apricot cloth',(.57,.32,.22),.95),'cloud':mat('Cloud support proxy',(.78,.8,.79)),'parcel':mat('Same parcel neutral wrapper',(.60,.45,.27)),'proxy':mat('Scale only human clay',(.55,.40,.30))})
def box(n,loc,size,key='wood',bevel=.02,solid=True):
    x,y,z=[v/2 for v in size];v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    o=surf(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],key,solid);o.location=loc
    if bevel:
        q=o.modifiers.new('Edge softness','BEVEL');q.width=bevel;q.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def ell(n,loc,scale,key='green'):
    v=[(math.sin(math.pi*j/6)*math.cos(math.tau*i/12),math.sin(math.pi*j/6)*math.sin(math.tau*i/12),math.cos(math.pi*j/6)) for j in range(7) for i in range(12)]
    f=[(j*12+i,j*12+(i+1)%12,(j+1)*12+(i+1)%12,(j+1)*12+i) for j in range(6) for i in range(12)]
    o=surf(n,v,[tuple(reversed(q)) for q in f],key);o.location=loc;o.scale=scale
    for f in o.data.polygons:f.use_smooth=True
    return o
def rod(n,a,b,r=.05,key='wood'):
    a,b=Vector(a),Vector(b);d=b-a;v=[(r*math.cos(i*math.tau/10),r*math.sin(i*math.tau/10),z) for z in [-d.length/2,d.length/2] for i in range(10)];f=[tuple(reversed(range(10))),tuple(range(10,20))]+[(i,(i+1)%10,(i+1)%10+10,i+10) for i in range(10)]
    o=surf(n,v,f,key);o.location=(a+b)/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def surf(n,v,f,key,solid=True):
    d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);G.objects.link(o);o.data.materials.append(M[key]);o['physical']=solid;return o
def slab(n,x1,y1,x2,y2,z,key='stone',th=.18):return box(n,((x1+x2)/2,(y1+y2)/2,z-th/2),(x2-x1,y2-y1,th),key,0)
def roof(n,x1,y1,x2,y2,z,key='roof'):
    mid=(y1+y2)/2;rise=min(1.35,(y2-y1)*.22)
    v=[(x1,y1,z),(x2,y1,z),(x1,mid,z+rise),(x2,mid,z+rise),(x1,y2,z),(x2,y2,z)]
    o=surf(n,v,[(0,1,3,2),(2,3,5,4)],key);m=o.modifiers.new('Roof thickness','SOLIDIFY');m.thickness=.10
    rod(n+' ridge',(x1,mid,z+rise+.04),(x2,mid,z+rise+.04),.075,key)
    for i in range(max(2,int((x2-x1)/.65))):
        x=x1+(i+.5)*.65
        for y in [y1,y2]:rod(n+' tile seam',(x,y,z+.015),(x,mid,z+rise+.015),.025,key)
def table(n,x,y,z,w=2,d=.85,h=.76,key='wood'):
    box(n+' top',(x,y,z+h),(w,d,.09),key)
    for dx in [-w/2+.1,w/2-.1]:
        for dy in [-d/2+.1,d/2-.1]:box(n+' leg',(x+dx,y+dy,z+h/2),(.09,.09,h),key)
def bench(n,x,y,z,w=1.8,key='wood',back=1):
    table(n,x,y,z,w,.48,.43,key);box(n+' back',(x,y+back*.22,z+.69),(w,.07,.5),key)
def tree(n,x,y,z,h=3,key='green',trunk='wood'):
    rod(n+' trunk',(x,y,z),(x,y,z+h*.85),.085,trunk)
    for k in range(6):
        aa=k*2.4;tip=(x+math.cos(aa)*h*.30,y+math.sin(aa)*h*.30,z+h*(.65+.05*(k%3)))
        rod(n+' branch',(x,y,z+h*.5),tip,.035,trunk)
        ell(n+' canopy',tip,(h*.28,h*.25,h*.19),key)
def railing(n,a,b,key='wood',gaps=()):
    a,b=Vector(a),Vector(b);d=b-a;length=d.length
    rod(n+' handrail',a+Vector((0,0,1)),b+Vector((0,0,1)),.055,key)
    for i in range(math.ceil(length/.9)+1):
        q=a+d*i/math.ceil(length/.9);rod(n+' post',q,q+Vector((0,0,1)),.045,key)
def road(n,pts,width=2.4,key='stone',rails=False):
    for i,(aa,bb) in enumerate(zip(pts,pts[1:])):
        aa,bb=Vector(aa),Vector(bb);d=bb-aa;side=Vector((-d.y,d.x,0)).normalized()*width/2
        vs=[aa+side,aa-side,bb-side,bb+side];o=surf(n+f'_{i}',vs,[(0,1,2,3)],key);m=o.modifiers.new('Walkable deck thickness','SOLIDIFY');m.thickness=.18
        if rails:
            trim=1.8 if n=='Terraced long ramp' else 0
            if d.length>trim*2:
                for sign in [-1,1]:railing(n+f'_rail_{i}_{sign}',aa+side*sign+d.normalized()*trim,bb+side*sign-d.normalized()*trim,'ink' if key=='gray' else 'wood')
def room(n,x1,y1,x2,y2,z,h=3.4,key='wall',timber='wood',front_gap=None,window=False):
    slab(n+' floor',x1,y1,x2,y2,z,'floor' if timber=='wood' else 'gray')
    for x in [x1,x2]:box(n+' side wall',(x,(y1+y2)/2,z+h/2),(.16,y2-y1,h),key,0)
    box(n+' back wall',((x1+x2)/2,y2,z+h/2),(x2-x1,.16,h),key,0)
    if front_gap:
        left,right=front_gap
        if left>x1:box(n+' front left',((x1+left)/2,y1,z+h/2),(left-x1,.16,h),key,0)
        if right<x2:box(n+' front right',((x2+right)/2,y1,z+h/2),(x2-right,.16,h),key,0)
        box(n+' front lintel',((left+right)/2,y1,z+h-.25),(right-left,.16,.5),key,0)
    else:box(n+' front sill',((x1+x2)/2,y1,z+.42),(x2-x1,.16,.84),key,0)
    box(n+' ceiling',((x1+x2)/2,(y1+y2)/2,z+h+.05),(x2-x1,y2-y1,.10),key,0)
    for x in [x1+.12,x2-.12]:
        for y in [y1+.12,y2-.12]:box(n+' post',(x,y,z+h/2),(.17,.17,h),timber)
    for x in [x1+.2,(x1+x2)/2,x2-.2]:box(n+' beam',(x,(y1+y2)/2,z+h-.15),(.14,y2-y1,.22),timber)
    roof(n+' roof',x1-.35,y1-.35,x2+.35,y2+.35,z+h+.13,'ink' if timber=='ink' else 'roof')
def area(n,loc,target,power,size,color=(1,1,1)):
    d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);G.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False

# A/B/G home: extend the copied bedroom, never mutate its source file.
section('E01_HOME_EXTENSION')
old=bpy.data.objects.get('Garden facing wall')
if old:bpy.data.objects.remove(old,do_unlink=True)
box('Home north wall with real exit',(-.75,8.65,1.24),(5.1,.18,2.48),'wall',0) # x=-3.30..1.80
for x in [1.78,3.18]:box('Home garden gate jamb',(x,8.65,1.25),(.12,.22,2.5))
box('Home garden gate lintel',(2.48,8.65,2.42),(1.52,.22,.16))
slab('Bedroom door threshold',2.85,.55,3.4,1.3,0)
slab('Garden corridor landing',3.05,5.0,4.5,6.1,0)
slab('Home exit landing',1.7,8.4,4.9,10.7,0)
road('Garden exit path',[(2.4,5.7,0),(2.4,9.5,0)],1.05)
slab('East home connection',3.1,.5,6.1,2.4,0)
room('Living room',5.9,-2,11.9,3.8,0,front_gap=(7.4,9.4))
# west opening connects directly to existing corridor
for o in list(G.objects):
    if o.name=='Living room side wall':bpy.data.objects.remove(o,do_unlink=True)
box('Living west south',(5.9,-.65,1.7),(.16,2.7,3.4),'wall',0)
box('Living west north',(5.9,3.2,1.7),(.16,1.2,3.4),'wall',0)
box('Living west lintel',(5.9,1.7,3.1),(.16,1.8,.6),'wall',0)
for o in list(G.objects):
    if o.name=='Living room back wall':bpy.data.objects.remove(o,do_unlink=True)
box('Living north sill',(8.9,3.8,.48),(6,.16,.96),'wall',0)
box('Living north frame',(8.9,3.8,3.1),(6,.16,.6))
box('Living north glass',(8.9,3.8,1.95),(5.7,.015,1.95),'glass',0)
box('Living low couch',(9.8,.2,.36),(2.5,1.05,.5))
box('Living couch cushion',(9.8,.2,.66),(2.4,.96,.2),'sage',.07)
box('Living couch back',(9.8,-.26,.94),(2.5,.15,.75),'cream',.06)
table('Living tea table',8.5,1.65,0,1.3,.65,.48)
box('Call display placeholder',(8.5,1.72,.82),(.36,.04,.32),'sage')
box('Inactive simulation interface',(11.78,1.3,1.7),(.04,2.1,1.8),'stone')
for yy in [-.8,0,.8]:table('Living shelves',6.25,yy,0,.4,.6,1.7)
slab('East pocket court',5.9,3.9,11.9,8.8,0)
tree('Home pocket tree',10.8,6.2,0,2.8);bench('Home garden bench',6.7,7.6,0,1.5)
area('Living daylight',(9,4.2,2.6),(8.5,.6,.7),420,3,(1,.88,.72))
area('Living fill',(7,-1.3,2.8),(9,1,.8),150,2,(1,.84,.67))

section('E01_WATER_LANE')
slab('Home platform',-5,-4,13,11, -.10,'stone',2)
slab('Workshop platform',-6,16,13,29,-.10,'stone',2)
slab('Water lane basin',-22,10.8,17,16.2,-.8,'stone',.30)
box('Actual lane water',(-2.5,13.5,-.48),(39,5.4,.055),'water',0,False)
slab('South public lane',-22,8.9,17,10.8,0)
slab('North public lane',-22,16.2,17,18.6,0)
road('Home footbridge',[(8,9.5,0),(8,17.4,0)],2.0,rails=True)
# bank rails have intentional bridge and docking gaps
for y,spans in [(10.7,[(-22,6.9),(9.1,14.2)]),(16.3,[(-22,6.9),(9.1,9.5),(11.8,14.2)])]:
    for x1,x2 in spans:railing('Water bank rail',(x1,y,0),(x2,y,0))
for x in [-17,-11]:
    room('Lane home '+str(x),x-2,2,x+2,7,0,3.1,front_gap=(x-.6,x+.6))
    tree('Lane tree',x+2.4,8,0,2.5);bench('Lane bench',x,8,0,1.4)

# C/D/E/F: independent workshop across the lane, facade towards the home.
section('E01_WORKSHOP')
room('Workshop',-5,19,9.5,27,0,3.8,front_gap=(-3.6,8.1))
slab('Workshop covered porch',-5.4,17.8,9.9,19,0)
roof('Workshop porch roof',-5.5,17.5,10,19.1,3.1)
for x in [-5.1,9.6]:box('Porch column',(x,18,1.52),(.17,.17,3.04))
table('Repair island',.2,22.5,0,3.0,1.35,.83)
bench('Repair stool',.2,23.6,0,1.25)
box('Repair mat',(.2,22.5,.89),(1.8,.8,.025),'sage')
for x in [-.25,.25]:ell('Old shoe PLACEHOLDER', (x,22.5,.97),(.15,.28,.08),'cream')
for i in range(7):
    ang=math.pi*i/6
    if i:
        prev=(.2+math.cos(math.pi*(i-1)/6)*.55,22.65,.92+math.sin(math.pi*(i-1)/6)*.55)
        now=(.2+math.cos(ang)*.55,22.65,.92+math.sin(ang)*.55)
        rod('Inspection arch placeholder',prev,now,.035,'ceramic')
table('Intake desk',-3.5,20.5,0,1.9,.75,.78);bench('Visitor seat',-3.5,22.1,0,1.8)
for x in [-3.8,-1.9,0,1.9,3.8,5.7,7.6]:
    box('Material drawer cabinet',(x,26.5,.48),(1.65,.65,.96))
    for z in [1.1,1.85,2.6]:
        box('Material shelf',(x,26.55,z),(1.65,.6,.07))
        for j in range(3):box('Folded material',(x-.5+j*.45,26.5,z+.12),(.32,.36,.16),'cream' if j%2 else 'sage')
# 4.5 x 3.5m clear dry trial rectangle, not a dance stage.
slab('Dry trial floor',4,21,8.5,24.5,.012,'floor',.03)
bench('Trial changing bench',8.9,25.5,0,1.0)
box('Spare shoe storage',(8.9,20.2,.32),(.8,.6,.64))
slab('Dock recess',9.7,17.4,12.6,20,0)
table('Receiving perch',10.8,18.5,0,1.0,.65,1.0)
roof('Receiving dock canopy',9.7,17.4,12.6,20,3.1)
for x in [9.8,12.5]:box('Dock rear post',(x,19.8,1.52),(.12,.12,3.04))
area('Workshop front sky',(2,18,2.8),(2,23,1),1000,6,(1,.92,.83))
area('Workshop interior bounce',(1.5,24,3.3),(1.5,22,.5),250,4,(1,.9,.79))
for x in [-3.8,0,3.8,7.6]:area('Workshop shelf practical',(x,26.1,2.8),(x,26,.8),22,.8,(1,.73,.44))

# School uses monochrome exterior, warm personal interior. Terrain placement is a reversible staging hypothesis.
section('E01_SCHOOL_GROUND')
slab('School island',-57,35,-13,66,5.45,'gray',3.8)
slab('School south promenade',-55,42,-15,46,6,'gray')
slab('Dorm forecourt',-55,46,-44,62,6,'gray')
slab('Hall platform',-28,45,-14,63,6,'gray')
box('School upper water',(-36.5,54,5.66),(15,15,.05),'inkwater',0,False)
road('School low bridge',[(-45,47.5,6),(-27.5,47.5,6)],2.4,'gray',True)
road('School waterside north',[(-45,61,6),(-29,61,6),(-29,49.2,6)],2.4,'gray',True)
for x,y in [(-52,43),(-46,61),(-30,63),(-15,44)]:tree('School tree',x,y,6,3.2,'inkleaf','ink')
for x in [-53,-47,-41,-35,-29,-23]:
    box('Curve gallery post',(x,43,7.4),(.14,.14,2.8),'ink')
roof('School curve gallery',-55,42,-20,44.2,8.85,'ink')
# Distant ink forms are spatial placeholders, not definitive real mountain geography.
for i in range(10):
    x=-61+i*5.3;y=70+random.random()*5;h=random.uniform(8,18)
    bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=4.8,radius2=.5,depth=h,location=(x,y,6+h/2));o=group(bpy.context.object);o.name='Ink distant terrain PROXY';o.data.materials.append(M['gray']);o['physical']=False

section('E01_DORM')
room('An Qingyi dorm',-54,50,-46,58,6,3.4,'paper','ink',(-52.7,-47.3))
slab('Dorm covered exterior',-54.5,47.8,-45.5,50,6,'gray')
roof('Dorm veranda canopy',-54.5,47.6,-45.5,50.1,9.1,'ink')
table('Dorm wrapping table',-52,53.1,6,1.9,.80,.76)
bench('Dorm desk chair',-52,52,6,.65)
box('Parcel wrapping position',(-52,53.1,6.88),(.52,.34,.18),'parcel')
box('Dorm bed',(-47.5,55.7,6.33),(1.45,2.3,.5))
box('Dorm apricot quilt',(-47.5,55.7,6.64),(1.38,2.25,.18),'apricot',.08)
ell('Dorm pillow',(-47.5,56.4,6.85),(.55,.3,.15),'cream')
box('Dorm wardrobe',(-46.65,51.4,7.25),(.9,1.7,2.5))
# Colour simulation is an inactive enclosed reference surface, not a physical new garden.
box('Dorm personal simulation placeholder',(-50,57.87,7.85),(5,.03,2.3),'sage',0,False)
for x in [-52.9,-48.5]:table('Dorm shelf',x,57.3,6,1,.45,1.1)
area('Dorm warm light',(-50,54,9),(-50,54,6.5),300,3,(1,.79,.60))
# Working branch-like dock outside the rail line: hands approach from back, wings exit south.
slab('Dorm dispatch bay',-50.9,46.1,-48.9,48.5,6,'gray')
table('Dispatch perch',-49.9,46.65,6,1,.65,1.0,'ink')
for x1,x2 in [(-54.5,-51.0),(-48.8,-45.5)]:railing('Dorm balcony railing',(x1,47.8,6),(x2,47.8,6),'ink')

section('E01_DANCE_HALL')
room('Dance hall',-27,49,-15,61,6,4.4,'paper','ink',(-25.7,-16.3))
for o in list(G.objects):
    if o.name=='Dance hall side wall':bpy.data.objects.remove(o,do_unlink=True)
# West windows face actual water court, with a covered gallery in between.
box('Dance west sill',(-27,55,6.46),(.16,12,.92),'paper',0)
box('Dance west header',(-27,55,10.1),(.16,12,.6),'paper',0)
box('Dance west glazing',(-27,55,8.2),(.015,11.4,2.6),'glass',0)
for y in [50,54,58,60]:box('Dance west pier',(-27,y,8.2),(.16,.16,4.4),'ink')
slab('Dance covered waterside',-29,49,-27,61,6,'gray')
roof('Dance waterside gallery',-29.2,48.8,-26.8,61.2,9.3,'ink')
mirror=mat('Dance mirror',(.86,.86,.86),.025,1);M['mirror']=mirror
box('Dance east mirror',(-15.10,55,8.0),(.025,8.5,2.6),'mirror',0)
rod('Dance removable barre',(-15.7,51,7.05),(-15.7,59,7.05),.035,'ink')
for y in [51,55,59]:rod('Barre support',(-15.7,y,6),(-15.7,y,7.05),.035,'ink')
bench('Dance entry changing bench',-25,50.2,6,1.4,'ink')
table('Bags and water shelf',-17,50.3,6,1.2,.4,1,'ink')
# G proposal: small demonstration reuses the dry hall; no extra theatre.
slab('Demonstration clear floor',-24,53,-18,59,6.012,'gray',.025)
for x in [-23,-21,-19]:bench('Small demonstration audience',x,51.6,6,1.4,'ink',back=-1)
box('Backstage fold screen',(-25.5,52.4,7.0),(1.3,.08,2.0),'paper')
# Three surface interfaces reserved; default disabled, no claim of immersion implementation.
for name,loc,size in [('Simulation_WALL',(-21,60.86,8.2),(11.5,.025,4.1)),('Simulation_CEILING',(-21,55,10.33),(11.5,11.5,.025)),('Simulation_FLOOR',(-21,55,6.04),(11.5,11.5,.025))]:
    o=box(name,loc,size,'paper',0,False);o.hide_render=True;o.hide_set(True);o['status']='Reserved interface only; inactive; structural floor remains'
area('Dance neutral daylight',(-28,55,9),(-21,55,7),1200,7)
area('Dance interior bounce',(-21,55,10),(-21,55,6),350,5)

section('E01_CONNECTING_ROADS')
# Elevated path with approximately 1:10 to 1:12 straight gradients. Worldbuilding mechanism at boundary is not decided.
ramp=[(-20,39,6),(-18,39,6),(-8,39,5),(4,39,4),(14,39,3),(16,39,3),(16,37,3),(16,27,2),(16,15,1),(16,5,0),(16,3,0)]
road('School exit walk',[(-21,47.5,6),(-21,44.5,6),(-20,39,6)],2.6,'gray',False)
road('Terraced long ramp',ramp,3.0,'stone',True)
road('Town east return',[(16,3,0),(13,3,0),(13,9.5,0),(8,9.5,0)],2.4,'stone')
for x,y,z in ramp:
    if (x,y)==(16,39):slab('Ramp turning landing',x-1.5,y-1.5,x+1.5,y+1.5,z,'stone')
    if z>.3:box('Ramp stone pier',(x,y,(z-1)/2),(1.1,1.1,z+1),'stone',0)
slab('Ramp east garden base',12,0,20,42,-.2,'stone',2.3)
slab('Town stepped garden',-20,20,12,41,-.25,'stone',2.7)
# Everyday neighbourhood edge visible on the parcel journey, no unneeded interiors.
for x,y,z in [(-15,31,2),(-4,33,2.5),(6,31,1.5)]:
    slab('Neighbour terrace',x-3,y-3,x+3,y+3,z,'stone',z+1)
    room('Neighbour pavilion',x-2,y-1.8,x+2,y+1.8,z,2.5,front_gap=(x-.6,x+.6))
    tree('Neighbour tree',x+2.4,y+2,z,2.4)
# Cascade with explicit catchment; falls are geometry only, not fluid simulation.
for i,(y,z) in enumerate([(31,4.0),(28,2.5),(25,1.0)]):
    slab('Cascade support',-12,y-1.3,-6,y+1.3,z,'stone',z+1)
    box('Cascade water',(-9,y,z+.03),(5.7,2.3,.04),'water',0,False)
    endy,endz=(y-1.85,z-1.47) if i<2 else (23.5,.06)
    surf('Cascade fall',[(-11.4,y-1.32,z+.03),(-6.6,y-1.32,z+.03),(-6.6,endy,endz),(-11.4,endy,endz)],[(0,1,2,3)],'water',False)
slab('Cascade catch basin',-12,20.4,-6,24,0,'stone');box('Lower basin water',(-9,22.2,.04),(5.7,3.3,.04),'water',0,False)
road('Town garden walk',[(-18,18,0),(-20,18,0),(-20,32,0),(-19.2,32,0)],2.0)
road('Town east garden walk',[(13,18,0),(13,34,0)],2.0)
slab('East garden lookout',12.3,33.3,13.7,34.7,0)
slab('West garden lookout',-19.9,31.3,-18.5,32.7,0)
road('North quay connection',[(-18,18,0),(11,18,0)],2.3)
for x,y in [(-17,24),(-14,24),(10.8,29.5),(19,25),(19,35)]:tree('Town roadside tree',x,y,0,3)

section('E01_SUPPORT_CONTEXT')
for x,y,z,scale in [(-39,52,1,(22,16,2.5)),(1,11,-4,(17,19,2.6)),(-4,30,-4,(22,12,2.2)),(17,24,-3,(5,22,2))]:
    ell('Cloud support mass proxy',(x,y,z),scale,'cloud')['physical']=False

section('E01_LIGHTING')
next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(.75,.75,.75,1);next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.55
d=bpy.data.lights.new('Neutral morning sun','SUN');d.energy=2.0;d.angle=.10;o=bpy.data.objects.new('Neutral morning sun',d);G.objects.link(o);o.rotation_euler=(math.radians(32),math.radians(-28),math.radians(-20))

section('E01_CAMERAS');CAMS={}
specs=[
('E01-OV','第一集局部总览',(66,-61,83),(-15,30,2),42,'A-G'),
('E01-HOME','半园两岸与桥',(20,-4,17),(2,13,1),35,'C/F/G'),
('E01-LIVING','起居通话',(6.5,-1.2,1.65),(9.1,1.2,1.05),25,'B-G01'),
('E01-WORK','作坊入口看室内',(2,19.4,1.65),(2,24.2,1.25),23,'D/E/F'),
('E01-REVERSE','作坊望住家',(1.2,23.4,1.65),(2,10,1.1),30,'C/D/G'),
('E01-TRIAL','干燥试穿区',(2.6,20.1,1.65),(6.7,23.2,.8),28,'F'),
('E01-DOCK','作坊收件接口',(13.2,15.2,1.7),(10.8,18.5,1.1),30,'C-G06'),
('E01-SCHOOL','宿舍水庭与练功厅',(-52,47.0,8.0),(-34,60,7.0),28,'C-G02/G03'),
('E01-DORM','宿舍桌边',(-50,50.6,7.65),(-51,55,7.1),25,'B-G02/G05'),
('E01-SEND','宿舍寄件口',(-53.1,45.3,7.65),(-49.9,47.2,7.0),28,'B-G06/C-G01'),
('E01-DANCE','舞室日常母版方向',(-21,60,7.65),(-21,53,7.2),24,'G-G02'),
('E01-STAGE','小型展示与观众',(-21,49.8,7.65),(-21,56.5,7.2),24,'G-G03'),
('E01-ROAD','书院出入口与缓坡',(-18,33,9), (9,39,4.8),30,'C/G-G01'),
('E01-CASCADE','叠水与沿途园城',(-19,17,8),(-8,28,2.8),28,'C-G04'),
('E01-NIGHT','归家两岸灯光',(12,5,5),(2,17,1),28,'G-G05')]
for cid,title,pos,target,lens,shots in specs:
    d=bpy.data.cameras.new(cid);d.lens=lens;d.clip_start=.06;d.clip_end=500;o=bpy.data.objects.new(cid+'_'+title,d);G.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o['shot_groups']=shots;CAMS[cid]=o

# Route data is shared by geometry checking, plan and saved camera animation.
routes={
'home_to_work':{'kind':'walk','shots':['C-G05','G-G05'],'points':[(0,-.7,0),(1.9,-.3,0),(2.7,.8,0),(3.8,1.2,0),(3.6,3.2,0),(3.6,5.7,0),(2.4,5.7,0),(2.4,9.1,0),(8,9.1,0),(8,17.9,0),(2.2,17.9,0),(2.2,21,0)]},
'home_to_living':{'kind':'walk','shots':['B-G01'],'points':[(0,-.7,0),(1.9,-.3,0),(2.7,.8,0),(3.8,1.2,0),(5.1,1.6,0),(6.6,1.6,0),(7.2,.7,0)]},
'dorm_to_dispatch':{'kind':'walk','shots':['B-G05','B-G06'],'points':[(-50.5,53.1,6),(-50.5,51,6),(-49.9,49.0,6),(-49.9,47.4,6)]},
'dorm_to_hall':{'kind':'walk','shots':['G-G02'],'points':[(-49.9,49,6),(-49.9,47.35,6),(-48,47.3,6),(-45.5,47.5,6),(-40,47.5,6),(-28,47.5,6),(-21,47.5,6),(-21,50.2,6)]},
'school_to_work':{'kind':'walk','shots':['F-G01','G-G01'],'points':[(-21,50.2,6),(-21,47.5,6),(-21,44.5,6),*ramp,(13,3,0),(13,9.1,0),(8,9.1,0),(8,17.9,0),(2.2,17.9,0),(2.2,21,0)]},
'dock_to_repair':{'kind':'walk','shots':['C-G06','D-G01'],'points':[(11.7,18.5,0),(11.7,19.3,0),(10,19.3,0),(10,18.6,0),(2.2,18.6,0),(2.2,21,0),(.2,21.2,0)]},
'backstage_to_floor':{'kind':'walk','shots':['G-G02'],'points':[(-24.3,51.6,6),(-24.3,54,6.012),(-22,54,6.012)]},
'east_garden_walk':{'kind':'walk','shots':['C-G04'],'points':[(13,18,0),(13,34,0)]},
'neighbour_walk':{'kind':'walk','shots':['C-G04','G-G05'],'points':[(-18,18,0),(-20,18,0),(-20,32,0),(-19.2,32,0)]},
'trial_line':{'kind':'walk','shots':['F-G02','F-G05'],'points':[(6.2,21.5,.012),(6.2,24.0,.012)]},
'parcel':{'kind':'flight','shots':['C-G01','C-G06'],'points':[(-49.9,46.65,7.132),(-49.9,45.7,7.132),(-45,45.7,9),(-38,53,10.8),(-30,54,10.8),(-30,44,11),(-19,42,12),(-8,36,10),(14,30,8),(14,22,5),(14,14,3),(10.8,15.5,1.132),(10.8,18.5,1.132)]}}
# Logical audience/backstage layout stored, no new character design.
stage={'clear_rectangle':[-24,53,-18,59,6.012],'audience':[[-23,51.6,6],[-21,51.6,6],[-19,51.6,6]],'backstage':[-24.3,51.6,6],'status':'Proposed reuse of daily dance hall for small demonstration; not author-adopted venue or choreography proof'}
section('E01_FLIGHT_PROXY')
flightcol=G
carrier=bpy.data.objects.new('Same carrier ROOT placeholder',None);G.objects.link(carrier)
body=ell('Carrier body SCALE ONLY',(0,0,.22),(.35,.46,.18),'ceramic');body.parent=carrier
for sign in [-1,1]:
    o=ell('Folded wing SCALE ONLY',(sign*.38,0,.20),(.22,.36,.06),'sage');o.parent=carrier
box('Rigid cargo cradle',(0,0,-.05),(.62,.44,.07),'wood').parent=carrier
parcel=box('SAME_PARCEL', (0,0,.075),(.52,.34,.18),'parcel');parcel.parent=carrier
for x in [-.29,.29]:rod('Cargo restraint',(x,-.20,-.015),(x,.20,.18),.015,'brass').parent=carrier
points=[Vector(q) for q in routes['parcel']['points']];lengths=[(b-a).length for a,b in zip(points,points[1:])];total=sum(lengths)
def interpolate(t):
    s=t*total
    for i,ll in enumerate(lengths):
        if s<=ll:return points[i].lerp(points[i+1],s/ll),(points[i+1]-points[i]).normalized()
        s-=ll
    return points[-1],(points[-1]-points[-2]).normalized()
section('E01_CAMERAS_PATH')
cd=bpy.data.cameras.new('Parcel route technical camera');cd.lens=26;cd.clip_start=.05;cd.clip_end=500
fc=bpy.data.objects.new('PATH_parcel_technical',cd);G.objects.link(fc)
for frame in range(1,241):
    pos,heading=interpolate((frame-1)/239);carrier.location=pos;carrier.rotation_euler=(0,0,math.atan2(-heading.x,heading.y));carrier.keyframe_insert('location',frame=frame);carrier.keyframe_insert('rotation_euler',frame=frame)
    # Unreviewed technical following camera; its full animated framing is not accepted.
    fc.location=pos+Vector((-3,-4,2));fc.rotation_euler=(pos-fc.location).to_track_quat('-Z','Y').to_euler();fc.keyframe_insert('location',frame=frame);fc.keyframe_insert('rotation_euler',frame=frame)
S.frame_start=1;S.frame_end=240;S.render.fps=24;S.frame_set(1)
# Technical flight view layer is normally hidden in static space renders, not scene geometry.
for o in flightcol.objects:o.hide_render=True

refs=['视频制作/修复作坊室内-20261014-v0.1/修复作坊-室内全景01.png','视频制作/水墨学院宿舍-20261015-v0.2/山水书院-水墨世界与彩色宿舍02.png','视频制作/山水书院总景-20261015-v0.1/山水书院-宿舍水庭舞院总景01.png','视频制作/山水书院舞蹈室-20261015-v0.1/舞蹈室01-日常练功.png']
data={'version':'v0.1','status':'Episode spatial candidate; dimensions and school-city boundary provisional','bedroom_source':str(SOURCE.relative_to(ROOT)),'bedroom_source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'routes':routes,'stage':stage,'cameras':[{'id':v[0],'title':v[1],'position':v[2],'target':v[3],'lens_mm':v[4],'shot_groups':v[5]} for v in specs],'reference_images':[{'path':r,'sha256':hashlib.sha256((ROOT/r).read_bytes()).hexdigest()} for r in refs],'limits':['Exterior school palette and sky monochrome; dorm personal space warm','School-city ramp is reversible physical-continuity hypothesis, not a worldbuilding decision','Immersive interfaces reserved, not simulated','Water geometry not fluid or water-supply validation','Flight carrier and shoes are scale proxies, not adopted designs','Road and camera checks are discrete spatial tests, not gameplay or structural certification']}
(OUT/'episode-layout.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
notes=bpy.data.texts.new('EPISODE_SCOPE_README');notes.write(json.dumps(data,ensure_ascii=False,indent=2))
S.camera=CAMS['E01-OV'];S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True;S.cycles.max_bounces=5
cp=bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
for dev in cp.devices:dev.use=dev.type=='OPTIX'
S.cycles.device='GPU';S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'episode1-connected-sets-v01.blend'))
ids=list(CAMS) if a.render=='all' else ([] if a.render=='none' else a.render.split(','))
for cid in ids:
    S.camera=CAMS[cid]
    if cid=='E01-NIGHT':
        bpy.data.lights['Neutral morning sun'].energy=.08;next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.08
    S.render.filepath=str(OUT/(cid+'.png'));bpy.ops.render.render(write_still=True)
    if cid=='E01-NIGHT':
        bpy.data.lights['Neutral morning sun'].energy=2;next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.55
print('EPISODE_BUILD_OK',flush=True)
