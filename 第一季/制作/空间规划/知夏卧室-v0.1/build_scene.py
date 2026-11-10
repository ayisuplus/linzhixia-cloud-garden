"""Editable spatial study. Run Blender -b -t 12 --python this.py -- --root PROJECT.
All dimensions are working hypotheses. No generated/reference image is used as geometry.
"""
import argparse, sys, math, json, random, hashlib
from pathlib import Path
import bpy
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

p = argparse.ArgumentParser()
p.add_argument('--root', required=True)
p.add_argument('--render', default='all', help='all, none, or comma-separated camera IDs')
p.add_argument('--gpu', action='store_true', help='Use verified idle NVIDIA GPU via OptiX')
args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT = Path(args.root).resolve()
OUT = ROOT / '视频制作/知夏卧室三维空间-20261022-v0.1'
OUT.mkdir(parents=True, exist_ok=True)
random.seed(22)
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.unit_settings.system = 'METRIC'; S.unit_settings.scale_length = 1
S.render.engine = 'CYCLES'; S.cycles.device = 'CPU'; S.cycles.samples = 24
if args.gpu:
    cp=bpy.context.preferences.addons['cycles'].preferences;cp.compute_device_type='OPTIX';cp.get_devices()
    for dev in cp.devices:dev.use=dev.type=='OPTIX'
    if not any(d.use for d in cp.devices):raise RuntimeError('No OptiX GPU available')
    S.cycles.device='GPU';S.cycles.samples=40
S.cycles.use_denoising = True; S.cycles.max_bounces = 6
S.render.threads_mode = 'FIXED'; S.render.threads = 12
S.render.resolution_x = 1120; S.render.resolution_y = 630; S.render.resolution_percentage = 100
S.render.image_settings.file_format = 'PNG'
S.view_settings.view_transform = 'AgX'
S.world = bpy.data.worlds.new('Morning sky'); S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.68,.79,1,1)
S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
COL={}
for name in ['01_Architecture','02_Bed','03_Cabinet','04_Desk','05_Curtains','06_Corridor','07_Garden','08_Props','09_Lighting','10_Cameras','11_Reference']:
    c=bpy.data.collections.new(name); S.collection.children.link(c); COL[name]=c
GROUP='01_Architecture'
def group(o):
    for c in list(o.users_collection):c.objects.unlink(o)
    COL[GROUP].objects.link(o)
    return o
def mat(name,c,rough=.6,noise=False,scale=(1,1,1)):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1);m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=rough
    if noise:
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=4;tex.inputs['Detail'].default_value=2
        co=n.new('ShaderNodeTexCoord');mp=n.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=scale
        l.new(co.outputs['Generated'],mp.inputs[0]);l.new(mp.outputs[0],tex.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(v*.65 for v in c),1);ramp.color_ramp.elements[1].color=(*(min(v*1.2,1) for v in c),1)
        l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.025
        l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    return m
M={
'wood':mat('Warm timber / reference-derived family',(.29,.145,.065),.42,True,(2,2,20)),
'floor':mat('Honey timber floor',(.37,.215,.11),.5,True,(1,22,2)),
'wall':mat('Warm mineral plaster',(.72,.66,.53),.85,True),
'cream':mat('Ivory cloth',(.78,.73,.61),.9,True,(20,20,20)),
'sage':mat('Sage bedding',(.30,.39,.27),.92,True,(25,25,25)),
'curtain':mat('Oatmeal blackout cloth',(.55,.46,.34),.95,True,(20,20,25)),
'stone':mat('Warm gray garden stone',(.43,.44,.38),.85,True),
'roof':mat('Gray clay roof',(.19,.22,.21),.85),
'leaf':mat('Garden leaves',(.17,.31,.075),.9),
'leaflight':mat('Sunlit green leaf',(.32,.43,.12),.88),
'soil':mat('Soil',(.13,.09,.045),1),
'brass':mat('Muted brass',(.47,.31,.105),.3),
'ceramic':mat('Ivory ceramic',(.76,.74,.65),.3),
'dark':mat('Clock face markings',(.08,.07,.045),.65),
'rug':mat('Woven natural rug',(.46,.35,.20),.95,True,(28,28,2))}
M['glass']=mat('Single continuous clear pane',(.95,.98,1),.04)
bs=M['glass'].node_tree.nodes.get('Principled BSDF');bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.45
def box(n,loc,size,key='wood',bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=group(bpy.context.object);o.name=n;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(M[key])
    if bevel:
        mod=o.modifiers.new('Soft physical edges','BEVEL');mod.width=bevel;mod.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def ell(n,loc,scale,key):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);o=group(bpy.context.object);o.name=n;o.scale=scale;o.data.materials.append(M[key])
    for f in o.data.polygons:f.use_smooth=True
    return o
