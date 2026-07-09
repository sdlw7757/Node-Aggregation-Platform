#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成HTML页面 - 科技感风格，按网站分类显示
"""

import html as html_module
import json
import os
import string
from collections import defaultdict
from datetime import datetime, timezone, timedelta

# 北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'nodes.json')
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')

# 网站配置
SOURCE_CONFIG = {
    'freev2raynode.com': {
        'name': 'FreeV2RayNode',
        'url': 'https://www.freev2raynode.com/',
        'color': '#ff6b6b',
        'bg': 'rgba(255, 107, 107, 0.1)',
    },
    'freeclashnode.com': {
        'name': 'FreeClashNode',
        'url': 'https://www.freeclashnode.com/',
        'color': '#51cf66',
        'bg': 'rgba(81, 207, 102, 0.1)',
    },
    'clashnode.cc': {
        'name': 'ClashNode',
        'url': 'https://clashnode.cc/',
        'color': '#ffd43b',
        'bg': 'rgba(255, 212, 59, 0.1)',
    },
    'v2rayshare.net': {
        'name': 'V2RayShare',
        'url': 'https://v2rayshare.net/',
        'color': '#339af0',
        'bg': 'rgba(51, 154, 240, 0.1)',
    },
}


def load_data() -> list:
    """加载数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def generate_card(article: dict) -> str:
    """生成单个文章卡片HTML"""
    title = html_module.escape(article.get('title', '未知标题'))
    date = html_module.escape(article.get('date', '未知日期'))
    url = article.get('url', '')

    def escape_link(link):
        """转义链接用于HTML属性和JS字符串"""
        js_safe = link.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
        href_safe = html_module.escape(link)
        text_safe = html_module.escape(link)
        return href_safe, js_safe, text_safe

    def make_link_items(links, css_class, icon):
        """生成链接列表HTML"""
        return ''.join(
            f'<a href="{href}" class="link-item {css_class}" target="_blank" '
            f'onclick="copyLink(\'{js}\');return false;">'
            f'<span class="link-icon">{icon}</span>'
            f'<span class="link-text">{text}</span>'
            f'<span class="copy-hint">复制</span>'
            f'</a>'
            for link in links
            for href, js, text in [escape_link(link)]
        )

    def make_link_group(links, css_class, badge_class, label, icon):
        """生成链接分组HTML"""
        if not links:
            return ''
        return f'''
        <div class="link-group">
            <div class="link-group-title">
                <span class="protocol-badge {badge_class}">{label}</span>
                <span class="link-count">{len(links)} 条</span>
            </div>
            <div class="link-list">{make_link_items(links, css_class, icon)}</div>
        </div>'''

    v2ray_links = article.get('v2ray_links', [])
    clash_links = article.get('clash_links', [])
    sing_box_links = article.get('sing_box_links', [])
    mihomo_links = article.get('mihomo_links', [])

    links_html = (
        make_link_group(v2ray_links, 'link-v2ray', 'badge-v2ray', 'V2Ray', '📡') +
        make_link_group(clash_links, 'link-clash', 'badge-clash', 'Clash', '🔗') +
        make_link_group(sing_box_links, 'link-singbox', 'badge-singbox', 'Sing-Box', '📦') +
        make_link_group(mihomo_links, 'link-mihomo', 'badge-mihomo', 'Mihomo', '🚀')
    )

    return f'''
    <div class="card">
        <div class="card-header">
            <div class="card-date">
                <span class="date-icon">📅</span>
                {date}
            </div>
        </div>
        <h3 class="card-title">{title}</h3>
        <div class="card-links">
            {links_html if links_html else '<div class="no-links">暂无订阅链接</div>'}
        </div>
        <div class="card-footer">
            <a href="{html_module.escape(url)}" target="_blank" class="original-link">查看原文 →</a>
        </div>
    </div>'''


