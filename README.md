<div align="center">

# ✦ 免费节点订阅聚合平台

**实时聚合多个源站的免费 V2Ray / Clash / Sing-Box / Mihomo 节点订阅链接**

[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/sdlw7757/Node-Aggregation-Platform/scrape.yml?style=flat-square&label=自动抓取)](https://github.com/sdlw7757/Node-Aggregation-Platform/actions)
[![更新频率](https://img.shields.io/badge/更新频率-每日2次-00d2ff?style=flat-square)](https://github.com/sdlw7757/Node-Aggregation-Platform)
[![节点数量](https://img.shields.io/badge/节点-100%2B-00ff88?style=flat-square)](https://github.com/sdlw7757/Node-Aggregation-Platform)
[![开源协议](https://img.shields.io/badge/协议-MIT-blue?style=flat-square)](https://github.com/sdlw7757/Node-Aggregation-Platform/blob/main/LICENSE)

[🌐 在线预览 Demo](https://sdlw7757.github.io/Node-Aggregation-Platform/) · [📦 订阅链接](https://github.com/sdlw7757/Node-Aggregation-Platform) · [🐛 反馈问题](https://github.com/sdlw7757/Node-Aggregation-Platform/issues)

</div>

---

## 📡 数据来源

| 源站 | 地址 | 说明 |
|:---:|:---|:---|
| FreeV2RayNode | [freev2raynode.com](https://www.freev2raynode.com/) | V2Ray / Clash / Sing-Box 订阅 |
| FreeClashNode | [freeclashnode.com](https://www.freeclashnode.com/) | V2Ray / Clash / Sing-Box 订阅 |
| ClashNode | [clashnode.cc](https://clashnode.cc/) | V2Ray / Clash / Sing-Box 订阅 |
| V2RayShare | [v2rayshare.net](https://v2rayshare.net/) | V2Ray / Clash / Mihomo 订阅 |

## ✨ 功能特性

- 🔗 **多协议支持** — 自动识别并分类 V2Ray / Clash / Sing-Box / Mihomo 订阅链接
- 🌐 **自动抓取**：每日北京时间 06:00 和 10:00 定时更新，确保节点新鲜度
- 📱 **响应式设计** — 完美适配桌面端与移动端
- 🌐 **IP 地理位置显示** — 自动检测本机 IP 及所在地区（中文显示）
- 🛠️ **实用工具集成** — 订阅转换、UUID 生成、VPS 一键脚本
- 🔒 **安全防护** — XSS 转义、请求超时、失败重试
- 📊 **数据统计** — 实时展示文章数、各协议链接数

## 🖼️ 页面预览

> 📌 **[点击查看在线 Demo](https://sdlw7757.github.io/Node-Aggregation-Platform/)**

## 🚀 快速开始

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/sdlw7757/Node-Aggregation-Platform.git
cd Node-Aggregation-Platform

# 安装依赖
pip install -r requirements.txt

# 运行爬虫（抓取最新数据）
python scraper.py

# 生成 HTML 页面
python generate_html.py

# 本地预览
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

### 部署到 GitHub Pages

1. Fork 本仓库
2. 进入仓库 **Settings → Pages**
3. Source 选择 **GitHub Actions**
4. 等待 Actions 自动运行，即可通过 `https://<username>.github.io/Node-Aggregation-Platform/` 访问

## 📁 项目结构

```
Node-Aggregation-Platform/
├── .github/
│   └── workflows/
│       └── scrape.yml          # GitHub Actions 定时任务
├── data/
│   └── nodes.json              # 抓取数据存储
├── scraper.py                  # 爬虫核心逻辑
├── generate_html.py            # HTML 页面生成器
├── requirements.txt            # Python 依赖
├── index.html                  # 生成的页面（自动）
└── README.md
```

## 🔧 技术栈

| 类别 | 技术 |
|:---:|:---|
| 爬虫 | Python + Requests + BeautifulSoup |
| 页面 | 原生 HTML / CSS / JavaScript |
| 部署 | GitHub Pages + GitHub Actions |
| 模板 | string.Template（避免 CSS/JS 花括号冲突） |

## ⚠️ 免责声明

1. 本项目仅提供免费节点订阅链接的**聚合展示**，所有节点资源均来源于第三方网站，本项目不生产、不存储任何节点。
2. 免费节点仅供**学习研究和技术交流**使用，请勿用于任何商业或非法活动。
3. 使用节点时产生的任何流量费用由使用者**自行承担**，与本站无关。
4. 请遵守当地法律法规，因使用不当造成的后果由使用者自行负责。
5. 如有任何侵权问题，请联系删除。

## ☕ 赞赏支持

如果这个项目对你有帮助，欢迎请作者喝杯咖啡 ☕

<div align="center">

| 微信 | 支付宝 |
|:---:|:---:|
| ![微信赞赏](wechat-qr.png) | ![支付宝赞赏](alipay-qr.jpg) |

</div>

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 📄 开源协议

本项目基于 [MIT License](https://github.com/sdlw7757/Node-Aggregation-Platform/blob/main/LICENSE) 开源。

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sdlw7757/Node-Aggregation-Platform&type=Date)](https://star-history.com/#sdlw7757/Node-Aggregation-Platform&Date)

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

</div>
