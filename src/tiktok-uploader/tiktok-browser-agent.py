# TikTok Browser Agent v2 — Mở Chrome thật qua CDP, nhận lệnh từ file
#
# Cách hoạt động:
#   1. Mở Chrome thật với --remote-debugging-port=9222
#   2. Playwright kết nối vào Chrome đang mở qua CDP
#   3. Claude ghi lệnh vào commands.json
#   4. Agent đọc + thực thi + ghi status.json + screenshot
#
# Usage: python src/tiktok-uploader/tiktok-browser-agent.py

import json
import os
import subprocess
import time
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Paths
BASE_DIR = "src/tiktok-uploader"
COMMANDS_FILE = os.path.join(BASE_DIR, "commands.json")
STATUS_FILE = os.path.join(BASE_DIR, "status.json")
SCREENSHOT_DIR = "output/upload-screenshots"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_DATA_DIR = r"C:\tiktok-chrome-data"
CDP_PORT = 9222
POLL_INTERVAL = 1


def write_status(status, message, extra=None):
    """Ghi trạng thái ra file để Claude đọc"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "message": message,
    }
    if extra:
        data.update(extra)
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  [{status}] {message}")


def take_screenshot(page, name):
    """Chụp screenshot"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    filename = f"{ts}-{name}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)
    try:
        page.screenshot(path=path)
        print(f"  📸 {path}")
        return path
    except Exception as e:
        print(f"  📸 Screenshot lỗi: {e}")
        return None


def read_command():
    """Đọc lệnh từ Claude"""
    if not os.path.exists(COMMANDS_FILE):
        return None
    try:
        with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
            cmd = json.load(f)
        os.remove(COMMANDS_FILE)
        return cmd
    except Exception:
        return None


def launch_chrome():
    """Mở Chrome thật với remote debugging port"""
    print(f"  Mở Chrome thật...")
    print(f"  Chrome: {CHROME_PATH}")
    print(f"  Data: {CHROME_DATA_DIR}")
    print(f"  CDP port: {CDP_PORT}")

    # Mở Chrome như 1 process riêng
    proc = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={CHROME_DATA_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "about:blank",
    ])
    print(f"  Chrome PID: {proc.pid}")
    time.sleep(3)  # Chờ Chrome khởi động
    return proc


