# Splatnet Rich Presence

### Get's Splatoon game information and does fancy Discord rich presence stuff with it!

---

# Requirements

- Python 3.6+
- Discord
- Pip
- Android emulator / device running android 6 or below, or an iOS device

(If using iOS, I recommend using ikaWidget2 instead of the official NSO app, as you can pull to refresh to quickly get the cookie)

# Setup

1. Make sure discord is running
2. Clone the repository
3. Run setup.py - we do make some installations using pip here, so if pip needs root/admin access for you, run this as such
4. Run discord_rich_presence.py - you should be prompted to how to login once running this, and you should be up and running in no time!

# FAQs

## How do I change the friend code?

Run the script once, log in, then stop it. Open up `config.txt` in the config folder and change the friend code parameter to yours!

## Why can't you get the game I'm in right now?

Nintendo haven't documented any of their API, seeing as they only expected it to be used for the Nintendo Switch Online app, and only data within this app is avaliable on the API, which right now does not include your current match. If you find a way to get the current match, please tell me!


# Security

In order to get your cookie from the official app, we have to use a man-in-the-middle attack in order to take this cookie during natural operation. However, we use mitmproxy as a base, which generates certificates on your machine, meaning installing our certificate won't put your device at risk unless these certificates leak. If you are still paranoid, we can recommend using an Android emulator running Android 6.0 or lower.

# License

This is licensed under the MIT License.

Many thanks to *Splatnet2statink*, for having an open source and readily documented method for logging into Splatnet2! A lot of our code is based off theirs, and it's pretty cool, so check it out!
