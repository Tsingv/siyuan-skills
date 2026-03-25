# AGENTS.md

## 项目概览

本仓库用于提供一个可复用的 SiYuan（思源笔记）集成能力，当前主实现已经从 shell SDK 迁移为 **Python CLI + 标准 skill 结构**。

当前推荐入口：
- 标准 skill：`skill/SKILL.md`
- 主执行入口：`skill/scripts/siyuan_cli.py`

---

## 当前架构

### 目录

```text
.
├── AGENTS.md
├── README.md
└── skill/
    ├── SKILL.md
    ├── requirements.txt
    ├── pyproject.toml
    ├── references/
    │   ├── auth-and-config.md
    │   ├── output-format-spec.md
    │   ├── pandas-conversion-guide.md
    │   └── migration-notes.md
    ├── scripts/
    │   ├── bootstrap.py
    │   ├── check_env.py
    │   └── siyuan_cli.py
    └── python/
        └── siyuan_skill/
            ├── __init__.py
            ├── auth.py
            ├── client.py
            ├── config.py
            ├── conversions.py
            ├── errors.py
            ├── formatters.py
            └── operations/
```

### 分层说明

- `skill/scripts/bootstrap.py`
  - 检查 Python 版本与依赖
  - 缺失依赖时自动安装
- `skill/python/siyuan_skill/config.py`
  - 统一读取配置
- `skill/python/siyuan_skill/auth.py`
  - 处理 token / password 登录与缓存
- `skill/python/siyuan_skill/client.py`
  - 统一 HTTP 调用与鉴权重试
- `skill/python/siyuan_skill/formatters.py`
  - 统一输出 `json / markdown / csv / text`
- `skill/python/siyuan_skill/conversions.py`
  - 统一 pandas/DataFrame 转换
- `skill/python/siyuan_skill/operations/*.py`
  - 按领域组织 API 能力

---

## 运行方式

统一使用 Python CLI。

示例：

```bash
python3 skill/scripts/siyuan_cli.py health
python3 skill/scripts/siyuan_cli.py notebooks list --format markdown
python3 skill/scripts/siyuan_cli.py query sql --stmt "select * from blocks limit 5"
```

说明：
- 全局参数支持：`--format`、`--host`、`--token`、`--password`、`--timeout`
- 这些参数可以放在顶层命令前，也可以放在子命令后
- 通知命令额外使用 `--message-timeout`，不要与全局 `--timeout` 混淆

---

## 依赖与运行环境

### Python 要求

- Python `>=3.10`

### 项目依赖

来自 `requirements.txt` / `pyproject.toml`：
- `requests>=2.32.0`
- `python-dotenv>=1.0.1`
- `pandas>=2.2.0`
- `tabulate>=0.9.0`

### 自动安装

CLI 启动时会先执行 `bootstrap.py`：
1. 检查 Python 版本
2. 检查依赖是否可 import
3. 若缺失，则自动执行：
   ```bash
   python3 -m pip install -r requirements.txt
   ```

---

## 配置与认证

配置优先级：
1. CLI 参数
2. 环境变量
3. 项目根目录 `.env`
4. 默认值

支持的配置：
- `SIYUAN_HOST`
- `SIYUAN_TOKEN`
- `PASSWORD`
- `SIYUAN_TIMEOUT`
- `SIYUAN_OUTPUT_FORMAT`

默认地址：
- `http://127.0.0.1:6806`

认证流程：
1. 若有 `SIYUAN_TOKEN`，直接使用
2. 否则尝试读取缓存 token
3. 若仍无 token，则使用 `PASSWORD` 调 `/api/system/loginAuth`
4. 再调 `/api/system/getConf` 获取 token
5. 若 token 失效，自动重试一次

Token 缓存位置：
- `~/.cache/siyuan-skill/token.json`

---

## 输出规范

默认输出格式是 `json`，最适合 Agent 消费。

支持格式：
- `json`
- `markdown`
- `csv`
- `text`

### 标准 JSON envelope

```json
{
  "ok": true,
  "endpoint": "/api/notebook/lsNotebooks",
  "data": [],
  "meta": {
    "format": "json",
    "tabular": true,
    "row_count": 0,
    "columns": ["id", "name"]
  }
}
```

### pandas 使用规则

只在 **同构 `list[dict]`** 结果上使用 pandas，例如：
- notebook 列表
- SQL 查询
- 搜索结果
- 最近更新块
- 文档列表
- 标签、书签、牌组等列表型结果

