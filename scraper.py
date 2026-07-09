#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
免费节点爬虫 - 从多个源站抓取免费节点订阅链接
"""

import json
import logging
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from typing import Optional

# 北京时间 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

import requests
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# 请求超时
TIMEOUT = 30

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'nodes.json')

# 全局 Session（连接池复用，减少 TCP 握手开销）
_session = None

def _get_session() -> requests.Session:
    """获取全局 Session（懒初始化）"""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update(HEADERS)
        # 连接池：每个域名最多 10 个连接
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
        _session.mount('https://', adapter)
        _session.mount('http://', adapter)
    return _session


def fetch_url(url: str) -> Optional[str]:
    """获取URL内容"""
    try:
        resp = _get_session().get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        # 优先用响应头声明的编码，其次用chardet猜测
        encoding = resp.encoding or resp.apparent_encoding or 'utf-8'
        # 规范化编码名称
        if encoding.lower() in ('gb2312', 'gbk', 'gb18030'):
            encoding = 'gbk'
        resp.encoding = encoding
        text = resp.text
        if not text or not text.strip():
            logger.warning(f"响应内容为空: {url} (HTTP {resp.status_code})")
            return None
        return text
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP错误: {url} - {e}")
        return None
    except requests.exceptions.Timeout:
        logger.error(f"请求超时: {url} ({TIMEOUT}s)")
        return None
    except requests.exceptions.ConnectionError as e:
        logger.error(f"连接失败: {url} - {e}")
        return None
    except Exception as e:
        logger.error(f"获取失败: {url} - {type(e).__name__}: {e}")
        return None


def extract_subscribe_links(html: str) -> dict:
    """
    从详情页HTML中提取订阅链接
    根据URL路径和扩展名综合判断类型
    """
    links = {'v2ray': [], 'clash': [], 'sing_box': [], 'mihomo': []}

    if not html:
        return links

    # 从原始HTML直接正则提取所有订阅URL
    url_pattern = re.compile(
        r'https?://[^\s<>"\']+\.(?:txt|yaml|yml|json)(?:\?[^\s<>"\']*)?',
        re.IGNORECASE
    )
    raw_urls = url_pattern.findall(html)

    if not raw_urls:
        return links

    seen = set()
    for url in raw_urls:
        if url in seen:
            continue
        seen.add(url)

        url_lower = url.lower()

        # freev2raynode / freeclashnode / clashnode — 相同分类规则
        if 'freev2raynode' in url_lower or 'freeclashnode' in url_lower or 'clashnode' in url_lower:
            if 'mihomo' in url_lower:
                links['mihomo'].append(url)
            elif '.yaml' in url_lower or '.yml' in url_lower:
                links['clash'].append(url)
            elif '.json' in url_lower:
                links['sing_box'].append(url)
            else:
                links['v2ray'].append(url)

        # v2rayshare - .txt=v2ray, .yaml/.yml=clash, m开头.yaml=mihomo
        elif 'v2rayshare' in url_lower:
            if 'mihomo' in url_lower or re.search(r'/m\d{8}\.', url_lower):
                links['mihomo'].append(url)
            elif '.yaml' in url_lower or '.yml' in url_lower:
                links['clash'].append(url)
            elif '.json' in url_lower:
                links['sing_box'].append(url)
            else:
                links['v2ray'].append(url)

        # 其他来源 - 根据扩展名和关键词判断
        else:
            if 'mihomo' in url_lower:
                links['mihomo'].append(url)
            elif 'sing-box' in url_lower or 'singbox' in url_lower:
                links['sing_box'].append(url)
            elif '.yaml' in url_lower or '.yml' in url_lower:
                links['clash'].append(url)
            elif '.json' in url_lower:
                links['sing_box'].append(url)
            else:
                links['v2ray'].append(url)

    return links


def scrape_freev2raynode() -> list:
    """抓取 freev2raynode.com"""
    logger.info("正在抓取 freev2raynode.com ...")
    url = 'https://www.freev2raynode.com/free-node-subscription/'
    html = fetch_url(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    articles = []

    # 查找文章条目 - 图片链接中包含文章URL
    for a_tag in soup.select('a[href*="/free-node-subscription/"]'):
        href = a_tag.get('href', '').strip()
        if not href or href.startswith('#'):
            continue
        # 必须包含日期格式，排除分类导航链接
        if not re.search(r'/\d{4}-\d{1,2}-\d{1,2}', href):
            continue
        if not href.startswith('http'):
            href = 'https://www.freev2raynode.com' + href

        # 提取标题
        img = a_tag.find('img')
        title = ''
        if img:
            title = img.get('alt', '') or img.get('title', '')

        if not title:
            title = a_tag.get_text(strip=True)

        if not title and a_tag.parent:
            title = a_tag.parent.get_text(strip=True)

        if not title:
            continue

        # 去重
        if any(a['url'] == href for a in articles):
            continue

        # 从标题中提取日期
        date = extract_date_from_title(title, href)
        if not date:
            date = extract_date_from_url(href)

        articles.append({
            'source': 'freev2raynode.com',
            'title': title.strip(),
            'date': date,
            'url': href,
        })

    logger.info(f"freev2raynode.com 找到 {len(articles)} 篇文章，只取前3条")
    return articles[:3]


def scrape_generic_site(domain: str, base_url: str, source_name: str) -> list:
    """通用抓取函数 - 适用于 freeclashnode.com 和 clashnode.cc 等同类站点"""
    logger.info(f"正在抓取 {domain} ...")
    url = base_url
    html = fetch_url(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    articles = []
    seen_urls = set()

    # 方法1: BeautifulSoup 查找所有 free-node 链接
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        if '/free-node/' not in href:
            continue
        # 补全相对路径
        if href.startswith('/'):
            href = base_url.rstrip('/') + href
        elif not href.startswith('http'):
            href = base_url.rstrip('/') + '/' + href

        # 必须包含日期
        if not re.search(r'/\d{4}-\d{1,2}-\d{1,2}', href):
            continue

        title = ''
        parent = a_tag.parent
        if parent and parent.name in ('h3', 'h2', 'h4'):
            title = parent.get_text(strip=True)
        if not title:
            title = a_tag.get_text(strip=True)
        if not title or len(title) < 5:
            continue

        if href in seen_urls:
            continue
        seen_urls.add(href)

        date = extract_date_from_title(title, href)
        if not date:
            date = extract_date_from_url(href)

        articles.append({
            'source': source_name,
            'title': title.strip(),
            'date': date,
            'url': href,
        })

    # 方法2: 原始HTML正则提取（补充分号引号等边界）
    if not articles:
        url_re = re.compile(
            r'href=["\']([^"\']*?/free-node/\d{4}-\d{1,2}-\d{1,2}[^"\']*?)["\']',
            re.IGNORECASE
        )
        hrefs_found = url_re.findall(html)
        for href in hrefs_found:
            href = href.strip()
            if href.startswith('/'):
                href = base_url.rstrip('/') + href
            elif not href.startswith('http'):
                href = base_url.rstrip('/') + '/' + href

            if href in seen_urls:
                continue
            seen_urls.add(href)

            # 从周围文本提取标题
            idx = html.find(href[:50])
            context = html[max(0, idx - 200):idx + 200] if idx >= 0 else ''
            ctx_soup = BeautifulSoup(context, 'lxml')
            title = ctx_soup.get_text(strip=True)
            if not title or len(title) < 5:
                title = f'{source_name} {extract_date_from_url(href)}'

            date = extract_date_from_url(href)
            articles.append({
                'source': source_name,
                'title': title[:100],
                'date': date,
                'url': href,
            })

    logger.info(f"{domain} 找到 {len(articles)} 篇文章，只取前3条")
    return articles[:3]


def scrape_freeclashnode() -> list:
    """抓取 freeclashnode.com"""
    return scrape_generic_site(
        domain='freeclashnode.com',
        base_url='https://www.freeclashnode.com/',
        source_name='freeclashnode.com',
    )


def scrape_clashnode() -> list:
    """抓取 clashnode.cc"""
    return scrape_generic_site(
        domain='clashnode.cc',
        base_url='https://clashnode.cc/',
        source_name='clashnode.cc',
    )


def scrape_v2rayshare() -> list:
    """抓取 v2rayshare.net"""
    logger.info("正在抓取 v2rayshare.net ...")
    url = 'https://v2rayshare.net/'
    html = fetch_url(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'lxml')
    articles = []

    # v2rayshare 文章格式
    for h3_tag in soup.find_all('h3'):
        a_tag = h3_tag.find('a')
        if not a_tag:
            continue
        href = a_tag.get('href', '').strip()
        if not href or '/p/' not in href:
            continue
        if not href.startswith('http'):
            href = 'https://v2rayshare.net' + href

        title = h3_tag.get_text(strip=True)

        if not title or len(title) < 5:
            continue

        if any(a['url'] == href for a in articles):
            continue

        date = extract_date_from_title(title, href)
        if not date:
            date = extract_date_from_url(href)

        articles.append({
            'source': 'v2rayshare.net',
            'title': title.strip(),
            'date': date,
            'url': href,
        })

    logger.info(f"v2rayshare.net 找到 {len(articles)} 篇文章，只取前3条")
    return articles[:3]


def extract_date_from_title(title: str, url: str = "") -> str:
    """从标题中提取日期 (格式: YYYY-MM-DD)，优先使用URL中的年份"""
    # 先尝试标题中的完整日期
    match = re.search(r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})', title)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"

    # 标题只有月日时，优先从URL中取年份
    match = re.search(r'(\d{1,2})月(\d{1,2})日', title)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        year_match = re.search(r'/(\d{4})-\d{1,2}-\d{1,2}', url) if url else None
        if year_match:
            year = int(year_match.group(1))
        else:
            year = datetime.now(BEIJING_TZ).year
            # 跨年修正：如果月日组合在当前年份下构成未来日期，回退到上一年
            try:
                if datetime(year, month, day, tzinfo=BEIJING_TZ) > datetime.now(BEIJING_TZ):
                    year -= 1
            except ValueError:
                logger.warning(f"无效日期: {title} (月={month}, 日={day})")
                return ''
        try:
            datetime(year, month, day)  # 验证日期有效性
            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            logger.warning(f"无效日期: {title} (年={year}, 月={month}, 日={day})")
            return ''

    return ''


def extract_date_from_url(url: str) -> str:
    """从URL中提取日期"""
    # 匹配 /2026-6-5-xxx 或 /2026-06-05-xxx 格式
    match = re.search(r'/(\d{4})-(\d{1,2})-(\d{1,2})', url)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    return ''


def scrape_all() -> list:
    """并发抓取所有源站列表页"""
    all_articles = []

    scrapers = [
        scrape_freev2raynode,
        scrape_freeclashnode,
        scrape_clashnode,
        scrape_v2rayshare,
    ]

    # 并发抓取4个列表页（不同域名，互不影响）
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(scraper): scraper for scraper in scrapers}
        for future in as_completed(futures):
            scraper = futures[future]
            try:
                articles = future.result()
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"抓取出错 {scraper.__name__}: {e}")

    # 按日期排序（最新的在前）
    all_articles.sort(key=lambda x: x['date'], reverse=True)

    return all_articles


def fetch_detail_and_extract(article: dict, max_retries: int = 2) -> dict:
    """获取文章详情页并提取订阅链接，支持重试"""
    url = article['url']
    # 随机短延时，避免并发请求同一域名触发反爬
    time.sleep(random.uniform(0.2, 0.5))

    for attempt in range(1, max_retries + 1):
        logger.info(f"获取详情: {url}" + (f" (重试 {attempt}/{max_retries})" if attempt > 1 else ''))
        html = fetch_url(url)
        if html:
            links = extract_subscribe_links(html)
            article['v2ray_links'] = links['v2ray']
            article['clash_links'] = links['clash']
            article['sing_box_links'] = links['sing_box']
            article['mihomo_links'] = links['mihomo']
            logger.info(f"  v2ray: {len(links['v2ray'])} 条, "
                         f"clash: {len(links['clash'])} 条, "
                         f"sing-box: {len(links['sing_box'])} 条, "
                         f"mihomo: {len(links['mihomo'])} 条")
            return article
        if attempt < max_retries:
            time.sleep(2)

    logger.warning(f"详情页获取失败（已重试{max_retries}次）: {url}")
    article['v2ray_links'] = []
    article['clash_links'] = []
    article['sing_box_links'] = []
    article['mihomo_links'] = []

    return article


def load_existing_data() -> list:
    """加载已存在的数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"读取现有数据失败: {e}")
    return []


