import argparse
import requests
from stem import Signal
from stem.control import Controller
import time

# Configurações padrão
DEFAULT_TOR_SOCKS_PORT = 9050
DEFAULT_TOR_CONTROL_PORT = 9051
DEFAULT_I2P_HTTP_PORT = 4444
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # segundos

def print_start():
    print("""   whosurf: v1.5\n""")

def conn_tor(tor_socks_port):
    session = requests.Session()
    session.proxies = {
        'http': f'socks5://127.0.0.1:{tor_socks_port}',
        'https': f'socks5://127.0.0.1:{tor_socks_port}',
    }
    return session

def conn_i2p(i2p_http_port):
    session = requests.Session()
    session.proxies = {
        'http': f'http://127.0.0.1:{i2p_http_port}',
        'https': f'http://127.0.0.1:{i2p_http_port}',
    }
    return session

def authn(tor_control_port):
    with Controller.from_port(port=tor_control_port) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

def fetch_url(session, url, max_attempts=RETRY_ATTEMPTS, delay=RETRY_DELAY):
    attempt = 0
    while attempt < max_attempts:
        try:
            response = session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            attempt += 1
            if attempt < max_attempts:
                print(f'[!] erro: {e}. tentativa {attempt} de {max_attempts}! esperando {delay} segundos antes da próxima tentativa...')
                time.sleep(delay)
            else:
                return f'[!] erro: {e}. número máximo de tentativas atingido... ;/'

def main():
    parser = argparse.ArgumentParser(description=print_start())
    
    subparsers = parser.add_subparsers(dest='network', required=True)
    
    # Argumentos para Tor
    tor_parser = subparsers.add_parser('tor', help='conectar via TOR')
    tor_parser.add_argument('--tor-socks-port', type=int, default=DEFAULT_TOR_SOCKS_PORT, help='porta do proxy SOCKS do Tor (padrão: 9050)')
    tor_parser.add_argument('--tor-control-port', type=int, default=DEFAULT_TOR_CONTROL_PORT, help='porta do controle do Tor (padrão: 9051)')
    tor_parser.add_argument('--tor-url', type=str, default='http://check.torproject.org', help='URL para acessar via Tor (padrão: http://check.torproject.org)')

    # Argumentos para I2P
    i2p_parser = subparsers.add_parser('i2p', help='conectar via I2P')
    i2p_parser.add_argument('--i2p-http-port', type=int, default=DEFAULT_I2P_HTTP_PORT, help='porta do proxy HTTP do I2P (padrão: 4444)')
    i2p_parser.add_argument('--i2p-url', type=str, default='http://i2p-projekt.i2p', help='URL para acessar via I2P (padrão: http://i2p-projekt.i2p)')

    args = parser.parse_args()

    if args.network == 'tor':
        tor_session = conn_tor(args.tor_socks_port)
        print("[+] conectando via Tor...")
        print(fetch_url(tor_session, args.tor_url))
        print("[+] renovando IP do Tor...")
        authn(args.tor_control_port)
    elif args.network == 'i2p':
        i2p_session = conn_i2p(args.i2p_http_port)
        print("[+] conectando via I2P...")
        print(fetch_url(i2p_session, args.i2p_url))

if __name__ == "__main__":
    main()

