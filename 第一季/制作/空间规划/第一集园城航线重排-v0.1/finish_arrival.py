"""Let the preview camera settle in front of the receiving perch while the carrier docks."""
import bpy,sys,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
root=Path(sys.argv[sys.argv.index('--')+1]);out=root/'视频制作/第一集园城航线重排-20261023-v0.1';p=out/'garden-city-flight-58s-v04.blend'
bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;cam=s.objects['FAST_ROUTE_FPV']
report=json.loads((out/'flight-checks.json').read_text(encoding='utf8'));rows=report['records'];start=55.;duration=2.2;j=round(start*24)
pp=np.array([r['camera'] for r in rows]);p0=pp[j];v0=(pp[j+1]-pp[j-1])*12;a0=(pp[j+1]-2*p0+pp[j-1])*576
end=np.array([10.8,16.2,2.6]);c0=p0;c1=v0*duration;c2=a0*duration**2/2
c3,c4,c5=np.linalg.solve(np.array([[1,1,1],[3,4,5],[6,12,20]],float),np.array([end-c0-c1-c2,-c1-2*c2,-2*c2]))
target=Vector((10.8,18.5,1.05))
for i in range(j,len(rows)):
    t=i/24;u=min(1,(t-start)/duration);s.frame_set(i+1)
    pos=Vector(c0+c1*u+c2*u*u+c3*u**3+c4*u**4+c5*u**5)
    q=cam.rotation_quaternion.copy();wanted=(target-pos).to_track_quat('-Z','Y');w=u*u*u*(10-15*u+6*u*u)
    cam.location=pos;cam.rotation_quaternion=q.slerp(wanted,w);cam.keyframe_insert('location',frame=i+1);cam.keyframe_insert('rotation_quaternion',frame=i+1)
    rows[i]['camera']=list(pos);rows[i]['forward']=list(cam.rotation_quaternion@Vector((0,0,-1)))
quats=[]
for i in range(1392):s.frame_set(i+1);quats.append(cam.rotation_quaternion.copy())
report['max_camera_turn_deg_per_frame']=max(math.degrees(2*math.acos(min(1,abs(u.dot(v))))) for u,v in zip(quats,quats[1:]))
report['arrival_camera']={'start_s':55,'end_s':57.2,'camera_end':list(end),'target':list(target),'note':'Camera settles before the perch; carrier retains its exact original endpoint. This last 2.2s is an observation camera, not rigid FPV.'}
(out/'flight-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(p));print('ARRIVAL_CAMERA_READY',report['max_camera_turn_deg_per_frame'])
