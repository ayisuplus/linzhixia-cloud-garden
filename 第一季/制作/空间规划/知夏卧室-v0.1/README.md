# 知夏卧室空间构建脚本 v0.1

成果与范围见[三维空间审阅说明](../../../../视频制作/知夏卧室三维空间-20261022-v0.1/README.md)。Blender 5.1；参考原文件与现行分镜，不使用旧半园院内工坊布局。

```powershell
& 'D:/blender/blender.exe' -b -t 12 --python '第一季/制作/空间规划/知夏卧室-v0.1/build_scene.py' -- --root 'E:/projects/内容创作/未来女孩林知夏' --render all --gpu
& 'D:/blender/blender.exe' -b --python '第一季/制作/空间规划/知夏卧室-v0.1/render_path.py' -- --root 'E:/projects/内容创作/未来女孩林知夏'
& 'D:/blender/blender.exe' -b --python '第一季/制作/空间规划/知夏卧室-v0.1/verify_saved.py' -- --root 'E:/projects/内容创作/未来女孩林知夏'
```

先核实GPU可用；省略`--gpu`时静态构建用CPU。路径渲染脚本固定OptiX。旧模型、人物与采用配色不修改。
