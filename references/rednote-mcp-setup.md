# 小红书 MCP 配置指南

让 AI 编程环境直接搜索、抓取小红书内容（徒步路况、攻略、劝退贴）。一次配置，长期受用。

适用场景：徒步调研、旅游攻略、产品调研、内容创作等所有需要小红书一手资料的任务。

---

## 一分钟了解

- **MCP** = Model Context Protocol，AI Agent 连接外部服务的标准协议。
- **RedNote-MCP** = 社区维护的开源 MCP 服务器（npm 包名 `rednote-mcp`），封装小红书搜索/笔记读取 API。
- 登录一次保存 Cookie，之后 Agent 调用 `search_notes` / `get_note_content` 就能直接返回笔记内容。
- Cookie 有效期几周到几个月，过期了 `rednote-mcp init` 重来即可。

---

## 前置条件

| 项 | 要求 | 验证命令 |
|---|------|---------|
| Node.js | ≥ 16，推荐 20+ | `node --version` |
| npm | ≥ 7 | `npm --version` |
| 代理（中国大陆） | Clash/V2Ray 等，需要能访问 xiaohongshu.com | 浏览器打开 xiaohongshu.com 确认 |
| 操作系统 | Windows / macOS / Linux 均可 | — |

---

## 三步完成配置

### Step 1：安装 rednote-mcp

```bash
npm install -g rednote-mcp
```

装完验证：

```bash
rednote-mcp --version
# 应输出形如 0.2.3
```

**如果 `rednote-mcp --version` 提示找不到命令**，先确认 npm 全局目录在 PATH 里：

```bash
npm config get prefix
# 输出类似 C:\Users\你的名字\AppData\Roaming\npm（Windows）
#        或 /usr/local 或 /opt/homebrew（Mac/Linux）
```

把这个目录加到 PATH。Windows 下还要把 `<prefix>\node_modules\.bin` 也加上。

### Step 2：登录小红书（交互式）

```bash
rednote-mcp init
```

该命令会**弹出 Playwright 管理的 Chromium 浏览器窗口**，你用小红书 App 扫码或输入账号密码登录一次即可。登录后 Cookie 自动保存到：

- Windows: `C:\Users\你的名字\.mcp\rednote\cookies.json`
- macOS / Linux: `~/.mcp/rednote/cookies.json`

**注意：**
- 第一次运行可能需要下载 Playwright Chromium（大约 150 MB），自动进行。
- 如果国内网络下载 Chromium 失败，手动执行：`npx playwright install chromium`（必要时加 `--with-deps`）。
- 登录过程中如果浏览器白屏打不开 xiaohongshu.com，确认代理已启动（Clash/V2Ray）并且能访问小红书。必要时在运行前手动设置：
  - **Bash/Git Bash:** `export HTTP_PROXY=http://127.0.0.1:7890 HTTPS_PROXY=http://127.0.0.1:7890`
  - **PowerShell:** `$env:HTTP_PROXY="http://127.0.0.1:7890"; $env:HTTPS_PROXY="http://127.0.0.1:7890"`
  - **CMD:** `set HTTP_PROXY=http://127.0.0.1:7890` 然后 `set HTTPS_PROXY=http://127.0.0.1:7890`

### Step 3：在 AI 编程环境里注册 MCP

`rednote-mcp --stdio` 这个 stdio 命令在所有支持 MCP 的 agent 里都一样；**只是注册它的配置文件路径和包装语法各有不同**。下表列出 5 种主流 agent：

| Agent | 配置文件 | 格式 | 顶层键 |
|-------|---------|------|--------|
| Claude Code | `~/.claude/settings.json` | JSON | `mcpServers` |
| Cursor | `~/.cursor/mcp.json` | JSON | `mcpServers`（schema 同 Claude Code） |
| Codex CLI | `~/.codex/config.toml` | TOML | `[mcp_servers.<name>]` 表（注意下划线，非短横线） |
| OpenClaw | OpenClaw config（JSON） | JSON | `mcp.servers` 嵌套对象 |
| Hermes Agent | Hermes YAML config | YAML | `mcp_servers` |

