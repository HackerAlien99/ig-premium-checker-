# ig-premium-checker-
Multi-threaded Instagram availability checker for 3-4 character premium handles. Parses proxies, Discord webhooks, and Telegram alerts directly from a local config.txt file. Features automated proxy rotation, dead node filtering, multi-threaded parallel execution, and automated local logging to minimize rate-limiting and maximize stability.

# Instagram Handle Hunter

A multi-threaded Python utility designed to check the availability of short, premium Instagram handle structures (3-character and 4-character combinations). It features asynchronous checking, proxies rotation to mitigate rate limits, and live alerting integration for Discord and Telegram.

## Features
* Multi-threaded engine for parallel checks.
* Automated proxy rotation with broken proxy filtering.
* Direct configuration via a single local text file.
* Real-time notifications sent to Discord and Telegram channels.

## Installation

1. Ensure Python 3.10 or higher is installed on your system.
2. Clone this repository or download the source files.
3. Open a terminal or command prompt in the project folder and install the required library:

```bash
pip install requests
