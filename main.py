import asyncio
from config_manager import load_config
from bot_client import AutoBot

async def main():
    config = load_config()
    accounts = config.get("accounts", [])
    if not accounts:
        print("[LỖI] Không có tài khoản nào được cấu hình trong config.json")
        return
    print(f"--- KHỞI ĐỘNG HỆ THỐNG VỚI {len(accounts)} TÀI KHOẢN ---")
    clients = []
    tasks = []

    for acc in accounts:
        acc_name = acc.get("account_name", "Unknown")
        token = acc.get("token")
        target_bot_id = acc.get("target_bot_id")
        channel_id = acc.get("channel_id")
        if not token or token == "TOKEN_CUA_ACC_CLONE":
            print(f"[{acc_name}] Bỏ qua vì chưa cấu hình Token.")
            continue
        if not target_bot_id or not channel_id:
            print(f"[{acc_name}] CẢNH BÁO: Bỏ qua vì thiếu target_bot_id hoặc channel_id.")
            continue
        client = AutoBot(
            acc_name=acc_name,
            target_bot_id=target_bot_id,
            channel_id=channel_id,
            cmd_config=acc.get("commands", {})
        )
        clients.append(client)
        tasks.append(client.start(token))

    if not tasks:
        print("Không có token/cấu hình hợp lệ nào để chạy.")
        return
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[HỆ THỐNG] Đã dừng tool an toàn.")