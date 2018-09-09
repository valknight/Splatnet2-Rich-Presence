# Splatnet Rich Presence

### Get's Splatoon game information and does fancy Discord rich presence stuff with it!

---

# Requirements

- Python 3.6+
- Discord
- Pip
- Git installed, and on your PATH

# Setup

1. Make sure discord is running
2. Clone the repository. You should find it only has 2 files, and this is normal.
3. Run install_statink - we do make some installations using pip here, so if pip needs root/admin access for you, run this as such
4. Run discord_rich_presence.py - the script uses the Splatnet2statink login flow, so you should be up and running in no time!

# FAQs

## How do I change the friend code?

Open up `discord_rich_presence.py` in your favourite text editor, and change the link underneath `# config` that reads `friend_code = "Unset"` to `friend_code = "xxxx-xxxx-xxxx"` where `"xxxx-xxxx-xxxx"` is your friend code.

## Why can't you get the game I'm in right now?

Nintendo haven't documented any of their API, seeing as they only expected it to be used for the Nintendo Switch Online app, and only data within this app is avaliable on the API, which right now does not include your current match. If you find a way to get the current match, please tell me!

## Why do you use Splatnet2statink as a requirement?

Splatnet2statink seems to be the only thing I can find which has managed to solve the issue of the "f" Nintendo introduced to many of the APIs, and instead of rewriting the wheel, it's much easier just to use this tried and tested work. Also, the "f" param is highly sensitive, and Splatnet2statink handles it in a way meaning it never touches the disk, and I've gone through the code to make sure it isn't doing anything malicious, and I can't say the same about more sensible libraries that may exist for Splatnet.

# Security

Your session token and cookie are stored on disk in config.txt, to make automatic login easier. To prevent your account being abused, protect this file, and if you are worried about security, consider using a script to delete this when you close out of the rich presence script.

# License

This is licensed under the MIT License, with Splatnet2statink being licensed under GPLv3