不要强制转 DataFrame 的结果：
- 文档 Markdown 原文
- 大纲树
- 图谱
- 任意嵌套 JSON
- 上传结果

额外规则：
- `None` 统一转空串
- 嵌套对象会转 JSON 字符串并截断长文本
- markdown 表格默认展示前 50 行
- CSV 仅用于表格型结果

---

## 写入流程

当用户要求写入内容到思源时，必须先确认：

1. 写入到哪个笔记本
   - 笔记本 ID
   - 笔记本名称（模糊匹配）
   - 默认：`AgentWorkspace`

2. 写入到哪个位置
   - 创建新文档
   - 追加到已有文档/块
   - 自动归类到 `AgentWorkspace`

默认行为：
- notebook：`AgentWorkspace`
- mode：`workspace write` 或 `workspace smart-write`

默认分类可用：
- `研究笔记`
- `会议记录`
- `代码片段`
- `TODO`
- `参考资料`
- `日志`

---

## 已迁移的能力范围

当前 Python CLI 已覆盖以下能力组：

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

其中通知命令为：
- `notifications push-msg`
- `notifications push-err`

并使用：
- `--message-timeout`

---

## 已验证的代表命令

以下命令已实际验证通过：

```bash
python3 skill/scripts/siyuan_cli.py health --format text
python3 skill/scripts/siyuan_cli.py notebooks list --format markdown
python3 skill/scripts/siyuan_cli.py docs read <doc_id> --format text
python3 skill/scripts/siyuan_cli.py docs get-path <doc_id> --format json
python3 skill/scripts/siyuan_cli.py blocks info <block_id> --format json
python3 skill/scripts/siyuan_cli.py query recent --limit 1 --format json
python3 skill/scripts/siyuan_cli.py system version --format text
python3 skill/scripts/siyuan_cli.py tags list --format markdown
python3 skill/scripts/siyuan_cli.py bookmarks list --format markdown
python3 skill/scripts/siyuan_cli.py graph local <block_id> --format text
python3 skill/scripts/siyuan_cli.py ref backlinks <block_id> --format text
python3 skill/scripts/siyuan_cli.py templates render-sprig --template '{{ "hi" | upper }}' --format text
python3 skill/scripts/siyuan_cli.py riff list-decks --format json
python3 skill/scripts/siyuan_cli.py files read-dir / --format json
python3 skill/scripts/siyuan_cli.py notifications push-msg "hello" --message-timeout 1500 --format text
```

---

## 面向后续 Agent 的工作约定

### 做新增功能时

优先顺序：
1. 先看 `skill/SKILL.md`
2. 再看 `skill/references/*.md`
3. 然后查看对应 `skill/python/siyuan_skill/operations/*.py`
4. 最后查看 `skill/references/migration-notes.md`

### 修改原则

- 新功能优先加到 Python CLI
- 输出风格必须走 `formatters.py` / `conversions.py`
- 列表型结果要显式声明是否 `tabular`
- 尽量为表格型结果提供稳定 `columns`
- 不要在业务层随意拼 markdown/csv
- 如果是写入型操作，遵循写入确认流程

### 兼容原则

- 标准 skill 入口始终是 `skill/SKILL.md`

---

## 推荐的排查顺序

如果 CLI 有问题，按这个顺序排查：

1. `python3 skill/scripts/siyuan_cli.py health --format text`
2. `python3 skill/scripts/check_env.py`
3. 检查 `.env` 中的 `SIYUAN_TOKEN` / `PASSWORD`
4. 检查思源本地实例是否运行在 `127.0.0.1:6806`
5. 检查 `auth.py`、`client.py`、`config.py`
6. 再检查对应 `operations/*.py`

---

## 相关文件

关键文件：
- `skill/SKILL.md`
- `skill/scripts/siyuan_cli.py`
- `skill/scripts/bootstrap.py`
- `skill/python/siyuan_skill/config.py`
- `skill/python/siyuan_skill/auth.py`
- `skill/python/siyuan_skill/client.py`
- `skill/python/siyuan_skill/formatters.py`
- `skill/python/siyuan_skill/conversions.py`
- `skill/references/auth-and-config.md`
- `skill/references/output-format-spec.md`
- `skill/references/pandas-conversion-guide.md`
- `skill/references/migration-notes.md`

---

## 一句话结论

这个仓库现在已经是一个 **以 Python CLI 为主、将 skill 资源独立收纳在 `skill/` 目录下、可被其他 Agent 发现和复用的 SiYuan skill 项目**。后续工作应继续围绕 `skill/SKILL.md / skill/scripts / skill/python / skill/references` 结构演进。
