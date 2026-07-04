import asyncio
from src.core.config_manager import load_config
from src.core.bot_client import AutoBot

async def main():
    config = load_config()
    accounts = config.get("accounts", [])
    if not accounts:
        print("[ERROR] No accounts configured in config.json")
        return
    print(f"--- STARTING SYSTEM WITH {len(accounts)} ACCOUNTS ---")
    clients = []
    tasks = []

    for acc in accounts:
        acc_name = acc.get("account_name", "Unknown")
        token = acc.get("token")
        target_bot_id = acc.get("target_bot_id")
        channel_id = acc.get("channel_id")
        if not token or token == "TOKEN_CUA_ACC_CLONE":
            print(f"[{acc_name}] Skipped because Token is not configured.")
            continue
        if not target_bot_id or not channel_id:
            print(f"[{acc_name}] WARNING: Skipped due to missing target_bot_id or channel_id.")
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
        print("No valid token/configuration to run.")
        return
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SYSTEM] Tool stopped safely.")