def rod(n,a,b,r,key='wood',vertices=12):
    a,b=Vector(a),Vector(b);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2)
    o=group(bpy.context.object);o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(M[key]);return o
def mesh(n,v,f,key):
    me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);COL[GROUP].objects.link(o);o.data.materials.append(M[key]);return o
def pot(x,y,z,r=.16):
    ell('Ceramic planter',(x,y,z+r*.7),(r,r,r*.8),'ceramic')
    for k in range(9):
        a=random.random()*math.tau;h=random.uniform(.20,.48)
        tip=(x+math.cos(a)*r*1.5,y+math.sin(a)*r*1.5,z+r+h)
        rod('Plant stem',(x,y,z+r),tip,.009,'leaf')
        leaf=ell('Leaf',tip,(.095,.045,.018),'leaflight');leaf.rotation_euler=(random.random(),.3,a)
def table(n,x,y,w,d,h):
    box(n+' top',(x,y,h),(w,d,.08))
    for dx in [-w/2+.07,w/2-.07]:
        for dy in [-d/2+.07,d/2-.07]:box(n+' leg',(x+dx,y+dy,h/2),(.07,.07,h))

# Room 6.0 x 5.4 m, north window faces real garden. Full envelope kept in every camera.
for i in range(24):
    x=-3+(i+.5)*.25
    for j in range(5):box('Floor plank',(x,-3+(j+.5)*1.08,-.045),(.246,1.075,.09),'floor',.003)
box('West wall',(-3.10,-.3,1.65),(.2,5.8,3.3),'wall')
box('South wall',(0,-3.1,1.65),(6.4,.2,3.3),'wall')
box('East wall south of corridor',(3.1,-1.35,1.65),(.2,3.3,3.3),'wall')
box('East corridor lintel',(3.1,1.35,3.03),(.2,2.1,.54),'wall')
box('North wall sill',(0,2.5,.43),(6.4,.2,.86),'wall')
box('North wall left pier',(-2.4,2.5,1.83),(1.6,.2,1.94),'wall')
box('North wall right pier',(2.36,2.5,1.83),(1.68,.2,1.94),'wall')
box('North wall header',(0,2.5,3.07),(6.4,.2,.46),'wall')
box('Ceiling - never hidden',(0,-.3,3.36),(6.4,5.8,.12),'wall')
for x in [-2.8,0,2.8]:box('Ceiling beam',(x,-.3,3.18),(.15,5.6,.21))
for x in [-1.63,1.63]:box('Window outer jamb',(x,2.35,1.84),(.12,.21,2.03))
for z in [.86,2.83]:box('Window outer rail',(0,2.35,z),(3.38,.21,.12))
box('Window original sill',(0,2.27,.84),(3.48,.46,.10))
glass=box('WINDOW_single_continuous_glass',(0,2.43,1.845),(3.14,.012,1.85),'glass',0)
glass['invariant']='No inner mullions; original sill and solid lower wall retained'
for z in [.13,3.03]:box('West timber skirting',(-2.98,-.3,z),(.09,5.4,.13))

GROUP='02_Bed'
box('Bed frame',(-1.62,-.78,.34),(1.76,2.36,.25))
box('Bed mattress',(-1.62,-.78,.55),(1.70,2.28,.24),'cream',.09)
box('Headboard',(-1.62,.43,.83),(1.84,.12,1.10))
for x in [-2.35,-.89]:
    for y in [-1.80,.20]:box('Bed foot',(x,y,.16),(.12,.12,.32))
for x in [-2.03,-1.22]:ell('Pillow',(x,.05,.76),(.39,.27,.13),'cream')
# Actual surface quilt, with gently irregular edge; no reference image pasted on a plane.
v=[];f=[];nx=26;ny=34
for j in range(ny):
    y=-2.00+j*2.0/(ny-1)
    for i in range(nx):
        x=-2.59+i*1.94/(nx-1);edge=max(0,abs(x+1.62)-.77)
        z=.72-.8*edge+.028*math.sin(i*1.7+j*.7)+.025*math.sin(j*1.6)
        v.append((x,y,z))
