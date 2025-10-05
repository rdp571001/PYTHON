import asyncio
import logging
import os
import random
import sys
import getpass
from itertools import count
from urllib.parse import unquote
from pyfiglet import figlet_format
from cfonts import render
from playwright.async_api import async_playwright

# --- Cute Colors ---
COLORS = {
    'pink': '\033[38;5;218m',
    'purple': '\033[38;5;177m',
    'magenta': '\033[38;5;201m',
    'cyan': '\033[38;5;123m',
    'reset': '\033[0m',
    'bold': '\033[1m',
}

# --- Banner ---
def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(COLORS['magenta'] + "♥" * 60 + COLORS['reset'])
    print(COLORS['pink'] + figlet_format("ANANYA", font="bubble") + COLORS['reset'])
    print(COLORS['purple'] + "♡ Instagram Group Utility ♡" + COLORS['reset'])
    print(COLORS['magenta'] + "Author: ANANYA | Fast Debug Version" + COLORS['reset'])
    print(COLORS['cyan'] + "Optimized Async Engine ⚡🦋" + COLORS['reset'])
    print(COLORS['magenta'] + "♥" * 60 + COLORS['reset'])

# --- Authentication ---
password = getpass.getpass(f"{COLORS['pink']}🌸 Enter your secret key to continue:{COLORS['reset']} ").strip()
if password != "pyscriptqueen":
    print(f"{COLORS['magenta']}✖ Access Denied! Only Python Queen ANANYA may enter.{COLORS['reset']}")
    sys.exit(1)

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Name generation ---
ufo_bases = ["Rose", "Lily", "Daisy", "Orchid", "Cherry", "Star", "Nova"]
emoji_suffixes = ["🌸", "💜", "✨", "💕", "🦋"]
name_counter = count(1)
used_names = set()
success_count = 0
fail_count = 0
lock = asyncio.Lock()

# --- Inputs ---
banner()
session_id = input(f"{COLORS['pink']}🌸 Enter Session ID:{COLORS['reset']} ").strip()
dm_url = input(f"{COLORS['cyan']}🦋 Enter Group chat URL:{COLORS['reset']} ").strip()
user_prefix = input(f"{COLORS['purple']}💜 Enter prefix (e.g., angel, queen):{COLORS['reset']} ").strip() or "Princess"

try:
    task_count = int(input(f"{COLORS['magenta']}✨ Number of async tasks:{COLORS['reset']} ").strip())
except ValueError:
    task_count = 5

def generate_name():
    """Generate a cute unique group name."""
    while True:
        base = random.choice(ufo_bases)
        emoji = random.choice(emoji_suffixes)
        suffix = next(name_counter)
        name = f"{user_prefix} {base} {emoji}_{suffix}"
        if name not in used_names:
            used_names.add(name)
            return name

async def rename_loop(context):
    """Main loop that keeps renaming the group."""
    global success_count, fail_count
    page = await context.new_page()
    try:
        await page.goto(dm_url, wait_until="domcontentloaded", timeout=120_000)

        # Flexible selector for "info" button
        gear = page.locator(
            'svg[aria-label*="onversation"], svg[aria-label*="Info"], svg[aria-label*="Details"]'
        )
        await gear.wait_for(timeout=20_000)
        await gear.click()
        logging.info("Opened group info panel ✅")
    except Exception as e:
        logging.error(f"Page initialization failed: {e}")
        return

    change_btn = page.locator('div[aria-label="Change group name"][role="button"]')
    group_input = page.locator('input[aria-label="Group name"], input[name="change-group-name"]')
    save_btn = page.locator('div[role="button"]:has-text("Save")')

    while True:
        try:
            name = generate_name()
            await change_btn.click()
            await group_input.click(click_count=3)
            await group_input.fill(name)

            if await save_btn.get_attribute("aria-disabled") == "true":
                async with lock:
                    fail_count += 1
                continue

            await save_btn.click()
            async with lock:
                success_count += 1

            logging.info(f"✔ Renamed group to: {name}")
            await asyncio.sleep(0.2)  # faster than 1s
        except Exception as e:
            async with lock:
                fail_count += 1
            logging.warning(f"Rename attempt failed: {e}")
            await asyncio.sleep(0.3)

async def live_stats():
    """Show live statistics of progress."""
    while True:
        async with lock:
            print(
                f"{COLORS['pink']}🌸 DM URL: {dm_url}{COLORS['reset']}\n"
                f"{COLORS['purple']}💜 Tasks: {task_count}{COLORS['reset']}\n"
                f"{COLORS['cyan']}🦋 Unique Names: {len(used_names)}{COLORS['reset']}\n"
                f"{COLORS['magenta']}✨ Success: {success_count}{COLORS['reset']} | "
                f"{COLORS['pink']}✖ Failed: {fail_count}{COLORS['reset']}\n",
                flush=True
            )
        await asyncio.sleep(3)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # 👀 show browser
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            locale="en-US",
            extra_http_headers={"Referer": "https://www.instagram.com/"},
        )
        await context.add_cookies([{
            "name": "sessionid",
            "value": session_id,
            "domain": ".instagram.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "None"
        }])

        tasks = [asyncio.create_task(rename_loop(context)) for _ in range(task_count)]
        tasks.append(asyncio.create_task(live_stats()))

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logging.info("Interrupted by user.")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
