#!/usr/bin/env python3
"""Build EPUB and a server-independent static reading site from the same chapters."""
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CONFIG = json.loads((ROOT / 'edition.json').read_text())
TITLE = CONFIG['title']
SUBTITLE = CONFIG['subtitle']
EDITION = CONFIG['edition']
SOURCE_COUNT = len(json.loads((ROOT / 'research/sources.json').read_text())['files'])
REPOSITORY = 'https://github.com/Aias00/coding-agent-book'
PUBLIC = 'https://aias00.github.io/coding-agent-book/'
EPUB = 'coding-agent-engineering.epub'

def pandoc(body, *args):
    return subprocess.run(['pandoc', '--from=markdown', *args], input=body,
        text=True, capture_output=True, check=True).stdout

def references(body, prefix=''):
    return re.sub(r'〔([CDPA]\d{2})〕', lambda m: f'[{m[1]}]({prefix}#evidence-{m[1].lower()})', body)

def make_sources(snapshot):
    rows = ['# 附录 B 源码快照与证据索引\n',
        '研究日期为 2026-10-30。以下链接固定到所读提交，行号是定位入口而非整章唯一依据。所有 SHA-256 来自本地文件原始字节。没有上传上游源码。\n',
        '## 快照身份\n', '| 项目 | 提交或包版本 | 说明 |', '|---|---|---|']
    for name, project in snapshot['projects'].items():
        commit = project['commit'] or 'Claude Code 2.1.88；无 Git 提交'
        note = 'Git 工作区干净' if project['working_tree_status'] == '' else (
            '仅有未跟踪 docs/epub/；本书不将其作为实现证据' if name == 'codex' else '按发布包与 source map 标识')
        rows.append(f'| {name} | `{commit}` | {note} |')
    rows += ['\n## 材料与验证方法\n',
        f'研究脚本记录 {len(snapshot["files"])} 个文件。Claude Code 被引用的提取实现逐一与 `cli.js.map` 内对应 `sourcesContent` 对照；这验证本地一致性，不替代发布包来源认证或构建可达性证明。研究材料中有既有书稿和压缩包，本书未将其并入分析正文。\n',
        '这些快照作为设计方案的参考依据。可运行参考内核和故障实验见第 23 章；完整方案包含明确标注的扩展设计。未构建四个上游项目或执行统一真实模型评测。\n']
    for row in snapshot['files']:
        key = row['id']
        rows += [f'## {key} · {row["project"]} {{#evidence-{key.lower()}}}\n',
            f'- 相对路径：`{row["project"]}/{row["path"]}`',
            f'- 定位：第 {row["line"]} 行，`{row["locator"]}`；文件共 {row["lines"]} 行。',
            f'- SHA-256：`{row["sha256"]}`']
        if row['url']:
            rows.append(f'- [固定提交源码]({row["url"]})')
        if row.get('matches_embedded_source'):
            rows.append('- 本地提取文本与发布包 source map 嵌入文本一致。')
        rows.append('')
    rows += ['## 官方补充资料\n',
        '- [OpenAI：Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform)，访问日期 2026-10-30，仅用于 harness 术语与职责说明。',
        '- 开源项目的许可证与署名见仓库 `NOTICE.md` 和 `LICENSES/`。\n']
    return '\n'.join(rows).rstrip() + '\n'

def group(stem):
    n = int(stem.split('-')[0])
    return next(label for maximum, label in CONFIG['sections'] if n <= maximum)

def navigation(chapters, current):
    items = ['<nav aria-label="全书目录">']
    last = None
    for c in chapters:
        section = group(c['stem'])
        if section != last:
            if last is not None: items.append('</ul>')
            items.append(f'<p class="nav-group">{section}</p><ul>')
            last = section
        active = ' aria-current="page"' if current == c['stem'] else ''
        items.append(f'<li><a href="{c["stem"]}.html"{active}>{html.escape(c["title"])}</a></li>')
    items.append('</ul></nav>')
    return ''.join(items)