for j in range(ny-1):
    for i in range(nx-1):a=j*nx+i;f.append((a,a+1,a+nx+1,a+nx))
q=mesh('Sage quilt spatial proxy',v,f,'sage');sol=q.modifiers.new('Cloth thickness','SOLIDIFY');sol.thickness=.018
for poly in q.data.polygons:poly.use_smooth=True
box('Bedside rug',(-.15,-1.1,.014),(1.15,2.5,.025),'rug',.015)
# Headboard belongs against the left wall, not between bed and wardrobe/window.
bed_transform=Matrix.Translation((-1.62,-.78,0)) @ Matrix.Rotation(math.pi/2,4,'Z') @ Matrix.Translation((1.62,.78,0))
for obj in list(COL['02_Bed'].objects):
    if obj.name!='Bedside rug':obj.matrix_world=bed_transform @ obj.matrix_world
table('Bedside table',-2.55,.82,.65,.62,.60)
rod('Bedside lamp foot',(-2.55,.88,.65),(-2.55,.88,.82),.065,'brass')
ell('Round bedside lamp',(-2.55,.88,1.00),(.17,.13,.18),'ceramic')
# Ordinary clock, no obsolete wall-mounted mechanical fist.
clock=rod('Round alarm clock',(-2.20,.57,.78),(-2.20,.66,.78),.105,'brass',32)
rod('Clock ivory dial',(-2.20,.565,.78),(-2.20,.558,.78),.091,'cream',32)
rod('Clock hand',(-2.20,.55,.78),(-2.20,.55,.845),.006,'dark')

GROUP='03_Cabinet'
box('Wardrobe back',(-2.38,2.24,1.42),(1.04,.10,2.78))
for x in [-2.92,-1.84]:box('Wardrobe side',(x,1.88,1.42),(.08,.8,2.78))
for z in [.10,1.95,2.80]:box('Wardrobe shelf',(-2.38,1.88,z),(1.1,.8,.08))
for x in [-2.67,-2.13]:
    door=box('Wardrobe door CLOSED proxy',(x,1.45,1.43),(.51,.07,2.67))
    box('Wardrobe recessed panel',(x,1.40,1.48),(.40,.022,2.20),'wood',.005)
    rod('Wardrobe handle',(x+(.15 if x<-2.4 else -.15),1.37,1.2),(x+(.15 if x<-2.4 else -.15),1.37,1.42),.013,'brass')
rod('Fixed vertical shaft',(-2.40,1.85,1.7),(-2.40,1.85,2.62),.025,'brass')
rod('Rigid swing arm STOWED',(-2.40,1.85,2.45),(-2.20,1.85,2.45),.025)
rod('Direct hanger connector',(-2.20,1.85,2.45),(-2.20,1.85,2.27),.018,'brass')
rod('Hanger left shoulder',(-2.20,1.85,2.27),(-2.41,1.85,2.14),.018)
rod('Hanger right shoulder',(-2.20,1.85,2.27),(-1.99,1.85,2.14),.018)
# Narrow the complete cabinet assembly about its center; clear curtain AND west wall.
cabinet_transform=Matrix.Translation((-2.4,0,0)) @ Matrix.Diagonal((.9,1,1,1)) @ Matrix.Translation((2.4,0,0))
for obj in COL['03_Cabinet'].objects:obj.matrix_world=cabinet_transform @ obj.matrix_world

GROUP='04_Desk'
table('Writing desk',1.65,1.67,1.55,.68,.77)
box('Desk drawer',(1.65,1.67,.64),(1.38,.57,.19))
table('Chair',1.60,.90,.47,.47,.43)
box('Chair cushion',(1.60,.90,.48),(.44,.44,.08),'sage',.045)
box('Chair back',(1.60,.64,.75),(.48,.08,.61))
for z in [1.45,2.16]:box('Plant wall shelf',(2.55,2.25,z),(.70,.28,.065))
pot(2.5,2.20,2.20,.13);pot(2.5,2.18,1.49,.11);pot(1.88,1.67,.82,.13)
tablet=box('Calendar spatial placeholder',(1.40,1.78,1.01),(.40,.05,.35),'sage');tablet.rotation_euler[0]=math.radians(-12)
for k in range(4):box('Desk books',(1.1,1.60,.84+k*.032),(.24,.18,.025),'cream')
table('Low window book bench',-.25,2.03,1.15,.35,.46)
for k in range(9):box('Book under bench',(-.70+k*.11,2.03,.24),(.07,.23,.32),['cream','sage','wood'][k%3],.004)

