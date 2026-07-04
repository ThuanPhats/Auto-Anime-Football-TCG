import discord
import asyncio
import random
import re
import time
from datetime import datetime, timedelta

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
            "club_wage": 24 * 60 * 60,
            "arena-match": 15 * 60
        }

    async def on_ready(self):
        print(f"[{self.get_time()}] [{self.acc_name}] Connected: {self.user.name}")
        channel = self.get_channel(self.channel_id)
        
        if not channel:
            print(f"[{self.acc_name}] Error: Chat channel {self.channel_id} not found!")
            return
        try:
            commands = await channel.application_commands()
        except Exception as e:
            print(f"[{self.acc_name}] Error loading commands: {e}")
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
        if self.cmd_config.get("arena-match"):
            asyncio.create_task(self.run_command_loop(channel, commands, "arena-match", self.cooldowns["arena-match"]))

    async def run_command_loop(self, channel, commands, cmd_name, base_cooldown, sub_command=None):
        target_cmd = None
        for cmd in commands:
            if cmd.application_id == self.target_bot_id and cmd.name == cmd_name:
                target_cmd = cmd
                break
        if not target_cmd:
            print(f"[{self.acc_name}] WARNING: Command /{cmd_name} not found")
            return
        if sub_command:
            target_cmd = next((c for c in target_cmd.children if c.name == sub_command), None)
            if not target_cmd:
                 return
            display_name = f"{cmd_name} {sub_command}"
        else:
            display_name = cmd_name
            
        daily_uses = 0
        last_date = datetime.now().date()
        
        await asyncio.sleep(random.randint(5, 30))

        while not self.is_closed():
            current_date = datetime.now().date()
            if current_date != last_date:
                daily_uses = 0
                last_date = current_date

            if cmd_name == "arena-match" and daily_uses >= 10:
                now = datetime.now()
                tomorrow = now + timedelta(days=1)
                midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0)
                sleep_time = (midnight - now).total_seconds()
                next_run_minutes = int(sleep_time // 60)
                
                print(f"[{self.get_time()}] [{self.acc_name}] 10 uses of /{display_name} reached today. Pausing for {next_run_minutes} minutes until next day.")
                await asyncio.sleep(sleep_time + random.randint(120, 600))
                continue

            print(f"[{self.get_time()}] [{self.acc_name}] Sending command: /{display_name}")
            success = False
            for attempt in range(2):
                try:
                    await target_cmd(channel=channel)
                    success = True
                    break 
                except Exception as e:
                    error_str = str(e)
                    if "Did not receive a response" in error_str or "NotFound" in error_str or "Timeout" in error_str:
                        print(f"[{self.get_time()}] [{self.acc_name}] Timeout /{display_name}, retrying in 5s... (Attempt {attempt+1}/2)")
                        await asyncio.sleep(5)
                    else:
                        print(f"[{self.get_time()}] [{self.acc_name}] Error running /{display_name}: {e}")
                        break
            if not success:
                print(f"[{self.get_time()}] [{self.acc_name}] Skipping /{display_name} due to network lag.")
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
                        
                if "Cooldown" not in content and "come back later" not in content:
                    if cmd_name == "arena-match":
                        daily_uses += 1
                        print(f"[{self.get_time()}] [{self.acc_name}] Used /{display_name} {daily_uses}/10 times.")
                        
                if "Cooldown" in content or "come back later" in content:
                    timestamps = re.findall(r'<t:(\d+)(?::[a-zA-Z])?>', content)
                    if timestamps:
                        target_unix = max([int(ts) for ts in timestamps])
                        sleep_time = max(0, target_unix - int(time.time()))
                        print(f"[{self.get_time()}] [{self.acc_name}] Caught timestamp for /{display_name}: Waiting {int(sleep_time)}s.")
                    else:
                        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4} at \d{1,2}:\d{2} [AP]M)', content)
                        if date_match:
                            try:
                                date_str = date_match.group(1)
                                target_dt = datetime.strptime(date_str, "%B %d, %Y at %I:%M %p")
                                sleep_time = max(0, (target_dt - datetime.now()).total_seconds())
                                print(f"[{self.get_time()}] [{self.acc_name}] Read text time for /{display_name}: Waiting {int(sleep_time)}s.")
                            except Exception as e:
                                pass 

            except asyncio.TimeoutError:
                pass

            human_delay = random.randint(60, 300) 
            total_sleep = sleep_time + human_delay
            
            next_run_minutes = int(total_sleep // 60)
            print(f"[{self.get_time()}] [{self.acc_name}] Completed /{display_name}. Resting for {next_run_minutes} minutes (Added {human_delay}s random delay).")
            await asyncio.sleep(total_sleep)
            
    def get_time(self):
        return datetime.now().strftime("%H:%M:%S")
