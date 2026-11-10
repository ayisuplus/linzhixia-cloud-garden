"""Reference motion render; approximate cloud multiple scattering explicitly for EEVEE."""
import bpy,sys,argparse,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--test',action='store_true');p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=1392);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);R=Path(a.root);O=R/'视频制作/第一集巨云重构-20261024-v0.1';bpy.ops.wm.open_mainfile(filepath=str(O/'mother-cloud-flight-58s-v01.blend'));s=bpy.context.scene
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=8;s.eevee.volumetric_tile_size='8';s.eevee.volumetric_samples=48;s.eevee.use_volume_custom_range=True;s.eevee.volumetric_start=.3;s.eevee.volumetric_end=5000;s.eevee.use_volumetric_shadows=True
s.render.use_motion_blur=False;s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
for m in bpy.data.materials:
 if not m.use_nodes or not m.name.startswith(('MOTHER CLOUD','Lower ambient','Ordinary mist /')):continue
 n=m.node_tree.nodes;l=m.node_tree.links;v=next(x for x in n if x.type=='PRINCIPLED_VOLUME');em=v.inputs['Emission Strength'].links[0].from_node
 tc=next(x for x in n if x.type=='TEX_COORD');xyz=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Generated'],xyz.inputs[0]);r=n.new('ShaderNodeMapRange');r.inputs['To Min'].default_value=.35;r.inputs['To Max'].default_value=.85;l.new(xyz.outputs['Z'],r.inputs['Value']);l.new(r.outputs[0],em.inputs[1])
s['preview_lighting_note']='EEVEE height-dependent cloud fill approximates multiple scattering. Geometry, camera, architectural materials unchanged.'
if not a.test:bpy.ops.wm.save_as_mainfile(filepath=str(O/'mother-cloud-reference-58s-v01.blend'))
dest=O/('motion-test' if a.test else 'motion-frames');dest.mkdir(exist_ok=True)
frames=[280,282,284] if a.test else range(a.start,a.end+1,2)
for f in frames:
 if not a.test and (dest/f'{f:04}.png').exists():continue
 start=time.time();s.frame_set(f);s.render.image_settings.file_format='PNG';s.render.filepath=str(dest/f'{f:04}.png');bpy.ops.render.render(write_still=True);print('MOTION_FRAME',f,'SECONDS',round(time.time()-start,2),flush=True)