def generate_section(source: str, articles: list, config: dict) -> str:
    """生成网站分类区块HTML"""
    if not articles:
        return ''

    cards_html = ''.join(generate_card(a) for a in articles)

    total_links = sum(
        len(a.get('v2ray_links', [])) +
        len(a.get('clash_links', [])) +
        len(a.get('sing_box_links', [])) +
        len(a.get('mihomo_links', []))
        for a in articles
    )

    return f'''
    <section class="source-section">
        <div class="section-header" style="border-left-color: {config['color']}; background: {config['bg']};">
            <div class="section-title">
                <span class="section-dot" style="background: {config['color']};"></span>
                {config['name']}
            </div>
            <div class="section-stats">
                <span>{len(articles)} 篇</span>
                <span class="divider">|</span>
                <span>{total_links} 个链接</span>
                <a href="{config['url']}" target="_blank" class="section-link">官网 →</a>
            </div>
        </div>
        <div class="section-content">
            {cards_html}
        </div>
    </section>'''


def generate_html(articles: list) -> str:
    """生成完整HTML"""
    now = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M')

    # 按网站分类
    by_source = defaultdict(list)
    for a in articles:
        by_source[a.get('source', 'unknown')].append(a)

    # 每个源站只取前3条
    for source in by_source:
        by_source[source] = by_source[source][:3]

    # 生成各网站区块
    sections_html = ''
    for source in ['freev2raynode.com', 'freeclashnode.com', 'clashnode.cc', 'v2rayshare.net']:
        if source in by_source:
            config = SOURCE_CONFIG.get(source, {
                'name': source,
                'url': '#',
                'color': '#666',
                'bg': 'rgba(255,255,255,0.05)',
            })
            sections_html += generate_section(source, by_source[source], config)

    # 统计（基于截断后的数据）
    display_articles = [a for arts in by_source.values() for a in arts]
    total_articles = len(display_articles)
    total_v2ray = sum(len(a.get('v2ray_links', [])) for a in display_articles)
    total_clash = sum(len(a.get('clash_links', [])) for a in display_articles)
    total_singbox = sum(len(a.get('sing_box_links', [])) for a in display_articles)
    total_mihomo = sum(len(a.get('mihomo_links', [])) for a in display_articles)
    total_links = total_v2ray + total_clash + total_singbox + total_mihomo

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>免费节点订阅 · 实时聚合</title>
<meta name="description" content="聚合免费V2Ray/Clash/Sing-Box/Mihomo节点订阅链接，每日定时自动更新">
<style>
/* ===== Reset & Base ===== */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    background: #0a0e1a;
    color: #c8d6e5;
    min-height: 100vh;
}

/* Background */
body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(0, 150, 255, 0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    position: relative;
    z-index: 1;
}

