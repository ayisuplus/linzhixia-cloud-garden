# 项目生成工具

**2026-10-19更新：** API技能与LibTV插件源码已移至[公共工具库](../../../../OpenCut/toolkit/README.md)，原位置为目录链接，`.codex/config.toml`引用公共市场。下面2026-10-17安装记录保留作来源；其中“源码只在本项目内”的描述已被本次迁移替代。RunningHub CLI与虚拟环境不变，认证需当次核实。

2026-10-17 安装。制作仍以资产图册、关键帧图册、视频生成镜头表为准；工具只负责执行，不强制增加画布或另建资产表。

| 能力 | 项目位置 | 当前状态 |
| --- | --- | --- |
| RunningHub 官方 Skill | `.agents/skills/runninghub/` | 完整目录已安装 |
| RunningHub 官方 CLI | `tools/vendor/runninghub-cli/` + `.venv-media/` | 0.1.0，命令启动、模型目录和账户只读检查通过 |
| LibTV API Skill | `.agents/skills/libtv-skill/` | 完整目录已安装；当前进程未配置 `LIBTV_ACCESS_KEY` |
| LibTV 官方 Codex 插件 | `plugins/libtv/` | 1.0.0，Codex 已识别 installed/enabled；OAuth 已登录（2026-10-17 复查通过） |
| LibTV 随包 Skills | `plugins/libtv/skills/` | 导演提案、Blender 联动、配乐广告共 3 项，随插件完整安装 |

来源、固定提交号与文件 SHA-256 见 `sources.lock.json`。上游源码与技能正文保持原样，许可证和仓库说明保存在 `upstream-notices/`。未找到可确认的 RunningHub 官方 Codex 插件；没有用第三方 MCP 冒充，也没有改动本地 ComfyUI。LibTV 配乐广告的 Swift 脚本要求 macOS 15+，本 Windows 项目只安装随包素材与说明，不声称该脚本可运行。

## 使用

下一轮对话即可发现项目 Skills。LibTV 若未出现在本轮工具列表，重新打开本项目任务或重启 Codex，本机已完成 `libtv` 的 OAuth 登录；其他机器或授权失效时，可在插件连接管理中重新登录，也可在项目目录运行 `codex mcp login libtv`。OAuth 由 Codex 管理，**不要把密钥贴进聊天或提交到 Git**。

RunningHub 使用项目启动器：

```powershell
./tools/media/rh.ps1 --version
./tools/media/rh.ps1 model list --type video
./tools/media/rh.ps1 check
```

启动器默认输出到 `视频制作/生成结果/RunningHub`；正式执行某一批次时传 `--output-dir` 或子命令 `-o` 指向对应镜头目录。已有 RunningHub 账户配置已通过只读连通检查；安装验证没有上传参考图或提交生成。官方 CLI 和 Skill 的模型目录来自不同提交，不能假定两者完全同步；提交前重新核对所选端点和参数。

RunningHub CLI 使用 `RUNNINGHUB_API_KEY` 环境变量或 `%APPDATA%\rh\config.toml` 的 `api_key`。Skill 脚本以环境变量鉴权；不能因为 CLI 已登录就推断 Skill 脚本自动共享其 TOML 配置。优先使用 CLI；需要 Skill 脚本时在本地安全注入环境变量。

LibTV 官方插件使用 OAuth。独立 API Skill 使用另外的 `LIBTV_ACCESS_KEY` 环境变量，二者不能互换。API Skill 以项目 `.venv-media/Scripts/python.exe` 执行；下载结果时显式传 `--output-dir` 指向对应镜头目录。`create_session.py`、`change_project.py`、`upload_file.py` 会更改云端状态，不用作安装冒烟检查。`change_project.py` 甚至不会把 `--help` 当帮助参数处理，检查它只做语法解析。

## 项目范围

插件源文件和 marketplace 都在项目内：`.agents/plugins/marketplace.json`、`plugins/libtv/`。项目 `.codex/config.toml` 注册本地源并启用插件。Codex 按其机制在用户缓存目录保留运行副本及 OAuth 凭据；这不代表全局启用。安装命令新增的用户级启用项已移除，其他项目不自动启用本插件。

项目移动位置后，更新 `.codex/config.toml` 中 marketplace 的绝对 `source` 路径。项目需要被 Codex 标记为可信才会读取此配置。插件完整安装状态可查：

```powershell
codex plugin list --json --marketplace libtv
codex mcp list --json
```

## 恢复运行环境

项目源文件随 Git 保存，`.venv-media` 不提交。本锁文件按 Python 3.12 验证，恢复时也使用 Python 3.12 和 uv，在项目根目录运行（上游虽支持 3.10+，其他版本需重新解析条件依赖）：

```powershell
uv venv --python 3.12 .venv-media
uv pip install --python .venv-media/Scripts/python.exe -r tools/media/requirements.lock.txt
uv pip install --python .venv-media/Scripts/python.exe --no-deps ./tools/vendor/runninghub-cli
codex plugin add libtv@libtv
```

最后一条会写入用户级 enabled 项；恢复后将用户配置中新增的 `[plugins."libtv@libtv"]` 项移除，保留项目内启用项。不要删除其他插件配置。更新应单独进行，重新固定上游提交、核对完整文件与验证结果；不自动拉最新覆盖采用版本。
