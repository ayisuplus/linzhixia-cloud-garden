"""One cloud bearing a garden city. Preserve architecture; rebuild supporting mass and reveals."""
import bpy,sys,ast,json,math,random,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(sys.argv[sys.argv.index('--')+1]);O=R/'视频制作/第一集巨云重构-20261024-v0.1';SOURCE=R/'视频制作/第一集园城航线重排-20261023-v0.1/garden-city-flight-58s-v04.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene;S.frame_set(1)
before={o.name:{'matrix':list(v for row in o.matrix_world for v in row),'mesh':o.data.name if o.type=='MESH' else None} for o in S.objects}
path=R/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py'
exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text('utf8')).body if isinstance(n,ast.FunctionDef) and n.name in {'section','group','ell','box','surf'}],type_ignores=[]),str(path),'exec'))
COL={};G=None;M={};hidden=[]
for o in S.objects:
 if any(t in o.name for t in ['structural cloud','garden surface','Billowing cloud margin','Pendant cloud lobe','Detached soft cloud wisp','Cloud material soft edge','Load-bearing cloud ribbon']):
  o.hide_render=True;o.hide_set(True);hidden.append(o.name)
def volume(name,density,feather=False,scale=.025):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');l.new(tc.outputs['Object'],noise.inputs['Vector']);noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3.5
 ramp=n.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=.22;ramp.inputs['From Max'].default_value=.76;ramp.inputs['To Min'].default_value=density*.12;ramp.inputs['To Max'].default_value=density;l.new(noise.outputs['Fac'],ramp.inputs['Value']);dens=ramp.outputs[0]
 if feather:
  sub=n.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';l.new(tc.outputs['Generated'],sub.inputs[0]);sub.inputs[1].default_value=(.5,.5,.5)
  length=n.new('ShaderNodeVectorMath');length.operation='LENGTH';l.new(sub.outputs[0],length.inputs[0]);fade=n.new('ShaderNodeMapRange');fade.clamp=True;fade.interpolation_type='SMOOTHERSTEP';fade.inputs['From Min'].default_value=.22;fade.inputs['From Max'].default_value=.49;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;l.new(length.outputs['Value'],fade.inputs['Value'])
  mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(dens,mul.inputs[0]);l.new(fade.outputs[0],mul.inputs[1]);dens=mul.outputs[0]
 v=n.new('ShaderNodeVolumePrincipled');l.new(dens,v.inputs['Density']);v.inputs['Color'].default_value=(.91,.95,1,1);v.inputs['Anisotropy'].default_value=.15
 em=n.new('ShaderNodeMath');em.operation='MULTIPLY';em.inputs[1].default_value=.09;l.new(dens,em.inputs[0]);l.new(em.outputs[0],v.inputs['Emission Strength']);v.inputs['Emission Color'].default_value=(.83,.9,1,1)
 out=n.new('ShaderNodeOutputMaterial');l.new(v.outputs['Volume'],out.inputs['Volume']);return m
M['body']=volume('MOTHER CLOUD connected supporting cloud',.075)
M['lobe']=volume('MOTHER CLOUD feathered folded shoulders',.055,True,1.8)
M['mist']=volume('Ordinary mist / open air only',.025,True,2.3)
M['sea']=volume('Lower ambient cloud sea',.025,True,2.8)
section('MOTHER_CLOUD_V01_SINGLE_SUPPORT')
data=np.load(O/'mother-cloud-body.npz');o=surf('One connected giant cloud / stable support',data['vertices'].tolist(),data['faces'].tolist(),'body');o['physical']=True
for p in o.data.polygons:p.use_smooth=True
section('MOTHER_CLOUD_V01_CURLS');rng=random.Random(2401)
# Curling flanks touch the common mass. None is a separate pedestal for a district.
for i in range(34):
 t=math.tau*i/34;cx=-650+925*math.cos(t);cy=430+570*math.sin(t);cz=-220+rng.uniform(-45,35)
 ell('Connected outer cloud fold',(cx,cy,cz),(rng.uniform(100,180),rng.uniform(90,140),rng.uniform(85,135)),'lobe')['physical']=False
