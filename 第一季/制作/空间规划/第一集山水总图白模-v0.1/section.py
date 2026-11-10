"""Measured longitudinal diagram of this proposed blockout, not site-survey elevations."""
import sys,json,numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import layout as L
O=Path(sys.argv[1])/'视频制作/第一集山水总图白模-20261024-v0.1'
plt.rcParams['font.sans-serif']=['Microsoft YaHei'];plt.rcParams['axes.unicode_minus']=False
s=np.linspace(0,1,1001);x=s*L.LENGTH;w=L.water_z(s)
fig,ax=plt.subplots(figsize=(15,5.2),layout='constrained');fig.patch.set_facecolor('#f5f2e8');ax.set_facecolor('#f5f2e8')
for side,color,label in [(1,'#a8ae99','左侧云质山势'),(-1,'#c7cabc','右侧云质山势')]:
 pts=np.array([L.point(t,side*(L.width(t,side)+118))[:2] for t in s]);z=L.terrain(pts);ax.fill_between(x,w-4,z,color=color,alpha=.65,label=label)
ax.plot(x,w,color='#238c7f',lw=3,label='主水脉水位')
for a,b,label in [(0,.12,'上游学园庭水 96m'),(.55,.72,'中部水湾 38m'),(.87,.975,'生活水巷 18m')]:
 m=(a+b)/2;ax.annotate(label,xy=(m*L.LENGTH,float(L.water_z(m))),xytext=(m*L.LENGTH,155 if a==0 else 125),ha='center',arrowprops={'arrowstyle':'->','color':'#52655f'},fontsize=11)
for p in L.COURTS:
 ax.scatter(p['s']*L.LENGTH,p['floor'],s=18,c='#a4533c',zorder=4)
ax.scatter([],[],s=18,c='#a4533c',label='院落落地高程')
ax.set(xlabel='沿主水脉里程 / 米',ylabel='本白模设计高程 / 米',xlim=(0,L.LENGTH),ylim=(0,205),title='山水总图纵向关系｜水平庭水之间由窄溪下降，院落落在两岸台地')
ax.grid(alpha=.18);ax.legend(loc='upper right',fontsize=9);fig.text(.11,.003,'地形线为两侧偏移断面；竖向尺度放大。不是地勘数据，也不是流体仿真。',fontsize=9,color='#666')
fig.savefig(O/'whitebox/07-longitudinal-section.png',dpi=150);fig.savefig(O/'whitebox/07-longitudinal-section.svg')
print('SECTION_READY',L.LENGTH)
