"""Cloud-sea context candidate; preserve the accepted route and existing architecture."""
import bpy,sys,argparse,math,random,json,hashlib,ast
from pathlib import Path
from mathutils import Vector,Matrix
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--frames',default='697');p.add_argument('--engine',default='BLENDER_EEVEE');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(a.root);OUT=ROOT/'视频制作/第一集云海城市-20261023-v0.1';OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'视频制作/第一集园城航线重排-20261023-v0.1/garden-city-flight-58s-v04.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));S=bpy.context.scene;S.frame_set(1)
protected={o.name:tuple(v for row in o.matrix_world for v in row) for o in S.objects}
layout=json.loads((ROOT/'视频制作/第一集浮空园城-20261022-v0.4/route-layout.json').read_text('utf8'))
path=ROOT/'第一季/制作/空间规划/第一集场景-v0.1/build_episode.py'
exec(compile(ast.Module(body=[n for n in ast.parse(path.read_text('utf8')).body if isinstance(n,ast.FunctionDef) and n.name in {'section','group','ell','box','surf'}],type_ignores=[]),str(path),'exec'))
COL={};G=None;M={};rng=random.Random(231024)
# Independent copied cloud materials: existing architectural material datablocks remain untouched.
def copied_cloud(name,base,density_scale,ambient):
 m=bpy.data.materials[base].copy();m.name=name
 for n in m.node_tree.nodes:
  if n.type=='MAP_RANGE' and n.inputs['To Max'].default_value<.5:n.inputs['To Max'].default_value*=density_scale
 v=next(n for n in m.node_tree.nodes if n.type=='PRINCIPLED_VOLUME')
 v.inputs['Color'].default_value=(.9,.94,.98,1);v.inputs['Emission Color'].default_value=(.86,.91,.97,1)
 v.inputs['Emission Strength'].links[0].from_node.inputs[1].default_value=ambient
 return m
M['cloud']=copied_cloud('Cloudsea daylight billows','V06 cloud lobe with feathered boundary',.7,.10)
M['wisps']=copied_cloud('Cloudsea thin tendrils','V06 translucent trailing cloud',.55,.10)
M['body']=copied_cloud('Cloudsea shore interior','V06 dense cloud interior',.9,.10)
remapped=[]
for o in S.objects:
 if o.type!='MESH':continue
 for i,m in enumerate(o.data.materials):
  if m and m.name.startswith('V06 '):
   o.data.materials[i]=M['body' if 'interior' in m.name else 'wisps' if 'trailing' in m.name else 'cloud'];remapped.append(o.name)
# A single continuous volume with an irregular noise-defined top, rather than one cloud per island.
def sea_material():
 m=bpy.data.materials.new('Continuous cloud sea / variable height');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 def node(t):return n.new(t)
 def mathn(op,x,y):
  v=node('ShaderNodeMath');v.operation=op
  for i,k in enumerate((x,y)):
   if isinstance(k,(int,float)):v.inputs[i].default_value=k
   else:l.new(k,v.inputs[i])
  return v.outputs[0]
 tc=node('ShaderNodeTexCoord');noise=node('ShaderNodeTexNoise');l.new(tc.outputs['Generated'],noise.inputs['Vector']);noise.inputs['Scale'].default_value=25;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.7
 sep=node('ShaderNodeSeparateXYZ');l.new(tc.outputs['Generated'],sep.inputs[0]);height=mathn('ADD',mathn('MULTIPLY',noise.outputs['Fac'],.48),.33)
 depth=mathn('SUBTRACT',height,sep.outputs['Z']);fade=node('ShaderNodeMapRange');fade.clamp=True;fade.interpolation_type='SMOOTHERSTEP';fade.inputs['From Min'].default_value=0;fade.inputs['From Max'].default_value=.1;fade.inputs['To Max'].default_value=.045;l.new(depth,fade.inputs['Value'])
 v=node('ShaderNodeVolumePrincipled');v.inputs['Color'].default_value=(.91,.95,1,1);v.inputs['Anisotropy'].default_value=.15;v.inputs['Emission Color'].default_value=(.86,.92,1,1);l.new(fade.outputs[0],v.inputs['Density']);l.new(mathn('MULTIPLY',fade.outputs[0],.06),v.inputs['Emission Strength']);out=node('ShaderNodeOutputMaterial');l.new(v.outputs['Volume'],out.inputs['Volume']);return m
M['sea']=sea_material();section('CLOUDSEA_V01_CONTINUOUS')
o=box('Continuous deep cloud sea',(-700,500,-82),(9000,8000,170),'sea',0,False);o.display_type='WIRE'
section('CLOUDSEA_V01_ROLLING_SHORES');lobes=[]
flight=json.loads((ROOT/'视频制作/第一集园城航线重排-20261023-v0.1/flight-checks.json').read_text('utf8'))
# Camera corridor stays optically open; shore vapour can overlap only empty margins.
records=flight['records'];samples=[Vector(r['camera']) for r in records[::8]]
def clear(loc,sc):
 return all(sum(((q[i]-loc[i])/sc[i])**2 for i in range(3))>1.6 for q in samples)
