# Instagram Handle Hunter

A multi-threaded Python utility designed to check the availability of short, premium Instagram handle structures (3-character and 4-character combinations). It features asynchronous checking, proxies rotation to mitigate rate limits, and live alerting integration for Discord and Telegram.

## Features
* Multi-threaded engine for parallel checks.
* Automated proxy rotation with broken proxy filtering.
* Direct configuration via a single local text file.
* Real-time notifications sent to Discord and Telegram channels.

## Installation

### Prerequisites
Before setting up the project, ensure you have Python 3.10 or higher installed on your local PC. You can check your current version by running the following command in your terminal or command prompt:
```bash
python --version
```
Clone this repository to your local machine using Git:
```bash
git clone [https://github.com/HackerAlien99/ig-premium-checker-.git](https://github.com/HackerAlien99/ig-premium-checker-.git)```

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