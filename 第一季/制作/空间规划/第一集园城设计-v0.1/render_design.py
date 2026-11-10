import bpy,sys,argparse,json
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--variant',choices=['before','after'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(a.root);out=root/'视频制作/第一集园城设计-20261023-v0.1';d=json.loads((out/'design-audit.json').read_text(encoding='utf8'))
source=root/d['source'] if a.variant=='before' else out/'garden-city-design-v01.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.eevee.volumetric_tile_size='8';s.eevee.volumetric_samples=64
s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
dest=out/'views'/a.variant;dest.mkdir(parents=True,exist_ok=True)
for name,loc,target,lens in d['review_views']:
    ca=bpy.data.cameras.new('review camera');ca.lens=lens;ca.clip_end=6000;ob=bpy.data.objects.new('review camera',ca);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();s.camera=ob
    s.render.filepath=str(dest/(name+'.png'));bpy.ops.render.render(write_still=True)
print('DESIGN_VIEWS_READY',a.variant,flush=True)
