import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sys
import random

def print_banner():
    print("\n")
    print("=" * 60)
    print("CONCORD.CLUB x the cult".center(60))
    print("=" * 60)
    print("Join us:".center(60))
    print("https://t.me/rubybotit".center(60))
    print("https://x.com/concordalpha".center(60))
    print("https://t.me/concordclub".center(60))
    print("=" * 60)
    print("\n")

def get_nocache_headers():
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0',
        'pragma': 'no-cache',
        'cache-control': 'no-cache, no-store, must-revalidate',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
    }

def check_wallet(address, retry=3):
    url = 'https://mefoundation.com/claim-token/amount'
    params = {
        'address': address,
        '_nc': str(int(time.time() * 1000)),
        'r': str(random.random())
    }
    
    for attempt in range(retry):
        try:
            response = requests.get(
                url, 
                params=params, 
                headers=get_nocache_headers(), 
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            amount_div = soup.find('div', class_='text-6xl font-extrabold')
            
            if amount_div:
                amount = int(amount_div.text.strip())
                return {'success': True, 'amount': amount}
            return {'success': True, 'amount': 0}
            
        except Exception as e:
            if attempt == retry - 1:
                return {'success': False, 'error': str(e)}
            time.sleep(1 + random.random())

def clear_line():
    sys.stdout.write('\r' + ' ' * 100)
    sys.stdout.write('\r')
    sys.stdout.flush()

def main():
    print_banner()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = open(f'results_{timestamp}.txt', 'w', encoding='utf-8')
    success_file = open(f'success_{timestamp}.txt', 'w', encoding='utf-8')
    
    def log(msg, success_only=False):
        clear_line()
        print(msg)
        log_file.write(f"{msg}\n")
        log_file.flush()
        if success_only:
            success_file.write(f"{msg}\n")
            success_file.flush()
    
    try:
        with open('wallets.txt', 'r') as f:
            wallets = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        log("Error: wallets.txt not found!")
        return

    log(f"Starting check of {len(wallets)} wallets...")
    results = {'success': 0, 'failed': 0, 'with_tokens': 0, 'total_me': 0}
    
    try:
        for i, wallet in enumerate(wallets, 1):
            result = check_wallet(wallet)
            
            if result['success']:
                results['success'] += 1
                if result.get('amount', 0) > 0:
                    amount = result['amount']
                    results['with_tokens'] += 1
                    results['total_me'] += amount
                    clear_line()
                    msg = f"{i}/{len(wallets)} | ✓ {wallet} | {amount} ME"
                    log(msg, success_only=True)
                else:
                    clear_line()
                    progress = f"Processed: {i}/{len(wallets)} | Found: {results['with_tokens']} | Total ME: {results['total_me']}"
                    sys.stdout.write(f"\r{progress}")
                    sys.stdout.flush()
            else:
                results['failed'] += 1
                clear_line()
                log(f"{i}/{len(wallets)} | ✕ {wallet} | Error: {result['error']}")

            if i % 10 == 0:
                clear_line()
                log(f"\nStatus: {i}/{len(wallets)} | Success: {results['success']} | With tokens: {results['with_tokens']} | Total ME: {results['total_me']} | Failed: {results['failed']}\n")

    except KeyboardInterrupt:
        clear_line()
        log("\nScript interrupted by user. Saving results...")
    
    finally:
        clear_line()
        log("\nFinal Results:")
        log(f"Total wallets checked: {len(wallets)}")
        log(f"Successful checks: {results['success']}")
        log(f"Wallets with tokens: {results['with_tokens']}")
        log(f"Total ME tokens: {results['total_me']}")
        log(f"Failed checks: {results['failed']}")
        
        log_file.close()
        success_file.close()

if __name__ == "__main__":
    main()