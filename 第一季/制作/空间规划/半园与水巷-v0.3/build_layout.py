"""Spatial iteration v0.3. Inherits original v0.2 geometry, never edits its files.
Run: D:/blender/blender.exe -b --python build_layout.py
Meters; X east, Y north. Original procedural geometry, no external assets.
"""
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent / '半园与水巷-v0.2/build_layout.py'
source = BASE.read_text(encoding='utf-8').split('\ndef camera(')[0]
source = source.replace("'半园与水巷布局-20261014-v0.2'", "'半园与水巷布局-20261014-v0.3'")
exec(compile(source, str(BASE), 'exec'))

def remove_prefix(*prefixes):
    for o in list(S.objects):
        if any(o.name.startswith(p) for p in prefixes):
            if o in roofs: roofs.remove(o)
            if o in routes: routes.remove(o)
            bpy.data.objects.remove(o, do_unlink=True)

# Reduce the oversized reception, retain a planted buffer to the boundary.
remove_prefix('tea reception', 'tea table', 'tea bench', 'entry screen',
              'workshop west door', 'main worktable', 'north middle wall',
              'visitor', 'trial point', 'trial0', 'trial1', 'private point')
pavilion('compact tea porch',17.2,18.3,23.8,22.6)
box('tea table',(20.6,20.5,.72),(1.4,.75,1.44),'wood')
for y in [19.6,21.5]:box('tea bench',(20.6,y,.23),(1.8,.42,.46),'wood')
slab('east pocket planting',24.4,18.2,27.2,23,.04,'green')
tree(25.6,20.8,h=3.7)

# Short entry screen and a low planted return: turn before seeing the entire pond.
wallx('entry screen',8.9,11.9,20.5,h=1.85)
box('screen plinth',(10.4,20.5,.10),(3.2,.38,.2),'wood')
slab('entry tree bed',11.7,18.0,13.7,20.2,.04,'green')
tree(12.65,19.0,h=3.4)
wally('entry low return',13.7,18.0,19.8,h=.55)
box('entry seat',(12.6,17.8,.23),(2.3,.45,.46),'wood')
# A little projecting covered stopping point gives the eastern walk an offset.
pavilion('pond viewing bay',14.6,15.5,17.0,18.0)
for o in list(S.objects):
    if o.name.startswith('pond viewing bay floor'):o.location.z+=.018
    if o.name.startswith('pond viewing bay canopy'):o.location.z+=.10
    if o.name.startswith('compact tea porch canopy'):o.location.z+=.18
    if o.name.startswith('private gate approach canopy'):o.location.z+=.06
    if o.name.startswith('dry trial porch canopy'):o.location.z+=.05
    if o.name.startswith('tree crown') and abs(o.location.x-12.65)<.01:
        o.scale=(.90,.80,.95)
bpy.data.objects['near water edge'].location.y=26.94
bpy.data.objects['far water edge'].location.y=32.06

# West-facing workshop opens broadly to the garden. A solid sill below window,
# a full-height doorway, and a second slender side opening stay distinct.
wally('workshop west south pier',19,7,8.5,h=2.9)
wally('workshop west north pier',19,16.5,17.4,h=2.9)
box('workshop window sill',(19,10.7,.43),(.2,4.4,.86))
box('workshop west head',(19,12.5,2.7),(.2,8,.4))
for y in [8.5,12.9,15.2,16.5]:rod('workshop opening post',(19,y,0),(19,y,2.55),.065,'wood')
rod('workshop sill edge',(19,8.5,.89),(19,12.9,.89),.065,'wood')
# A real opening through the north wall offers a narrow view of the water lane.
wallx('north view lower',11.4,14.2,23.8,h=.72)
box('north view head',(12.8,23.8,1.82),(2.8,.16,.16))
for x in [11.45,14.15]:rod('north view jamb',(x,23.8,.72),(x,23.8,1.9),.055,'wood')

# Table with legs rather than an opaque block, plus anonymous repair props.
box('worktable top',(22,11.8,.82),(2.5,1.15,.12),'wood')
for x in [21,23]:
    for y in [11.4,12.2]:box('worktable leg',(x,y,.4),(.09,.09,.8),'wood')
box('repair mat',(21.8,11.8,.895),(1.0,.7,.03),'living')
for x in [21.55,21.95]:sphere('old object placeholder',(x,11.8,.97),(.12,.25,.075),'white')
box('tool tray',(22.85,11.8,.94),(.38,.5,.12),'work')
rod('task lamp stem',(22.8,12.15,.88),(22.8,12.15,1.5),.025,'wood')
box('task lamp shade',(22.65,12.15,1.5),(.5,.18,.06),'white')