Windows 下的配置文件位置把 `~` 换成 `C:\Users\你的名字\`，其余规则一致。

#### Claude Code / Cursor（schema 相同）

打开 `~/.claude/settings.json`（Claude Code）或 `~/.cursor/mcp.json`（Cursor）的**顶层对象**，加入（或合并）：

```jsonc
{
  // ... 你原有的 env / permissions / model 等字段 ...

  "mcpServers": {
    "rednote": {
      "command": "rednote-mcp",
      "args": ["--stdio"],
      "env": {
        "HTTP_PROXY": "http://127.0.0.1:7890",
        "HTTPS_PROXY": "http://127.0.0.1:7890"
      }
    }
  }
}
```

> 不需要代理的海外用户可以删除 `env` 字段。

#### Codex CLI

打开 `~/.codex/config.toml`，追加：

```toml
[mcp_servers.rednote]
command = "rednote-mcp"
args = ["--stdio"]

[mcp_servers.rednote.env]
HTTP_PROXY = "http://127.0.0.1:7890"
HTTPS_PROXY = "http://127.0.0.1:7890"
```

> 注意：表名必须是 `mcp_servers`（下划线），写成 `mcp-servers` 或 `mcpservers` Codex 会静默忽略。

#### OpenClaw

打开 OpenClaw 配置文件（参考 `openclaw mcp list` 所在位置），在 `mcp.servers` 节点下加入：

```json
{
  "mcp": {
    "servers": {
      "rednote": {
        "command": "rednote-mcp",
        "args": ["--stdio"],
        "env": {
          "HTTP_PROXY": "http://127.0.0.1:7890",
          "HTTPS_PROXY": "http://127.0.0.1:7890"
        }
      }
    }
  }
}
```

或等效 CLI：`openclaw mcp set rednote --command rednote-mcp --arg --stdio`。

#### Hermes Agent

在 Hermes YAML 配置里追加：

```yaml
mcp_servers:
  rednote:
    command: rednote-mcp
    args:
      - "--stdio"
    env:
      HTTP_PROXY: "http://127.0.0.1:7890"
      HTTPS_PROXY: "http://127.0.0.1:7890"
```

---

保存后**完全退出并重启 agent**（MCP 服务器只在会话启动时初始化，热重载无效）。

---

## 验证配置生效

完全退出并重启 agent 进入新会话，输入：

> 帮我在小红书搜一下"北灵山徒步"

如果返回笔记列表，说明配置成功。

Agent 会自动调用名为 `mcp__rednote__search_notes` 的工具。你也可以在对话里手动触发：

> 调用 rednote 的 search_notes，query="北灵山徒步"，limit=5

---

## 常用工具

RedNote-MCP 暴露两个核心工具：

| 工具 | 作用 | 典型参数 |
|------|------|---------|
| `search_notes` | 按关键词搜索笔记列表 | `query`（必填）、`limit`（建议 10-20） |
| `get_note_content` | 获取单篇笔记完整正文 | `url` 或 `note_id` |

使用策略：先 `search_notes` 拉列表，对信息密度高的几篇再 `get_note_content` 抓全文，**不要对所有结果都抓全文**——费时、占 context、也容易触发限流。

---

## Windows 实战坑

下面这些坑在 Windows 下更容易出现，macOS/Linux 一般不会遇到。

### 坑 1：`which rednote-mcp` 找不到，但命令实际可用

Git Bash 的 `which` 不识别 `.cmd` / `.ps1` 文件。**用 `where rednote-mcp`**（原生 Windows 命令）或直接执行 `rednote-mcp --version` 验证。

### 坑 2：npm prefix 和 PATH 不一致导致装完找不到

如果你的 Windows 登录用户和 npm 配置的用户目录不同（比如多用户/管理员账号场景），`npm install -g` 会装到 `npm config get prefix` 指向的目录，但你的 shell PATH 可能指向另一个目录。

解决：

```bash
# 查当前 npm prefix
npm config get prefix

# 查 PATH 里的 npm 目录
echo $PATH | tr ':' '\n' | grep -i npm   # Git Bash
# 或 PowerShell: $env:PATH -split ';' | Select-String npm