def page(title, body, chapters, current='', previous=None, following=None):
    pager = '<nav class="pager" aria-label="章节翻页">'
    for label, value in [('上一章', previous), ('下一章', following)]:
        if value:
            pager += f'<a href="{value["stem"]}.html" rel="{"prev" if label == "上一章" else "next"}"><small>{label}</small>{html.escape(value["title"])}</a>'
        else: pager += '<span></span>'
    pager += '</nav>'
    canonical = PUBLIC + (current + '.html' if current else '')
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(SUBTITLE)}。24 章设计方案、可运行参考内核、28 项机制测试与 {SOURCE_COUNT} 项源码依据。">
<meta name="color-scheme" content="light dark"><title>{html.escape(title)} · {TITLE}</title>
<link rel="canonical" href="{canonical}"><link rel="stylesheet" href="assets/reader.css">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><script src="assets/reader.js" defer></script></head>
<body data-chapter="{current}" data-edition="{EDITION}"><a class="skip" href="#main">跳到正文</a>
<header class="topbar"><button id="menu-button" aria-controls="sidebar" aria-expanded="false">目录</button>
<a class="brand" href="index.html">AI CODING AGENT <span>设计与实现</span></a>
<div class="tools"><button id="search-button" aria-label="搜索全书">搜索</button><button id="font-down" aria-label="缩小字号">A−</button><button id="font-up" aria-label="放大字号">A+</button><button id="theme-button" aria-label="切换明暗主题">明暗</button><a href="downloads/{EPUB}" download>EPUB ↓</a></div></header>
<aside id="sidebar"><a class="book-home" href="index.html">架构、机制与关键工程细节</a>{navigation(chapters, current)}
<div class="sidebar-footer"><span>第 {EDITION} 版 · 2026-10-30</span><a href="{REPOSITORY}">GitHub · 书稿与实验 ↗</a></div></aside>
<main id="main" tabindex="-1"><article>{body}</article>{pager}<footer class="colophon">Aias00 · AI 辅助研究与编写 · <a href="notice.html">出处与许可</a> · <a href="validation.json">构建检查</a></footer></main>
<div class="reading-progress" role="progressbar" aria-label="本章阅读进度" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span></span></div>
<dialog id="search-dialog" aria-labelledby="search-label"><form method="dialog"><button class="close" aria-label="关闭搜索">关闭</button></form><h2 id="search-label">搜索全书</h2><label for="search-input">关键词</label><input id="search-input" type="search" placeholder="例如：并发、恢复、StepContext" autocomplete="off"><p id="search-status" role="status"></p><ol id="search-results"></ol></dialog>
</body></html>'''

def main():
    snapshot = json.loads((ROOT / 'research/sources.json').read_text())
    (ROOT / 'chapters/26-sources.md').write_text(make_sources(snapshot))
    chapters = []
    for path in sorted((ROOT / 'chapters').glob('*.md')):
        body = path.read_text()
        chapters.append({'stem': path.stem, 'title': body.splitlines()[0][2:], 'body': body})
    full = '\n\n'.join(references(c['body']) for c in chapters)
    (ROOT / 'book.md').write_text(full.rstrip() + '\n')
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    command = ['pandoc', str(ROOT / 'book.md'), '--from=markdown', '--to=epub3',
        '--metadata-file=' + str(ROOT / 'book.yaml'), '--toc', '--toc-depth=2',
        '--split-level=1', '--epub-cover-image=' + str(ROOT / 'assets/cover.png'),
        '--data-dir=' + str(ROOT / 'assets/pandoc'),
        '--css=' + str(ROOT / 'assets/epub.css'), '--resource-path=' + str(ROOT),
        '--output=' + str(output / EPUB)]
    build_env = {**os.environ, 'SOURCE_DATE_EPOCH': '1793318400'}
    subprocess.run(command, cwd=ROOT, env=build_env, check=True)
    # Only clear this script's generated output; chapter sources are separate.
    if SITE.exists(): shutil.rmtree(SITE)
    (SITE / 'assets').mkdir(parents=True)
    (SITE / 'downloads').mkdir()
    (SITE / '.nojekyll').touch()
    (SITE / 'validation.json').write_text('{"structural_checks":"pending"}\n')
    for path in (ROOT / 'assets').iterdir():
        if path.is_file(): shutil.copy2(path, SITE / 'assets' / path.name)
    for name in ['reader.css', 'reader.js']:
        shutil.copy2(ROOT / 'web' / name, SITE / 'assets' / name)
    shutil.copy2(output / EPUB, SITE / 'downloads' / EPUB)
    shutil.copy2(ROOT / 'book.md', SITE / 'downloads/book.md')
    shutil.copy2(ROOT / 'research/sources.json', SITE / 'sources.json')
    index = []
    for i, c in enumerate(chapters):
        content = pandoc(references(c['body'], '26-sources.html'), '--to=html5', '--section-divs', '--wrap=none')
        (SITE / (c['stem'] + '.html')).write_text(page(c['title'], content, chapters, c['stem'],
            chapters[i-1] if i else None, chapters[i+1] if i+1 < len(chapters) else None))
        text = pandoc(c['body'], '--to=plain', '--wrap=none')
        index.append({'title': c['title'], 'url': c['stem'] + '.html', 'text': text})
    chinese = len(re.findall('[\u4e00-\u9fff]', ''.join(c['body'] for c in chapters if c['stem'] != '26-sources')))
    catalog = navigation(chapters, '')
    prose = ''.join(c['body'] for c in chapters if c['stem'] != '26-sources')
    characters = len(re.sub(r'\s', '', prose))
    body = f'''<div class="hero"><div class="hero-copy"><p class="eyebrow">ARCHITECTURE / DESIGN DETAILS / IMPLEMENTATION</p><h1>AI Coding Agent<br><span>设计与实现</span></h1><p class="subtitle">{SUBTITLE}</p><p class="hero-description">从零构建一套 Coding Agent。把数据结构、执行时序、并发规则、权限校验和故障恢复，落实到接口与代码。</p><div class="hero-actions"><a class="primary" href="00-preface.html">开始阅读 →</a><a class="secondary" href="downloads/{EPUB}" download>下载 EPUB</a></div><a id="resume-reading" hidden>继续上次阅读 →</a></div><img class="cover" src="assets/cover.png" width="320" height="480" alt="AI Coding Agent 设计与实现书籍封面"></div>
