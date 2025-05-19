import json
import os
import random
import requests
import sys
import time
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from colorama import init, Fore, Style

init()

WEB3_PROVIDER = "https://testnet.dplabs-internal.com"
FAUCET_URL = "https://api.pharosnetwork.xyz/faucet/daily"
LOGIN_URL = "https://api.pharosnetwork.xyz/user/login"
INVITE_CODE = ""
WALLET_FILE = "wallet.txt"
DATA_FILE = "data.json"
import random

def get_random_headers():
    platforms = [
        ("Android", "Linux; Android 12; Pixel 6"),
        ("Windows", "Windows NT 10.0; Win64; x64"),
        ("macOS", "Macintosh; Intel Mac OS X 13_2"),
        ("iOS", "iPhone; CPU iPhone OS 16_0 like Mac OS X"),
        ("Linux", "X11; Linux x86_64")
    ]

    chromium_versions = ["117.0.5938.132", "118.0.5993.89", "120.0.6099.129", "125.0.6422.60"]
    safari_versions = ["537.36", "605.1.15"]
    ua_templates = {
        "Android": "Mozilla/5.0 ({os}) AppleWebKit/{safari} (KHTML, like Gecko) Chrome/{chrome} Mobile Safari/{safari}",
        "Windows": "Mozilla/5.0 ({os}) AppleWebKit/{safari} (KHTML, like Gecko) Chrome/{chrome} Safari/{safari}",
        "macOS": "Mozilla/5.0 ({os}) AppleWebKit/{safari} (KHTML, like Gecko) Chrome/{chrome} Safari/{safari}",
        "iOS": "Mozilla/5.0 ({os}) AppleWebKit/{safari} (KHTML, like Gecko) CriOS/{chrome} Mobile/15E148 Safari/{safari}",
        "Linux": "Mozilla/5.0 ({os}) AppleWebKit/{safari} (KHTML, like Gecko) Chrome/{chrome} Safari/{safari}"
    }

    platform_name, os_string = random.choice(platforms)
    chrome_version = random.choice(chromium_versions)
    safari_version = random.choice(safari_versions)
    ua_string = ua_templates[platform_name].format(os=os_string, chrome=chrome_version, safari=safari_version)

    sec_ch_ua = '"Chromium";v="{}"'.format(chrome_version.split('.')[0])
    sec_ch_ua_mobile = "?1" if "Android" in platform_name or "iOS" in platform_name else "?0"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ja-ID,ja;q=0.9,id-ID;q=0.8,id;q=0.7,en-ID;q=0.6,en-US;q=0.5,en;q=0.4",
        "Origin": "https://testnet.pharosnetwork.xyz",
        "Referer": "https://testnet.pharosnetwork.xyz/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Sec-Ch-Ua": sec_ch_ua,
        "Sec-Ch-Ua-Mobile": sec_ch_ua_mobile,
        "Sec-Ch-Ua-Platform": f'"{platform_name}"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": ua_string
    }

    return headers

HEADERS = get_random_headers()

w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))

BANNER = f"""
{Fore.MAGENTA}{Style.BRIGHT}>_< Sorry Bro >_<
{Fore.YELLOW}═══════════════════════════════════════════════
{Fore.BLUE}👨‍💻  Developed by: Poopbot Enjoy - Ok Bro
{Fore.YELLOW}═══════════════════════════════════════════════{Style.RESET_ALL}
"""
DELAY_SECONDS = 1

def progress_bar_animation(message, duration):
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    i = 0

    while time.time() < end_time:
        sys.stdout.write(f'\r{Fore.YELLOW}{message} {spinner[i % len(spinner)]}{Style.RESET_ALL}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

    sys.stdout.write(f'\r{Fore.YELLOW}{message} Done!{Style.RESET_ALL}\n')
    sys.stdout.flush()

def check_rpc_connection():
    print(f"{Fore.BLUE}[i] Checking RPC connection...{Style.RESET_ALL}")
    try:
        if w3.is_connected():
            print(f"{Fore.GREEN}[✓] Connected to RPC: {WEB3_PROVIDER}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}[x] Failed to connect to RPC: {WEB3_PROVIDER}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}[x] Error checking RPC: {str(e)}{Style.RESET_ALL}")
        return False

def generate_wallet():
    account = Account.create()
    address = account.address
    private_key = account._private_key.hex()
    save_wallet_to_json(address, private_key)
    return address, private_key

def save_wallet_to_json(address, private_key):
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data.append({
        "address": address,
        "privatekey": private_key
    })

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)    