# Garden layers and a narrow planted shelf soften the straight opposite bank.
for x,y,sz in [(10.2,15.5,.5),(10.0,14.8,.45),(14.4,9,.55),(15.1,9.6,.35)]:
    sphere('garden rock',(x,y,sz*.5),(sz,sz*.7,sz*.5),'bone')
slab('far bank planting shelf',11,33.1,16,34.4,.05,'green')
tree(15,34,h=3.5)
# Neighbor gaps are deliberately staggered, not a continuous parallel facade.
for o in list(S.objects):
    if o.name.startswith('neighbor B'):o.location.x+=3;o.location.y+=1

# New route lines remain a plan-only aid.
remove_prefix('visitor', 'trial', 'private0','private1','private2','private3','private4')
visitor=[(10.1,25.5,.12),(10.1,22,.12),(14.6,22,.12),(16,20.2,.12),(17.8,19,.12),(17.8,14.1,.12),(20,14.1,.12)]
trial=[(17.8,14.1,.12),(17.8,8,.12),(17.8,5.7,.12)]
private=[(10.1,22.2,.12),(8.2,22.2,.12),(8.2,19.3,.12),(8.2,16.2,.12),(8.2,12.8,.12),(6.5,12.8,.12)]
passer=[(-3.6,25.6,.12),(10.1,25.6,.12),(32,25.6,.12)]
path('visitor',visitor,'route');path('trial',trial,'route');path('private',private,'private');path('passer',passer,'green')
slab('trial clear inset',14,2.5,18.5,6,.04,'path',.015)
for o in routes:o.hide_render=True

def camera(n,loc,target,lens=27,ortho=None):
    d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);S.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.lens=lens;d.clip_start=.08;d.clip_end=300
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    return o
C={
 '01_lane':camera('01 Lane to gate',(17.5,33,1.65),(10.4,23.7,1.45),30),
 '02_entry':camera('02 Turn into garden',(14.6,21.5,1.65),(12.7,11.2,1.25),24),
 '03_workshop':camera('03 Workshop to garden',(23.8,10.5,1.65),(12,18.5,1.0),26),
 '04_overview':camera('04 Overall',(49,60,50),(13,18,0),ortho=59),
 '05_plan':camera('05 Plan',(14,17,80),(14,17,0),ortho=61),
}
C['05_plan'].rotation_euler=(0,0,0)
S.render.resolution_x=1600;S.render.resolution_y=1000
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True
S.cycles.device='CPU'
S.view_settings.view_transform='AgX'
S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.82,1,1)
S.world.node_tree.nodes['Background'].inputs[1].default_value=.65
for m in M.values():
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=m.diffuse_color
    bs.inputs['Roughness'].default_value=.75
M['water'].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.24
bpy.ops.object.light_add(type='SUN',location=(0,0,20))
sun=bpy.context.object;sun.name='Study sunlight';sun.data.energy=2.1
sun.data.angle=math.radians(12);sun.rotation_euler=(Vector((14,14,0))-Vector((-8,32,25))).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(23,12,2.75))
fill=bpy.context.object;fill.name='Workshop ceiling bounce study';fill.data.energy=450;fill.data.shape='DISK';fill.data.size=4
# Beveled edges help explain form; this is still a blockout, not final material art.
for o in list(S.objects):
    if o.type=='MESH' and len(o.data.polygons)==6:
        bevel=o.modifiers.new('small edge softening','BEVEL');bevel.width=.035;bevel.segments=2
camera_data={}
for name,cam in C.items():
    S.camera=cam
    plan=name=='05_plan'
    for o in roofs:o.hide_render=plan
    for o in routes:o.hide_render=not plan
    if plan:
        S.render.engine='BLENDER_WORKBENCH';S.view_settings.view_transform='Standard'
    else:
        S.render.engine='CYCLES';S.view_settings.view_transform='AgX'
    S.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    camera_data[name]={'position':list(cam.location),'rotation_euler':list(cam.rotation_euler),'lens_mm':cam.data.lens,'type':cam.data.type}
for o in roofs:o.hide_render=False
for o in routes:o.hide_render=True
S.render.engine='CYCLES';S.view_settings.view_transform='AgX';S.camera=C['03_workshop']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=50
            area.spaces.active.region_3d.view_location=Vector((14,17,0))
            area.spaces.active.region_3d.view_rotation=C['04_overview'].rotation_euler.to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'banyuan-water-lane-v03.blend'))
(OUT/'layout-data.json').write_text(json.dumps({'status':'proposal, not adopted','units':'meters','site':[28,24],'cameras':camera_data,'visitor_route':visitor,'trial_route':trial,'private_route':private,'passer_route':passer,'objects':len(S.objects),'limitations':['No collision simulation','No drainage or accessibility engineering','No final art','North wall view is a real aperture, not holography']},ensure_ascii=False,indent=2),encoding='utf-8')
print('V03_DONE',OUT,len(S.objects))