GROUP='05_Curtains'
for y in [2.10,2.19]:rod('Hidden double curtain rail',(-1.94,y,2.94),(1.94,y,2.94),.018,'brass')
def curtain(n,side,y,width,key):
    verts=[];faces=[];count=40
    for z in [.77,2.9]:
        for i in range(count):
            x=side*(1.65+width*i/(count-1));verts.append((x,y+.048*math.sin(i*math.pi/2),z))
    for i in range(count-1):faces.append((i,i+1,count+i+1,count+i))
    o=mesh(n,verts,faces,key);sol=o.modifiers.new('Cloth thickness','SOLIDIFY');sol.thickness=.008
for side in [-1,1]:
    curtain('Blackout curtain OPEN',side,2.08,.13,'curtain')
    curtain('Ivory sheer OPEN',side,2.18,.10,'cream')

GROUP='06_Corridor'
box('Corridor floor',(3.94,1.15,-.055),(1.68,8.3,.11),'stone')
box('Corridor outer south wall',(4.88,-1.38,1.58),(.16,3.25,3.16),'wall')
box('Corridor roof',(3.95,1.15,3.25),(2.1,8.65,.14))
for y in [-2.8,-1.6,-.4,.8,2,3.2,4.4,5.2]:box('Corridor roof rafter',(3.95,y,3.08),(2.0,.10,.14))
for y in [.38,2.40,5.05]:box('Corridor timber post',(4.65,y,1.5),(.14,.14,3))
for y in [.34,2.36]:box('Doorway jamb',(3.03,y,1.42),(.18,.12,2.84))
box('Doorway upper frame',(3.03,1.35,2.81),(.18,2.15,.13))
# Open lattice door folded to the south reveal; not a replacement window mullion.
for x in [3.13,3.77]:box('Lattice door outer stile',(x,.36,1.40),(.065,.07,2.72))
for z in [.08,.75,2.15,2.72]:box('Lattice door rail',(3.45,.36,z),(.70,.07,.065))
for x in [3.25,3.38,3.51,3.64]:box('Lattice door vertical',(x,.36,1.48),(.025,.04,1.35))
for z in [.9,1.15,1.40,1.65,1.90,2.1]:box('Lattice door horizontal',(3.45,.36,z),(.65,.04,.025))
rod('Hidden roller shade RAISED',(3.20,.42,2.83),(3.20,2.28,2.83),.065,'curtain')
pot(4.3,3.4,.05,.23)

GROUP='07_Garden'
box('Garden ground',(0,5.75,-.12),(6.2,6.3,.20),'soil')
box('Garden facing wall',(0,8.65,1.24),(6.6,.18,2.48),'wall')
box('Garden west boundary wall',(-3.15,5.55,1.25),(.16,6.2,2.5),'wall')
box('Garden east wall beyond corridor',(3.15,7.35,1.25),(.16,2.6,2.5),'wall')
# The covered corridor opens directly to the garden between y=2.6 and y=6.05.
for x in [-2.9,-.9,1.1,2.9]:box('Garden wall timber pier',(x,8.5,1.28),(.10,.12,2.55))
# Pitched tiled roof along borrowed-scene wall; thickness and two sides.
for sign in [-1,1]:
    roof=box('Garden roof slope',(0,8.68+sign*.49,2.75),(6.85,1.08,.09),'roof');roof.rotation_euler[0]=sign*math.radians(-22)
    for k in range(40):
        x=-3.36+k*.172
        rod('Clay roof ridge',(x,8.68,2.98),(x,8.68+sign*1.0,2.58),.047,'roof',8)