<div class="book-stats"><div><strong>24</strong><span>章设计与实现方案</span></div><div><strong>{characters/10000:.1f} 万</strong><span>正文字符 · 含接口与伪代码</span></div><div><strong>{SOURCE_COUNT}</strong><span>项源码参考依据</span></div><div><strong>{CONFIG['reference_tests'] + CONFIG['lab_tests']}</strong><span>项机制与故障测试</span></div></div>
<section class="introduction"><h2>关键细节，写到可以动手实现</h2><p>模型请求何时冻结？工具参数何时能执行？审批后参数变了怎么办？两个编辑怎样避免覆盖？写入成功、结果没保存就崩溃，恢复时该做什么？</p><p>全书沿着系统设计问题展开，给出字段、状态机、算法、失败分支和验收方法。Codex、DeepSeek Harness、Pi 与 Claude Code 作为参考实现穿插其中；附一套可运行、可测试的模型驱动内核。</p></section>
<section class="catalog"><h2>全书目录</h2>{catalog}</section><section class="edition-note"><h2>第二版增订 · 按源码追踪关键细节</h2><p>第 {EDITION} 版。本次补齐模型重试、流式失败、文件编辑、持久化恢复、输入接纳和子代理生命周期；延续权限、沙箱、runtime 与上下文分析，并列明仍需补充的证据。</p><p><a href="06-streaming.html">流式失败 →</a>　<a href="09-filesystem.html">文件编辑 →</a>　<a href="17-recovery.html">重启恢复 →</a>　<a href="20-multi-agent.html">子代理生命周期 →</a>　<a href="25-glossary.html">覆盖与证据 →</a>　<a href="26-sources.html">源码依据 →</a></p></section>'''
    (SITE / 'index.html').write_text(page(TITLE, body, chapters))
    notice = pandoc((ROOT / 'NOTICE.md').read_text(), '--to=html5', '--wrap=none')
    notice = notice.replace('href="LICENSES/', 'href="licenses/')
    (SITE / 'notice.html').write_text(page('出处与许可', notice, chapters))
    shutil.copytree(ROOT / 'LICENSES', SITE / 'licenses')
    (SITE / 'search-index.json').write_text(json.dumps(index, ensure_ascii=False))
    (SITE / '404.html').write_text(page('页面不存在', '<h1>这页暂时找不到</h1><p><a href="' + PUBLIC + '">返回全书目录</a></p>', chapters))
    for old, target in CONFIG['redirects'].items():
        redirect_body = f'<h1>章节已按设计问题重写</h1><p>第二版已重新组织内容，<a href="{target}.html">继续阅读对应设计章节 →</a></p>'
        (SITE / (old + '.html')).write_text(page('第二版章节入口', redirect_body, chapters))
    urls = ['index.html', 'notice.html'] + [c['stem'] + '.html' for c in chapters]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{PUBLIC}{u}</loc></url>' for u in urls) + '</urlset>'
    (SITE / 'sitemap.xml').write_text(sitemap)
    report = {'edition': EDITION, 'chapters': len(chapters), 'main_chapters': 24, 'body_characters_excluding_source_index': characters, 'chinese_characters_excluding_source_index': chinese,
        'evidence_files': len(snapshot['files']), 'epub_sha256': hashlib.sha256((output / EPUB).read_bytes()).hexdigest(),
        'pandoc': subprocess.check_output(['pandoc', '--version'], text=True).splitlines()[0]}
    (output / 'build-info.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
