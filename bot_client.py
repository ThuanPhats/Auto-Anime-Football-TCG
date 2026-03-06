import discord
import asyncio
import random
import re
import time
from datetime import datetime

class AutoBot(discord.Client):
    def __init__(self, acc_name, target_bot_id, channel_id, cmd_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.acc_name = acc_name
        self.target_bot_id = int(target_bot_id)
        self.channel_id = int(channel_id)
        self.cmd_config = cmd_config
        
        self.cooldowns = {
            "claim": 60 * 60,
            "daily": 24 * 60 * 60,
            "weekly": 7 * 24 * 60 * 60,
            "wage": 24 * 60 * 60,
            "club_wage": 24 * 60 * 60
        }

    async def on_ready(self):
        print(f"[{self.get_time()}] [{self.acc_name}] Đã kết nối: {self.user.name}")
        channel = self.get_channel(self.channel_id)
        
        if not channel:
            print(f"[{self.acc_name}] Lỗi: Không tìm thấy kênh chat {self.channel_id}!")
            return
        try:
            commands = await channel.application_commands()
        except Exception as e:
            print(f"[{self.acc_name}] Lỗi tải lệnh: {e}")
            return
        if self.cmd_config.get("claim"):
            asyncio.create_task(self.run_command_loop(channel, commands, "claim", self.cooldowns["claim"]))
        if self.cmd_config.get("daily"):
            asyncio.create_task(self.run_command_loop(channel, commands, "daily", self.cooldowns["daily"]))
        if self.cmd_config.get("weekly"):
            asyncio.create_task(self.run_command_loop(channel, commands, "weekly", self.cooldowns["weekly"]))
        if self.cmd_config.get("wage"):
            asyncio.create_task(self.run_command_loop(channel, commands, "wage", self.cooldowns["wage"]))
        if self.cmd_config.get("club_wage"):
            asyncio.create_task(self.run_command_loop(channel, commands, "club", self.cooldowns["club_wage"], sub_command="wage"))

    async def run_command_loop(self, channel, commands, cmd_name, base_cooldown, sub_command=None):
        target_cmd = None
        for cmd in commands:
            if cmd.application_id == self.target_bot_id and cmd.name == cmd_name:
                target_cmd = cmd
                break
        if not target_cmd:
            print(f"[{self.acc_name}] CẢNH BÁO: Không tìm thấy /{cmd_name}")
            return
        if sub_command:
            target_cmd = next((c for c in target_cmd.children if c.name == sub_command), None)
            if not target_cmd:
                 return
            display_name = f"{cmd_name} {sub_command}"
        else:
            display_name = cmd_name
        await asyncio.sleep(random.randint(5, 30))

        while not self.is_closed():
            print(f"[{self.get_time()}] [{self.acc_name}] Gửi lệnh: /{display_name}")
            success = False
            for attempt in range(2):
                try:
                    await target_cmd(channel=channel)
                    success = True
                    break 
                except Exception as e:
                    error_str = str(e)
                    if "Did not receive a response" in error_str or "NotFound" in error_str or "Timeout" in error_str:
                        print(f"[{self.get_time()}] [{self.acc_name}] Timeout /{display_name}, thử lại sau 5s... (Lần {attempt+1}/2)")
                        await asyncio.sleep(5)
                    else:
                        print(f"[{self.get_time()}] [{self.acc_name}] Lỗi khi chạy /{display_name}: {e}")
                        break
            if not success:
                print(f"[{self.get_time()}] [{self.acc_name}] Bỏ qua /{display_name} do mạng lag.")
                await asyncio.sleep(120)  
                continue
            def check_reply(msg):
                if msg.author.id != self.target_bot_id or msg.channel.id != channel.id:
                    return False
                if msg.interaction and msg.interaction.user.id == self.user.id:
                    inter_name = msg.interaction.name.lower()
                    if inter_name == display_name.lower() or inter_name == cmd_name.lower():
                        return True
                if self.user.mentioned_in(msg):
                    msg_text = msg.content.lower()
                    if msg.embeds:
                        for em in msg.embeds:
                            msg_text += f" {(em.title or '').lower()} {(em.description or '').lower()}"
                    if cmd_name.lower() in msg_text:
                        return True
                return False
            sleep_time = base_cooldown
            try:
                reply = await self.wait_for('message', check=check_reply, timeout=15.0)
                content = reply.content
                if reply.embeds:
                    for embed in reply.embeds:
                        if embed.description: content += f" {embed.description}"
                        if embed.title: content += f" {embed.title}"
                if "Cooldown" in content or "come back later" in content:
                    timestamps = re.findall(r'<t:(\d+)(?::[a-zA-Z])?>', content)
                    if timestamps:
                        target_unix = max([int(ts) for ts in timestamps])
                        sleep_time = max(0, target_unix - int(time.time()))
                        print(f"[{self.get_time()}] [{self.acc_name}] Bắt được mốc thời gian /{display_name}: Chờ {int(sleep_time)}s.")
                    else:
                        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [AP]M)', content)
                        if date_match:
                            try:
                                date_str = date_match.group(1)
                                target_dt = datetime.strptime(date_str, "%B %d, %Y at %I:%M %p")
                                sleep_time = max(0, (target_dt - datetime.now()).total_seconds())
                                print(f"[{self.get_time()}] [{self.acc_name}] Đọc được text thời gian /{display_name}: Chờ {int(sleep_time)}s.")
                            except Exception as e:
                                pass 

            except asyncio.TimeoutError:
                pass

            human_delay = random.randint(60, 300) 
            total_sleep = sleep_time + human_delay
            
            next_run_minutes = int(total_sleep // 60)
            print(f"[{self.get_time()}] [{self.acc_name}] Hoàn tất /{display_name}. Nghỉ ngơi {next_run_minutes} phút (Đã cộng {human_delay}s random).")
            await asyncio.sleep(total_sleep)
    def get_time(self):
        return datetime.now().strftime("%H:%M:%S")