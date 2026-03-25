#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
PYTHON_DIR = SKILL_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from bootstrap import ensure_runtime

ensure_runtime(auto_install=True)

from siyuan_skill.client import SiYuanClient
from siyuan_skill.config import SiYuanConfig
from siyuan_skill.formatters import OperationResult, render_result
from siyuan_skill.operations import (
    AssetOperations,
    AttrOperations,
    BlockOperations,
    BookmarkOperations,
    DocOperations,
    FileOperations,
    GraphOperations,
    HistoryOperations,
    ImportOperations,
    NotebookOperations,
    NotificationOperations,
    QueryOperations,
    RefOperations,
    RiffOperations,
    SystemOperations,
    TagOperations,
    TemplateOperations,
    WorkspaceOperations,
)


def build_runtime_parent() -> argparse.ArgumentParser:
    runtime = argparse.ArgumentParser(add_help=False)
    runtime.add_argument("--format", choices=["json", "markdown", "csv", "text"], default=None)
    runtime.add_argument("--host", default=None)
    runtime.add_argument("--token", default=None)
    runtime.add_argument("--password", default=None)
    runtime.add_argument("--timeout", type=float, default=None)
    return runtime


def build_parser() -> argparse.ArgumentParser:
    runtime_parent = build_runtime_parent()
    parser = argparse.ArgumentParser(
        description="SiYuan Python CLI",
        parents=[runtime_parent],
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", parents=[runtime_parent])

    notebooks = subparsers.add_parser("notebooks", parents=[runtime_parent])
    notebook_sub = notebooks.add_subparsers(dest="action", required=True)
    notebook_sub.add_parser("list", parents=[runtime_parent])
    notebook_create = notebook_sub.add_parser("create", parents=[runtime_parent])
    notebook_create.add_argument("name")
    notebook_open = notebook_sub.add_parser("open", parents=[runtime_parent])
    notebook_open.add_argument("id")
    notebook_close = notebook_sub.add_parser("close", parents=[runtime_parent])
    notebook_close.add_argument("id")
    notebook_rename = notebook_sub.add_parser("rename", parents=[runtime_parent])
    notebook_rename.add_argument("id")
    notebook_rename.add_argument("name")
    notebook_remove = notebook_sub.add_parser("remove", parents=[runtime_parent])
    notebook_remove.add_argument("id")
    notebook_conf = notebook_sub.add_parser("conf", parents=[runtime_parent])
    notebook_conf.add_argument("id")
    notebook_find = notebook_sub.add_parser("find", parents=[runtime_parent])
    notebook_find.add_argument("keyword")
    notebook_sub.add_parser("ensure-workspace", parents=[runtime_parent])

    docs = subparsers.add_parser("docs", parents=[runtime_parent])
    doc_sub = docs.add_subparsers(dest="action", required=True)
    doc_create = doc_sub.add_parser("create-md", parents=[runtime_parent])
    doc_create.add_argument("--notebook", required=True)
    doc_create.add_argument("--path", required=True)
    doc_create.add_argument("--markdown")
    doc_create.add_argument("--input-file")
    doc_read = doc_sub.add_parser("read", parents=[runtime_parent])
    doc_read.add_argument("id")
    doc_export = doc_sub.add_parser("export-md", parents=[runtime_parent])
    doc_export.add_argument("id")
    doc_outline = doc_sub.add_parser("outline", parents=[runtime_parent])
    doc_outline.add_argument("id")
    doc_list = doc_sub.add_parser("list", parents=[runtime_parent])
    doc_list.add_argument("--notebook", required=True)
    doc_list.add_argument("--path", default="/")
    doc_list.add_argument("--sort", type=int, default=0)
    doc_hpath = doc_sub.add_parser("get-hpath", parents=[runtime_parent])
    doc_hpath.add_argument("id")
    doc_path = doc_sub.add_parser("get-path", parents=[runtime_parent])
    doc_path.add_argument("id")
    doc_ids = doc_sub.add_parser("get-ids", parents=[runtime_parent])
    doc_ids.add_argument("--hpath", required=True)
    doc_ids.add_argument("--notebook", required=True)
    doc_rename = doc_sub.add_parser("rename", parents=[runtime_parent])
    doc_rename.add_argument("id")
    doc_rename.add_argument("title")
    doc_rename_path = doc_sub.add_parser("rename-path", parents=[runtime_parent])
    doc_rename_path.add_argument("--notebook", required=True)
    doc_rename_path.add_argument("--path", required=True)
    doc_rename_path.add_argument("--title", required=True)
    doc_remove = doc_sub.add_parser("remove", parents=[runtime_parent])
    doc_remove.add_argument("id")
    doc_remove_path = doc_sub.add_parser("remove-path", parents=[runtime_parent])
    doc_remove_path.add_argument("--notebook", required=True)
    doc_remove_path.add_argument("--path", required=True)
    doc_move = doc_sub.add_parser("move", parents=[runtime_parent])
    doc_move.add_argument("--from-path", action="append", required=True)
    doc_move.add_argument("--to-notebook", required=True)
    doc_move.add_argument("--to-path", required=True)

    blocks = subparsers.add_parser("blocks", parents=[runtime_parent])
    block_sub = blocks.add_subparsers(dest="action", required=True)
    for action_name in ["append", "prepend", "insert", "update"]:
        block_cmd = block_sub.add_parser(action_name, parents=[runtime_parent])
        block_cmd.add_argument("--markdown")
        block_cmd.add_argument("--input-file")
        if action_name == "insert":
            block_cmd.add_argument("--previous-id", required=True)
        elif action_name == "update":
            block_cmd.add_argument("--block-id", required=True)
        else:
            block_cmd.add_argument("--parent-id", required=True)
    block_delete = block_sub.add_parser("delete", parents=[runtime_parent])
    block_delete.add_argument("id")
    block_move = block_sub.add_parser("move", parents=[runtime_parent])
    block_move.add_argument("id")
    block_move.add_argument("--previous-id")
    block_move.add_argument("--parent-id")
    block_info = block_sub.add_parser("info", parents=[runtime_parent])
    block_info.add_argument("id")
    block_children = block_sub.add_parser("children", parents=[runtime_parent])
    block_children.add_argument("id")
    block_kramdown = block_sub.add_parser("get-kramdown", parents=[runtime_parent])
    block_kramdown.add_argument("id")
    block_dom = block_sub.add_parser("get-dom", parents=[runtime_parent])
    block_dom.add_argument("id")
    block_fold = block_sub.add_parser("fold", parents=[runtime_parent])
    block_fold.add_argument("id")
    block_unfold = block_sub.add_parser("unfold", parents=[runtime_parent])
    block_unfold.add_argument("id")
    block_batch_append = block_sub.add_parser("batch-append", parents=[runtime_parent])
    block_batch_append.add_argument("--parent-id", required=True)
    block_batch_append.add_argument("--markdown", action="append")
    block_batch_append.add_argument("--input-file", action="append")
    block_batch_update = block_sub.add_parser("batch-update", parents=[runtime_parent])
    block_batch_update.add_argument("--blocks")
    block_batch_update.add_argument("--blocks-file")

    query = subparsers.add_parser("query", parents=[runtime_parent])
    query_sub = query.add_subparsers(dest="action", required=True)
    query_sql = query_sub.add_parser("sql", parents=[runtime_parent])
    query_sql.add_argument("--stmt", required=True)
    query_search = query_sub.add_parser("search-blocks", parents=[runtime_parent])
    query_search.add_argument("keyword")
    query_search.add_argument("--limit", type=int, default=20)
    query_tag = query_sub.add_parser("search-tag", parents=[runtime_parent])
    query_tag.add_argument("tag")
    query_tag.add_argument("--limit", type=int, default=20)
    query_tag_api = query_sub.add_parser("search-tag-api", parents=[runtime_parent])
    query_tag_api.add_argument("keyword")
    query_fulltext = query_sub.add_parser("fulltext", parents=[runtime_parent])
    query_fulltext.add_argument("query")
    query_fulltext.add_argument("--page", type=int, default=1)
    query_docs = query_sub.add_parser("list-docs", parents=[runtime_parent])
    query_docs.add_argument("--limit", type=int, default=50)
    query_recent = query_sub.add_parser("recent", parents=[runtime_parent])
    query_recent.add_argument("--limit", type=int, default=20)

    attrs = subparsers.add_parser("attrs", parents=[runtime_parent])
    attr_sub = attrs.add_subparsers(dest="action", required=True)
    attr_get = attr_sub.add_parser("get", parents=[runtime_parent])
    attr_get.add_argument("id")
    attr_set = attr_sub.add_parser("set", parents=[runtime_parent])
    attr_set.add_argument("id")
    attr_set.add_argument("--attrs", required=True, help="JSON object")

    assets = subparsers.add_parser("assets", parents=[runtime_parent])
    asset_sub = assets.add_subparsers(dest="action", required=True)
    asset_upload = asset_sub.add_parser("upload", parents=[runtime_parent])
    asset_upload.add_argument("file_path")
    asset_upload.add_argument("--assets-dir", default="/assets/")

    files = subparsers.add_parser("files", parents=[runtime_parent])
    file_sub = files.add_subparsers(dest="action", required=True)
    file_get = file_sub.add_parser("get", parents=[runtime_parent])
    file_get.add_argument("path")
    file_read_dir = file_sub.add_parser("read-dir", parents=[runtime_parent])
    file_read_dir.add_argument("path")
    file_remove = file_sub.add_parser("remove", parents=[runtime_parent])
    file_remove.add_argument("path")

    refs = subparsers.add_parser("ref", parents=[runtime_parent])
    ref_sub = refs.add_subparsers(dest="action", required=True)
    ref_backlinks = ref_sub.add_parser("backlinks", parents=[runtime_parent])
    ref_backlinks.add_argument("id")
    ref_backlinks.add_argument("--sort", default="3")
    ref_backlinks.add_argument("--m-sort", default="3")

    notifications = subparsers.add_parser("notifications", parents=[runtime_parent])
    notification_sub = notifications.add_subparsers(dest="action", required=True)
    push_msg = notification_sub.add_parser("push-msg", parents=[runtime_parent])
    push_msg.add_argument("message")
    push_msg.add_argument("--message-timeout", dest="message_timeout", type=int, default=7000)
    push_err = notification_sub.add_parser("push-err", parents=[runtime_parent])
    push_err.add_argument("message")
    push_err.add_argument("--message-timeout", dest="message_timeout", type=int, default=7000)

    templates = subparsers.add_parser("templates", parents=[runtime_parent])
    template_sub = templates.add_subparsers(dest="action", required=True)
    template_render = template_sub.add_parser("render", parents=[runtime_parent])
    template_render.add_argument("--id", required=True)
    template_render.add_argument("--path", required=True)
    template_sprig = template_sub.add_parser("render-sprig", parents=[runtime_parent])
    template_sprig.add_argument("--template")
    template_sprig.add_argument("--input-file")

    riff = subparsers.add_parser("riff", parents=[runtime_parent])
    riff_sub = riff.add_subparsers(dest="action", required=True)
    riff_create = riff_sub.add_parser("create-deck", parents=[runtime_parent])
    riff_create.add_argument("name")
    riff_sub.add_parser("list-decks", parents=[runtime_parent])
    riff_add = riff_sub.add_parser("add-cards", parents=[runtime_parent])
    riff_add.add_argument("deck_id")
    riff_add.add_argument("--block-id", action="append", required=True)
    riff_due = riff_sub.add_parser("due-cards", parents=[runtime_parent])
    riff_due.add_argument("--deck-id")
    riff_review = riff_sub.add_parser("review-card", parents=[runtime_parent])
    riff_review.add_argument("deck_id")
    riff_review.add_argument("card_id")
    riff_review.add_argument("rating", type=int)

    tags = subparsers.add_parser("tags", parents=[runtime_parent])
    tag_sub = tags.add_subparsers(dest="action", required=True)
    tag_sub.add_parser("list", parents=[runtime_parent])
    tag_rename = tag_sub.add_parser("rename", parents=[runtime_parent])
    tag_rename.add_argument("old_label")
    tag_rename.add_argument("new_label")

    bookmarks = subparsers.add_parser("bookmarks", parents=[runtime_parent])
    bookmark_sub = bookmarks.add_subparsers(dest="action", required=True)
    bookmark_sub.add_parser("list", parents=[runtime_parent])

    history = subparsers.add_parser("history", parents=[runtime_parent])
    history_sub = history.add_subparsers(dest="action", required=True)
    history_doc = history_sub.add_parser("get-doc", parents=[runtime_parent])
    history_doc.add_argument("history_path")
    history_search = history_sub.add_parser("search", parents=[runtime_parent])
    history_search.add_argument("query")
    history_search.add_argument("--page", type=int, default=1)
    history_search.add_argument("--history-type", type=int, default=0)

    graph = subparsers.add_parser("graph", parents=[runtime_parent])
    graph_sub = graph.add_subparsers(dest="action", required=True)
    graph_sub.add_parser("global", parents=[runtime_parent])
    graph_local = graph_sub.add_parser("local", parents=[runtime_parent])
    graph_local.add_argument("id")

    system = subparsers.add_parser("system", parents=[runtime_parent])
    system_sub = system.add_subparsers(dest="action", required=True)
    system_sub.add_parser("version", parents=[runtime_parent])
    system_sub.add_parser("conf", parents=[runtime_parent])
    system_sub.add_parser("boot-progress", parents=[runtime_parent])

    imports = subparsers.add_parser("imports", parents=[runtime_parent])
    import_sub = imports.add_subparsers(dest="action", required=True)
    import_std = import_sub.add_parser("import-std-md", parents=[runtime_parent])
    import_std.add_argument("--notebook", required=True)
    import_std.add_argument("--local-path", required=True)

    workspace = subparsers.add_parser("workspace", parents=[runtime_parent])
    workspace_sub = workspace.add_subparsers(dest="action", required=True)
    workspace_sub.add_parser("ensure", parents=[runtime_parent])
    workspace_write = workspace_sub.add_parser("write", parents=[runtime_parent])
    workspace_write.add_argument("--category", required=True)
    workspace_write.add_argument("--title", required=True)
    workspace_write.add_argument("--markdown")
    workspace_write.add_argument("--input-file")
    workspace_smart = workspace_sub.add_parser("smart-write", parents=[runtime_parent])
    workspace_smart.add_argument("--title", required=True)
    workspace_smart.add_argument("--markdown")
    workspace_smart.add_argument("--input-file")
    workspace_smart.add_argument("--notebook-hint")
    workspace_smart.add_argument("--category")

    return parser


def create_client(args: argparse.Namespace) -> SiYuanClient:
    config = SiYuanConfig.load(
        host=args.host,
        token=args.token,
        password=args.password,
        timeout=args.timeout,
        default_format=args.format,
    )
    return SiYuanClient(config)


def resolve_text(direct_text: str | None, input_file: str | None, *, error_message: str) -> str:
    if direct_text is not None:
        return direct_text
    if input_file:
        return Path(input_file).read_text(encoding="utf-8")
    raise ValueError(error_message)


def resolve_text_list(
    direct_texts: list[str] | None,
    input_files: list[str] | None,
    *,
    error_message: str,
) -> list[str]:
    values = list(direct_texts or [])
    for file_path in input_files or []:
        values.append(Path(file_path).read_text(encoding="utf-8"))
    if not values:
        raise ValueError(error_message)
    return values


def load_json_value(raw_json: str | None, input_file: str | None, *, error_message: str) -> Any:
    if raw_json is not None:
        return json.loads(raw_json)
    if input_file:
        return json.loads(Path(input_file).read_text(encoding="utf-8"))
    raise ValueError(error_message)


def health_result(client: SiYuanClient) -> OperationResult:
    status = client.health_status()
    return OperationResult(
        endpoint="/api/system/version",
        data=status,
        summary=f"思源已连接，版本 {status['version']}，笔记本数量 {status['notebook_count']}",
    )


def dispatch(args: argparse.Namespace, client: SiYuanClient) -> OperationResult:
    notebooks = NotebookOperations(client)
    docs = DocOperations(client)
    blocks = BlockOperations(client)
    query = QueryOperations(client)
    attrs = AttrOperations(client)
    assets = AssetOperations(client)
    files = FileOperations(client)
    refs = RefOperations(client)
    notifications = NotificationOperations(client)
    templates = TemplateOperations(client)
    riff = RiffOperations(client)
    tags = TagOperations(client)
    bookmarks = BookmarkOperations(client)
    history = HistoryOperations(client)
    graph = GraphOperations(client)
    system = SystemOperations(client)
    imports = ImportOperations(client)
    workspace = WorkspaceOperations(client)

    if args.command == "health":
        return health_result(client)

    if args.command == "notebooks":
        if args.action == "list":
            return notebooks.list()
        if args.action == "create":
            return notebooks.create(args.name)
        if args.action == "open":
            return notebooks.open(args.id)
        if args.action == "close":
            return notebooks.close(args.id)
        if args.action == "rename":
            return notebooks.rename(args.id, args.name)
        if args.action == "remove":
            return notebooks.remove(args.id)
        if args.action == "conf":
            return notebooks.get_conf(args.id)
        if args.action == "find":
            return notebooks.find(args.keyword)
        if args.action == "ensure-workspace":
            return notebooks.ensure_agent_workspace()

    if args.command == "docs":
        if args.action == "create-md":
            return docs.create_markdown(
                args.notebook,
                args.path,
                resolve_text(args.markdown, args.input_file, error_message="需要提供 --markdown 或 --input-file"),
            )
        if args.action == "read":
            return docs.read_doc(args.id)
        if args.action == "export-md":
            return docs.export_markdown(args.id)
        if args.action == "outline":
            return docs.outline(args.id)
        if args.action == "list":
            return docs.list(args.notebook, args.path, args.sort)
        if args.action == "get-hpath":
            return docs.get_hpath_by_id(args.id)
        if args.action == "get-path":
            return docs.get_path_by_id(args.id)
        if args.action == "get-ids":
            return docs.get_ids_by_hpath(args.hpath, args.notebook)
        if args.action == "rename":
            return docs.rename_by_id(args.id, args.title)
        if args.action == "rename-path":
            return docs.rename(args.notebook, args.path, args.title)
        if args.action == "remove":
            return docs.remove_by_id(args.id)
        if args.action == "remove-path":
            return docs.remove(args.notebook, args.path)
        if args.action == "move":
            return docs.move_docs(args.from_path, args.to_notebook, args.to_path)

    if args.command == "blocks":
        if args.action == "append":
            return blocks.append(resolve_text(args.markdown, args.input_file, error_message="需要提供 --markdown 或 --input-file"), args.parent_id)
        if args.action == "prepend":
            return blocks.prepend(resolve_text(args.markdown, args.input_file, error_message="需要提供 --markdown 或 --input-file"), args.parent_id)
        if args.action == "insert":
            return blocks.insert_after(resolve_text(args.markdown, args.input_file, error_message="需要提供 --markdown 或 --input-file"), args.previous_id)
        if args.action == "update":
            return blocks.update(resolve_text(args.markdown, args.input_file, error_message="需要提供 --markdown 或 --input-file"), args.block_id)
        if args.action == "delete":
            return blocks.delete(args.id)
        if args.action == "move":
            if not args.previous_id and not args.parent_id:
                raise ValueError("blocks move 需要至少提供 --previous-id 或 --parent-id")
            return blocks.move(args.id, args.previous_id, args.parent_id)
        if args.action == "info":
            return blocks.get_info(args.id)
        if args.action == "children":
            return blocks.children(args.id)
        if args.action == "get-kramdown":
            return blocks.get_kramdown(args.id)
        if args.action == "get-dom":
            return blocks.get_dom(args.id)
        if args.action == "fold":
            return blocks.fold(args.id)
        if args.action == "unfold":
            return blocks.unfold(args.id)
        if args.action == "batch-append":
            datas = resolve_text_list(
                args.markdown,
                args.input_file,
                error_message="batch-append 需要至少一个 --markdown 或 --input-file",
            )
            return blocks.batch_append(args.parent_id, datas)
        if args.action == "batch-update":
            block_payload = load_json_value(args.blocks, args.blocks_file, error_message="需要提供 --blocks 或 --blocks-file")
            if not isinstance(block_payload, list):
                raise ValueError("batch-update 需要 JSON 数组")
            return blocks.batch_update(block_payload)

    if args.command == "query":
        if args.action == "sql":
            return query.sql(args.stmt)
        if args.action == "search-blocks":
            return query.search_blocks(args.keyword, args.limit)
        if args.action == "search-tag":
            return query.search_by_tag(args.tag, args.limit)
        if args.action == "search-tag-api":
            return query.search_tag(args.keyword)
        if args.action == "fulltext":
            return query.fulltext_search(args.query, args.page)
        if args.action == "list-docs":
            return query.list_all_docs(args.limit)
        if args.action == "recent":
            return query.recent_blocks(args.limit)

    if args.command == "attrs":
        if args.action == "get":
            return attrs.get(args.id)
        if args.action == "set":
            return attrs.set(args.id, json.loads(args.attrs))

    if args.command == "assets":
        if args.action == "upload":
            return assets.upload(args.file_path, args.assets_dir)

    if args.command == "files":
        if args.action == "get":
            return files.get_file(args.path)
        if args.action == "read-dir":
            return files.read_dir(args.path)
        if args.action == "remove":
            return files.remove_file(args.path)

    if args.command == "ref":
        if args.action == "backlinks":
            return refs.backlinks(args.id, args.sort, args.m_sort)

    if args.command == "notifications":
        if args.action == "push-msg":
            return notifications.push_msg(args.message, args.message_timeout)
        if args.action == "push-err":
            return notifications.push_err_msg(args.message, args.message_timeout)

    if args.command == "templates":
        if args.action == "render":
            return templates.render(args.id, args.path)
        if args.action == "render-sprig":
            return templates.render_sprig(
                resolve_text(args.template, args.input_file, error_message="需要提供 --template 或 --input-file")
            )

    if args.command == "riff":
        if args.action == "create-deck":
            return riff.create_deck(args.name)
        if args.action == "list-decks":
            return riff.get_decks()
        if args.action == "add-cards":
            return riff.add_cards(args.deck_id, args.block_id)
        if args.action == "due-cards":
            return riff.get_due_cards(args.deck_id)
        if args.action == "review-card":
            return riff.review_card(args.deck_id, args.card_id, args.rating)

    if args.command == "tags":
        if args.action == "list":
            return tags.get_tags()
        if args.action == "rename":
            return tags.rename_tag(args.old_label, args.new_label)

    if args.command == "bookmarks":
        if args.action == "list":
            return bookmarks.get_bookmarks()

    if args.command == "history":
        if args.action == "get-doc":
            return history.get_doc_history(args.history_path)
        if args.action == "search":
            return history.search_history(args.query, args.page, args.history_type)

    if args.command == "graph":
        if args.action == "global":
            return graph.get_graph()
        if args.action == "local":
            return graph.get_local_graph(args.id)

    if args.command == "system":
        if args.action == "version":
            return system.version()
        if args.action == "conf":
            return system.get_conf()
        if args.action == "boot-progress":
            return system.boot_progress()

    if args.command == "imports":
        if args.action == "import-std-md":
            return imports.import_std_md(args.notebook, args.local_path)

    if args.command == "workspace":
        if args.action == "ensure":
            return workspace.ensure_workspace()
        if args.action == "write":
            return workspace.write_to_workspace(
                args.category,
                args.title,
                resolve_text(args.markdown, args.input_file, error_message="需要提供 --markdown 或 --input-file"),
            )
        if args.action == "smart-write":
            return workspace.smart_write(
                resolve_text(args.markdown, args.input_file, error_message="需要提供 --markdown 或 --input-file"),
                args.title,
                args.notebook_hint,
                args.category,
            )

    raise ValueError("未识别的命令")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    client = create_client(args)
    result = dispatch(args, client)
    output_format = args.format or client.config.default_format
    print(render_result(result, output_format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
