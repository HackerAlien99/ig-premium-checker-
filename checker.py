import requests
import random
import string
import time
import threading
import itertools
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys

# ─── CONFIGURATION LOADING (TXT PARSER) ───
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TARGET = int(os.getenv("TARGET", "20"))
RESIDENTIAL_PROXIES = []

CONFIG_FILE = "config.txt"

if os.path.exists(CONFIG_FILE):
    print(f" Found {CONFIG_FILE}! Parsing local user definitions...")
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        parsing_proxies = False
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            # Switch to proxy collecting mode if we hit the header line
            if line.upper().startswith("PROXIES="):
                parsing_proxies = True
                # Check if there's an inline proxy string right after the equals sign
                inline_p = line.split("=", 1)[1].strip()
                if inline_p and not any(x in inline_p for x in ["user:pass", "example"]):
                    for p in inline_p.split(","):
                        p = p.strip()
                        if p.startswith(("http://", "https://", "socks4://", "socks5://")):
                            RESIDENTIAL_PROXIES.append(p)
                continue
            
            if parsing_proxies:
                if not any(x in line for x in ["user:pass", "example"]) and line.startswith(("http://", "https://", "socks4://", "socks5://")):
                    RESIDENTIAL_PROXIES.append(line)
            else:
                if "=" in line:
                    key, val = line.split("=", 1)
                    key, val = key.strip().upper(), val.strip()
                    if not val or any(x in val for x in ["your_", "token_here", "webhook_here"]):
                        continue
                    if key == "DISCORD_WEBHOOK":
                        DISCORD_WEBHOOK = val
                    elif key == "TELEGRAM_BOT_TOKEN":
                        TELEGRAM_BOT_TOKEN = val
                    elif key == "TELEGRAM_CHAT_ID":
                        TELEGRAM_CHAT_ID = val
                    elif key == "TARGET":
                        try: TARGET = int(val)
                        except: pass
    except Exception as e:
        print(f"⚠️ Error reading config.txt: {e}")

# If config.txt didn't load proxies, check system variables as fallback
if not RESIDENTIAL_PROXIES and os.getenv("PROXIES"):
    for p in os.getenv("PROXIES", "").split(","):
        p = p.strip()
        if p.startswith(("http://", "https://", "socks4://", "socks5://")):
            RESIDENTIAL_PROXIES.append(p)

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
]

HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Upgrade-Insecure-Requests": "1",
}

MAX_WORKERS = 15  
TIMEOUT = 12
DELAY_MIN = 1
DELAY_MAX = 3

print(f" Runtime Parameters:")
print(f"   -> Target Hits Needed: {TARGET}")
print(f"   -> Discord Alert Pipeline: {'ACTIVE' if DISCORD_WEBHOOK else 'DISABLED'}")
print(f"   -> Telegram Alert Pipeline: {'ACTIVE' if (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID) else 'DISABLED'}")
print(f"   -> Total Valid Proxies Loaded: {len(RESIDENTIAL_PROXIES)}")

BASE_DIR = os.getcwd() 
AVAILABLE_FILE = os.path.join(BASE_DIR, "available.txt")
CACHE_FILE = os.path.join(BASE_DIR, "checked.txt")
STATS_FILE = os.path.join(BASE_DIR, "stats.json")

for f_path in [AVAILABLE_FILE, CACHE_FILE]:
    if not os.path.exists(f_path):
        with open(f_path, "w") as f: f.write("")

# ─── UNIVERSAL NOTIFICATION MANAGER ───
class NotificationManager:
    def __init__(self, discord_url, tg_token, tg_chat):
        self.discord_url = discord_url
        self.tg_token = tg_token
        self.tg_chat = tg_chat
    
    def send_alert(self, username):
        message = f"🎯 IG Hunter Found an Available Username!\n\n Username: @{username}\n Link: https://instagram.com/{username}"
        
        if self.discord_url:
            embed = {
                "title": "🔥 AVAILABLE USERNAME FOUND!",
                "description": f"🔗 [@{username}](https://instagram.com/{username}) is currently unregistered!",
                "color": 0x00FF00,
                "timestamp": datetime.now().isoformat(),
            }
            try: requests.post(self.discord_url, json={"embeds": [embed]}, timeout=8)
            except: pass
            
        if self.tg_token and self.tg_chat:
            tg_url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
            try: requests.post(tg_url, json={"chat_id": self.tg_chat, "text": message}, timeout=8)
            except: pass

