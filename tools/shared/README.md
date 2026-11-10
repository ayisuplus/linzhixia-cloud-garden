# 公共创作工具入口

本项目共用同级[创作工具库](../../../../OpenCut/toolkit/README.md)。日常改公共技能/插件/通用脚本只改公共库；本项目的角色、素材、进度和项目技能仍在本项目维护。

- `.agents/skills/runninghub`、`libtv-skill`、`color-expert` 为相对目录符号链接。
- `.codex/config.toml` 指向公共 LibTV 市场，保持 `libtv@libtv` 身份；`plugins/libtv` 为兼容链接。
- 图册、资产和生成校验的旧脚本路径保留为薄包装，数据根显式传 `--root`。
- 不复制 OAuth/API Key，不改变现有用户级达芬奇/ComfyUI配置。安装/发现与实际鉴权分开核实。
- 恢复时运行公共库 `setup.ps1`（PowerShell 7）；Git需保留符号链接。验证范围与记录见公共库 `migration/`。