for bank in layout['platforms']:
 cx,cy,z=bank['center'];rx,ry=bank['radii'];core=S.objects[bank['name']+' structural cloud'];contour=[core.matrix_world@v.co for v in core.data.vertices[:64]]
 for i in [0,5,11,14,23,27,36,43,48,53,59]:
  q=contour[i];rad=Vector((q.x-cx,q.y-cy,0)).normalized();f=rng.uniform(.8,1.3)
  sc=(min(rx*.30,65)*f,min(ry*.4,55)*f,rng.uniform(18,36))
  loc=q+rad*rng.uniform(-8,3)+Vector((0,0,-sc[2]*.30))
  if not clear(loc,sc):loc.z-=15
  if not clear(loc,sc):continue
  o=ell('Shore rises from rolling cloud',loc,sc,'cloud');o['physical']=False;lobes.append(o.name)
 # Broad underlying cloud currents overlap adjacent banks at unequal levels.
 for j in range(2):
  loc=(cx+rng.uniform(-rx*.4,rx*.4),cy+rng.uniform(-ry*.4,ry*.4),min(z-33,-25)-j*15)
  sc=(rx*rng.uniform(.9,1.3),ry*rng.uniform(.9,1.5),rng.uniform(24,40))
  if clear(loc,sc):
   o=ell('Connected undercity cloud current',loc,sc,'cloud');o['physical']=False;lobes.append(o.name)
# Uneven large billows connect the banks with crests and cloud valleys.
for ix in range(10):
 for iy in range(7):
  loc=Vector((-1600+ix*210+rng.uniform(-50,50),-250+iy*230+rng.uniform(-50,50),rng.uniform(-65,-38)))
  sc=(rng.uniform(100,175),rng.uniform(90,140),rng.uniform(40,65))
  if clear(loc,sc):
   o=ell('Cloud sea rolling crest',loc,sc,'cloud');o['physical']=False;lobes.append(o.name)
# Distant districts reuse the current roof/wall language; they are scenery, outside the flight corridor.
section('CLOUDSEA_V01_DISTANT_CITY');source_group=[o for o in list(S.objects) if o.name.startswith('Replan 03 compound 00') and not o.hide_render]
if not source_group:source_group=[o for o in list(S.objects) if o.name.startswith('Replan 02 compound 00') and not o.hide_render]
vs=[o.matrix_world@Vector(c) for o in source_group for c in o.bound_box];origin=Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs),min(v.z for v in vs)))
template=bpy.data.collections.new('Cloudsea distant courtyard template')
for src in source_group:
 if not any(t in src.name for t in ['paved','apron','entrance path','perimeter walk']):template.objects.link(src)
far=[]
for cx,cy,z in [(-550,1060,-8),(-40,740,-13),(180,400,-18),(450,-200,-12),(-640,-330,-18)]:
 for j in range(7):
  t=j*2.399;r=25+18*(j%3);target=Vector((cx+math.cos(t)*r,cy+math.sin(t)*r,z+2*(j%3)));xf=Matrix.Translation(target)@Matrix.Rotation((j%3)*.22,4,'Z')@Matrix.Translation(-origin)
  o=bpy.data.objects.new('Distant cloud district instance',None);o.instance_type='COLLECTION';o.instance_collection=template;G.objects.link(o);o.matrix_world=xf;o['physical']=False
  far.append(list(target))
 o=ell('Distant district cloud pedestal',(cx,cy,z-26),(150,110,44),'cloud');o['physical']=False
# Leave all original object transforms, animation and building palette unchanged.
print('DISTANT_CITY_READY',len(far),flush=True)
bpy.context.view_layer.update();lookup={o.name:o for o in S.objects};changes=[name for name,m in protected.items() if tuple(v for row in lookup[name].matrix_world for v in row)!=m];assert not changes,changes
S.camera.data.clip_end=7000;S.render.engine=a.engine;S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
S.eevee.taa_render_samples=32;S.eevee.volumetric_tile_size='4';S.eevee.volumetric_samples=128;S.eevee.use_volume_custom_range=True;S.eevee.volumetric_start=.3;S.eevee.volumetric_end=6500;S.eevee.volumetric_sample_distribution=.7
S.eevee.use_volumetric_shadows=True
if a.engine=='CYCLES':
 S.cycles.samples=24;S.cycles.use_denoising=True;S.cycles.max_bounces=4;S.cycles.volume_bounces=1;S.cycles.volume_step_rate=2;S.cycles.volume_max_steps=512
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 S.cycles.device='GPU'
S['cloudsea_candidate']='Continuous cloud sea and uneven shore billows; existing route and architecture preserved'
(OUT/'cloudsea-audit.json').write_text(json.dumps({'source':str(SOURCE.relative_to(ROOT)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'original_objects':len(protected),'changed_transforms':changes,'cloud_objects_remapped':len(remapped),'added_shore_clouds':len(lobes),'distant_compounds':len(far),'distant_compound_origins':far,'scope':'Cloud appearance, continuous cloud sea and distant scenery. Foreground architecture and flight unchanged. Candidate, optical review pending.'},indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cloudsea-city-v02.blend'))
(OUT/'preview-v02').mkdir(exist_ok=True)
for f in map(int,a.frames.split(',')):
 S.frame_set(f);S.render.image_settings.file_format='PNG';S.render.filepath=str(OUT/'preview-v02'/f'{f:04}.png');bpy.ops.render.render(write_still=True);print('PREVIEW_DONE',f,flush=True)