def create_signature(private_key, message="pharos"):
    try:
        account = w3.eth.account.from_key(private_key)
        message_hash = encode_defunct(text=message)
        signed_message = w3.eth.account.sign_message(message_hash, private_key=private_key)
        return signed_message.signature.hex(), account.address
    except Exception as e:
        print(f"{Fore.RED}[x] Failed to create signature: {str(e)}{Style.RESET_ALL}")
        return None, None

def login(address, signature, retries=3):
    login_params = {
        "address": address,
        "signature": signature,
        "invite_code": INVITE_CODE
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(LOGIN_URL, headers=HEADERS, params=login_params)
            if response.status_code == 200 and response.json().get("code") == 0:
                print(f"{Fore.GREEN}[✓] Login successful for {address}{Style.RESET_ALL}")
                return response.json().get("data").get("jwt")
            print(f"{Fore.RED}[x] Login failed (Attempt {attempt+1}/{retries}): {response.json()}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[x] Login failed (Attempt {attempt+1}/{retries}): {str(e)}{Style.RESET_ALL}")
        
        if attempt < retries - 1:
            progress_bar_animation("[~] Retrying login...", 2)
    
    print(f"{Fore.RED}[x] Login failed after {retries} attempts{Style.RESET_ALL}")
    return None

def claim_faucet(address, private_key):
    signature, recovered_address = create_signature(private_key)
    if not signature or recovered_address.lower() != address.lower():
        print(f"{Fore.RED}[x] Failed to create signature or address mismatch{Style.RESET_ALL}")
        return False
    
    jwt = login(address, signature)
    if not jwt:
        print(f"{Fore.RED}[x] Login failed{Style.RESET_ALL}")
        return False
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {jwt}"
    
    for attempt in range(3):
        try:
            response = requests.post(f"{FAUCET_URL}?address={address}", headers=headers)
            if response.status_code == 200:
                print(f"{Fore.GREEN}[✓] Successfully claimed faucet for {address}{Style.RESET_ALL}")
                return True
            print(f"{Fore.RED}[x] Failed to claim faucet (Attempt {attempt+1}/3): {response.json()}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[x] Failed to claim faucet (Attempt {attempt+1}/3): {str(e)}{Style.RESET_ALL}")
        
        if attempt < 2:
            progress_bar_animation("[~] Retrying faucet claim...", 2)
    
    print(f"{Fore.RED}[x] Failed to claim faucet after 3 attempts{Style.RESET_ALL}")
    return False

def get_balance(address):
    try:
        balance_wei = w3.eth.get_balance(address)
        balance_phrs = w3.from_wei(balance_wei, "ether")
        return balance_wei, balance_phrs
    except Exception as e:
        print(f"{Fore.RED}[x] Failed to get balance for {address}: {str(e)}{Style.RESET_ALL}")
        return 0, 0

def transfer_peach(private_key, to_address, amount_wei):
    try:
        account = w3.eth.account.from_key(private_key)
        from_address = account.address
        
        nonce = w3.eth.get_transaction_count(from_address, "pending")
        gas_price = w3.eth.gas_price
        gas_limit = 21000
        
        tx = {
            "from": from_address,
            "to": to_address,
            "value": amount_wei,
            "gas": gas_limit,
            "gasPrice": gas_price,
            "nonce": nonce,
            "chainId": 688688
        }
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)

        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        except Exception as e1:
            print(f"{Fore.YELLOW}[!] raw_transaction failed: {e1}{Style.RESET_ALL}")
            try:
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            except Exception as e2:
                print(f"{Fore.RED}[x] Failed: {e2}{Style.RESET_ALL}")
                progress_bar_animation("[~] Waiting before retry...", 3)
                return False

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print(f"{Fore.GREEN}[✓] Tx Hash: {w3.to_hex(tx_hash)}{Style.RESET_ALL}")
            progress_bar_animation("[~] Processing transaction...", 3)
            return True
        else:
            print(f"{Fore.RED}[x] Transfer failed for {from_address}{Style.RESET_ALL}")
            progress_bar_animation("[~] Waiting before retry...", 3)
            return False

    except Exception as e:
        print(f"{Fore.RED}[x] Failed to transfer from {from_address}: {str(e)}{Style.RESET_ALL}")
        progress_bar_animation("[~] Waiting before retry...", 3)
        return False

