# 🤖 Auto Farm For Aniime Football TCG

This project is a Discord self-bot automation tool that automatically sends slash commands (`/claim`, `/daily`, etc.) to specified channels. Initially optimized for the **Blue Lock TCG** bot, but it can be easily adapted for other Discord bots.

The system supports running multiple accounts simultaneously, automatically reads bot response messages to calculate highly accurate cooldown times, and simulates human delay to minimize detection risks.

⚠️ **IMPORTANT WARNING:** Using a Self-bot (automating a personal user account) **violates Discord's Terms of Service (ToS)**. If abused, your account is at risk of being banned. Use this tool at your own risk. Absolutely **NEVER** share your `config.json` file or your Token with anyone!

---

## ✨ Features

- **Multi-account Support:** Run dozens of accounts simultaneously on a single Terminal window.
- **Independent Threading:** Each account can be deployed in a different Server / Channel to avoid drawing attention.
- **Command Customization:** Enable or disable specific commands (`claim`, `daily`, `weekly`, etc.) individually for each account.
- **Smart Cooldown Reading:** Say goodbye to hard-coded wait times. The tool automatically catches the Bot's reply messages, parses the Unix Timestamp or Text Date, and calculates the exact seconds to sleep.
- **Human Jitter:** Adds a random delay of 1 to 5 minutes after each command execution to break the perfect, detectable loop of a machine.

---

## 🛠️ Prerequisites

To run this script, your machine needs to have the following installed:
1. **[Python 3.8+](https://www.python.org/downloads/):** The runtime environment (Note: Remember to check *"Add Python to PATH"* during installation on Windows).
2. **[Git](https://git-scm.com/downloads):** Strictly required to download the `discord.py-self` library directly from GitHub.

---

## 🚀 Installation

**Step 1:** Download the source code (Clone the repository or download the ZIP file and extract it).

**Step 2:** Open your Terminal (or Command Prompt / PowerShell) in the source code directory.

**Step 3:** Install the required dependencies using the following command:
```bash
pip install -r requirements.txt
```
**Step 4:** Adjust your config.json file

**Step 5:** Run command:
```bash
python main.py
```
