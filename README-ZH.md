# 📚 Z-Library to NotebookLM

[English](README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README-ZH.md)

> 一鍵自動從 Z-Library 下載書籍並上傳至 Google NotebookLM。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-success.svg)](https://claude.ai/claude-code)

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
- 📦 **智慧分塊** - 針對大檔案（>35 萬字）自動分割，確保 CLI 上傳穩定
- 🤖 **全自動化** - 單一指令完成完整工作流程
- 🎯 **格式自適應** - 自動偵測並處理多種格式（PDF, EPUB, MOBI 等）
- 📊 **視覺化進度** - 即時顯示下載與轉換進度

## 🎯 作為 Claude Skill 使用（推薦）

### 安裝方式

```bash
# 1. 進入 Claude Skills 目錄
cd ~/.claude/skills  # Windows: %APPDATA%\Claude\skills

# 2. 複製儲存庫
git clone https://github.com/zstmfhy/zlibrary-to-notebooklm.git zlib-to-notebooklm

# 3. 完成初始登入
cd zlib-to-notebooklm
python3 scripts/login.py
```

### 使用方法

安裝完成後，只需告訴 Claude Code：

```text
使用 zlib-to-notebooklm skill 處理這個 Z-Library 連結：
https://zh.zlib.li/book/25314781/aa05a1/book-title
```

Claude 將會自動：

- 下載書籍（優先選擇 PDF）
- 建立 NotebookLM 筆記本
- 上傳檔案
- 回傳筆記本 ID
- 建議後續問題

---

## 🛠️ 傳統安裝方式

### 1. 安裝相依套件

```bash
# 複製儲存庫
git clone https://github.com/zstmfhy/zlibrary-to-notebooklm.git
cd zlibrary-to-notebooklm

# 安裝 Python 相依套件
pip install playwright ebooklib

# 安裝 Playwright 瀏覽器
playwright install chromium
```

### 2. 登入 Z-Library（僅需一次）

```bash
python3 scripts/login.py
```

**步驟：**

1. 瀏覽器將自動開啟並進入 Z-Library
2. 在瀏覽器中完成登入
3. 回到終端機並按 **ENTER** 鍵
4. 工作階段已儲存！

### 3. 下載並上傳書籍

```bash
python3 scripts/upload.py "https://zh.zlib.li/book/..."
```

**自動完成以下項目：**

- ✅ 使用儲存的工作階段登入
- ✅ 下載 PDF（保留排版）
- ✅ 降級至 EPUB → Markdown
- ✅ 針對大檔案（>35 萬字）進行智慧分塊
- ✅ 建立 NotebookLM 筆記本
- ✅ 上傳內容
- ✅ 回傳筆記本 ID

## 📖 使用範例

### 基本使用

```bash
# 下載單一書籍
python3 scripts/upload.py "https://zh.zlib.li/book/12345/..."
```

### 批次處理

```bash
# 批次下載多本書籍
for url in "url1" "url2" "url3"; do
    python3 scripts/upload.py "$url"
done
```

### 使用 NotebookLM

```bash
# 上傳後，使用筆記本
notebooklm use <回傳的筆記本 ID>

# 開始提問
notebooklm ask "這本書的核心概念是什麼？"
notebooklm ask "總結第三章"
```

## 🔄 工作流程

```text
Z-Library URL
    ↓
1. 啟動瀏覽器（使用儲存的工作階段）
    ↓
2. 訪問書籍頁面
    ↓
3. 智慧格式選擇：
   -優先：PDF（保留排版）
   - 備案：EPUB（轉換為 Markdown）
   - 其他格式（自動轉換）
    ↓
4. 下載至 ~/Downloads
    ↓
5. 格式處理：
   - PDF → 直接使用
   - EPUB → 轉換為 Markdown
   - 檢查檔案大小 → 若 >35 萬字則自動分塊
    ↓
6. 建立 NotebookLM 筆記本
    ↓
7. 上傳內容（分塊檔案將個別上傳）
    ↓
8. 回傳筆記本 ID ✅
```

## 📁 專案結構

```text
zlibrary-to-notebooklm/
├── SKILL.md              # 核心 Skill 定義（必須）
├── README.md             # 專案文件
├── README.zh-CN.md       # 簡體中文文件
├── README-ZH.md          # 繁體中文文件
├── LICENSE               # MIT 授權條款
├── package.json          # npm 設定（用於 Claude Code skill）
├── skill.yaml            # Skill 設定
├── requirements.txt      # Python 相依套件
├── scripts/              # 可執行腳本（官方標準）
│   ├── login.py         # 登入腳本
│   ├── upload.py        # 下載 + 上傳腳本
│   └── convert_epub.py  # EPUB 轉換工具
├── docs/                 # 文件
│   ├── WORKFLOW.md      # 工作流程詳情
│   └── TROUBLESHOOTING.md # 故障排除指南
└── INSTALL.md            # 安裝指南
```

## 🔧 設定

所有設定皆儲存於 `~/.zlibrary/` 目錄：

```text
~/.zlibrary/
├── storage_state.json    # 登入工作階段（cookies）
├── browser_profile/      # 瀏覽器資料
└── config.json          # 帳戶設定（備份）
```

## 🛠️ 相依需求

- **Python 3.8+**
- **playwright** - 瀏覽器自動化
- **ebooklib** - EPUB 檔案處理
- **NotebookLM CLI** - Google NotebookLM 命令列工具

## 📝 指令參考

### 登入

```bash
python3 scripts/login.py
```

### 上傳

```bash
python3 scripts/upload.py <Z-Library URL>
```

### 檢查工作階段狀態

```bash
ls -lh ~/.zlibrary/storage_state.json
```

### 重新登入

```bash
rm ~/.zlibrary/storage_state.json
python3 scripts/login.py
```

## 📊 NotebookLM 限制

本專案已針對 NotebookLM 的實際限制進行最佳化：

### 官方限制

- **檔案大小**：每個檔案 200MB
- **來源字數**：500,000 字

### 實務建議（CLI 工具）

- **安全字數**：每個檔案最多 350,000-380,000 字
- **原因**：NotebookLM CLI 工具在處理大檔案時容易逾時或受 API 限制

### 我們的解決方案

✅ **自動檔案分塊**：

- 當 EPUB 轉換為 Markdown 時，腳本會自動偵測字數
- 超過 350,000 字的檔案將自動分割為多個較小的檔案
- 每個分塊將個別上傳至同一個 NotebookLM 筆記本
- 智慧章節分割以保留內容完整性

**範例**：

```bash
📊 Word count: 2,700,000
⚠️  File exceeds 350k words (NotebookLM CLI limit)
📊 File too large, starting split...
   Total words: 2,700,000
   Max per chunk: 350,000 words
   ✅ Part 1/8: 342,000 words
   ✅ Part 2/8: 338,000 words
   ...
📦 Detected 8 file chunks
```

### 為什麼是 35 萬字？

- 官方限制為 50 萬字，但 CLI 工具在此限制附近容易逾時
- 35 萬字是經過測試可穩定上傳的安全數值
- 網頁介面可直接處理較大的檔案，但 CLI 工具需要分塊

## 🤝 貢獻

歡迎貢獻！請隨時提交 Pull Request。

1. Fork 本儲存庫
2. 建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送至分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權 - 詳情請見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [Z-Library](https://zh.zlib.li/) - 全球最大的數位圖書館
- [Google NotebookLM](https://notebooklm.google.com/) - AI 驅動的筆記工具
- [Playwright](https://playwright.dev/) - 強大的瀏覽器自動化工具

## 📮 聯絡方式

- GitHub Issues: [提交議題](https://github.com/zstmfhy/zlibrary-to-notebooklm/issues)
- Discussions: [GitHub 討論區](https://github.com/zstmfhy/zlibrary-to-notebooklm/discussions)

---

**⭐ 如果這個專案對您有幫助，請給我們一顆星！**