rod('Ridge cap',(-3.46,8.68,3.01),(3.46,8.68,3.01),.09,'roof')
for j in range(9):box('Garden stepping stone',(2.26,3.0+j*.61,.025),(.78,.48,.09),'stone',.07)
for j in range(5):box('Cross path stone',(2.4-j*.76,6.65,.03),(.64,.58,.10),'stone',.07)
for k in range(15):
    x=random.uniform(-2.9,1.5);y=random.uniform(3.3,8.0)
    ell('Garden shrub',(x,y,.25),(random.uniform(.25,.45),.32,.32),'leaf')
def tree(x,y):
    rod('Garden tree trunk',(x,y,0),(x+.15,y,2.65),.10)
    for i in range(12):
        a=i*2.4;tip=(x+math.cos(a)*random.uniform(.55,1.25),y+math.sin(a)*random.uniform(.5,1.1),random.uniform(2.2,3.6))
        rod('Garden branch',(x+.07,y,1.45+random.random()*.8),tip,.028)
        for j in range(40):
            pt=(tip[0]+random.uniform(-.4,.4),tip[1]+random.uniform(-.4,.4),tip[2]+random.uniform(-.17,.17))
            o=ell('Tree foliage',pt,(.13,.065,.025),'leaflight' if j%3 else 'leaf');o.rotation_euler=(random.random(),random.random(),random.random()*6)
tree(-.7,4.70);tree(-2.2,7.0)
for x,y,s in [(-1.1,6.6,.5),(.7,7.4,.3),(-2.6,3.5,.25)]:ell('Garden stone',(x,y,.15),(s,s*.6,s*.5),'stone')

GROUP='08_Props'
for x in [-.40,-.05]:
    ell('Slipper spatial proxy',(x,-1.50,.065),(.13,.26,.055),'cream')
    ell('Slipper upper',(x,-1.40,.12),(.12,.14,.07),'sage')
pot(-2.85,-2.6,.1,.16)

