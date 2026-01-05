# 如何用 Cloudflare Workers 免费搭建代理 IP 池？保姆级教程

> 零成本、企业级 IP、每日 10 万次请求、全球 300+ 节点。这可能是目前最划算的代理 IP 方案。

---

## 前言：为什么需要代理 IP？

做过爬虫的同学都知道，直接用自己的 IP 去爬数据，分分钟被封。

传统解决方案：
- **住宅代理**：$5-15/GB，太贵
- **数据中心代理**：$1-5/月，容易被识别
- **免费公共代理**：可用率 <10%，还可能泄露数据

**有没有既免费、又稳定、IP 质量还高的方案？**

答案是：**Cloudflare Workers**。

---

## 一、Cloudflare Workers 是什么？

Cloudflare Workers 是一个 Serverless 边缘计算平台：

- 🌍 **全球 300+ 数据中心**，覆盖 100+ 国家
- ⚡ **0ms 冷启动**，响应极快
- 💰 **每日 10 万次免费请求**，无需信用卡
- 🔒 **企业级 IP 信誉**，与 Discord、Shopify 共用 IP 段

简单说：你写一段代码部署到 Cloudflare，请求就会从 Cloudflare 的服务器发出，对方看到的 IP 是 Cloudflare 的 IP（如 `172.64.x.x`、`104.21.x.x`）。

---

## 二、5 分钟搭建代理服务

### Step 1: 注册 Cloudflare 账号