/* ===== Header ===== */
.header {
    text-align: center;
    padding: 40px 20px;
}
.header h1 {
    font-size: 2.2em;
    font-weight: 800;
    background: linear-gradient(135deg, #00d2ff, #3a7bd5, #00c6fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
}

/* ===== Stats Bar ===== */
.stats-bar {
    display: flex;
    justify-content: center;
    gap: 30px;
    padding: 20px;
    margin: 10px auto 30px;
    max-width: 700px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(0, 150, 255, 0.1);
    border-radius: 16px;
    backdrop-filter: blur(10px);
    flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-value {
    font-size: 1.6em;
    font-weight: 700;
    background: linear-gradient(135deg, #00d2ff, #3a7bd5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-label {
    font-size: 0.75em;
    color: #5a7a9a;
    margin-top: 4px;
}

/* ===== Last Updated ===== */
.last-updated {
    text-align: center;
    color: #3a5a7a;
    font-size: 0.8em;
    margin-bottom: 30px;
    padding: 6px 16px;
    display: inline-block;
    position: relative;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 150, 255, 0.03);
    border: 1px solid rgba(0, 150, 255, 0.08);
    border-radius: 20px;
}
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #00ff88;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 4px #00ff88; }
    50% { opacity: 0.5; box-shadow: 0 0 12px #00ff88; }
}

/* ===== Source Section ===== */
.source-section {
    margin-bottom: 40px;
}
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-left: 4px solid;
    border-radius: 8px 8px 0 0;
    margin-bottom: 0;
    flex-wrap: wrap;
    gap: 10px;
}
.section-title {
    font-size: 1.2em;
    font-weight: 700;
    color: #e0e8f0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}
.section-stats {
    font-size: 0.85em;
    color: #5a7a9a;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-stats .divider { color: #2a4a6a; }
.section-link {
    color: #00d2ff;
    text-decoration: none;
    padding: 2px 8px;
    border: 1px solid rgba(0, 150, 255, 0.2);
    border-radius: 4px;
    transition: all 0.2s;
}
.section-link:hover {
    background: rgba(0, 150, 255, 0.1);
}
.section-content {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 16px;
    padding: 16px;
    background: rgba(255, 255, 255, 0.01);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-top: none;
    border-radius: 0 0 12px 12px;
}

/* ===== Tools Section ===== */
.tools-section {
    margin-top: 40px;
}
.tools-content {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
    padding: 16px;
    background: rgba(255, 255, 255, 0.01);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-top: none;
    border-radius: 0 0 12px 12px;
}
.tool-card {
    display: flex;
    gap: 16px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    transition: all 0.3s;
}
.tool-card:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(0, 150, 255, 0.15);
    transform: translateY(-2px);
}
.tool-icon {
    width: 40px;
    height: 40px;
    color: #00d2ff;
    flex-shrink: 0;
}
.tool-icon svg {
    width: 100%;
    height: 100%;
}
.tool-info h4 {
    color: #e0e8f0;
    font-size: 1em;
    margin-bottom: 6px;
}
.tool-info p {
    color: #5a7a9a;
    font-size: 0.82em;
    margin-bottom: 12px;
}
.tool-btn {
    display: inline-block;
    padding: 6px 16px;
    background: rgba(0, 150, 255, 0.15);
    color: #4db8ff;
    border: 1px solid rgba(0, 150, 255, 0.25);
    border-radius: 6px;
    text-decoration: none;
    font-size: 0.82em;
    transition: all 0.2s;
}
.tool-btn:hover {
    background: rgba(0, 150, 255, 0.25);
    color: #00d2ff;
}
.tool-script {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 8px 12px;
}
.tool-script code {
    flex: 1;
    font-size: 0.72em;
    color: #8ab4d6;
    font-family: 'Cascadia Code', 'Fira Code', monospace;
    word-break: break-all;
}
.copy-btn {
    padding: 4px 12px;
    background: rgba(0, 150, 255, 0.15);
    color: #4db8ff;
    border: 1px solid rgba(0, 150, 255, 0.25);
    border-radius: 4px;
    font-size: 0.72em;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
}
.copy-btn:hover {
    background: rgba(0, 150, 255, 0.25);
}

/* ===== Disclaimer ===== */
.disclaimer {
    margin-top: 40px;
    padding: 20px 24px;
    background: rgba(255, 170, 0, 0.05);
    border: 1px solid rgba(255, 170, 0, 0.15);
    border-radius: 12px;
}
.disclaimer h3 {
    color: #ffb84d;
    font-size: 1em;
    margin-bottom: 12px;
}
.disclaimer p {
    color: #8a9aaa;
    font-size: 0.82em;
    line-height: 1.8;
    margin-bottom: 6px;
}
.disclaimer p:last-child {
    margin-bottom: 0;
}

/* ===== IP Info ===== */
.ip-info {
    margin-top: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 10px 24px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 24px;
}
.ip-label {
    color: #5a7a9a;
    font-size: 0.85em;
}
.ip-value {
    color: #00d2ff;
    font-size: 0.9em;
    font-weight: 600;
    font-family: 'Cascadia Code', monospace;
}
.ip-divider {
    color: #2a4a6a;
}

/* ===== Footer ===== */
.footer {
    text-align: center;
    padding: 30px 20px;
    color: #4a6a8a;
    font-size: 0.8em;
    line-height: 1.8;
    border-top: 1px solid rgba(255,255,255,0.04);
    margin-top: 40px;
}
.footer a {
    color: #00d2ff;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
.footer .mt-1 {
    margin-top: 4px;
}
.card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.3s ease;
}
.card:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(0, 150, 255, 0.15);
    transform: translateY(-2px);
}
.card-header {
    margin-bottom: 12px;
}
.card-date {
    font-size: 0.8em;
    color: #4a6a8a;
}
.date-icon { margin-right: 4px; }
.card-title {
    font-size: 1em;
    color: #e0e8f0;
    font-weight: 600;
    line-height: 1.5;
    margin-bottom: 14px;
}
.card-links { margin-bottom: 12px; }
.card-footer {
    text-align: right;
}
.original-link {
    color: #3a7a9a;
    text-decoration: none;
    font-size: 0.8em;
    transition: color 0.2s;
}
.original-link:hover { color: #00d2ff; }

/* ===== Link Groups ===== */
.link-group { margin-bottom: 12px; }
.link-group:last-child { margin-bottom: 0; }
.link-group-title {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}
.protocol-badge {
    font-size: 0.72em;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 4px;
    letter-spacing: 1px;
}
.badge-v2ray {
    background: rgba(0, 150, 255, 0.15);
    color: #4db8ff;
    border: 1px solid rgba(0, 150, 255, 0.25);
}
.badge-clash {
    background: rgba(255, 170, 0, 0.15);
    color: #ffb84d;
    border: 1px solid rgba(255, 170, 0, 0.25);
}
.badge-singbox {
    background: rgba(0, 255, 136, 0.12);
    color: #4dffb8;
    border: 1px solid rgba(0, 255, 136, 0.2);
}
.badge-mihomo {
    background: rgba(180, 80, 255, 0.15);
    color: #c480ff;
    border: 1px solid rgba(180, 80, 255, 0.25);
}
.link-count {
    font-size: 0.72em;
    color: #4a6a8a;
}

.link-list { display: flex; flex-direction: column; gap: 4px; }
.link-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 6px;
    text-decoration: none;
    color: #8ab4d6;
    font-size: 0.78em;
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    word-break: break-all;
    transition: all 0.2s;
    cursor: pointer;
}
.link-item:hover {
    background: rgba(0, 150, 255, 0.08);
    border-color: rgba(0, 150, 255, 0.2);
    color: #b0d4f0;
}
.link-item .link-icon { font-size: 0.85em; flex-shrink: 0; }
.link-item .link-text { flex: 1; min-width: 0; }
.link-item .copy-hint {
    font-size: 0.7em;
    color: #3a5a7a;
    flex-shrink: 0;
    opacity: 0;
    font-family: 'Segoe UI', sans-serif;
}
.link-item:hover .copy-hint { opacity: 1; }
.no-links {
    color: #3a5a7a;
    font-size: 0.85em;
    font-style: italic;
}

/* ===== Toast ===== */
.toast {
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%) translateY(20px);
    background: rgba(0, 20, 40, 0.95);
    color: #00d2ff;
    padding: 10px 24px;
    border-radius: 8px;
    border: 1px solid rgba(0, 150, 255, 0.2);
    font-size: 0.85em;
    opacity: 0;
    transition: all 0.3s ease;
    pointer-events: none;
    z-index: 1000;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}