def execute_command(page, cmd):
    """Thực thi 1 lệnh"""
    action = cmd.get("action", "")
    print(f"\n>>> Lệnh: {action}")

    try:
        if action == "goto":
            url = cmd.get("url", "")
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            time.sleep(3)
            sc = take_screenshot(page, "goto")
            write_status("ok", f"Đã mở: {url}", {"url": page.url, "screenshot": sc})

        elif action == "screenshot":
            sc = take_screenshot(page, cmd.get("name", "screen"))
            write_status("ok", "Screenshot", {"screenshot": sc, "url": page.url})

        elif action == "click":
            selector = cmd.get("selector", "")
            text = cmd.get("text", "")
            if text:
                # Thử nhiều loại element có text này
                for tag in ['button', 'a', 'div', 'span', '[role="button"]']:
                    try:
                        sel = f'{tag}:has-text("{text}")'
                        el = page.wait_for_selector(sel, timeout=3000)
                        if el:
                            el.click()
                            time.sleep(1)
                            sc = take_screenshot(page, "click")
                            write_status("ok", f"Đã click: {text}", {"screenshot": sc, "url": page.url})
                            return
                    except PlaywrightTimeout:
                        continue
                write_status("error", f"Không tìm thấy text: {text}")
            elif selector:
                el = page.wait_for_selector(selector, timeout=cmd.get("timeout", 5000))
                el.click()
                time.sleep(1)
                sc = take_screenshot(page, "click")
                write_status("ok", f"Đã click: {selector}", {"screenshot": sc, "url": page.url})

        elif action == "type":
            selector = cmd.get("selector", "")
            value = cmd.get("value", "")

            if selector:
                el = page.wait_for_selector(selector, timeout=5000)
                if el:
                    el.click()
                    time.sleep(0.3)

            if cmd.get("clear", False):
                page.keyboard.press("Control+a")
                page.keyboard.press("Backspace")
                time.sleep(0.2)

            page.keyboard.type(value, delay=cmd.get("delay", 20))
            time.sleep(0.5)
            sc = take_screenshot(page, "type")
            write_status("ok", f"Đã gõ: {value[:40]}...", {"screenshot": sc, "url": page.url})

        elif action == "upload":
            file_path = os.path.abspath(cmd.get("file", ""))
            if not os.path.exists(file_path):
                write_status("error", f"File không tồn tại: {file_path}")
                return

            uploaded = False

            # Cách 1: Tìm input[type=file] trong tất cả frames
            for frame in page.frames:
                inputs = frame.query_selector_all('input[type="file"]')
                if inputs:
                    for inp in inputs:
                        try:
                            inp.set_input_files(file_path)
                            uploaded = True
                            break
                        except Exception:
                            continue
                if uploaded:
                    break

            # Cách 2: Unhide
            if not uploaded:
                page.evaluate("""() => {
                    document.querySelectorAll('input[type="file"]').forEach(i => {
                        i.style.display = 'block';
                        i.style.position = 'fixed';
                        i.style.top = '0';
                        i.style.opacity = '1';
                        i.style.zIndex = '99999';
                    });
                }""")
                time.sleep(1)
                inputs = page.query_selector_all('input[type="file"]')
                for inp in inputs:
                    try:
                        inp.set_input_files(file_path)
                        uploaded = True
                        break
                    except Exception:
                        continue

            # Cách 3: File chooser
            if not uploaded and cmd.get("click_selector"):
                try:
                    with page.expect_file_chooser(timeout=5000) as fc:
                        page.click(cmd["click_selector"])
                    fc.value.set_files(file_path)
                    uploaded = True
                except Exception:
                    pass

            if uploaded:
                time.sleep(8)
                sc = take_screenshot(page, "uploaded")
                write_status("ok", f"Upload OK: {os.path.basename(file_path)}", {"screenshot": sc, "url": page.url})
            else:
                sc = take_screenshot(page, "upload-fail")
                write_status("error", "Upload thất bại", {"screenshot": sc, "url": page.url})

        elif action == "keyboard":
            key = cmd.get("key", "")
            page.keyboard.press(key)
            time.sleep(0.5)
            sc = take_screenshot(page, "key")
            write_status("ok", f"Phím: {key}", {"screenshot": sc, "url": page.url})

        elif action == "scroll":
            dy = cmd.get("dy", 800)
            page.evaluate(f"window.scrollBy(0, {dy})")
            time.sleep(0.5)
            sc = take_screenshot(page, "scroll")
            write_status("ok", f"Scroll dy={dy}", {"screenshot": sc, "url": page.url})

        elif action == "eval":
            code = cmd.get("code", "")
            result = page.evaluate(code)
            time.sleep(0.3)
            sc = take_screenshot(page, "eval")
            write_status("ok", f"Eval OK", {"screenshot": sc, "url": page.url, "result": str(result)[:500]})

        elif action == "click_xy":
            x = cmd.get("x", 0)
            y = cmd.get("y", 0)
            page.mouse.click(x, y)
            time.sleep(0.5)
            sc = take_screenshot(page, "click-xy")
            write_status("ok", f"Click ({x},{y})", {"screenshot": sc, "url": page.url})

        elif action == "wait":
            seconds = cmd.get("seconds", 3)
            time.sleep(seconds)
            sc = take_screenshot(page, "wait")
            write_status("ok", f"Chờ {seconds}s", {"screenshot": sc, "url": page.url})

        elif action == "dump":
            info = {"url": page.url, "title": page.title(), "buttons": [], "inputs": [], "frames": []}
            for btn in page.query_selector_all('button')[:60]:
                try:
                    t = btn.inner_text().strip()[:60]
                    if t:
                        info["buttons"].append(t)
                except Exception:
                    pass
            for inp in page.query_selector_all('input'):
                try:
                    info["inputs"].append(f"type={inp.get_attribute('type')} accept={inp.get_attribute('accept') or ''}")
                except Exception:
                    pass
            for i, frame in enumerate(page.frames):
                fi = len(frame.query_selector_all('input[type="file"]'))
                if fi:
                    info["frames"].append(f"frame[{i}]: {fi} file inputs")
            sc = take_screenshot(page, "dump")
            write_status("ok", "Dump xong", {"screenshot": sc, "page_info": info, "url": page.url})

        elif action == "quit":
            write_status("quit", "Đóng")
            return "quit"
        else:
            write_status("error", f"Lệnh lạ: {action}")

    except Exception as e:
        sc = take_screenshot(page, "error")
        write_status("error", f"{action}: {str(e)[:100]}", {"screenshot": sc})


def main():
    print("=== TIKTOK BROWSER AGENT v2 ===")
    print("Dùng Chrome thật + CDP connection")
    print()

    # Xóa file cũ
    for f in [COMMANDS_FILE, STATUS_FILE]:
        if os.path.exists(f):
            os.remove(f)

    # Bước 1: Mở Chrome thật
    chrome_proc = launch_chrome()

    # Bước 2: Kết nối Playwright vào Chrome qua CDP
    print("\n  Kết nối Playwright vào Chrome...")
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{CDP_PORT}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            print("  ✓ Kết nối thành công!")
            write_status("ready", "Chrome đã mở. Đang chờ lệnh...")
            print("\nĐang chờ lệnh... (ghi vào commands.json)")
            print("Ctrl+C để dừng\n")

            while True:
                cmd = read_command()
                if cmd:
                    result = execute_command(page, cmd)
                    if result == "quit":
                        break
                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\nDừng agent.")
        except Exception as e:
            print(f"\n  ✗ Lỗi kết nối CDP: {e}")
            print("  Kiểm tra Chrome đã mở chưa?")
        finally:
            write_status("closed", "Agent đã dừng")
            # Không đóng Chrome — để user tiếp tục dùng
            print("  Chrome vẫn mở — bạn có thể dùng tiếp.")


if __name__ == "__main__":
    main()