# 两者不一致时，把 prefix 改到 PATH 里的那个目录
npm config set prefix "C:\Users\你的名字\AppData\Roaming\npm"
```

### 坑 3：Agent 启动 MCP 时报 `spawn rednote-mcp ENOENT`

Windows 下 Node 的 `spawn` 有时不能直接执行 `.cmd` 包装器。如果设置了 `"command": "rednote-mcp"` 启动失败，改成显式用 `cmd`：

```jsonc
"mcpServers": {
  "rednote": {
    "command": "cmd",
    "args": ["/c", "rednote-mcp", "--stdio"],
    "env": { "HTTP_PROXY": "http://127.0.0.1:7890", "HTTPS_PROXY": "http://127.0.0.1:7890" }
  }
}
```

或者用 `.cmd` 绝对路径：

```jsonc
"command": "C:\\Users\\你的名字\\AppData\\Roaming\\npm\\rednote-mcp.cmd",
"args": ["--stdio"]
```

### 坑 4：代理被子进程继承不到

Agent 的 MCP 子进程**不一定继承**你终端里的 `HTTP_PROXY` 环境变量。最稳的做法是在配置的 `env` 字段里**显式写进去**（上面的配置模板已包含）。

### 坑 5：Playwright 下载 Chromium 卡住

代理对 Playwright 下载器可能不生效。手动设置：

```bash
# Bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
npx playwright install chromium
```

或者临时关代理再装。

---

## Cookie 过期 / 重新登录

用一段时间后 Agent 调 `search_notes` 可能返回认证错误。重新跑一次 init 就行：

```bash
rednote-mcp init
```

settings.json 不用动。

---

## 常见问题

### Q: 不装 MCP，能用 WebSearch 搜小红书吗？
A: 能搜到第三方转载的小红书内容，但不全面、时效差，而且搜不到带图/带视频的原贴。装 MCP 是质量差别很大的升级。

### Q: 隐私和账号安全？
A: Cookie 保存在本地 `~/.mcp/rednote/cookies.json`，不会上传任何地方。但要注意：
- **不要在公共电脑配置**
- 如果账号被限流/封禁，是风控层面的事，和 MCP 无关
- 建议用小号而非主号登录

### Q: 限流策略？
A: RedNote-MCP 底层走 Playwright 模拟浏览器，请求频率不高一般没事。在一次对话里别连续调几十次 `search_notes`，够用就停。

### Q: 商用 / 数据爬取 / 大规模抓取？
A: 不要。小红书有明确的反爬和内容版权政策，此工具仅用于**个人研究和辅助创作**。大规模抓取违反平台 TOS 且违法。

### Q: Mac / Linux 有差别吗？
A: 三步一模一样，配置文件路径以 `~` 开头（如 Claude Code 用 `~/.claude/settings.json`，Cursor 用 `~/.cursor/mcp.json`），Cookie 保存在 `~/.mcp/rednote/cookies.json`。不会有 Windows 那几个坑。

### Q: 能同时给别人分享这套配置吗？
A: settings.json 里的 `mcpServers` 配置可以分享（不含敏感信息）；但 `cookies.json` **不能分享**（包含你的账号 session）。每台电脑/每个人都要自己 `rednote-mcp init` 一次。

---

## 故障排查速查

| 现象 | 检查 |
|------|------|
| `rednote-mcp: command not found` | PATH 是否包含 npm 全局目录；Windows 下用 `where` 而不是 `which` |
| `rednote-mcp init` 浏览器打不开小红书 | 代理是否启动；直接用浏览器访问 xiaohongshu.com 能否打开 |
| `rednote-mcp init` 卡在下载 Chromium | 换 npmmirror 镜像；或关闭代理 |
| Agent 重启后没有 `mcp__rednote__*` 工具 | 看配置文件是否合法 JSON/TOML/YAML；是否彻底退出重启；查看 agent 日志有无 MCP 启动错误 |
| MCP 启动报 `spawn ENOENT` | 按上面"坑 3"改成 `cmd /c` 或绝对路径 |
| `search_notes` 返回认证错误 | Cookie 过期，`rednote-mcp init` 重来 |
| `search_notes` 返回空 | 搜索词太冷门；换个关键词或加 `limit` |

---

## 版本信息

- 本指南基于 `rednote-mcp` v0.2.3 撰写
- MCP 协议各 agent 实现详见各自官方文档
- 如命令行参数有变更，以 `rednote-mcp --help` 为准

---

*最后更新：2026-04-22*
