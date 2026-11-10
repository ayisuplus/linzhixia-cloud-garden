"""Local Blender massing study; meters, X east, Y north, Z up.
Run D:/blender/blender.exe -b --python build_layout.py
Original geometry for this project. Study dimensions are proposals, not adopted.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / '视频制作' / '半园与水巷布局-20261014-v0.2'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
S.unit_settings.system = 'METRIC'
S.render.engine = 'BLENDER_WORKBENCH'
S.render.resolution_x = 1600
S.render.resolution_y = 1100
S.render.resolution_percentage = 100
S.render.image_settings.file_format = 'PNG'
S.render.film_transparent = False
S.world = bpy.data.worlds.new('World')
S.world.color = (.89, .91, .89)
S.view_settings.view_transform = 'Standard'
sh=S.display.shading
sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True
sh.show_cavity=True;sh.cavity_type='BOTH';sh.show_object_outline=True
sh.background_type='WORLD'

def mat(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);return m
M={
'plaster':mat('warm plaster',(.82,.79,.71)),
'roof':mat('gray roof mass',(.38,.43,.42)),
'floor':mat('courtyard floor',(.74,.73,.67)),
'path':mat('covered path',(.86,.82,.71)),
'work':mat('work zone ochre',(.77,.59,.36)),
'living':mat('living zone sage',(.57,.68,.60)),
'water':mat('water',(.40,.67,.71)),
'green':mat('vegetation',(.45,.59,.46)),
'wood':mat('wood',(.43,.34,.25)),
'cloud':mat('cloud material proxy',(.83,.87,.88)),
'bone':mat('load bearing cloud layer',(.62,.69,.70)),
'person':mat('scale figure coral',(.82,.37,.26)),
'route':mat('visitor route',(.87,.42,.20)),
'private':mat('private route',(.23,.49,.66)),
'white':mat('parcel',(.89,.88,.82)),
}
roofs=[];routes=[];blocks=[]
def box(n,loc,size,key='plaster',roof=False):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=n;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(M[key])
    if roof:roofs.append(o)
    return o
def sphere(n,loc,size,key='green'):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc)
    o=bpy.context.object;o.name=n;o.scale=size;o.data.materials.append(M[key]);return o
def rod(n,a,b,r,key):
    a,b=Vector(a),Vector(b);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(M[key]);return o
def mesh(n,v,f,key):
    d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update()
    o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.data.materials.append(M[key]);return o
def slab(n,x1,y1,x2,y2,z=0,key='floor',th=.14):
    if z==0 and key in ['living','work','path']: z=.025
    return box(n,((x1+x2)/2,(y1+y2)/2,z-th/2),(x2-x1,y2-y1,th),key)
def gable(n,x1,y1,x2,y2,z=3.2,rise=1):
    yc=(y1+y2)/2
    v=[(x1,y1,z),(x2,y1,z),(x1,y2,z),(x2,y2,z),(x1,yc,z+rise),(x2,yc,z+rise)]
    o=mesh(n,v,[(0,1,5,4),(2,4,5,3),(0,4,2),(1,3,5)],'roof');roofs.append(o)
def wallx(n,x1,x2,y,z=0,h=2.6):return box(n,((x1+x2)/2,y,z+h/2),(x2-x1,.16,h))
def wally(n,x,y1,y2,z=0,h=2.6):return box(n,(x,(y1+y2)/2,z+h/2),(.16,y2-y1,h))
def open_wall_y(n,x,y1,y2,g1,g2,h=2.8):
    wally(n+' lower',x,y1,g1,h=h);wally(n+' upper',x,g2,y2,h=h)
    box(n+' lintel',(x,(g1+g2)/2,2.55),(.16,g2-g1,.5))
def pavilion(n,x1,y1,x2,y2,z=0,key='path'):
    slab(n+' floor',x1,y1,x2,y2,z,key)
    for x in [x1+.2,x2-.2]:
        for y in [y1+.2,y2-.2]:rod(n+' post',(x,y,z),(x,y,z+2.8),.09,'wood')
    box(n+' canopy',((x1+x2)/2,(y1+y2)/2,z+2.85),(x2-x1+.4,y2-y1+.4,.13),'roof',roof=True)
def path(n,pts,key):
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        routes.append(rod(n+str(i),a,b,.075,key))
    for p in pts: routes.append(sphere(n+' point',p,(.12,.12,.05),key))
def person(x,y,z=0):
    # 1.6m anonymous figure, not a redesign of Zhixia.
    rod('scale body',(x,y,z+.65),(x,y,z+1.25),.16,'person')
    sphere('scale head',(x,y,z+1.45),(.15,.15,.15),'person')
    for dx in [-.11,.11]:rod('scale leg',(x+dx,y,z+.08),(x+dx,y,z+.7),.065,'person')
def tree(x,y,z=0,h=4):
    rod('tree trunk',(x,y,z),(x,y,z+h*.65),.15,'wood')
    sphere('tree crown',(x,y,z+h*.82),(1.4,1.2,h*.32),'green')

# Main datum: house, gate and near-bank walk all +0.00.
slab('cloud structural core',0,0,28,24,-.15,'bone',.65)
for i,rect in enumerate([(0,0,9.7,24),(15,0,28,24),(9.7,0,15,8.1),(9.7,16.3,15,24)]):
    slab('garden ground '+str(i),*rect,0)
# Floor patches around the non-rectangular pool opening.
for i,poly in enumerate([[(13.9,8.1),(15,8.1),(15,10.5)],[(15,10.5),(15,16.3),(11.1,16.3),(14.4,15.8)],[(9.7,14.2),(11.1,16.3),(9.7,16.3)]]):
    mesh('pool corner floor '+str(i),[(x,y,0) for x,y in poly],[tuple(range(len(poly)))],'floor')
for x,y,sx,sy in [(3,-.4,3,1.3),(10,-.6,4,1.5),(20,-.4,4,1.5),(27,2,2,3),(-.4,8,1.5,4)]:
    sphere('soft cloud edge',(x,y,-.55),(sx,sy,.6),'cloud')

# Northern water lane. The public ferry stop lies beyond the east end, not at the front door.
slab('near bank public path',-4,24,34,27,0,'path',.3)
slab('water channel',-4,27,34,32,-.45,'water',.15)
slab('far bank walk',-4,32,34,34.5,0,'path',.3)
box('near water edge',(15,26.9,-.2),(38,.20,.5),'plaster')
box('far water edge',(15,32.1,-.2),(38,.20,.5),'plaster')
# Modest bridge just outside western site boundary, at same pedestrian level.
slab('neighborhood bridge',-3,24,-.6,34.5,.02,'path',.25)
for x in [-2.95,-.65]:
    rod('bridge railing',(x,26,.95),(x,33,.95),.05,'wood')
    for y in [26,28,30,32,33]:rod('bridge rail post',(x,y,0),(x,y,.95),.04,'wood')
for a,b in [(-.4,14.2),(17.8,34)]:
    rod('bank rail',(a,26.82,.9),(b,26.82,.9),.045,'wood')
    for x in range(math.ceil(a),math.floor(b)+1,2):rod('bank rail post',(x,26.82,0),(x,26.82,.9),.035,'wood')
# Parcel recess is separated from the continuous 3m public walk; rail stays between it and canal.
slab('parcel recess',14.3,22.8,17.5,24,0,'work')
box('parcel counter',(16,23.65,.75),(1.8,.7,1.5),'wood')
box('parcel',(16,23.65,1.62),(.55,.4,.24),'white')
rod('parcel recess bank rail',(14.2,26.82,.9),(17.8,26.82,.9),.045,'wood')
wallx('parcel recess back',14.2,17.7,22.8,h=1.9)
wally('parcel recess west',14.2,22.8,23.8,h=1.9)
wally('parcel recess east',17.7,22.8,23.8,h=1.9)

# Boundary, north gate [8.8,11.4].
wallx('north west wall',0,8.8,23.8,h=1.9)
wallx('north middle wall',11.4,14.2,23.8,h=1.9)
wallx('north east wall',17.7,28,23.8,h=1.9)
wally('west boundary',0,0,24,h=1.9);wally('east boundary',28,0,24,h=1.9)
wallx('south boundary',0,28,0,h=1.2)
gable('gate canopy',8.3,23,11.9,24.5,2.7,.5)
wallx('entry screen',9.0,12.5,20.6,h=1.8)

# East public tea porch and workshop, all doors facing courtyard.
pavilion('tea reception',16,18,27,23)
box('tea table',(20.3,20.4,.65),(1.6,.8,1.3),'wood')
box('tea bench',(20.3,21.5,.4),(2,.45,.8),'wood')
slab('workshop floor',19,7,27,17.4,0,'work')
wally('workshop east',27,7,17.4,h=2.9)
wallx('workshop south',19,27,7,h=2.9)
wallx('workshop north',19,27,17.4,h=2.9)
open_wall_y('workshop west door',19,7,17.4,13.1,15.1,h=2.9)
gable('workshop roof',18.7,6.7,27.3,17.7,3.0,1.1)
box('main worktable',(22,13.8,.76),(2.4,1.15,1.52),'wood')
box('material cabinet',(26.25,11,1.05),(.8,5.7,2.1),'wood')
pavilion('east covered spine',16,7.5,18.7,18)
pavilion('dry trial porch',13.5,1.5,19,7.4,key='work')
# Clear inset footprint for 4.5 x 3.5m trial walking; no professional dance claim.
slab('trial clear area',14,2.5,18.5,6,.035,'path',.02)

# West private wing. Three rooms with separate doors to covered corridor.
slab('private wing floor',1,1.5,7,18,0,'living')
wally('private west',1,1.5,18,h=2.8)
wallx('private north',1,7,18,h=2.8);wallx('private south',1,7,1.5,h=2.8)
wallx('bed bath divider',1,7,7,h=2.8);wallx('bath living divider',1,7,10,h=2.8)
for label,y1,y2,d1,d2 in [('bedroom',1.5,7,4.2,5.5),('bath laundry',7,10,8.0,9.1),('living',10,18,12,13.8)]:
    open_wall_y(label+' door',7,y1,y2,d1,d2)
gable('private wing roof',.7,1.2,7.3,18.3,2.9,.9)
box('bed',(3.2,4.2,.35),(1.5,2.1,.7),'wood')
box('living bench',(2.1,13.5,.4),(1,3,.8),'wood')
box('bath proxy',(3.8,8.6,.4),(2,1.2,.8),'white')
pavilion('private covered corridor',7.2,1.5,9.2,19.5)
pavilion('private gate approach',7.2,19.5,9.2,22.9)
box('private inner gate leaf open',(7.35,17.85,1.0),(.12,1.5,2),'living')
slab('kitchen dining',9.2,1.5,13,6.2,0,'living')
wallx('kitchen south',9.2,13,1.5,h=2.8);wally('kitchen east',13,1.5,6.2,h=2.8)
wallx('kitchen north',9.2,13,6.2,h=2.8)
gable('kitchen roof',9,1.2,13.3,6.5,2.9,.7)
box('kitchen counter',(12.4,3.8,.85),(.6,3,1.7),'wood')
# A private courtyard access in west wing is represented by the corridor; kitchen west side open in study.

# Pool and foreground planting leave a generous east route.
pool=[(9.7,8.1),(13.9,8.1),(15,10.5),(14.4,15.8),(11.1,16.3),(9.7,14.2)]
mesh('garden pool',[(x,y,-.08) for x,y in pool],[tuple(range(len(pool)))],'water')
for a,b in zip(pool,pool[1:]+pool[:1]):rod('pool rim',(*a,.06),(*b,.06),.09,'plaster')
box('pool sitting bench',(11.3,17.35,.38),(3,.5,.76),'wood')
tree(11,7.1,h=3.5);tree(3.5,20.7,h=3.8)
slab('soil planting',20,1.6,26.5,5.8,.02,'green')
# Selective cloud-root plant proxy is speculative, not an adopted species model.
tree(25,3.7,h=4.2)
for x in [24.5,25,25.5]:rod('hanging root proxy',(x,3.7,-.1),(x+.1,3.4,-2),.035,'wood')

# Distant neighborhood offers elevation contrast without making daily rooms multi-level.
slab('far neighborhood terrace',-3,34.5,33,40,1.8,'floor',1.8)
for name,x1,x2,y1,y2,z in [('neighbor A',2,10,35,39,1.8),('neighbor B',18,25,35,39,1.8)]:
    box(name,((x1+x2)/2,(y1+y2)/2,z+1.4),(x2-x1,y2-y1,2.8))
    gable(name+' roof',x1-.3,y1-.3,x2+.3,y2+.3,z+2.8,.8)
tree(13,37,1.8,h=4)
person(10.1,22.5);person(20.5,12.5);person(5,25.5)
visitor=[(10.1,25.5,.10),(10.1,22,.10),(13.6,22,.10),(14.6,19,.10),(17,19,.10),(17,14.1,.10),(20.0,14.1,.10)]
trial=[(17,14.1,.11),(17,8,.11),(17,5.7,.11)]
private=[(10.1,22.2,.13),(8.2,22.2,.13),(8.2,19.3,.13),(8.2,16.2,.13),(8.2,12.8,.13),(6.5,12.8,.13)]
path('visitor',visitor,'route');path('trial',trial,'route');path('private',private,'private')
for o in routes:o.hide_render=True

def camera(n,loc,target,ortho=48):
    d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);S.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.type='ORTHO';d.ortho_scale=ortho;d.clip_end=300;return o
C={
'overview':camera('Overview',(54,65,53),(13,18,0),60),
'cutaway':camera('Cutaway',(43,54,61),(13,16,0),55),
'street':camera('Street',(35,37,17),(13,19,1),43),
'plan':camera('Plan',(14,17,80),(14,17,0),64),
}
# Top view north up.
C['plan'].rotation_euler=(0,0,0)
markers={
'overview':{'门外水巷':(12,29,0),'北侧园门':(10,23.7,2.6),'接待茶廊':(21,20.5,4),'修复工坊':(23,12,4),'西侧生活翼':(4,11,4),'池庭':(12.4,12,0),'干燥试用廊':(16,4,3.6),'邻里小桥':(-1.7,29,1)},
'cutaway':{'接待':(21,20,0),'修复台':(22,13.8,.8),'试穿留空':(16.2,4.2,0),'卧室':(3.8,4,0),'卫浴 / 洗衣':(3.8,8.5,0),'起居':(3.8,14,0),'厨房 / 餐位':(11,4,0),'可关闭内门':(8.2,18.6,2),'池庭':(12.5,12.5,0)},
'street':{'连续沿水步道':(10,25.4,0),'园门':(10,23.8,2.8),'收件凹位':(16,23.6,1.5),'通往巷口 / 公共画舫站':(31,25.5,0)},
'plan':{'01 园门':(10.1,23.7,0),'02 接待':(21,20.5,0),'03 修复工坊':(23,12,0),'04 试用廊':(16.1,4.2,0),'05 起居':(3.8,14,0),'06 卧室':(3.8,4,0),'07 卫浴':(3.8,8.5,0),'08 厨房':(11,4,0),'09 池庭':(12.2,12,0),'收件':(16,23.7,0),'水巷 · 约5m':(15,29.4,0)}
}
projected={}
for name in ['overview','cutaway','street','plan']:
    S.camera=C[name]
    cut=name in ['cutaway','plan']
    for o in roofs:o.hide_render=cut
    for o in routes:o.hide_render=not cut
    S.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    projected[name]={}
    for k,p in markers[name].items():
        uv=world_to_camera_view(S,S.camera,Vector(p))
        projected[name][k]=[round(uv.x*1600,1),round((1-uv.y)*1100,1)]
for o in roofs:o.hide_render=False
for o in routes:o.hide_render=True
S.camera=C['overview']
# Convenient native viewport on opening file.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=51
            area.spaces.active.region_3d.view_location=Vector((14,17,0))
            area.spaces.active.region_3d.view_rotation=C['overview'].rotation_euler.to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'banyuan-water-lane-v02.blend'))
(OUT/'label-projections.json').write_text(json.dumps(projected,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'layout-data.json').write_text(json.dumps({'units':'metres','status':'proposal','site':[28,24],'near_walk_width':3,'canal_width':5,'indoor_level':0,'water_level':-.45,'neighbor_terrace':1.8,'trial_clear':[4.5,3.5],'visitor_route':visitor,'trial_route':trial,'private_route':private,'objects':len(S.objects),'cameras':list(C)},ensure_ascii=False,indent=2),encoding='utf-8')
print('LAYOUT_DONE',OUT,len(S.objects))
