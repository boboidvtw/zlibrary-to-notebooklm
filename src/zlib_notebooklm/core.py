"""
Z-Library Core Logic - 下载并上传到 NotebookLM
"""

import asyncio
import sys
import time
import re
from pathlib import Path
from urllib.parse import unquote
import subprocess
import json

try:
    from playwright.async_api import async_playwright
except ImportError:
    pass

from .epub_converter import epub_to_markdown

class ZLibraryAutoUploader:
    """Z-Library 自动下载上传器"""

    def __init__(self):
        self.downloads_dir = Path.home() / "Downloads"
        self.temp_dir = Path("/tmp")
        self.config_dir = Path.home() / ".zlibrary"
        self.config_file = self.config_dir / "config.json"
        
        # Ensure temp dir exists (Windows compatibility)
        if sys.platform == "win32":
             self.temp_dir = Path(sys.getenv("TEMP"))
    
    async def download_from_zlibrary(self, url: str) -> tuple[Path | None, str | None]:
        """从 Z-Library 下载书籍"""
        print("="*70)
        print("🌐 启动浏览器自动化下载")
        print("="*70)

        # 检查是否有保存的会话
        storage_state = self.config_dir / "storage_state.json"

        if not storage_state.exists():
            print("❌ 未找到会话状态")
            print("💡 请先运行登录工具")
            return None, None

        print(f"✅ 使用已保存的会话")

        async with async_playwright() as p:
            # 启动浏览器（使用持久化上下文）
            print("🚀 启动浏览器...")

            browser = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.config_dir / "browser_profile"),
                headless=False,
                accept_downloads=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            page = browser.pages[0] if browser.pages else await browser.new_page()
            page.set_default_timeout(60000)

            # 设置下载处理
            download_path = None
            downloaded_format = None

            async def handle_download(download):
                nonlocal download_path
                print("✅ 检测到下载开始...")
                suggested_filename = download.suggested_filename
                print(f"📄 文件名: {suggested_filename}")
                download_path = self.downloads_dir / suggested_filename
                await download.save_as(download_path)
                print(f"💾 已保存: {download_path}")

            page.on('download', handle_download)

            try:
                # 访问目标页面
                print(f"📖 访问书籍页面...")
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)

                print("⏳ 等待页面加载...")
                await asyncio.sleep(5)

                # 步骤1: 查找下载方式（优先 PDF，然后 EPUB）
                print("🔍 步骤1: 查找下载方式...")

                # 首先检查是否有三个点的菜单按钮（新界面）
                dots_button = await page.query_selector('button[aria-label="更多选项"], button[title="更多"], .more-options, [class*="dots"], [class*="more"]')

                download_link = None
                
                if dots_button:
                    print("📱 检测到新版界面（三点菜单）")
                    # 点击打开菜单
                    await dots_button.click()
                    await asyncio.sleep(2)

                    # 查找 PDF 选项（优先）
                    print("🔍 查找 PDF 选项...")
                    pdf_options = await page.query_selector_all('a:has-text("PDF"), button:has-text("PDF")')
                    if pdf_options:
                        # 选择第一个 PDF（通常文件最小）
                        download_link = pdf_options[0]
                        downloaded_format = 'pdf'
                        print(f"✅ 找到 PDF 选项")
                    else:
                        # 备选：查找 EPUB
                        print("🔍 未找到 PDF，查找 EPUB 选项...")
                        epub_options = await page.query_selector_all('a:has-text("EPUB"), button:has-text("EPUB")')
                        if epub_options:
                            download_link = epub_options[0]
                            downloaded_format = 'epub'
                            print(f"✅ 找到 EPUB 选项")

                else:
                    # 旧界面：检查转换按钮
                    print("📱 检测到旧版界面")
                    convert_selector_pdf = 'a[data-convert_to="pdf"]'
                    convert_selector_epub = 'a[data-convert_to="epub"]'

                    # 优先尝试 PDF
                    convert_button = await page.query_selector(convert_selector_pdf)

                    if convert_button:
                        print("📝 检测到 PDF 转换按钮")
                        downloaded_format = 'pdf'
                        await convert_button.evaluate('el => el.click()')
                        print("✅ 已点击 PDF 转换按钮")

                        # 等待转换完成
                        print("⏳ 等待 PDF 转换完成...")
                        for i in range(60):
                            await asyncio.sleep(1)
                            try:
                                message = await page.query_selector('.message:has-text("转换为")')
                                if message:
                                    message_text = await message.inner_text()
                                    if 'pdf' in message_text.lower() and '完成' in message_text:
                                        print("✅ PDF 转换已完成!")
                                        break
                            except:
                                pass
                            if i % 10 == 0 and i > 0:
                                print(f"   ⏳ 等待中... {i}秒")

                        # 查找下载链接
                        download_link = await page.query_selector('a[href*="/dl/"][href*="convertedTo=pdf"]')

                        if not download_link:
                            all_links = await page.query_selector_all('a[href*="/dl/"]')
                            if all_links:
                                download_link = all_links[0]
                                href = await download_link.get_attribute('href')
                                print(f"✅ 找到下载链接: {href}")

                    else:
                        # 备选：尝试 EPUB
                        convert_button = await page.query_selector(convert_selector_epub)

                        if convert_button:
                            print("📝 检测到 EPUB 转换按钮")
                            downloaded_format = 'epub'
                            await convert_button.evaluate('el => el.click()')
                            print("✅ 已点击 EPUB 转换按钮")

                            # 等待转换完成
                            print("⏳ 等待 EPUB 转换完成...")
                            for i in range(60):
                                await asyncio.sleep(1)
                                try:
                                    message = await page.query_selector('.message:has-text("转换为")')
                                    if message:
                                        message_text = await message.inner_text()
                                        if 'epub' in message_text.lower() and '完成' in message_text:
                                            print("✅ EPUB 转换已完成!")
                                            break
                                except:
                                    pass
                                if i % 10 == 0 and i > 0:
                                    print(f"   ⏳ 等待中... {i}秒")

                            # 查找下载链接
                            download_link = await page.query_selector('a[href*="/dl/"][href*="convertedTo=epub"]')

                            if not download_link:
                                all_links = await page.query_selector_all('a[href*="/dl/"]')
                                if all_links:
                                    download_link = all_links[0]
                                    href = await download_link.get_attribute('href')
                                    print(f"✅ 找到下载链接: {href}")

                # 如果还是没找到，尝试直接下载链接
                if not download_link:
                    print("🔍 未检测到转换按钮，查找直接下载链接...")

                    selectors = [
                        'a[href*="/dl/"]',
                        'a:has-text("下载")',
                        'a:has-text("Download")',
                        'button:has-text("下载")',
                    ]

                    for selector in selectors:
                        try:
                            links = await page.query_selector_all(selector)
                            if links:
                                for link in links:
                                    href = await link.get_attribute('href')
                                    if href and '/dl/' in href:
                                        download_link = link
                                        # 从 URL 判断格式
                                        if 'pdf' in href.lower():
                                            downloaded_format = 'pdf'
                                        elif 'epub' in href.lower():
                                            downloaded_format = 'epub'
                                        print(f"✅ 找到下载链接: {href} (格式: {downloaded_format})")
                                        break
                                if download_link:
                                    break
                        except:
                            continue

                if not download_link:
                    print("❌ 未找到下载链接")
                    await browser.close()
                    return None, None

                # 点击下载
                print("⬇️  步骤2: 点击下载链接...")

                try:
                    await download_link.evaluate('el => el.click()')
                    print("✅ 点击成功")
                except Exception as e:
                    print(f"❌ 点击失败: {e}")
                    await browser.close()
                    return None, None

                # 等待下载
                print("⏳ 步骤3: 等待下载完成...")
                await asyncio.sleep(20)

                # 检查结果
                if download_path and download_path.exists():
                    # 再次确认格式
                    if not downloaded_format:
                        if download_path.suffix.lower() == '.pdf':
                             downloaded_format = 'pdf'
                        elif download_path.suffix.lower() == '.epub':
                             downloaded_format = 'epub'

                    file_size = download_path.stat().st_size / 1024
                    print(f"✅ 下载成功!")
                    print(f"   格式: {downloaded_format.upper() if downloaded_format else '未知'}")
                    print(f"   文件: {download_path.name}")
                    print(f"   路径: {download_path}")
                    print(f"   大小: {file_size:.1f} KB")
                    await browser.close()
                    return download_path, downloaded_format

                print("❌ 未找到下载的文件")
                await browser.close()
                return None, None

            except Exception as e:
                print(f"❌ 下载失败: {e}")
                # import traceback
                # traceback.print_exc()
                await browser.close()
                return None, None

    def count_words(self, text: str) -> int:
        """统计中英文单词数"""
        import re
        # 匹配中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # 匹配英文单词
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        return chinese_chars + english_words

    def split_markdown_file(self, file_path: Path, max_words: int = 350000) -> list[Path]:
        """分割大 Markdown 文件为多个小文件"""
        print(f"📊 文件过大，开始分割...")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        total_words = self.count_words(content)
        print(f"   总词数: {total_words:,}")
        print(f"   每块最大: {max_words:,} 词")

        # 按章节分割（寻找 ## 或 ### 标题）
        import re
        chapters = re.split(r'\n(?=#{1,3}\s)', content)

        chunks = []
        current_chunk = ""
        current_words = 0
        chunk_num = 1

        for i, chapter in enumerate(chapters):
            chapter_words = self.count_words(chapter)

            # 如果单个章节就超过限制，需要进一步分割
            if chapter_words > max_words:
                # 先保存当前 chunk
                if current_chunk:
                    chunks.append(current_chunk)
                    chunk_num += 1
                    current_chunk = ""
                    current_words = 0

                # 分割大章节（按段落）
                paragraphs = chapter.split('\n\n')
                temp_chunk = ""
                temp_words = 0

                for para in paragraphs:
                    para_words = self.count_words(para)
                    if temp_words + para_words > max_words and temp_chunk:
                        chunks.append(temp_chunk)
                        chunk_num += 1
                        temp_chunk = para + "\n\n"
                        temp_words = para_words
                    else:
                        temp_chunk += para + "\n\n"
                        temp_words += para_words

                if temp_chunk:
                    current_chunk = temp_chunk
                    current_words = temp_words

            elif current_words + chapter_words > max_words:
                # 当前 chunk 已满，保存并开始新的
                chunks.append(current_chunk)
                chunk_num += 1
                current_chunk = chapter + "\n\n"
                current_words = chapter_words
            else:
                # 添加到当前 chunk
                current_chunk += chapter + "\n\n"
                current_words += chapter_words

        # 保存最后一个 chunk
        if current_chunk:
            chunks.append(current_chunk)

        # 写入文件
        chunk_files = []
        stem = file_path.stem
        for i, chunk in enumerate(chunks, 1):
            chunk_file = file_path.parent / f"{stem}_part{i}.md"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            chunk_files.append(chunk_file)
            chunk_words = self.count_words(chunk)
            print(f"   ✅ Part {i}/{len(chunks)}: {chunk_words:,} 词")

        return chunk_files

    def convert_to_txt(self, file_path: Path, file_format: str = None) -> Path | list[Path]:
        """转换文件为 TXT 或直接使用 PDF"""
        print("")
        print("="*70)
        print("📝 处理文件")
        print("="*70)

        file_ext = file_path.suffix.lower()

        # 如果是 PDF，直接使用（方案 A）
        if file_ext == '.pdf' or file_format == 'pdf':
            print("✅ 检测到 PDF 格式，直接使用")
            print(f"   文件: {file_path.name}")
            return file_path

        md_file = self.temp_dir / f"{file_path.stem}.md"

        # 如果是 EPUB，转换为 Markdown
        if file_ext == '.epub':
            print("📖 检测到 EPUB 格式，转换为 Markdown...")
            
            # 使用导入的函數進行轉換
            success = epub_to_markdown(file_path, md_file)

            if not success:
                print(f"❌ 转换失败")
                return file_path

            print(f"✅ 转换成功: {md_file}")

            # 检查文件大小，如果过大则分割
            word_count = self.count_words(open(md_file, 'r', encoding='utf-8').read())
            print(f"📊 词数统计: {word_count:,}")

            if word_count > 350000:
                print(f"⚠️  文件超过 350k 词（NotebookLM CLI 限制）")
                return self.split_markdown_file(md_file)
            else:
                return md_file

        else:
            print(f"ℹ️  文件格式: {file_ext}，直接使用")
            return file_path

    def upload_to_notebooklm(self, file_path: Path | list[Path], title: str = None) -> dict:
        """上传到 NotebookLM"""
        print("")
        print("="*70)
        print("⬆️  上传到 NotebookLM")
        print("="*70)

        # 处理文件列表（分割后的文件）
        if isinstance(file_path, list):
            print(f"📦 检测到 {len(file_path)} 个文件分块")

            # 使用第一个文件确定书名
            first_file = file_path[0]
            if not title:
                title = first_file.stem.replace('_part1', '').replace('_', ' ')
                # 清理文件名
                title = re.sub(r'\[.*?\]', '', title)
                title = re.sub(r'\(.*?\)', '', title)
                title = re.sub(r'\s+', ' ', title).strip()
                if len(title) > 50:
                    title = title[:50] + "..."

            # 创建笔记本
            print(f"📚 创建笔记本: {title}")
           
            try:
                cmd = f"notebooklm create '{title}' --json"
                if sys.platform == "win32":
                      # Windows quoting is different, but subprocess can handle list slightly better or just trust shell=True with care
                      # For simplicity and given environment, shell=True with double quotes might be safer for titles with spaces
                      cmd = f'notebooklm create "{title}" --json'

                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    return {"success": False, "error": result.stderr}

                data = json.loads(result.stdout)
                notebook_id = data['notebook']['id']
                print(f"✅ 笔记本已创建 (ID: {notebook_id[:8]}...)")
            except Exception as e:
                return {"success": False, "error": f"创建笔记本失败: {str(e)}"}

            # 设置上下文
            print(f"🎯 设置笔记本上下文...")
            cmd = f"notebooklm use {notebook_id}"
            subprocess.run(cmd, shell=True, capture_output=True)

            # 上传所有分块
            source_ids = []
            for i, chunk_file in enumerate(file_path, 1):
                print(f"📄 上传分块 {i}/{len(file_path)}: {chunk_file.name}")
                chunk_str = str(chunk_file)
                if sys.platform == "win32":
                    cmd = f'notebooklm source add "{chunk_str}" --json'
                else:
                    cmd = f"notebooklm source add '{chunk_str}' --json"
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    print(f"⚠️  分块 {i} 上传失败: {result.stderr}")
                    continue

                try:
                    data = json.loads(result.stdout)
                    source_id = data['source']['id']
                    source_ids.append(source_id)
                    print(f"   ✅ 成功 (ID: {source_id[:8]}...)")
                except:
                    print(f"⚠️  分块 {i} 解析失败")

            return {
                "success": len(source_ids) > 0,
                "notebook_id": notebook_id,
                "source_ids": source_ids,
                "title": title,
                "chunks": len(file_path)
            }

        # 单文件上传
        # 确定书名
        if not title:
            title = file_path.stem.replace('_', ' ')
            # 清理文件名
            title = re.sub(r'\[.*?\]', '', title)
            title = re.sub(r'\(.*?\)', '', title)
            title = re.sub(r'\s+', ' ', title).strip()
            # 截断过长的书名
            if len(title) > 50:
                title = title[:50] + "..."

        # 创建笔记本
        print(f"📚 创建笔记本: {title}")
        
        try:
            if sys.platform == "win32":
                cmd = f'notebooklm create "{title}" --json'
            else:
                cmd = f"notebooklm create '{title}' --json"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                return {"success": False, "error": result.stderr}

            data = json.loads(result.stdout)
            notebook_id = data['notebook']['id']
            print(f"✅ 笔记本已创建 (ID: {notebook_id[:8]}...)")
        except Exception as e:
            return {"success": False, "error": f"创建笔记本失败: {str(e)}"}

        # 设置上下文
        print(f"🎯 设置笔记本上下文...")
        cmd = f"notebooklm use {notebook_id}"
        subprocess.run(cmd, shell=True, capture_output=True)

        # 上传文件
        print(f"📄 上传文件...")
        file_str = str(file_path)
        if sys.platform == "win32":
             cmd = f'notebooklm source add "{file_str}" --json'
        else:
             cmd = f"notebooklm source add '{file_str}' --json"
             
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            return {"success": False, "error": result.stderr}

        try:
            data = json.loads(result.stdout)
            source_id = data['source']['id']
            print(f"✅ 上传成功 (ID: {source_id[:8]}...)")

            return {
                "success": True,
                "notebook_id": notebook_id,
                "source_id": source_id,
                "title": title
            }
        except:
            return {"success": False, "error": "解析来源 ID 失败"}
