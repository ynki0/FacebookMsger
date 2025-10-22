import asyncio
import os
import random
from fbchat_muqit import Client, ThreadType
from colorama import init, Fore

init(autoreset=True)

COOKIES_DIR = "cookies"
ATTACHMENTS_DIR = "attachments"
RATE_LIMIT_DELAY_RANGE = (1.5, 2.5)

def get_attachments():
    if not os.path.exists(ATTACHMENTS_DIR):
        return []
    files = [os.path.join(ATTACHMENTS_DIR, f) for f in os.listdir(ATTACHMENTS_DIR) 
             if os.path.isfile(os.path.join(ATTACHMENTS_DIR, f))]
    return files

async def process_account(cookies_path, initial_msg, attachments):
    print(Fore.CYAN + f"\n🔑 Starting session with {cookies_path}...")
    bot = await Client.startSession(cookies_path)
    if not await bot.isLoggedIn():
        print(Fore.RED + f"❌ Login failed for {cookies_path}")
        return
    
    print(Fore.GREEN + f"✅ Logged in as {bot.uid} ({cookies_path})")

    users = await bot.fetchAllUsers()
    if not users:
        print(Fore.YELLOW + "⚠️  No users found in this account.")
        return
    
    print(Fore.YELLOW + f"📂 Found {len(users)} users. Sending messages...")

    for user in users:
        if user.uid == bot.uid:
            continue

        print(Fore.MAGENTA + f"🎯 Sending to {user.name} ({user.uid})")

        try:
            msg_id = await bot.sendMessage(
                message=initial_msg,
                thread_id=user.uid,
                thread_type=ThreadType.USER
            )
            print(Fore.BLUE + f"💬 Sent initial message → ID: {msg_id}")

            for path in attachments:
                msg_id = await bot.sendLocalFiles(
                    file_paths=[path],
                    thread_id=user.uid,
                    thread_type=ThreadType.USER
                )
                print(Fore.GREEN + f"📷 Sent {os.path.basename(path)} → ID: {msg_id}")
                await asyncio.sleep(random.uniform(*RATE_LIMIT_DELAY_RANGE))

        except Exception as e:
            print(Fore.RED + f"🔥 Error sending to {user.name} ({user.uid}): {e}")

    print(Fore.CYAN + f"✨ Finished with account {bot.uid} ({cookies_path})")

async def main(initial_msg):
    attachments = get_attachments()
    if not attachments:
        print(Fore.RED + "❌ No files found in attachments/")
        return

    cookie_files = [f for f in os.listdir(COOKIES_DIR) if f.endswith(".json")]
    if not cookie_files:
        print(Fore.RED + "❌ No cookie files found in /cookies")
        return

    print(Fore.YELLOW + f"🚀 Starting bulk process for {len(cookie_files)} accounts...\n")

    for cookie_file in cookie_files:
        cookies_path = os.path.join(COOKIES_DIR, cookie_file)
        try:
            await process_account(cookies_path, initial_msg, attachments)
        except Exception as e:
            print(Fore.RED + f"🔥 Error with {cookie_file}: {e}")

    print(Fore.CYAN + "\n🌍 All accounts processed successfully!\n")

if __name__ == "__main__":
    try:
        initial_msg = input("✍️  Enter the initial message to send: ").strip()
    except EOFError:
        initial_msg = ""

    if not initial_msg:
        initial_msg = "."  # safe fallback

    asyncio.run(main(initial_msg))