.toast.show {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
    .header h1 { font-size: 1.6em; }
    .stats-bar { gap: 16px; padding: 14px; }
    .stat-value { font-size: 1.3em; }
    .section-content { grid-template-columns: 1fr; }
    .tools-content { grid-template-columns: 1fr; }
    .section-header { padding: 12px 16px; }
    .card { padding: 16px; }
    .ip-info { flex-direction: column; gap: 6px; }
    .ip-divider { display: none; }
}
@media (max-width: 400px) {
    .container { padding: 10px; }
    .header h1 { font-size: 1.3em; }
    .card { padding: 12px; }
    .tool-script { flex-direction: column; }
    .tool-script code { font-size: 0.65em; }
}
</style>
</head>
<body>

<div class="container">
    <header class="header">
        <h1>✦ 免费节点订阅聚合</h1>
    </header>

    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">$total_articles</div>
            <div class="stat-label">文章总数</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">$total_v2ray</div>
            <div class="stat-label">V2Ray</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">$total_clash</div>
            <div class="stat-label">Clash</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">$total_singbox</div>
            <div class="stat-label">Sing-Box</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">$total_mihomo</div>
            <div class="stat-label">Mihomo</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">$total_links</div>
            <div class="stat-label">总计</div>
        </div>
    </div>

    <div class="last-updated">
        <span class="status-dot"></span>
        更新: $now · 每日定时自动同步
    </div>

    <main>
        $sections_html
    </main>

    <!-- 实用工具 -->
    <section class="tools-section">
        <div class="section-header" style="border-left-color: #00d2ff; background: rgba(0, 150, 255, 0.08);">
            <div class="section-title">
                <span class="section-dot" style="background: #00d2ff;"></span>
                实用工具
            </div>
        </div>
        <div class="tools-content">
            <div class="tool-card">
                <div class="tool-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg></div>
                <div class="tool-info">
                    <h4>订阅转换工具</h4>
                    <p>解决节点链接兼容问题，支持多种格式转换</p>
                    <a href="https://acl4ssr-sub.github.io" target="_blank" class="tool-btn">立即使用 →</a>
                </div>
            </div>
            <div class="tool-card">
                <div class="tool-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg></div>
                <div class="tool-info">
                    <h4>UUID 一键生成</h4>
                    <p>生成符合标准的 UUID v4 格式</p>
                    <div class="tool-script">
                        <code id="uuid-value">点击按钮生成</code>
                        <button onclick="generateUUID()" class="copy-btn">生成</button>
                        <button onclick="copyLink(document.getElementById('uuid-value').innerText)" class="copy-btn">复制</button>
                    </div>
                </div>
            </div>
            <div class="tool-card">
                <div class="tool-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M4 9h16"/><path d="M9 4v5"/></svg></div>
                <div class="tool-info">
                    <h4>VPS 一键四协议安装脚本</h4>
                    <p>支持 V2Ray / Trojan / NaiveProxy / Shadowsocks</p>
                    <div class="tool-script">
                        <code>bash &lt;(curl -Ls https://raw.githubusercontent.com/eooce/sing-box/main/sing-box.sh)</code>
                        <button onclick="copyLink('bash &lt;(curl -Ls https://raw.githubusercontent.com/eooce/sing-box/main/sing-box.sh)')" class="copy-btn">复制</button>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- 免责声明 -->
    <section class="disclaimer">
        <h3>⚠️ 免责声明</h3>
        <p>1. 本网站仅提供免费节点订阅链接的聚合展示，所有节点资源均来源于第三方网站。</p>
        <p>2. 免费节点仅供学习研究和技术交流使用，请勿用于任何商业或非法活动。</p>
        <p>3. 使用节点时产生的任何流量费用由使用者自行承担，与本站无关。</p>
        <p>4. 如有任何侵权问题，请联系本站删除。</p>
    </section>

    <!-- IP信息 -->
    <section class="ip-info">
        <span class="ip-label">🌐 本机IP：</span>
        <span class="ip-value" id="ipAddress">检测中...</span>
        <span class="ip-divider">|</span>
        <span class="ip-label">📍 所在地区：</span>
        <span class="ip-value" id="ipRegion">获取地理位置中...</span>
    </section>

    <footer class="footer">
        <p>⚠️ 免责声明：本页面仅分享免费节点，使用需遵守当地法律法规</p>
        <p class="mt-1"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 16 16" style="vertical-align:-2px;fill:currentColor;"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg> 开源仓库：<a href="https://github.com/sdlw7757/Node-Aggregation-Platform" target="_blank">GitHub - Node-Aggregation-Platform</a></p>
        <p class="mt-1">数据来源：freev2raynode.com · freeclashnode.com · clashnode.cc · v2rayshare.net</p>
        <p>每日定时自动更新 · Powered by GitHub Actions</p>
    </footer>
</div>

<div class="toast" id="toast"></div>

<script>
let toastTimer = null;
function copyLink(link) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(link).then(() => showToast('✓ 已复制到剪贴板'));
    } else {
        const ta = document.createElement('textarea');
        ta.value = link;
        ta.style.cssText = 'position:fixed;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast('✓ 已复制到剪贴板');
    }
}
function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('show'), 2000);
}
// 获取IP和地区信息
async function fetchIpAndLocation() {
    const ipSpan = document.getElementById('ipAddress');
    const regionSpan = document.getElementById('ipRegion');
    if (!ipSpan || !regionSpan) return;

    ipSpan.innerText = '查询中...';
    regionSpan.innerText = '获取地理位置...';

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);
        const url = 'https://ip-api.com/json/?lang=zh-CN&fields=status,country,regionName,city,query,isp';
        const response = await fetch(url, {signal: controller.signal});
        clearTimeout(timeoutId);

        if (response.ok) {
            const data = await response.json();
            if (data && data.status === 'success') {
                const ip = data.query;
                let country = data.country || '';
                let region = data.regionName || '';
                let city = data.city || '';
                let isp = data.isp || '';

                let regionText = '';
                if (country && region && city) regionText = country + ' ' + region + ' ' + city;
                else if (country && city) regionText = country + ' ' + city;
                else if (country) regionText = country;
                else regionText = '未知地区';

                if (isp && !regionText.includes(isp)) regionText += ' (' + isp + ')';

                ipSpan.innerText = ip;
                regionSpan.innerText = regionText;
                return;
            }
        }
        throw new Error('ip-api 未返回成功');
    } catch (err) {
        try {
            const fallbackRes = await fetch('https://api.ip.sb/geoip');
            if (fallbackRes.ok) {
                const data = await fallbackRes.json();
                if (data && data.ip) {
                    const ip = data.ip;
                    let country = data.country || '';
                    let region = data.region || data.region_name || '';
                    let city = data.city || '';
                    let isp = data.isp || data.organization || '';

                    const countryMap = {
                        "China": "中国", "United States": "美国", "Japan": "日本", "Singapore": "新加坡",
                        "Germany": "德国", "United Kingdom": "英国", "France": "法国", "Canada": "加拿大",
                        "Australia": "澳大利亚", "South Korea": "韩国", "Korea": "韩国", "Russia": "俄罗斯",
                        "Taiwan": "台湾地区", "Hong Kong": "香港", "Macao": "澳门",
                        "India": "印度", "Brazil": "巴西", "Netherlands": "荷兰", "Sweden": "瑞典",
                        "Switzerland": "瑞士", "Norway": "挪威", "Finland": "芬兰", "Denmark": "丹麦",
                        "Italy": "意大利", "Spain": "西班牙", "Portugal": "葡萄牙", "Poland": "波兰",
                        "Ukraine": "乌克兰", "Turkey": "土耳其", "Thailand": "泰国", "Vietnam": "越南",
                        "Malaysia": "马来西亚", "Indonesia": "印度尼西亚", "Philippines": "菲律宾",
                        "Mexico": "墨西哥", "Argentina": "阿根廷", "Colombia": "哥伦比亚",
                        "South Africa": "南非", "Egypt": "埃及", "Israel": "以色列",
                        "United Arab Emirates": "阿联酋", "Saudi Arabia": "沙特阿拉伯",
                        "New Zealand": "新西兰", "Ireland": "爱尔兰", "Belgium": "比利时",
                        "Austria": "奥地利", "Czech Republic": "捷克", "Romania": "罗马尼亚"
                    };

                    if (countryMap[country]) country = countryMap[country];

                    let regionText = country;
                    if (region && region !== country) regionText += ' ' + region;
                    if (city) regionText += ' ' + city;
                    if (isp) regionText += ' (' + isp + ')';

                    ipSpan.innerText = ip;
                    regionSpan.innerText = regionText.trim() || '大致区域获取成功';
                    return;
                }
            }
            throw new Error('备用接口失败');
        } catch (finalErr) {
            ipSpan.innerText = '无法获取';
            regionSpan.innerText = '请稍后重试';
        }
    }
}
fetchIpAndLocation();
// 生成UUID v4
function generateUUID() {
    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
    document.getElementById('uuid-value').innerText = uuid;
}
</script>
</body>
</html>'''

    # 使用 Template 避免CSS花括号冲突
    tmpl = string.Template(html)
    html = tmpl.substitute(
        now=now,
        total_articles=total_articles,
        total_v2ray=total_v2ray,
        total_clash=total_clash,
        total_singbox=total_singbox,
        total_mihomo=total_mihomo,
        total_links=total_links,
        sections_html=sections_html
    )

    return html


def main():
    articles = load_data()

    # 与页面展示一致：每个源站只取前3条
    by_source = defaultdict(list)
    for a in articles:
        by_source[a.get('source', 'unknown')].append(a)
    for source in by_source:
        by_source[source] = by_source[source][:3]
    display_articles = [a for arts in by_source.values() for a in arts]

    html = generate_html(articles)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    articles_count = len(display_articles)
    total_links = sum(
        len(a.get('v2ray_links', [])) +
        len(a.get('clash_links', [])) +
        len(a.get('sing_box_links', [])) +
        len(a.get('mihomo_links', []))
        for a in display_articles
    )
    print(f"HTML 已生成: {OUTPUT_FILE}")
    print(f"共 {articles_count} 篇文章, {total_links} 条订阅链接")
    print(f"更新时间: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()