def save_data(articles: list):
    """保存数据到文件"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    logger.info(f"数据已保存到 {DATA_FILE}")


def filter_recent_articles(articles: list, days: int = 7) -> list:
    """只保留最近 N 天的文章"""
    cutoff_date = (datetime.now(BEIJING_TZ) - timedelta(days=days)).date()

    filtered = []
    for a in articles:
        date_str = a.get('date', '')
        if not date_str:
            continue
        try:
            article_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if article_date >= cutoff_date:
                filtered.append(a)
        except ValueError:
            continue

    return filtered


def main():
    logger.info("=" * 60)
    logger.info("免费节点爬虫启动")
    logger.info("=" * 60)

    # 加载已有数据
    existing = load_existing_data()
    existing_urls = {a['url'] for a in existing}

    # 抓取列表
    articles = scrape_all()

    # 只处理新文章（已有数据的保留旧记录）
    new_articles = [a for a in articles if a['url'] not in existing_urls]

    if new_articles:
        logger.info(f"\n发现 {len(new_articles)} 篇新文章，正在并发抓取详情...")
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fetch_detail_and_extract, art): art for art in new_articles}
            for i, future in enumerate(as_completed(futures), 1):
                art = futures[future]
                try:
                    result = future.result()
                    logger.info(f"[{i}/{len(new_articles)}] 完成: {result['title']}")
                except Exception as e:
                    logger.error(f"抓取详情异常: {art['title']} - {e}")
                    # 异常时确保文章有空的链接字段，避免后续 KeyError
                    art.setdefault('v2ray_links', [])
                    art.setdefault('clash_links', [])
                    art.setdefault('sing_box_links', [])
                    art.setdefault('mihomo_links', [])

    # 合并新旧数据
    url_map = {}
    for article in existing:
        url_map[article['url']] = article
    for article in articles:
        # 如果是新文章，用新数据；如果是旧文章，保留旧数据
        if article['url'] in url_map:
            # 更新可能变化的信息
            old = url_map[article['url']]
            old['title'] = article['title']
            old['date'] = article['date']
            old['source'] = article['source']
        else:
            url_map[article['url']] = article

    merged = list(url_map.values())
    merged.sort(key=lambda x: x['date'], reverse=True)

    # 只保留最近7天的文章
    merged = filter_recent_articles(merged, days=7)

    # 保存
    save_data(merged)

    # 统计
    total_links = sum(
        len(a.get('v2ray_links', [])) +
        len(a.get('clash_links', [])) +
        len(a.get('sing_box_links', [])) +
        len(a.get('mihomo_links', []))
        for a in merged
    )
    logger.info(f"\n完成！共 {len(merged)} 篇文章, {total_links} 条订阅链接")
    logger.info(f"数据文件: {DATA_FILE}")


if __name__ == '__main__':
    main()