GROUP='09_Lighting'
def light(n,loc,power,color,size,target):
    d=bpy.data.lights.new(n,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(n,d);COL[GROUP].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False
light('Window sky',(0,3.1,2.7),500,(1,.85,.65),3,(0,-.5,.5))
light('Corridor sky',(4.4,3.6,2.4),220,(1,.9,.75),2,(1,1,1))
light('Soft photographic bounce',(1,-2.5,2.6),100,(1,.8,.6),3,(-1,1,1))
d=bpy.data.lights.new('Morning sun','SUN');d.energy=2.1;d.angle=.07;o=bpy.data.objects.new('Morning sun',d);COL[GROUP].objects.link(o);o.rotation_euler=(math.radians(32),math.radians(-25),math.radians(-24))

GROUP='10_Cameras';CAM={}
specs=[
('C01','卧室全景',(.60,-2.80,1.60),(0,1.50,1.35),20,'E01-A-007-L / A011',(-1.62,-.78,.7)),
('C02','床侧关系',(-.15,-.75,1.32),(-2.35,-.70,.85),35,'E01-A-002..007',(-2.45,-.78,.8)),
('C03','贴地拖鞋',(.65,-2.40,.19),(-.20,-1.30,.16),32,'E01-A-008-PRE / A008',(-.40,-1.50,.11)),
('C04','衣柜与窗侧',(-.10,-.10,1.50),(-2.22,1.76,1.56),32,'E01-A-009',(-2.38,1.40,1.55)),
('C05','贴窗起点',(-1.30,2.20,1.24),(1.45,3.15,1.40),22,'E01-A-010-W',(-.6,2.43,1.28)),
('C06','通廊回望',(4.10,1.32,1.60),(-1.40,.03,1.10),26,'空间验证，不新增镜号',(-1.62,-.78,.7)),
('C07','庭院借景',(4.12,4.00,1.60),(-.50,5.9,1.55),30,'空间验证，不新增镜号',(-.7,4.7,1.5)),
('C08','贴窗终点',(-.30,2.20,1.24),(2.45,3.15,1.40),22,'E01-A-010-W', (.4,2.43,1.28))]
for id,title,pos,target,lens,shots,check in specs:
    d=bpy.data.cameras.new(id);d.lens=lens;d.clip_start=.04;d.clip_end=100
    o=bpy.data.objects.new(id+'_'+title,d);COL[GROUP].objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o['shot_ids']=shots;o['purpose']=title;CAM[id]=o
S.camera=CAM['C01'];S['status']='Spatial and camera candidate v0.1; inferred measurements; not final art or game validation'
S['references']='M-02 layout, M-08 continuous window, M-09 curtains; current atlas v2.1'
S['axes']='X east/right; Y north/window; Z up; metres'
# Camera path stored on dedicated camera, independent of still cameras.
pathcam=CAM['C05'].copy();pathcam.data=CAM['C05'].data.copy();COL[GROUP].objects.link(pathcam);pathcam.name='PATH_A010W_spatial_only'
for frame in range(1,146):
    x=-1.30+(frame-1)/144
    pathcam.location=(x,2.20,1.24);pathcam.keyframe_insert('location',frame=frame)
S.render.fps=24;S.frame_start=1;S.frame_end=145;S.frame_set(1)

# References packed into blend as hidden image empties for editable provenance.
GROUP='11_Reference'
refs=['视频制作/半园卧室试稿-v0.1/知夏卧室-清晨-候选02.png','视频制作/第一幕管家灯光与窗帘-20261018-v0.1/E01-A-007-L-02-双帘全开.png']
for k,rel in enumerate(refs):
    img=bpy.data.images.load(str(ROOT/rel));img.pack()
    o=bpy.data.objects.new('REFERENCE_ONLY_'+str(k),None);COL[GROUP].objects.link(o);o.empty_display_type='IMAGE';o.data=img;o.hide_render=True;o.hide_viewport=True;o['source']=rel

bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get();checks=[]
for id,title,pos,target,lens,shots,pt in specs:
    o=CAM[id];v=world_to_camera_view(S,o,Vector(pt));delta=Vector(pt)-o.location
    hit,loc,normal,idx,obj,matrix=S.ray_cast(deps,o.location,delta.normalized(),distance=delta.length+.03)
    checks.append({'camera':id,'title':title,'position_m':pos,'lens_mm':lens,'shot_ids':shots,'probe_target_m':pt,'probe_in_frame':0<=v.x<=1 and 0<=v.y<=1 and v.z>0,'first_ray_hit':obj.name if hit else None,'hit_distance_m':round((loc-o.location).length,3) if hit else None,'scope':'Single aim probe only; visual review still required; glass can be hit'})
path_hits=[]
for i in range(121):
    x=-1.3+i/120;pt=Vector((x,2.20,1.24))
    # Six-axis proximity probes only: not a conservative sphere or swept volume.
    for direction in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
        hit,loc,normal,idx,obj,matrix=S.ray_cast(deps,pt,Vector(direction),distance=.08)
        if hit:path_hits.append({'sample':i,'object':obj.name})
report={'scope':'Actual saved geometry; not continuous collision, full frustum, actor motion or game proof','room_inner_m':[6,5.4,3.3],'main_window_clear_m':[3.14,1.85],'window_sill_m':.84,'corridor_clear_width_m':1.45,'door_clear_width_m':1.90,'dimensions_status':'inferred design candidates, not image measurements','cameras':checks,'window_camera_path':{'samples':121,'probe_radius_m':.08,'six_axis_ray_hits':path_hits,'glass_plane_y':2.43,'path_y':2.02,'camera_to_glass_m':.41,'note':'Geometry path only; holographic wipe, speed ramp and frame continuity not validated'},'references':[{ 'path':r,'sha256':hashlib.sha256((ROOT/r).read_bytes()).hexdigest()} for r in refs], 'render_device':'CPU, 12 threads; existing GPU workload not altered'}
report['window_camera_path'].update(path_y=2.20,camera_to_glass_m=.23)
report['render_device']='OptiX GPU after idle ComfyUI queue verification' if args.gpu else 'CPU, 12 threads'
(OUT/'spatial-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
notes=bpy.data.texts.new('READ_ME_空间验证说明');notes.write(json.dumps(report,ensure_ascii=False,indent=2))
for a in bpy.context.screen.areas if bpy.context.screen else []:
    if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'zhixia-bedroom-v01.blend'))
render_ids=list(CAM) if args.render=='all' else ([] if args.render=='none' else args.render.split(','))
for id in render_ids:
    S.camera=CAM[id];S.render.filepath=str(OUT/(id+'.png'));bpy.ops.render.render(write_still=True)
print('ZHIXIA_SPATIAL_BUILD_OK',str(OUT),flush=True)
