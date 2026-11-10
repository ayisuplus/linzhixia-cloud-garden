import bpy,sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]);out=root/'视频制作/第一集园城航线重排-20261023-v0.1'
for name in ['garden-city-space-v01.blend','garden-city-flight-58s-v04.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(out/name))
    for i,ymin in [(0,-26),(5,-24.9)]:
        ob=bpy.data.objects[f'Replan canal {i} stone retaining podium'];ymax=-10.5
        ob.location.y=(ymin+ymax)/2;ob.scale.y=(ymax-ymin)/19
        if i==5:ob.location.x=(-75.5-50.2)/2;ob.scale.x=25.3/27
    bpy.ops.wm.save_as_mainfile(filepath=str(out/name))
print('PODIUMS_REFINED')
