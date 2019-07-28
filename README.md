# Splatnet Rich Presence

### Get's Splatoon game information and does fancy Discord rich presence stuff with it!

![GitHub Stars](https://img.shields.io/github/stars/valerokai/Splatnet2-Rich-Presence.svg?style=for-the-badge)
---

# Requirements

- Python 3.6.X
- Git
- Discord
- Pip (included with Python 3.6.X)
- **Only for Manually Generating a Cookie:** Android Emulator (Nox) / Device running Android 5 or 6, or an iOS device

(If using iOS, I recommend using ikaWidget2 instead of the official NSO app, as you can pull to refresh to quickly get the cookie)

# Setup

1. Make sure Discord is running
2. Install Python 3.6.X and Git
3. Clone the repository by using Git Bash (use the HTTPS Link when you've clicked on the "Clone or Download" button)
4. Run setup.py - we do make some installations using Pip here and upgrade Pip to the latest version (Python 3.6.X  contains a lower version of Pip), so if Pip needs root/admin access for you, run this as such
5. Run discord_rich_presence.py - you should be prompted to how to login once running this, and you should be up and running in no time!

Video Tutorial Coming Soon!

# FAQs

## How do I change the method of generating a new Cookie (From auto to manual or vice versa?

Delete the `config.txt` in the config folde, run the script (discord_rich_presence.py) and choose your new desired method.

## Why can't you get the game I'm in right now?

Nintendo haven't documented any of their API, seeing as they only expected it to be used for the Nintendo Switch Online app, and only data within this app is avaliable on the API, which right now does not include your current match. If you find a way to get the current match, please tell me!


# Security (Cookie Generation)

In order to get your cookie from the official app, we have to use a man-in-the-middle attack in order to take this cookie during natural operation. However, we use mitmproxy as a base, which generates certificates on your machine, meaning installing our certificate won't put your device at risk unless these certificates leak. If you are still paranoid, we can recommend using an Android emulator (Ex. Nox) running Android 6.0 or lower.

If you want to read more about this, click [here.](https://github.com/frozenpandaman/splatnet2statink#cookie-generation)

# License

This is licensed under the MIT License.

Many thanks to *Splatnet2statink*, for having an open source and readily documented method for logging into Splatnet2! A lot of our code is based off theirs, and it's pretty cool, so check it out!

[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=for-the-badge&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)
