# SiYuan Skill

一个基于 Python CLI 的 SiYuan 思源笔记 skill。为避免和仓库开发文件混放，所有 skill 相关文件都集中在 `skill/` 目录中。

## 特性

- 使用 Python CLI 统一封装 SiYuan HTTP API
- 默认输出标准 JSON envelope，便于 Agent 消费
- 支持 `json`、`markdown`、`csv`、`text` 四种输出格式
- 已覆盖旧版 shell SDK 的全部 API endpoint，并保留工作区写入等 helper 能力
- 兼容项目内调用，也可安装到不同 Agent 的技能目录中复用

## 目录

```text
.
├── AGENTS.md
├── README.md
└── skill/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    │   ├── bootstrap.py
    │   ├── check_env.py
    │   └── siyuan_cli.py
    ├── python/
    │   └── siyuan_skill/
    ├── requirements.txt
    └── pyproject.toml
```

## 环境要求

- Python 3.10+
- 本地运行中的 SiYuan，默认地址 `http://127.0.0.1:6806`

依赖：

- `requests>=2.32.0`
- `python-dotenv>=1.0.1`
- `pandas>=2.2.0`
- `tabulate>=0.9.0`

## 配置

配置优先级：

1. CLI 参数
2. 环境变量
3. 仓库根目录 `.env`
4. 默认值

支持变量：

- `SIYUAN_HOST`
- `SIYUAN_TOKEN`
- `PASSWORD`
- `SIYUAN_TIMEOUT`
- `SIYUAN_OUTPUT_FORMAT`

示例 `.env`：

```env
SIYUAN_HOST=http://127.0.0.1:6806
SIYUAN_TOKEN=your_api_token
# 或者使用 PASSWORD 让 CLI 自动登录后获取 token
PASSWORD=your_access_auth_code
SIYUAN_OUTPUT_FORMAT=json
```

## 安装

### 方式一：作为当前项目内 skill 使用

1. 克隆仓库。
2. 进入仓库目录。
3. 可选：先安装依赖。

```bash
git clone <your-repo-url> siyuan-skills
cd siyuan-skills
python3 -m pip install -r skill/requirements.txt
```

随后直接运行：

```bash
python3 skill/scripts/check_env.py
python3 skill/scripts/siyuan_cli.py health --format text
```

### 方式二：安装到其它智能体或工具

如果目标环境支持“目录内以 `SKILL.md` 为入口”的 skill 发现方式，直接把 `skill/` 目录作为一个独立 skill 安装即可。

如果你想把它复制到另一个项目中，直接复制整个 `skill/` 目录：

```bash
cp -R skill /path/to/project/your-siyuan-skill
```

命令入口为：

```bash
python3 /path/to/project/your-siyuan-skill/skill/scripts/siyuan_cli.py health
```

### 方式三：安装到统一技能目录

如果某个 Agent 或工具有统一的技能目录，直接把 `skill/` 复制进去即可：

```bash
mkdir -p ~/.codex/skills/siyuan
cp -R skill/* ~/.codex/skills/siyuan/
```

CLI 会以安装后的 skill 目录为根目录，读取同目录下的 `requirements.txt` 和 `.env`。

### 方式四：软链接安装

开发阶段更适合软链接，便于更新后立即生效：

```bash
mkdir -p ~/.codex/skills
ln -s "/absolute/path/to/siyuan-skills/skill" ~/.codex/skills/siyuan
```

对于其它支持 skill 目录软链接的 Agent 或工具，也建议直接链接 `skill/`：

```bash
ln -s "/absolute/path/to/siyuan-skills/skill" /path/to/project/your-siyuan-skill
```

## 快速验证

```bash
python3 skill/scripts/check_env.py
python3 skill/scripts/siyuan_cli.py health --format text
python3 skill/scripts/siyuan_cli.py notebooks list --format markdown
```

## 常用命令

```bash
python3 skill/scripts/siyuan_cli.py health
python3 skill/scripts/siyuan_cli.py notebooks list --format markdown
python3 skill/scripts/siyuan_cli.py docs read <doc_id> --format text
python3 skill/scripts/siyuan_cli.py query sql --stmt "select * from blocks limit 5"
python3 skill/scripts/siyuan_cli.py workspace smart-write --title "示例" --category "研究笔记" --input-file /tmp/example.md
```

## 功能覆盖

Python CLI 已覆盖此前 shell SDK 暴露的全部 API endpoint，包含：

- `health`
- `notebooks`
- `docs`
- `blocks`
- `query`
- `attrs`
- `assets`
- `files`
- `ref`
- `notifications`
- `templates`
- `riff`
- `tags`
- `bookmarks`
- `history`
- `graph`
- `system`
- `imports`
- `workspace`

说明：

- `health`、`workspace ensure`、`workspace write`、`workspace smart-write` 属于在原始 API 之上增加的 helper 工作流
- 旧的 shell 实现已经移除，后续只维护 Python CLI

## 多 Agent 兼容性

当前仓库已经具备更通用的独立 skill 目录形态：

- 有独立 `skill/SKILL.md`
- 有可执行脚本入口
- 有 `skill/references/` 和 `skill/scripts/`
- 默认输出结构化 JSON

但它不是“所有 Agent 零配置自动发现”的通用发布格式，原因是：

- 不同 Agent 对 skill 安装目录仍然有各自约定
- 但 skill 主体已经集中在单独的 `skill/` 目录，不再和项目开发文件混放

因此更准确的结论是：

- 作为项目内 skill：格式是标准的
- 作为跨 Agent 分发包：还需要按各 Agent 的技能目录做安装或软链接

## 开发建议

- 新功能继续加在 `skill/python/siyuan_skill/operations/`
- 输出统一走 `formatters.py` / `conversions.py`
- 不再恢复 shell 版实现
- 写入型操作保持 `AgentWorkspace` 和分类写入约定
