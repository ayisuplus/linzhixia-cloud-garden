"""Readable material/shape cues over the accepted v0.3 staging. No cloud generation."""
import bpy,math,random,json,sys,argparse,ast,hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--render',default='all');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root).resolve();SOURCE=ROOT/'视频制作/第一集浮空园城-20261022-v0.3/episode1-floating-garden-v03.blend';OUT=ROOT/'视频制作/第一集浮空园城-20261022-v0.4';OUT.mkdir(exist_ok=True,parents=True)
data=json.loads((SOURCE.parent/'route-layout.json').read_text(encoding='utf8'));bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene;random.seed(104)
helper=ROOT/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py';names={'section','group','box','ell','rod','surf','slab','roof','tree'}
exec(compile(ast.Module(body=[n for n in ast.parse(helper.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(helper),'exec'))
COL={};G=None
M={k:bpy.data.materials[v] for k,v in {'wood':'Warm timber / reference-derived family','wall':'Warm mineral plaster','stone':'Warm gray garden stone','green':'Garden leaves','roof':'Gray clay roof','ink':'School ink timber','paper':'School paper plaster','gray':'School gray stone','inkleaf':'School ink vegetation','water':'Longzhou water','inkwater':'School monochrome water','cloud':'V03 cloudhard','soft':'V03 cloudsoft'}.items()}
palette={k:list(next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value) for k,m in M.items()}
protected={o.name: {'matrix':[q for row in o.matrix_world for q in row],'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in S.objects if o.type=='MESH' and not any(c.name.startswith('V03_') for c in o.users_collection)}
def clone(key):
    m=M[key].copy();m.name='V04 '+key;M[key]=m;return m
def surface_texture(key,scale,dist,rough,stretch=(1,1,1),tile=False):
    m=clone(key);ns=m.node_tree.nodes;ls=m.node_tree.links;b=next(n for n in ns if n.type=='BSDF_PRINCIPLED');b.inputs['Roughness'].default_value=rough
    tex=ns.new('ShaderNodeTexCoord');mul=ns.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=stretch;ls.new(tex.outputs['Object'],mul.inputs[0])
    noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2;ls.new(mul.outputs[0],noise.inputs['Vector'])
    bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.35;bump.inputs['Distance'].default_value=dist;ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs[0],b.inputs['Normal'])
    if tile:
        wave=ns.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction='X';wave.inputs['Scale'].default_value=5;ls.new(mul.outputs[0],wave.inputs['Vector']);ls.new(wave.outputs['Fac'],bump.inputs['Height'])
    return m
for key,sc,dist,r,stretch,tile in [('wood',4,.025,.65,(1,1,14),False),('wall',2,.025,.92,(1,1,1),False),('paper',2,.025,.92,(1,1,1),False),('stone',5,.035,.87,(1,1,1),False),('gray',5,.035,.87,(1,1,1),False),('roof',3,.045,.74,(1,1,1),True),('ink',4,.02,.75,(1,1,1),False),('cloud',.12,.35,.97,(1,1,1),False)]:surface_texture(key,sc,dist,r,stretch,tile)
for key in ['water','inkwater']:
    surface_texture(key,1.6,.055,.14,(1,3,.3));b=next(n for n in M[key].node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Metallic'].default_value=0;b.inputs['Transmission Weight'].default_value=.32;b.inputs['IOR'].default_value=1.333
# Material swaps only on the new exterior layer: the original home/school interiors remain intact.
original_names={'wood':'Warm timber / reference-derived family','wall':'Warm mineral plaster','stone':'Warm gray garden stone','roof':'Gray clay roof','ink':'School ink timber','paper':'School paper plaster','gray':'School gray stone','water':'Longzhou water','inkwater':'School monochrome water','cloud':'V03 cloudhard'}
for o in S.objects:
    if o.type not in {'MESH','CURVE'} or not any(c.name.startswith('V03_') for c in o.users_collection):continue
    for slot in o.material_slots:
        for k,n in original_names.items():
            if slot.material and slot.material.name==n:slot.material=M[k];break
def simple(n,color,rough=.7):
    m=bpy.data.materials.new('V04 '+n);m.use_nodes=True;b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;m.diffuse_color=(*color,1);M[n]=m;return m
simple('window',(.12,.16,.15),.22);simple('inkwindow',(.12,.12,.12),.25);simple('foam',(.75,.82,.80),.38)

section('V04_ARCHITECTURAL_CUES')
# Restore a readable pitched roof silhouette and eave beams on new exterior buildings.
for o in list(S.objects):
    if o.type=='MESH' and any(c.name.startswith('V03_') for c in o.users_collection) and ('tile seam' in o.name or ' ridge' in o.name):o.hide_render=True
for o in list(S.objects):
    if o.type!='MESH' or len(o.data.vertices)!=6 or not any(c.name.startswith('V03_') for c in o.users_collection) or not any(m.type=='SOLIDIFY' for m in o.modifiers):continue
    if 'roof' not in o.name.lower() or 'coping' in o.name:continue
    vs=o.data.vertices;depth=abs(vs[4].co.y-vs[0].co.y);rise=min(4.5,depth*.22);base=vs[0].co.z
    vs[2].co.z=base+rise;vs[3].co.z=base+rise
    world=[o.matrix_world@v.co for v in vs];ink=bool(o.data.materials and 'ink' in o.data.materials[0].name.lower());key='ink' if ink else 'wood'
    for ia,ib in [(0,1),(4,5)]:rod('Readable timber eave',world[ia]-Vector((0,0,.16)),world[ib]-Vector((0,0,.16)),.12,key)
    rod('Roof ridge cap',world[2],world[3],.14,'ink' if ink else 'roof')
# Close triangular gables: an open black slot under a roof must not be read as a broken building.
gable_count=0
for o in list(S.objects):
    if o.type!='MESH' or len(o.data.vertices)!=6 or not any(c.name.startswith('V03_') for c in o.users_collection):continue
    if 'roof' not in o.name.lower() or not any(m.type=='SOLIDIFY' for m in o.modifiers):continue
    if any(t in o.name for t in ['pavilion','observatory','coping']):continue
    vs=[o.matrix_world@v.co for v in o.data.vertices];ink=bool(o.data.materials and 'ink' in o.data.materials[0].name.lower())
    surf('Filled roof gable',vs,[(0,2,4),(1,5,3)],'paper' if ink else 'wall');gable_count+=1
# Add flush windows, lintels and sills. These communicate buildings, not impenetrable storage boxes.
window_count=0
for block in data['blocks']:
    o=S.objects.get(block['name'])
    if not o:continue
    x,y,z=block['center'];w,d,h=block['size'];bottom=z-h/2;ink='LEARNING' in block['district'];wood='ink' if ink else 'wood';glass='inkwindow' if ink else 'window'
    # Four faces; low detail flats are enough for the reference video, no unnecessary room interiors.
    for axis,span,depth in [('X',d,w),('Y',w,d)]:
        for sign in [-1,1]:
            count=max(1,min(8,int(span/3.5)))
            for j in range(count):
                u=(j-(count-1)/2)*span/count;ww=min(1.8,span/count*.55);hh=1.9;zc=bottom+2.6
                loc=(x+sign*(w/2+.04),y+u,zc) if axis=='X' else (x+u,y+sign*(d/2+.04),zc)
                dims=(.045,ww,hh) if axis=='X' else (ww,.045,hh);box('Inset facade glazing',loc,dims,glass,0);window_count+=1
                for off in [-ww/2,0,ww/2]:
                    q=Vector(loc);q[1 if axis=='X' else 0]+=off;box('Window vertical timber',q,(.10,.09,hh+.14) if axis=='X' else (.09,.10,hh+.14),wood,0)
                for off in [-hh/2,hh/2]:
                    q=Vector(loc);q.z+=off;box('Window sill lintel',q,(.10,ww+.14,.12) if axis=='X' else (ww+.14,.10,.12),wood,0)
    # One readable central door on the narrow front elevation.
    box('House door',(x,y-d/2-.08,bottom+1.25),(1.5,.10,2.5),wood,.02)
    box('Door center seam',(x,y-d/2-.14,bottom+1.25),(.035,.015,2.4),glass,0)

section('V04_FOLIAGE_CUES')
# Replace the new exterior's candy-shaped canopy shells by deterministic leaf clusters.
# Leaf geometry stays within the old canopy envelope. Existing tree positions/trunks stay fixed.
foliage_count=0
for o in list(S.objects):
    if o.type!='MESH' or 'canopy' not in o.name.lower() or not any(c.name.startswith('V03_') for c in o.users_collection):continue
    key='inkleaf' if any('ink' in m.name.lower() for m in o.data.materials) else 'green'
    # One combined mesh per former canopy, no per-leaf scene objects.
    vertices=[];faces=[]
    for j in range(210):
        z=random.uniform(-1,1);t=random.random()*math.tau;rad=random.uniform(.6,.96);q=Vector((math.sqrt(1-z*z)*math.cos(t),math.sqrt(1-z*z)*math.sin(t),z))*rad
        direction=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-.3,.7))).normalized();side=direction.cross(Vector((0,0,1))).normalized();size=random.uniform(.07,.15)
        k=len(vertices);vertices.extend([q-direction*size,q+side*size*.43,q+Vector((0,0,size*.18)),q-side*size*.43,q+direction*size]);faces.extend([(k,k+1,k+2),(k+1,k+4,k+2),(k+4,k+3,k+2),(k+3,k,k+2)])
    leaf=surf('Leaf cluster '+o.name,vertices,faces,key);leaf.matrix_world=o.matrix_world.copy();leaf['physical']=True
    # An irregular leafy inner mass avoids the sparse/twiggy appearance of leaf cards alone.
    inner=o.copy();inner.data=o.data.copy();inner.name='Irregular foliage core';G.objects.link(inner);inner.scale=o.scale*.69;inner.hide_render=False;inner.hide_set(False)
    for v in inner.data.vertices:v.co*=random.uniform(.80,1.18)
    # Keep original geometry as hidden provenance; its volume was already checked in v0.3.
    o.hide_render=True;o.hide_set(True);o['replaced_for_reference_readability']=leaf.name;foliage_count+=1

section('V04_CLOUD_CUES')
def cloud_volume(n,ink=False):
    m=bpy.data.materials.new(n);m.use_nodes=True;ns=m.node_tree.nodes;ls=m.node_tree.links;ns.clear();out=ns.new('ShaderNodeOutputMaterial');v=ns.new('ShaderNodeVolumePrincipled');v.inputs['Color'].default_value=(.8,.8,.8,1) if ink else (.83,.87,.88,1);v.inputs['Anisotropy'].default_value=.15
    tc=ns.new('ShaderNodeTexCoord');sub=ns.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5);ls.new(tc.outputs['Generated'],sub.inputs[0]);length=ns.new('ShaderNodeVectorMath');length.operation='LENGTH';ls.new(sub.outputs[0],length.inputs[0])
    fade=ns.new('ShaderNodeMapRange');fade.clamp=True;fade.inputs['From Min'].default_value=.2;fade.inputs['From Max'].default_value=.52;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;ls.new(length.outputs['Value'],fade.inputs['Value'])
    noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6;noise.inputs['Detail'].default_value=3;ls.new(tc.outputs['Generated'],noise.inputs['Vector'])
    mult=ns.new('ShaderNodeMath');mult.operation='MULTIPLY';ls.new(noise.outputs['Fac'],mult.inputs[0]);ls.new(fade.outputs['Result'],mult.inputs[1]);den=ns.new('ShaderNodeMath');den.operation='MULTIPLY';den.inputs[1].default_value=.14;ls.new(mult.outputs[0],den.inputs[0]);ls.new(den.outputs[0],v.inputs['Density']);ls.new(v.outputs['Volume'],out.inputs['Volume']);return m
M['cloudv']=cloud_volume('V04 cloud-material soft fringe');M['inkcloudv']=cloud_volume('V04 ink cloud-material soft fringe',True)
for o in list(S.objects):
    if o.name.startswith('Cloud material soft edge'):
        o.hide_render=True
# Irregular, soft fringes around real load-bearing cores. These are cloud material, not walkable ordinary fog.
cloud_count=0
for bank in data['platforms']:
    cx,cy,z=bank['center'];rx,ry=bank['radii'];ink='School' in bank['name'];key='inkcloudv' if ink else 'cloudv'
    for i in range(15):
        t=i*math.tau/15+random.uniform(-.13,.13);x=cx+rx*.9*math.cos(t);y=cy+ry*.9*math.sin(t);depth=random.uniform(5,9)
        o=ell('Soft structural cloud fringe',(x,y,z-depth*.75),(rx*random.uniform(.11,.20),ry*random.uniform(.12,.20),depth),key);o['physical']=False;o['semantic_role']='Visual soft cloud-material margin around retained solid structural core';cloud_count+=1

section('V04_WATER_CUES')
# A thin vertical waterfall with a short overflow channel, not the old 45m diagonal solid-looking sheet.
fall_material=simple('fall',(.73,.82,.83),.18);fb=next(n for n in fall_material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');fb.inputs['Transmission Weight'].default_value=.4;fb.inputs['IOR'].default_value=1.333
water_rng=random.Random(4104)
for i,(cx,cy,top,lower) in enumerate([(-1070,805,45,23),(-1025,755,23,0)]):
    old=S.objects.get('Cascade falling water '+str(i));old.hide_render=True
    core=S.objects['Cascade garden '+str(i)+' structural cloud'];lip=core.matrix_world@core.data.vertices[48].co;lip.y-=1
    # Core top contour chooses an outlet outside the load-bearing margin; the pond feeds it.
    pond_south=cy-(45 if i==0 else 43)*.9
    channel=[(cx-5,pond_south,top+.08),(cx+5,pond_south,top+.08),(cx+5,lip.y,top+.02),(cx-5,lip.y,top+.02)]
    surf('Overflow channel water',channel,[(0,1,2,3)],'inkwater' if i==0 else 'water',False)
    for sign in [-1,1]:rod('Overflow channel stone bank',(cx+sign*5.4,pond_south,top+.1),(cx+sign*5.4,lip.y,top+.1),.25,'gray' if i==0 else 'stone')
    for j in range(56):
        x=cx+water_rng.uniform(-4.8,4.8);w=water_rng.uniform(.035,.10);phase=water_rng.random()*6.28;vs=[];faces=[]
        for k in range(19):
            f=k/18;zz=top+(lower-top)*f;yy=lip.y-f*.75+.10*math.sin(f*29+phase);xx=x+.19*f*math.sin(f*17+phase);width=w*(.65+.35*math.sin(f*23+phase));vs.extend([(xx-width,yy,zz),(xx+width,yy,zz)])
        for k in range(18):
            if k<4 or water_rng.random()>.10:faces.append((2*k,2*k+1,2*k+3,2*k+2))
        surf('Vertical waterfall filament',vs,faces,'fall',False)
    # Low foam marks the receiving water surface rather than filling the whole pool with white.
    for j in range(115):
        o=ell('Waterfall splash foam',(cx+water_rng.uniform(-5.5,5.5),lip.y+water_rng.uniform(-1.4,.8),lower+.035),(water_rng.uniform(.035,.18),water_rng.uniform(.025,.12),.008),'foam');o['physical']=False
    mist=ell('Receiving pool fine spray',(cx,lip.y-.5,lower+.6),(6,1.8,1.1),'cloudv');mist['physical']=False;mist['semantic_role']='Ordinary spray, not structural cloud material'

section('V04_LANDMARK_DETAILS')
# Small wooden balustrades make the double pavilion read as an inhabitable water pavilion.
for x,y,z,w,d in [(-810,678,58,23,18),(-810,678,68,15,12)]:
    for yy in [y-d/2,y+d/2]:
        rod('Pavilion timber balustrade',(x-w/2,yy,z+1),(x+w/2,yy,z+1),.07,'wood')
        for j in range(int(w)):
            xx=x-w/2+j;rod('Pavilion balustrade upright',(xx,yy,z),(xx,yy,z+1),.05,'wood')

# Keep all original lens/position values. Use a clearer soft daylight, without changing material families.
for o in S.objects:
    if o.type=='LIGHT' and o.data.type=='SUN':o.data.angle=math.radians(6);o.data.energy=2.6;o.data.color=(1,.96,.89)
bg=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.50,.66,.80,1);bg.inputs['Strength'].default_value=.7
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.cycles.use_denoising=True;S.cycles.max_bounces=5;S.cycles.volume_bounces=1;S.cycles.volume_step_rate=2;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
cameras={v['id']:next(o for o in S.objects if o.type=='CAMERA' and o.name.startswith(v['id']+' ')) for v in data['cameras']}
S.camera=cameras['V03-B1'];S['episode_scope']='v0.4 readable scene cues for later video control. v0.3 spatial mechanism accepted by author; not a tested video-model input yet.'
data.update(version='v0.4',status='Reference art readability candidate; v0.3 spatial mechanism accepted by author',previous_source=str(SOURCE.relative_to(ROOT)),previous_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),appearance_changes={'gables':gable_count,'window_panels':window_count,'leaf_clusters':foliage_count,'cloud_fringe_volumes':cloud_count,'vertical_waterfalls':2},reference_usage={'locks':['camera positions and lenses','flight/walk route points','original rooms and two-bank relationship','screen and landmark locations'],'model_should_refine':['leaf detail','cloud softness','roof tile detail','water movement','plaster and wood microtexture'],'do_not_infer':['game-low-poly style from remaining rough masses','rock or concrete islands from the retained cloud cores','solid ramps from waterfall water','character identity or final carrier form from proxies'],'video_model_input_tested':False})
data['limits']=['Reference-stage polish only; no final asset topology or physically solved cloud/water simulation.','Original adopted art and character references retain authority over final style.','No new route timing or camera animation; still frame inspection does not prove downstream video interpretation.']
(OUT/'route-layout.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'appearance-audit.json').write_text(json.dumps({'source_sha256':data['previous_sha256'],'base_palette_before':palette,'protected_geometry_count':len(protected),'protected_geometry_summary_sha256':hashlib.sha256(json.dumps(protected,sort_keys=True).encode()).hexdigest(),'scope':'Original room/campus objects retain topology and world transforms. New exterior roof pitch/material cues refined in this copy; v03 cameras and route arrays unchanged.'},ensure_ascii=False,indent=2),encoding='utf8')
for tx in bpy.data.texts:
    if tx.name=='V03_CURRENT_SCOPE':tx.name='ARCHIVE_V03_SCOPE'
tx=bpy.data.texts.new('V04_REFERENCE_SCOPE');tx.write(json.dumps(data['reference_usage'],ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'episode1-floating-garden-v04.blend'))
ids=list(cameras) if a.render=='all' else ([] if a.render=='none' else a.render.split(','))
for cid in ids:
    S.camera=cameras[cid];S.render.filepath=str(OUT/(cid.replace('V03','V04')+'.png'));bpy.ops.render.render(write_still=True)
print('REFERENCE_POLISH_OK',json.dumps(data['appearance_changes']),flush=True)
