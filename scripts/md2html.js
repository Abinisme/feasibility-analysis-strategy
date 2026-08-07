#!/usr/bin/env node
/* 将复盘 md 文件批量转换为浏览器可预览的独立 HTML
 * 用法: node scripts/md2html.js
 * 输入: ./A股深度复盘_*.md + ./复盘合集/*.md
 * 输出: ./复盘html/<原文件名>.html (每个文件独立页面)
 */
const fs = require('fs');
const path = require('path');
const MarkdownIt = require('markdown-it');

const md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    highlight: function(str, lang) {
        if (lang && require('highlight.js')) { /* 预留 */ }
        return '<pre class="code-block"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
    }
});

const BASE = __dirname + '/..';
const SRC_DIRS = [BASE, path.join(BASE, '复盘合集')];
const OUT_DIR = path.join(BASE, '复盘html');
const STYLE = `
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0d1117; color:#c9d1d9; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,"PingFang SC","Microsoft YaHei",sans-serif; line-height:1.8; padding:20px 14px 60px; }
.container { max-width:820px; margin:0 auto; }
.toolbar { position:sticky; top:0; background:rgba(13,17,23,0.95); backdrop-filter:blur(8px); padding:10px 0; margin-bottom:18px; display:flex; align-items:center; gap:10px; border-bottom:1px solid #30363d; z-index:10; }
.toolbar a { color:#58a6ff; text-decoration:none; font-size:0.85rem; white-space:nowrap; }
.toolbar a:hover { text-decoration:underline; }
.toolbar .sep { color:#484f58; }
h1 { font-size:1.5rem; color:#f0f6fc; border-bottom:2px solid #30363d; padding-bottom:10px; margin-bottom:18px; }
h2 { font-size:1.2rem; color:#58a6ff; margin:26px 0 12px; padding-left:10px; border-left:3px solid #58a6ff; }
h3 { font-size:1.05rem; color:#d29922; margin:20px 0 10px; }
h4 { font-size:0.98rem; color:#c9d1d9; margin:16px 0 8px; }
p { margin:8px 0; }
ul, ol { padding-left:24px; margin:8px 0; }
li { margin:4px 0; }
a { color:#58a6ff; text-decoration:none; }
a:hover { text-decoration:underline; }
blockquote { border-left:4px solid #30363d; background:#161b22; padding:8px 14px; margin:12px 0; color:#8b949e; border-radius:0 6px 6px 0; }
blockquote p { margin:4px 0; }
code { background:#161b22; padding:2px 6px; border-radius:4px; font-size:0.88em; font-family:"SF Mono",Consolas,Menlo,monospace; }
pre { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:12px 14px; overflow-x:auto; margin:12px 0; }
pre code { background:none; padding:0; }
table { border-collapse:collapse; width:100%; margin:12px 0; font-size:0.9em; display:block; overflow-x:auto; }
th, td { border:1px solid #30363d; padding:7px 10px; text-align:left; }
th { background:#161b22; color:#58a6ff; font-weight:600; }
tr:nth-child(even) td { background:rgba(22,27,34,0.5); }
hr { border:none; border-top:1px solid #30363d; margin:20px 0; }
img { max-width:100%; border-radius:6px; }
strong { color:#f0f6fc; }
.toc { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:14px 18px; margin:14px 0 20px; }
.toc h3 { margin:0 0 8px; color:#58a6ff; }
.toc a { display:block; padding:3px 0; font-size:0.9em; color:#8b949e; }
.toc a:hover { color:#58a6ff; text-decoration:none; }
.footer { text-align:center; color:#484f58; font-size:0.78rem; margin-top:40px; padding-top:16px; border-top:1px solid #30363d; }
`;

function collectFiles() {
    const files = [];
    for (const dir of SRC_DIRS) {
        if (!fs.existsSync(dir)) continue;
        for (const f of fs.readdirSync(dir)) {
            if (f.endsWith('.md')) {
                files.push(path.join(dir, f));
            }
        }
    }
    return files;
}

// 提取标题（首个 # 或文件名）
function extractTitle(raw, file) {
    const m = raw.match(/^\s*#\s+(.+)\s*$/m);
    if (m) return m[1].trim();
    return path.basename(file, '.md');
}

// 生成目录（提取 ## 和 ### 标题）
function buildToc(htmlBody) {
    const anchors = [];
    const re = /<h([23])>(.*?)<\/h[23]>/g;
    let m, i = 0;
    while ((m = re.exec(htmlBody)) !== null && i < 60) {
        const level = m[1];
        const text = m[2].replace(/<[^>]+>/g, '').trim();
        const id = 'sec-' + i++;
        anchors.push({ level, text, id });
    }
    if (anchors.length < 3) return '';
    let toc = '<div class="toc"><h3>📑 目录</h3>';
    for (const a of anchors) {
        const pad = a.level === '3' ? 'padding-left:14px;' : '';
        toc += `<a href="#${a.id}" style="${pad}">${a.text}</a>`;
    }
    return toc + '</div>';
}

// 给标题加锚点 id
function addAnchorIds(htmlBody) {
    let i = 0;
    return htmlBody.replace(/<h([23])>(.*?)<\/h[23]>/g, (whole, level, inner) => {
        const id = 'sec-' + i++;
        return `<h${level} id="${id}">${inner}</h${level}>`;
    });
}

function renderPage(file) {
    const raw = fs.readFileSync(file, 'utf8');
    const title = extractTitle(raw, file);
    const body = addAnchorIds(md.render(raw));
    const toc = buildToc(body);
    const rel = path.relative(path.dirname(file), file);
    const isSite = file.startsWith(BASE + path.sep) && !file.includes(path.sep + '复盘合集' + path.sep);
    const srcTag = isSite ? '本站A股复盘' : '任务库持仓复盘';
    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>${title}</title>
<style>${STYLE}</style>
</head>
<body>
<div class="container">
  <div class="toolbar">
    <a href="../index.html">🏠 首页</a><span class="sep">|</span>
    <a href="../replay_index.html">📚 复盘合集</a><span class="sep">|</span>
    <span style="color:#8b949e;font-size:0.8rem;">${srcTag} · ${path.basename(file)}</span>
  </div>
  ${toc}
  ${body}
  <div class="footer">来源：${srcTag} · ${path.basename(file)} | 由 markdown-it 转换 | 仅供参考，不构成投资建议</div>
</div>
</body>
</html>`;
}

function main() {
    const files = collectFiles();
    if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });
    let ok = 0, err = 0;
    for (const file of files) {
        try {
            const html = renderPage(file);
            const outName = path.basename(file, '.md') + '.html';
            fs.writeFileSync(path.join(OUT_DIR, outName), html, 'utf8');
            ok++;
        } catch (e) {
            console.error('ERR', file, e.message);
            err++;
        }
    }
    console.log(`转换完成：成功 ${ok} 个，失败 ${err} 个，共 ${files.length} 个`);
}

main();
