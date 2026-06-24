# Instagram Handle Hunter

A multi-threaded Python utility designed to check the availability of short, premium Instagram handle structures (3-character and 4-character combinations). It features asynchronous checking, proxies rotation to mitigate rate limits, and live alerting integration for Discord and Telegram.

## Features
* Multi-threaded engine for parallel checks.
* Automated proxy rotation with broken proxy filtering.
* Direct configuration via a single local text file.
* Real-time notifications sent to Discord and Telegram channels.

### Configuration
Before running the script, create a file named config.txt in the same directory as checker.py. Use the following template to supply your target metrics, webhook credentials, and proxy list:
DISCORD_WEBHOOK=https://discord.com/api/webhooks/your_webhook_url
TELEGRAM_BOT_TOKEN=123456789:ABCdefYourBotToken
TELEGRAM_CHAT_ID=987654321
TARGET=20
PROXIES=
http://username:password@ip:port
socks5://username:password@ip2:port2
Configuration Rules:
 If you do not wish to use Discord or Telegram notification pipelines, leave those variable values completely blank.
 Add your proxy list line-by-line directly beneath the PROXIES= marker line.
 Every proxy listed must include the protocol prefix (http://, https://, socks4://, or socks5://) to be properly injected into memory.


## Installation

### Prerequisites
Before setting up the project, ensure you have Python 3.10 or higher installed on your local PC. You can check your current version by running the following command in your terminal or command prompt:
```bash
python --version
```
Clone this repository to your local machine using Git:
```bash
git clone https://github.com/HackerAlien99/ig-premium-checker-.git

```
Change into the project directory:
```bash
cd ig-premium-checker-
```
Install the required network communication library using pip:
```bash
pip install requests
```
Execute the program directly from your command line interface:
```bash
python checker.py
```