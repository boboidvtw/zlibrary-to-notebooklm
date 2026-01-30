# 📚 Z-Library to NotebookLM MCP Server

[English](README-EN.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.md)

> Model Context Protocol (MCP) Server to automatically download books from Z-Library and upload them to Google NotebookLM.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Ready](https://img.shields.io/badge/MCP-Ready-green.svg)](https://modelcontextprotocol.org)

---

## ⚠️ Important Disclaimer

**This project is for educational, research, and technical demonstration purposes only. Please strictly comply with local laws and copyright regulations. Use only for:**

- ✅ Resources you have legal access to
- ✅ Public domain or open-source licensed documents (e.g., arXiv, Project Gutenberg)
- ✅ Content you personally own or have authorization to use

**The author does not encourage or support any form of copyright infringement and assumes no legal liability. Use at your own risk.**

**Please respect intellectual property rights and support authorized reading!**

---

## ✨ Features

- 🔐 **One-time Login, Forever Use** - Similar to `notebooklm login` experience
- 📥 **Smart Download** - Prioritizes PDF (preserves formatting), auto-fallback to EPUB → Markdown
- 📦 **Smart Chunking** - Large files auto-split (>350k words) for reliable upload
- 🤖 **MCP Ready** - Designed for Gemini / Claude and other MCP-compliant agents
- 🎯 **Format Adaptive** - Automatically detects and processes multiple formats (PDF, EPUB, MOBI, etc.)

## 🚀 Use as MCP Server (Recommended)

### Installation

Ensure you have Python 3.8+ installed.

```bash
# Install the project
pip install .
```

### Configure Antigravity / Gemini

Add the following configuration to your MCP settings file (e.g., `Gemini-MCP.md` or global settings):

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

### Usage

Once installed and configured, you can talk to Gemini directly:

```text
Download this book and upload to NotebookLM:
https://zh.zlib.li/book/25314781/aa05a1/book-title
```

Gemini will automatically call the `zlib_upload` tool:

1.  Download the book
2.  Create a NotebookLM notebook
3.  Upload the file(s)
4.  Return the notebook ID

---

## 🛠️ Initial Setup (Login)

You need to login to Z-Library once to save the session.

**Method 1: Ask Gemini**

Tell Gemini:

```text
Please help me login to Z-Library
```

It will call the `zlib_login` tool and open a browser on your machine for you to login.

**Method 2: Manual Execution**

```bash
python -m zlib_notebooklm.server
# This runs the server, usually you'd want to write a small script to call auth or use legacy scripts
```

---

## 📁 Project Structure

```text
zlibrary-to-notebooklm/
├── src/zlib_notebooklm/  # Python Package
│   ├── server.py        # MCP Server Entrypoint
│   ├── core.py          # Core Logic
│   ├── auth.py          # Authentication Logic
│   └── epub_converter.py# EPUB Converter
├── pyproject.toml        # Project Config & Dependencies
├── README-EN.md          # English Documentation
├── README.md             # Traditional Chinese Documentation (Home)
├── scripts/              # [Legacy] CLI Scripts
└── ...
```

## 🔧 Configuration

All configurations are saved in `~/.zlibrary/` directory:

```text
~/.zlibrary/
├── storage_state.json    # Login session (cookies)
├── browser_profile/      # Browser data
└── config.json          # Account config (backup)
```

## 📊 NotebookLM Limitations & Optimization

This tool handles NotebookLM limits automatically:

- **File Splitting**: Files converted to Markdown > 350k words are automatically split into multiple chunks and uploaded to the same notebook.
- **Format Priority**: PDF is prioritized for best layout analysis.

## 🤝 Contributing

Contributions are welcome! Please submit a PR or Issue.

## 📄 License

MIT License
