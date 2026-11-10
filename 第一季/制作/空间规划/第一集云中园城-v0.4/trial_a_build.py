"""v06: lower cloud density relief only. Retain palette, clearings, light and route."""
import bpy,sys,json,hashlib,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--proxy',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
R=Path(a.root);O=R/'视频制作/第一集云中园城-20261024-v0.4';O.mkdir(exist_ok=True)
src=R/'视频制作/第一集云中园城-20261024-v0.3'/('render-only-batched-v05.blend' if a.proxy else 'cloud-city-color-58s-v05.blend')
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene
changed=[]
for name in ['MOTHER CLOUD connected supporting cloud','ENCLOSING CLOUD with open courtyards']:
 m=bpy.data.materials[name];n=m.node_tree.nodes;l=m.node_tree.links;v=next(q for q in n if q.type=='PRINCIPLED_VOLUME')
 old=v.inputs['Density'].links[0].from_socket;oldem=v.inputs['Emission Strength'].links[0].from_socket
 def mathnode(op,a,b):
  q=n.new('ShaderNodeMath');q.operation=op
  for i,x in enumerate([a,b]):
   if isinstance(x,(float,int)):q.inputs[i].default_value=x
   else:l.new(x,q.inputs[i])
  return q.outputs[0]
 def remap(socket,lo,hi,to0,to1):
  q=n.new('ShaderNodeMapRange');q.clamp=True;q.interpolation_type='SMOOTHERSTEP'
  for k,x in [('From Min',lo),('From Max',hi),('To Min',to0),('To Max',to1)]:q.inputs[k].default_value=x
  l.new(socket,q.inputs['Value']);return q.outputs[0]
 tc=n.new('ShaderNodeTexCoord');tc.object=bpy.data.objects['Cloud clearing world coordinate origin'];tc.label='V06 fixed lower-cloud relief'
 xyz=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],xyz.inputs[0])
 lower=remap(xyz.outputs['Z'],-15,75,1,0)
 scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.009,.009,.021);l.new(tc.outputs['Object'],scale.inputs[0])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=1.5;noise.inputs['Roughness'].default_value=.48;l.new(scale.outputs[0],noise.inputs['Vector'])
 ribs=remap(noise.outputs['Fac'],.46,.65,.002,1)
 factor=mathnode('ADD',mathnode('SUBTRACT',1,lower),mathnode('MULTIPLY',lower,ribs))
 density=mathnode('MULTIPLY',old,factor);l.new(density,v.inputs['Density'])
 # Same world relief controls extinction/emission; original courtyard masks remain upstream.
 fill=mathnode('ADD',1,mathnode('MULTIPLY',lower,remap(noise.outputs['Fac'],.45,.65,.25,1.35)))
 l.new(mathnode('MULTIPLY',mathnode('MULTIPLY',oldem,factor),fill),v.inputs['Emission Strength'])
 changed.append(name)
s['revision']='v06 lower cloud relief; current v05 palette, lights, clearings, geometry and exact 58s animation retained.'
target=O/('render-only-batched-v06.blend' if a.proxy else 'cloud-city-layered-58s-v06.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(target))
if not a.proxy:
 (O/'revision.json').write_text(json.dumps({'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'changed_cloud_materials':changed,'scope':'two existing lower-cloud shaders; density reduced only, fixed world-coordinate relief. Original geometry, palette, lighting, camera and carrier retained.','height_blend_m':[-15,75],'noise_world_scale':[.009,.009,.021],'density_factor_range':[.002,1],'frames':1392,'fps':24,'duration_s':58},ensure_ascii=False,indent=2),encoding='utf8')
print('LOWER_CLOUD_READY',target,flush=True)
