"""Reuse the verified curve/envelope solver with the new explicitly authored plan."""
import sys
from pathlib import Path
R=Path(sys.argv[sys.argv.index('--')+2]);D=R/'第一季/制作/空间规划/第一集园城航线重排-v0.1'
code=(D/'build_route.py').read_text('utf8')
code=code.replace('第一集园城航线重排-20261023-v0.1','第一集巨云重构-20261024-v0.1').replace('garden-city-space-v01.blend','mother-cloud-space-v01.blend').replace('garden-city-flight-58s-v04.blend','mother-cloud-flight-58s-v01.blend')
exec(compile(code,str(D/'build_route.py'),'exec'))
code=(D/'finish_arrival.py').read_text('utf8').replace('第一集园城航线重排-20261023-v0.1','第一集巨云重构-20261024-v0.1').replace('garden-city-flight-58s-v04.blend','mother-cloud-flight-58s-v01.blend')
code=code.replace('for i in range(1392):s.frame_set(i+1);quats.append(cam.rotation_quaternion.copy())',"qcurves=sorted([fc for layer in cam.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves if fc.data_path=='rotation_quaternion'],key=lambda fc:fc.array_index)\nfor i in range(1392):quats.append(Quaternion([fc.evaluate(i+1) for fc in qcurves]))")
sys.argv=[sys.argv[0],'--',str(R)];exec(compile(code,str(D/'finish_arrival.py'),'exec'))