def is_valid_address(address):
    return address.startswith("0x") and len(address) == 42

def read_wallet_address():
    try:
        if not os.path.exists(WALLET_FILE):
            print(f"{Fore.RED}[x] {WALLET_FILE} not found! Please create it with a valid Ethereum address.{Style.RESET_ALL}")
            return None
        with open(WALLET_FILE, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            if not lines:
                print(f"{Fore.RED}[x] {WALLET_FILE} is empty! Please add a valid Ethereum address.{Style.RESET_ALL}")
                return None

            address = random.choice(lines)
            print(f"{Fore.MAGENTA}Randomly selected recipient: {address}{Style.RESET_ALL}")
            if is_valid_address(address):
                return w3.to_checksum_address(address)
            else:
                print(f"{Fore.RED}[x] Invalid address in {WALLET_FILE}: {address}{Style.RESET_ALL}")
                return None
    except Exception as e:
        print(f"{Fore.RED}[x] Error reading {WALLET_FILE}: {str(e)}{Style.RESET_ALL}")
        return None

def get_cycle_count():
    if len(sys.argv) > 1:
        try:
            cycles = int(sys.argv[1])
            if cycles <= 0:
                print(f"{Fore.RED}[x] Number of cycles must be greater than 0{Style.RESET_ALL}")
                sys.exit(1)
            print(f"{Fore.GREEN}[✓] Will run {cycles} cycles with 5 wallets each{Style.RESET_ALL}")
            return cycles
        except ValueError:
            print(f"{Fore.RED}[x] Invalid CLI argument. Please enter a valid number.{Style.RESET_ALL}")
            sys.exit(1)
    else:
        while True:
            try:
                cycles = int(input(f"{Fore.YELLOW}[i] Enter the number of cycles (each cycle creates 5 wallets): {Style.RESET_ALL}"))
                if cycles <= 0:
                    print(f"{Fore.RED}[x] Number of cycles must be greater than 0{Style.RESET_ALL}")
                    continue
                print(f"{Fore.GREEN}[✓] Will run {cycles} cycles with 5 wallets each{Style.RESET_ALL}")
                return cycles
            except ValueError:
                print(f"{Fore.RED}[x] Please enter a valid number{Style.RESET_ALL}")

def post_with_retry(url, headers, retries=3, delay=3):
    for attempt in range(retries + 1):
        try:
            response = requests.post(url, headers=headers)
            res_json = response.json()
            if response.status_code == 200 and res_json.get("code") == 0:
                return True, res_json
            else:
                msg = res_json.get("msg", "")
                if "cannot assign requested address" in msg and attempt < retries:
                    print(f"{Fore.CYAN}[~] Backend connection error, retrying in {delay} seconds... (Attempt {attempt + 1}/{retries}){Style.RESET_ALL}")
                    time.sleep(delay)
                    continue
                else:
                    print(f"{Fore.YELLOW}[i] Faucet claim failed: {msg}{Style.RESET_ALL}")
                    return False, res_json
        except Exception as e:
            print(f"{Fore.RED}[x] Request or JSON parse error: {e}{Style.RESET_ALL}")
            return False, None
    return False, None

def process_batch(recipient, batch_size=5):
    wallets = []

    print(f"{Fore.CYAN}[i] Creating {batch_size} new wallets...{Style.RESET_ALL}")
    progress_bar_animation("[~] Generating wallets...", DELAY_SECONDS)
    for _ in range(batch_size):
        address, private_key = generate_wallet()
        wallets.append((address, private_key))
        print(f"{Fore.BLUE}[i] New wallet created - Address: {address}{Style.RESET_ALL}")

    print(f"{Fore.CYAN}[~] Logging in for {batch_size} wallets...{Style.RESET_ALL}")
    progress_bar_animation("[~] Processing logins...", DELAY_SECONDS)
    for i, (address, private_key) in enumerate(wallets[:]):
        time.sleep(DELAY_SECONDS)
        signature, recovered_address = create_signature(private_key)
        if signature and recovered_address.lower() == address.lower():
            jwt = login(address, signature)
            if jwt:
                wallets[i] = (address, private_key, jwt)
            else:
                print(f"{Fore.RED}[x] Login failed for {address}, skipping this wallet{Style.RESET_ALL}")
                wallets[i] = None
        else:
            print(f"{Fore.RED}[x] Failed to create signature for {address}, skipping this wallet{Style.RESET_ALL}")
            wallets[i] = None

    print(f"{Fore.CYAN}[i] Claiming faucet for wallets that logged in successfully...{Style.RESET_ALL}")
    progress_bar_animation("[~] Claiming faucets...", DELAY_SECONDS)
    for i, wallet in enumerate(wallets[:]):
        if wallet is None:
            continue
        time.sleep(DELAY_SECONDS)
        address, private_key, jwt = wallet
        headers = HEADERS.copy()
        headers["Authorization"] = f"Bearer {jwt}"
        success, res_json = post_with_retry(f"{FAUCET_URL}?address={address}", headers)
        if success:
            print(f"{Fore.GREEN}[✓] Successfully claimed faucet for {address}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[x] Failed to claim faucet for {address}{Style.RESET_ALL}")
            wallets[i] = None

    print(f"{Fore.CYAN}[~] Transferring to {recipient}...{Style.RESET_ALL}")
    progress_bar_animation("[~] Initiating transfers...", DELAY_SECONDS)
    for wallet in wallets:
        if wallet is None:
            continue
        time.sleep(DELAY_SECONDS)
        address, private_key, _ = wallet
        balance_wei, balance_phrs = get_balance(address)
        print(f"{Fore.BLUE}[i] Balance {address}: {balance_phrs:.4f} PHRS{Style.RESET_ALL}")

        if balance_wei == 0:
            print(f"{Fore.RED}[x] Zero balance for {address}, skipping this wallet{Style.RESET_ALL}")
            continue

        gas_limit = 21000
        gas_price = w3.eth.gas_price
        gas_fee = gas_limit * gas_price

        if balance_wei <= gas_fee:
            print(f"{Fore.RED}[x] Insufficient balance for gas in {address}, skipping this wallet{Style.RESET_ALL}")
            continue

        amount_wei = balance_wei - gas_fee
        if amount_wei <= 0:
            print(f"{Fore.RED}[x] Invalid transfer amount for {address}, skipping this wallet{Style.RESET_ALL}")
            continue

        if transfer_peach(private_key, recipient, amount_wei):
            print(f"{Fore.GREEN}[✓] Successfully transferred to {recipient}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[x] Failed to transfer from {address}{Style.RESET_ALL}")

def main():
    print(BANNER)
    
    if not check_rpc_connection():
        print(f"{Fore.RED}[x] Cannot proceed due to RPC connection issue{Style.RESET_ALL}")
        return
    
    recipient = read_wallet_address()
    if not recipient:
        print(f"{Fore.RED}[x] Cannot proceed without a valid recipient address in {WALLET_FILE}{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}[✓] Using recipient address: {recipient} for all cycles{Style.RESET_ALL}")
    
    total_cycles = get_cycle_count()
    
    for cycle in range(1, total_cycles + 1):
        print(f"{Fore.MAGENTA}\n[+] Starting Cycle {cycle} of {total_cycles} [+]{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}[~] Processing 5 claims and transferring to {recipient}{Style.RESET_ALL}")
        process_batch(recipient)
        
        print(f"{Fore.GREEN}[✓] Completed Cycle {cycle}: Processed 5 claims and transfers!{Style.RESET_ALL}")
        if cycle < total_cycles:
            progress_bar_animation("[~] Waiting for next cycle...", 5)
    
    print(f"{Fore.GREEN}🎉 All {total_cycles} cycles completed successfully!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
