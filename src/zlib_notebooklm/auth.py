"""
Z-Library Login - 一次性登录，保存会话状态
"""

from pathlib import Path
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    pass

def zlibrary_login() -> bool:
    """Z-Library 登录并保存会话"""

    config_dir = Path.home() / ".zlibrary"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_dir.chmod(0o700)

    storage_state = config_dir / "storage_state.json"

    print("="*70)
    print("🔐 Z-Library 登录")
    print("="*70)
    print("")
    print("说明:")
    print("  1. 浏览器会自动打开并访问 Z-Library")
    print("  2. 请手动完成登录（如果需要）")
    print("  3. 登录成功后，回到终端按 ENTER")
    print("  4. 会话状态将被保存，后续无需再次登录")
    print("")

    try:
        with sync_playwright() as p:
            print("🚀 启动浏览器...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(config_dir / "browser_profile"),
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            try:
                print("📖 访问 Z-Library...")
                page.goto("https://zh.zlib.li/", wait_until='domcontentloaded', timeout=30000)

                print("")
                print("="*70)
                print("📋 操作步骤:")
                print("="*70)
                print("1. 在浏览器中完成登录（如果未登录）")
                print("2. 等待看到 Z-Library 主页")
                print("3. 回到终端，按 ENTER 继续")
                print("="*70)
                print("")

                input("✅ 已完成登录？按 ENTER 保存会话... ")

                # 保存会话状态
                browser.storage_state(path=str(storage_state))
                storage_state.chmod(0o600)

                print("")
                print("✅ 会话已保存！")
                print(f"📁 位置: {storage_state}")
                return True

            except Exception as e:
                print(f"❌ 运行错误: {e}")
                return False
            finally:
                browser.close()
    
    except Exception as e:
        print(f"❌ Playwright 启动失败: {e}")
        return False
