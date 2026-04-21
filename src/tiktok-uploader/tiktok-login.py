# TikTok Login — Dùng Chrome profile thật để login (tránh bị detect bot)
# Cách 1: Dùng persistent context (giống Chrome thật)
# Cách 2: Kết nối vào Chrome đang mở của user
# Usage: python src/tiktok-uploader/tiktok-login.py

import json
import os
import subprocess
import time
from playwright.sync_api import sync_playwright

COOKIE_FILE = "src/tiktok-uploader/cookies.json"
PROFILE_DIR = "src/tiktok-uploader/chrome-profile"
TIKTOK_URL = "https://www.tiktok.com/login"


def method_1_persistent_context():
    """Dùng persistent browser context — giống Chrome thật, lưu session vĩnh viễn"""
    print("=== PHƯƠNG PHÁP 1: Persistent Chrome Profile ===")
    print("Browser sẽ mở như Chrome thật (có lưu session)")
    print()

    with sync_playwright() as p:
        # Persistent context = Chrome profile thật, TikTok không detect
        context = p.chromium.launch_persistent_context(
            user_data_dir=os.path.abspath(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",  # Ẩn automation flag
            ],
            ignore_default_args=["--enable-automation"],  # Bỏ banner "Chrome is being controlled"
            channel="chrome",  # Dùng Chrome cài sẵn thay vì Chromium
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto(TIKTOK_URL)

        # Ẩn webdriver flag
        page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); }")

        print("Đang chờ bạn đăng nhập TikTok...")
        print("(Login bằng QR code, SĐT, Google, hoặc bất kỳ cách nào)")
        print()
        print("TIP: Nếu QR code không callback → thử login bằng SĐT + OTP")
        input("\n>>> Đã login xong? Nhấn ENTER để save cookies... ")

        # Save cookies
        cookies = context.cookies()
        os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)

        print(f"\nĐã lưu {len(cookies)} cookies vào {COOKIE_FILE}")
        print(f"Chrome profile lưu tại: {PROFILE_DIR}")
        print("Lần sau mở lại sẽ tự động đã login!")

        context.close()


def method_2_connect_existing_chrome():
    """Kết nối vào Chrome đang mở — user mở Chrome thật, login, rồi tool kết nối"""
    print("=== PHƯƠNG PHÁP 2: Kết nối Chrome đang mở ===")
    print()
    print("Bước 1: Đóng tất cả Chrome đang mở")
    print("Bước 2: Mở Chrome với debug port bằng lệnh sau:")
    print()
    print('  chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\\tiktok-chrome"')
    print()
    print("Bước 3: Login TikTok trên Chrome vừa mở")
    print("Bước 4: Quay lại đây nhấn ENTER")
    print()

    input(">>> Đã mở Chrome + login xong? Nhấn ENTER để kết nối... ")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]

            # Save cookies
            cookies = context.cookies()
            os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
            with open(COOKIE_FILE, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)

            print(f"\nĐã lưu {len(cookies)} cookies vào {COOKIE_FILE}")
            print("Tool upload sẽ kết nối vào Chrome này để upload!")
            # Không close browser — giữ Chrome mở
        except Exception as e:
            print(f"\nLỗi kết nối: {e}")
            print("Kiểm tra Chrome đã mở với --remote-debugging-port=9222 chưa?")


def main():
    print("=== TIKTOK LOGIN ===")
    print()
    print("Chọn phương pháp login:")
    print("  1. Persistent Chrome Profile (khuyến nghị)")
    print("     → Mở browser giống Chrome thật, TikTok không detect")
    print()
    print("  2. Kết nối Chrome đang mở (nếu cách 1 không được)")
    print("     → Bạn tự mở Chrome thật, login, rồi tool kết nối")
    print()

    choice = input("Chọn (1 hoặc 2): ").strip()

    if choice == "2":
        method_2_connect_existing_chrome()
    else:
        method_1_persistent_context()


if __name__ == "__main__":
    main()
