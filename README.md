# 📚 Z-Library to NotebookLM MCP Server

[English](README-EN.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.md)

> Model Context Protocol (MCP) Server，自動從 Z-Library 下載書籍並上傳至 Google NotebookLM。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Ready](https://img.shields.io/badge/MCP-Ready-green.svg)](https://modelcontextprotocol.org)

---

## ⚠️ 重要免責聲明

**本專案僅供教育、研究及技術展示用途。請嚴格遵守當地法律與版權規範。僅用於：**

- ✅ 您擁有合法存取權限的資源
- ✅ 公用領域或開源授權的文件（如 arXiv, Project Gutenberg）
- ✅ 您個人擁有或已獲授權使用的內容

**作者不鼓勵也不支持任何形式的侵權行為，且不承擔任何法律責任。使用風險請自行承擔。**

**請尊重智慧財產權並支持正版閱讀！**

---

## ✨ 功能特色

- 🔐 **一次登入，永久使用** - 提供類似 `notebooklm login` 的體驗
- 📥 **智慧下載** - 優先下載 PDF（保留排版），自動降級至 EPUB → Markdown
- 📦 **智慧分塊** - 針對大檔案（>35 萬字）自動分割，確保上傳穩定
- 🤖 **MCP 支援** - 專為 Gemini / Claude 等支援 MCP 的 Agent 設計
- 🎯 **格式自適應** - 自動偵測並處理多種格式（PDF, EPUB, MOBI 等）

## 🚀 作為 MCP Server 使用（推薦）

### 安裝

確保您已安裝 Python 3.8+。

```bash
#  安裝專案
pip install .
```

### 設定 Antigravity / Gemini

將以下設定新增至您的 MCP 設定檔（例如 `Gemini-MCP.md` 或全域設定）：

```json
{
  "mcpServers": {
    "zlib-tool": {
      "command": "python",
      "args": ["-m", "zlib_notebooklm.server"]
    }
  }
}
```

### 使用方法

安裝並設定完成後，您可以直接與 Gemini 對話：

```text
幫我下載這本書並上傳到 NotebookLM：
https://zh.zlib.li/book/25314781/aa05a1/book-title
```

Gemini 將會自動呼叫 `zlib_upload` 工具：

1.  下載書籍
2.  建立 NotebookLM 筆記本
3.  上傳檔案
4.  回傳筆記本 ID 給您

---

## 🛠️ 首次設定（登入）

在使用之前，您需要登入 Z-Library 一次以儲存工作階段。

**方式一：透過 Gemini 呼叫**

告訴 Gemini：

```text
請幫我登入 Z-Library
```

它會呼叫 `zlib_login` 工具，並在您的電腦上開啟瀏覽器供您登入。

**方式二：手動執行**

```bash
# 在專案目錄下
python -m zlib_notebooklm.server
# 注意：這將啟動 server，通常建議直接編寫一個簡單的 script 呼叫 auth 模組，或直接使用舊版 script
```

---

## 📁 專案結構

```text
zlibrary-to-notebooklm/
├── src/zlib_notebooklm/  # Python Package
│   ├── server.py        # MCP Server Entrypoint
│   ├── core.py          # 核心邏輯
│   ├── auth.py          # 登入邏輯
│   └── epub_converter.py# EPUB 轉換工具
├── pyproject.toml        # 專案設定與相依性
├── README.md             # 繁體中文文件（主頁）
├── README-EN.md          # 英文文件
├── scripts/              # [Legacy] 舊版 CLI 腳本
└── ...
```

## 🔧 設定檔位置

所有設定皆儲存於 `~/.zlibrary/` 目錄：

```text
~/.zlibrary/
├── storage_state.json    # 登入工作階段（cookies）
├── browser_profile/      # 瀏覽器資料
└── config.json          # 帳戶設定（備份）
```

## 📊 NotebookLM 限制最佳化

本工具已內建針對 NotebookLM 的最佳化處理：

- **單檔限制**：若轉換後的 Markdown 超過 35 萬字，將自動智慧分割為多個章節檔案，並分別上傳至同一個筆記本。
- **格式優先**：優先使用 PDF 以獲得最佳的排版分析效果。

## 🤝 貢獻

歡迎提交 PR 或 Issue。

## 📄 授權

MIT License

## ☕ 請我喝杯咖啡

如果您覺得這個工具對您有幫助，歡迎贊助支持開發！

- **PayPal**: [paypal.me/boboidvtw168](https://paypal.me/boboidvtw168)