访问 [cloudflare.com](https://cloudflare.com)，免费注册。

### Step 2: 创建 Workers

1. 登录后，左侧菜单找到 **Workers & Pages**
2. 点击 **Create Application** → **Create Worker**
3. 给 Worker 起个名字，比如 `my-proxy`
4. 点击 **Deploy** 创建

### Step 3: 编辑代码

点击 **Edit code**，删除默认代码，粘贴以下内容：

```javascript
// CFspider Workers 代理脚本 v1.7.3
const VERSION = '1.7.3';

export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        
        // 获取目标 URL
        let targetUrl = url.searchParams.get('url');
        if (!targetUrl) {
            // 显示使用说明
            return new Response(JSON.stringify({
                service: 'CFspider Proxy',
                version: VERSION,
                usage: '?url=https://example.com',
                your_ip: request.headers.get('CF-Connecting-IP'),
                cf_ray: request.headers.get('CF-Ray'),
                country: request.headers.get('CF-IPCountry')
            }, null, 2), {
                headers: { 'Content-Type': 'application/json' }
            });
        }
        
        // 转发请求
        try {
            const response = await fetch(targetUrl, {
                method: request.method,
                headers: {
                    'User-Agent': request.headers.get('User-Agent') || 'CFspider/' + VERSION,
                    'Accept': request.headers.get('Accept') || '*/*',
                    'Accept-Language': request.headers.get('Accept-Language') || 'en-US,en;q=0.9',
                }
            });
            
            // 返回响应
            return new Response(response.body, {
                status: response.status,
                headers: {
                    'Content-Type': response.headers.get('Content-Type'),
                    'X-Proxy-By': 'CFspider/' + VERSION,
                    'Access-Control-Allow-Origin': '*'
                }
            });
        } catch (error) {
            return new Response(JSON.stringify({ error: error.message }), {
                status: 500,
                headers: { 'Content-Type': 'application/json' }
            });
        }
    }
};
```

### Step 4: 部署

点击右上角 **Save and Deploy**，等待几秒钟。

### Step 5: 测试

访问你的 Workers 地址：

```
https://my-proxy.你的用户名.workers.dev
```

会看到类似返回：

```json
{
    "service": "CFspider Proxy",
    "version": "1.7.3",
    "usage": "?url=https://example.com",
    "your_ip": "1.2.3.4",
    "country": "CN"
}
```

**测试代理功能：**

```
https://my-proxy.xxx.workers.dev/?url=https://httpbin.org/ip
```

返回的 IP 就是 Cloudflare 的 IP！🎉

---

## 三、Python 客户端使用

手动拼接 URL 太麻烦？我开发了一个 Python 库 **CFspider**，语法和 `requests` 完全一样：

### 安装

```bash
pip install cfspider
```

### 基本用法

```python
import cfspider

# 设置你的 Workers 地址
workers_url = "https://my-proxy.xxx.workers.dev"

# 发起请求（语法和 requests 一模一样）
response = cfspider.get(
    "https://httpbin.org/ip",
    cf_proxies=workers_url
)

print(response.json())
# {'origin': '172.64.155.xxx'}  # Cloudflare IP！
```

### 隐身模式（反爬利器）

很多网站会检测请求头是否完整。CFspider 的隐身模式会自动添加 15+ 个浏览器请求头：

```python
import cfspider

# 隐身模式：自动添加完整浏览器请求头
response = cfspider.get(
    "https://httpbin.org/headers",
    cf_proxies="https://my-proxy.xxx.workers.dev",
    stealth=True,  # 开启隐身模式
    stealth_browser='chrome'  # 模拟 Chrome 浏览器
)

print(response.json())
```

返回的请求头包括：
- `User-Agent`（完整 Chrome UA）
- `Accept`、`Accept-Language`、`Accept-Encoding`
- `Sec-Fetch-Dest`、`Sec-Fetch-Mode`、`Sec-Fetch-Site`
- `Sec-CH-UA`、`Sec-CH-UA-Mobile`、`Sec-CH-UA-Platform`
- 等 15+ 个头

### 会话一致性

爬取多个页面时，保持同一个身份：

```python
from cfspider import StealthSession

# 创建隐身会话
session = StealthSession(
    cf_proxies="https://my-proxy.xxx.workers.dev",
    browser='chrome',
    delay=(1, 3)  # 每次请求随机等待 1-3 秒
)

# 模拟用户连续浏览
session.get("https://example.com")  # 自动保持相同 UA
session.get("https://example.com/page2")  # 自动添加 Referer
session.get("https://example.com/page3")  # 自动管理 Cookie
```

### TLS 指纹模拟

高级反爬网站会检测 TLS 指纹（JA3/JA4）。CFspider 支持模拟真实浏览器指纹：

```python
import cfspider

# 模拟 Chrome 131 的 TLS 指纹
response = cfspider.get(
    "https://tls.browserleaks.com/json",
    cf_proxies="https://my-proxy.xxx.workers.dev",
    impersonate="chrome131"  # 支持 chrome/safari/firefox/edge
)
```

### 异步请求（高并发）

```python
import asyncio
import cfspider

async def main():
    urls = [f"https://httpbin.org/get?id={i}" for i in range(10)]
    
    tasks = [
        cfspider.aget(url, cf_proxies="https://my-proxy.xxx.workers.dev")
        for url in urls
    ]
    
    responses = await asyncio.gather(*tasks)
    for r in responses:
        print(r.json())

asyncio.run(main())
```

### 浏览器自动化

需要渲染 JavaScript？CFspider 集成了 Playwright：

```python
from cfspider import Browser

# 创建浏览器实例（需要 VLESS 代理）
browser = Browser(
    vless_link="vless://...",  # 你的 VLESS 链接
    headless=True
)

# 访问页面
browser.goto("https://example.com")

# 截图
browser.screenshot("screenshot.png")

# 获取渲染后的 HTML
html = browser.content()

browser.close()
```

### 网页镜像

一键下载整个网页（包括 CSS/JS/图片）：

```python
from cfspider import mirror

# 下载完整网页到本地
mirror(
    "https://example.com",
    output_dir="./example_mirror",
    cf_proxies="https://my-proxy.xxx.workers.dev"
)
```

---

## 四、进阶：多 Workers 轮换

担心单个 Workers 请求过多？部署多个 Workers 轮换使用：

```python
import cfspider
import random

# 多个 Workers 地址
workers_list = [
    "https://proxy1.xxx.workers.dev",
    "https://proxy2.xxx.workers.dev",
    "https://proxy3.xxx.workers.dev",
]

# 随机选择一个
response = cfspider.get(
    "https://httpbin.org/ip",
    cf_proxies=random.choice(workers_list)
)
```

---

## 五、与其他方案对比

| 方案 | 价格 | IP 质量 | 速度 | 反爬能力 | 每日请求 |
|------|------|---------|------|----------|----------|
| **CFspider (Workers)** | **免费** | **企业级** | **极快** | **强** | **10万** |
| 住宅代理 | $5-15/GB | 极高 | 中等 | 极强 | 按流量 |
| 数据中心代理 | $1-5/月 | 中等 | 快 | 中等 | 不限 |
| 免费公共代理 | 免费 | 极差 | 慢 | 弱 | 不稳定 |

---

## 六、注意事项

### 合规使用

CFspider 仅供学习研究、网络安全测试、合规数据采集等**合法用途**。

✅ **合规场景**：学术研究、安全测试、公开数据采集、API 测试

❌ **禁止用途**：DDoS 攻击、侵犯隐私、网络诈骗、侵犯版权

### Workers 限制

- 免费版：每日 10 万请求，单次 CPU 时间 10ms
- 付费版（$5/月）：无限请求，CPU 时间更长

### 使用建议

1. 控制请求频率，模拟正常用户行为
2. 遵守目标网站的 robots.txt
3. 不要对同一网站高频请求

---

## 七、总结

Cloudflare Workers + CFspider 是目前最划算的代理 IP 方案：

- ✅ **完全免费**（每日 10 万请求）
- ✅ **企业级 IP 信誉**（与大型网站共用 IP 段）
- ✅ **全球 300+ 节点**（自动就近路由）
- ✅ **功能丰富**（隐身模式、TLS 指纹、浏览器自动化）
- ✅ **语法简单**（和 requests 一样）

---

## 相关链接

- **GitHub**: https://github.com/violettoolssite/CFspider
- **PyPI**: https://pypi.org/project/cfspider/
- **官网文档**: https://spider.violetteam.cloud
- **Workers 脚本**: https://spider.violetteam.cloud/workers.js

---

> 觉得有用的话，欢迎 Star ⭐ 支持一下~
> 
> 有问题可以在 GitHub Issues 或评论区交流！

---

**相关阅读**：
- [Python 爬虫反爬绕过：完整指南](#)
- [Cloudflare Workers 入门教程](#)
- [TLS 指纹是什么？如何绕过检测？](#)

---

*本文首发于知乎，作者：[你的知乎ID]*

*转载请注明出处*