bankdata=json.loads((R/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text('utf8'))['platforms']
flightdata=json.loads((R/'视频制作/第一集园城航线重排-20261023-v0.1/flight-checks.json').read_text('utf8'));nearroute=np.array([q['camera'] for q in flightdata['records']])
for b in bankdata:
 cx,cy,z=b['center'];rx,ry=b['radii']
 for i in range(11):
  t=i*math.tau/11+.3;loc=np.array([cx+rx*1.08*math.cos(t),cy+ry*1.08*math.sin(t),z-6])
  if np.linalg.norm(nearroute-loc,axis=1).min()<45:continue
  ell('Shared cloud ridge soft edge',loc,(rng.uniform(23,39),rng.uniform(23,39),rng.uniform(15,24)),'lobe')['physical']=False
section('MOTHER_CLOUD_V01_LOW_AMBIENT')
for i in range(17):
 t=i*2.399;r=1400+(i%3)*420
 ell('Lower detached environment cloud',(-650+math.cos(t)*r,430+math.sin(t)*r,-670-rng.uniform(0,100)),(420,310,130),'sea')['physical']=False
# Short optically permeable curtains. The supporting cloud remains below them.
section('MOTHER_CLOUD_V01_REVEAL_CURTAINS')
for name,loc,sc in [('A partial cloud veil',(-1130,809,67),(32,12,22)),('B cloud valley side veil',(-948,683,72),(30,45,29)),('C water lane side veil',(-235,16,10),(20,18,10))]:
 o=ell(name,loc,sc,'mist');o['physical']=False;o['role']='ordinary mist, not load-bearing cloud'
section('MOTHER_CLOUD_V01_INHABITED_SPINES')
M['stone']=bpy.data.materials['Warm gray garden stone']
fielddata=np.load(O/'mother-cloud-field.npz');field=fielddata['field'];origin=fielddata['origin'];step=float(fielddata['step'])
def top(x,y):
 ix,iy=np.rint((np.array([x,y])-origin[:2])/step).astype(int)
 if not (0<=ix<field.shape[0] and 0<=iy<field.shape[1]):return None
 col=field[ix,iy];idx=np.where(col>0)[0]
 if not len(idx):return None
 k=idx[-1];return float(origin[2]+step*(k+col[k]/(col[k]-col[k+1])))
source_group=[o for o in list(S.objects) if o.name.startswith('Replan 03 compound 00') and not o.hide_render]
template=bpy.data.collections.new('Mother cloud existing courtyard template')
for o in source_group:template.objects.link(o)
vv=[o.matrix_world@Vector(c) for o in source_group for c in o.bound_box];center0=Vector(((min(v.x for v in vv)+max(v.x for v in vv))/2,(min(v.y for v in vv)+max(v.y for v in vv))/2,min(v.z for v in vv)))
layout=json.loads((R/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text('utf8'))['platforms']
oldroute=json.loads((R/'视频制作/第一集园城航线重排-20261023-v0.1/flight-checks.json').read_text('utf8'));route=np.array([r['position'] for r in oldroute['records']])
newdistricts=[]
spines=[(np.array([-1140,390]),np.array([-380,410])),(np.array([-850,390]),np.array([-520,160])),(np.array([-690,420]),np.array([-630,610]))]
def spine_distance(q):
 return min(np.linalg.norm(q-(a+np.clip(np.dot(q-a,b-a)/np.dot(b-a,b-a),0,1)*(b-a))) for a,b in spines)
for y in range(160,650,36):
 for x in range(-1170,-290,36):
  y1=y
  if spine_distance(np.array([x,y1]))>42:continue
  if min(np.linalg.norm(route[:,:2]-[x,y1],axis=1))<65:continue
  if any(((x-b['center'][0])/(b['radii'][0]*1.15))**2+((y1-b['center'][1])/(b['radii'][1]*1.15))**2<1 for b in layout):continue
  heights=[top(x+dx,y1+dy) for dx in [-16,-8,0,8,16] for dy in [-16,-8,0,8,16]]
  if any(z is None for z in heights) or max(heights)-min(heights)>12 or max(heights)<-90:continue
  z=max(heights)+.25
  ob=bpy.data.objects.new('Cloud city linked courtyard',None);ob.instance_type='COLLECTION';ob.instance_collection=template;G.objects.link(ob);ob.matrix_world=Matrix.Translation((x,y1,z))@Matrix.Translation(-center0);ob['physical']=False
  box('Local reinforced courtyard foundation',(x,y1,(z+min(heights)-2)/2),(32,32,z-min(heights)+2),'stone',.3)
  newdistricts.append([x,y1,z])
(O/'added-districts.json').write_text(json.dumps({'count':len(newdistricts),'origins':newdistricts,'route_xy_exclusion_m':65,'role':'same mother-cloud interior, copied accepted courtyard vocabulary'},indent=2),encoding='utf8')
# B looks back into the inhabited valley, with a long straight passage through the real aperture.
center=Vector((-910,630,55));rot=Matrix.Identity(4);rotated=[]
for o in S.objects:
 if o.name.startswith(('Reveal B','Moon B')) or o.name=='Moon window trim.001':o.matrix_world=rot@o.matrix_world;rotated.append(o.name)
bpy.context.view_layer.update()
plan=json.loads((R/'视频制作/第一集园城航线重排-20261023-v0.1/space-plan.json').read_text('utf8'))
old=plan['nodes'];old[9][2]=65;old[10][2]=81;old[11][2]=83
plan['nodes']=old
(O/'space-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
# Reference-only whole-frame academy treatment. It is not a proposed boundary technology.
S.use_nodes=True;tree=bpy.data.node_groups.new('Academy full-view ink to city reference','CompositorNodeTree');S.compositing_node_group=tree
tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=tree.nodes.new('CompositorNodeRLayers');h=tree.nodes.new('CompositorNodeHueSat');outnode=tree.nodes.new('NodeGroupOutput');tree.links.new(rl.outputs['Image'],h.inputs['Image']);tree.links.new(h.outputs['Image'],outnode.inputs['Image'])
for f,v in [(1,0),(225,0),(325,1),(1392,1)]:h.inputs['Saturation'].default_value=v;h.inputs['Saturation'].keyframe_insert('default_value',frame=f)
S.camera.data.clip_end=9000;S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True;S.cycles.max_bounces=4;S.cycles.volume_bounces=1;S.cycles.volume_step_rate=2
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
S['design_status']='Reconstruction candidate: one connected support cloud; architectural palette retained; ink boundary only a reference treatment'
after={o.name:o for o in S.objects};changed=[name for name,v in before.items() if name not in rotated and v['matrix']!=list(x for row in after[name].matrix_world for x in row)]
assert not changed,changed
(O/'scene-audit.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'hidden_old_support_objects':hidden,'reoriented_B_screen_objects':rotated,'other_original_transform_changes':changed,'original_object_count':len(before),'academy_boundary':'Reference-only full-frame saturation transition, technical mechanism unresolved'},ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'mother-cloud-space-v01.blend'));print('SCENE_READY',flush=True)