notifier = NotificationManager(DISCORD_WEBHOOK, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

# ─── USERNAME GENERATOR POOL ───
class UsernamePool:
    def __init__(self):
        self.letters = string.ascii_lowercase
        self.digits = string.digits
        self.separators = ['.', '_']
        self.pool = []
        self.index = 0
        self.lock = threading.Lock()
        self._generate()
    
    def _generate(self):
        print(f" Compiling structural handle combination matrices (Target Lengths: 3-4)...")
        all_names = set()
        for total_len in [3, 4]:
            for left_len in range(1, total_len):
                right_len = total_len - left_len - 1
                if right_len < 0: continue
                left_combos = [''.join(p) for p in itertools.product(self.letters, repeat=left_len)]
                if right_len == 0:
                    right_combos = [""]
                else:
                    right_combos = [''.join(p) for p in itertools.product(self.letters, repeat=right_len)] + [''.join(p) for p in itertools.product(self.digits, repeat=right_len)]
                
                for prefix in left_combos:
                    for sep in self.separators:
                        for suffix in right_combos:
                            user = f"{prefix}{sep}{suffix}" if suffix else f"{prefix}{sep}"
                            if not user.endswith(('.', '_')): all_names.add(user)
                            
        self.pool = list(all_names)
        random.shuffle(self.pool)
        if len(self.pool) > 15000: self.pool = self.pool[:15000]
        print(f"   Matrix Synthesized: {len(self.pool):,} clean premium sequences mapped.")
    
    def get_next(self):
        with self.lock:
            if self.index >= len(self.pool): return None
            u = self.pool[self.index]; self.index += 1; return u

# ─── PROXY MANAGER ───
class ProxyManager:
    def __init__(self, proxy_list):
        self.proxies = list(proxy_list)
        self.index = 0
        self.lock = threading.Lock()
        self.failure_counter = {}
    def get_proxy(self):
        if not self.proxies: return None
        with self.lock:
            if self.index >= len(self.proxies): self.index = 0
            p = self.proxies[self.index]; self.index = (self.index + 1) % len(self.proxies); return {"http": p, "https": p}
    def mark_bad(self, pd):
        if not pd or not self.proxies: return
        p_url = pd["http"]
        if p_url in self.proxies:
            with self.lock:
                self.failure_counter[p_url] = self.failure_counter.get(p_url, 0) + 1
                if self.failure_counter[p_url] >= 3: self.proxies.remove(p_url)

proxy_manager = ProxyManager(RESIDENTIAL_PROXIES)

# ─── CONNECTION SESSION MANAGER ───
class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.lock = threading.Lock()
    def get(self, tid):
        with self.lock:
            if tid not in self.sessions:
                s = requests.Session()
                hdrs = HEADERS_BASE.copy(); hdrs["User-Agent"] = random.choice(USER_AGENTS); s.headers.update(hdrs)
                self.sessions[tid] = s
            return self.sessions[tid]

session_manager = SessionManager()

# ─── CACHE CONTROLLER ───
class Cache:
    def __init__(self):
        self.checked = set(); self.available = []; self.lock = threading.Lock()
        self._load()
    def _load(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    for line in f: self.checked.add(line.strip())
            except: pass
    def is_checked(self, u):
        with self.lock: return u in self.checked
    def add_checked(self, u):
        with self.lock: self.checked.add(u)
        try:
            with open(CACHE_FILE, "a") as f: f.write(u + "\n")
        except: pass
    def add_available(self, u):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"@{u} | {ts}"
        with self.lock: self.available.append(entry)
        try:
            with open(AVAILABLE_FILE, "a") as f: f.write(entry + "\n")
        except: pass

cache = Cache()

# ─── METRICS TRACKER ───
class Stats:
    def __init__(self):
        self.checked = 0; self.available = 0; self.taken = 0; self.errors = 0; self.start = time.time(); self.lock = threading.Lock()
    def update(self, s):
        with self.lock:
            self.checked += 1
            if s == "available": self.available += 1
            elif s == "taken": self.taken += 1
            else: self.errors += 1
    def show(self):
        with self.lock:
            el = time.time() - self.start; sp = self.checked / el if el > 0 else 0
            print(f"\r Checked: {self.checked:,} | ✅ Avail: {self.available} | ❌ Taken: {self.taken} | Speed: {sp:.1f}/s", end="")
            sys.stdout.flush()

stats = Stats()

# ─── CORE REQUEST NETWORK EVALUATION ───
def check(username, tid=0):
    session = session_manager.get(tid)
    proxy = proxy_manager.get_proxy()
    url = f"https://www.instagram.com/{username}/"
    
    for attempt in range(1, 4):
        try:
            r = session.get(url, proxies=proxy, timeout=TIMEOUT, allow_redirects=False)
            if r.status_code == 404: return True
            if r.status_code == 200: return False
            if r.status_code in (301, 302, 403, 429):
                proxy_manager.mark_bad(proxy)
                proxy = proxy_manager.get_proxy()
                time.sleep(2)
                continue
            return None
        except:
            proxy_manager.mark_bad(proxy)
            proxy = proxy_manager.get_proxy()
            time.sleep(1)
            continue
    return None

# ─── THREAD WORKER RUNNER ───
def worker(found_ref, found_lock, pool):
    tid = threading.current_thread().ident % 10000
    while True:
        with found_lock:
            if found_ref[0] >= TARGET: return
        username = pool.get_next()
        if username is None: return
        if cache.is_checked(username): continue
        cache.add_checked(username)
        
        result = check(username, tid)
        if result is None:
            stats.update("error")
            continue
            
        if result is True:
            cache.add_available(username); stats.update("available")
            notifier.send_alert(username)
            with found_lock:
                found_ref[0] += 1
                if found_ref[0] >= TARGET: return
        else:
            stats.update("taken")
            
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        stats.show()

# ─── MAIN ENTRYPOINT ───
print("=" * 60)
print(f" Multi-Threaded Local Intelligence Engine Initialized")
print("=" * 60)

pool = UsernamePool()
found_ref = [0]
found_lock = threading.Lock()

try:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(worker, found_ref, found_lock, pool) for _ in range(MAX_WORKERS)]
        for f in as_completed(futures):
            try: f.result()
            except: pass
except KeyboardInterrupt:
    print("\n\n Execution terminated by user command.")

try:
    with open(STATS_FILE, "w") as f:
        json.dump({"checked": stats.checked, "available": stats.available, "taken": stats.taken}, f, indent=2)
except: pass

print("\n Process finished.")
