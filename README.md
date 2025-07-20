# Discord Server Cloner

A Python selfbot script to clone the structure of one Discord server to another, including:

- Server name, icon, and banner
- Roles with permissions
- Categories and channels with channel permissions
- Custom emojis

> **Warning:** This script uses a selfbot, which is against Discord's Terms of Service. Use it only on servers you own or have explicit permission to manage. Use at your own risk. The author is not responsible for any bans or damages.

## Features

- Deletes existing roles and channels in the target server (except `@everyone`)
- Copies roles, permissions, and role properties
- Copies categories and channels with permissions and settings
- Copies custom emojis
- Copies server name, icon, and banner

## Requirements

- Python 3.8+
- `discord.py`
- `rich`

Install dependencies with:

```bash
pip install -r requirements.txt
