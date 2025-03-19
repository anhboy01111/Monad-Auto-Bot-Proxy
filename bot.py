import os
import sys
import asyncio
from colorama import init, Fore, Style
from dotenv import load_dotenv
import pyfiglet
from halo import Halo

# Khởi tạo colorama
init(autoreset=True)
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")

def display_header():
    ascii_banner = pyfiglet.figlet_format("AUTO TX MONAD")
    border = "=" * 80
    print(Style.BRIGHT + Fore.CYAN + border)
    print(Style.BRIGHT + Fore.YELLOW + ascii_banner)
    sub_header = "By SHARE IT HUB".center(80)
    print(Style.BRIGHT + Fore.MAGENTA + sub_header)
    print(Style.BRIGHT + Fore.CYAN + border + "\n")

def check_env_vars():
    required_vars = ["PRIVATE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(Fore.RED + f"❌ Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

check_env_vars()

module_folder = "./modules"
if not os.path.isdir(module_folder):
    print(Fore.RED + f"Folder '{module_folder}' tidak ditemukan!")
    sys.exit(1)

module_files = [f for f in os.listdir(module_folder) if f.endswith(".py")]
scripts = [{"name": os.path.splitext(f)[0].title(), "path": os.path.join(module_folder, f)} for f in module_files]

def get_private_keys_and_proxies():
    num_keys = int(input("Bạn muốn chạy mấy private key: "))
    private_keys = []
    proxies = []
    for i in range(num_keys):
        key = input(f"Nhập private key {i+1}: ")
        private_keys.append(key)
    use_proxy = input("Bạn muốn chạy proxy không? (Bấm 1 là có, 0 là không): ")
    if use_proxy == "1":
        for i in range(num_keys):
            proxy = input(f"Nhập proxy cho private key {i+1} (hoặc nhập 0 nếu không dùng proxy): ")
            proxies.append(proxy if proxy != "0" else None)
    else:
        proxies = [None] * num_keys
    return private_keys, proxies

async def run_script(script, private_key, proxy):
    print(Fore.YELLOW + f"\n📜 Menjalankan: {script['name']} dengan Private Key {private_key[:6]}...\n")
    os.environ['PRIVATE_KEY'] = private_key
    if proxy:
        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy
        print(Fore.CYAN + f"🌐 Sử dụng Proxy: {proxy}")
    else:
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        print(Fore.CYAN + "🚀 Không sử dụng proxy")
    
    spinner = Halo(text='Sedang mengeksekusi...', spinner='dots', color='cyan')
    spinner.start()
    proc = await asyncio.create_subprocess_exec(
        sys.executable, script["path"],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    spinner.stop()

    if stdout:
        print(Fore.WHITE + stdout.decode())
    if stderr:
        print(Fore.RED + "Error: " + stderr.decode())
    
    if proc.returncode == 0:
        print(Fore.GREEN + f"✅ Berhasil: {script['name']}\n")
    else:
        print(Fore.RED + f"❌ Gagal: {script['name']} (Kode keluar: {proc.returncode})")

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    display_header()
    private_keys, proxies = get_private_keys_and_proxies()
    
    print(Fore.BLUE + "\n📜 Pilih modul untuk chạy:")
    for idx, script in enumerate(scripts, start=1):
        print(f"{Fore.YELLOW}{idx}. {Fore.WHITE}{script['name']}")
    selected_indices = input(Fore.CYAN + "\nNhập số module muốn chạy (VD: 1,3,5 hoặc enter để chạy tất cả): ").strip()
    if selected_indices:
        selected_scripts = [scripts[int(i) - 1] for i in selected_indices.split(",") if i.isdigit() and 1 <= int(i) <= len(scripts)]
    else:
        selected_scripts = scripts
    
    loop_count_str = input(Fore.CYAN + "\nBạn muốn chạy bao nhiêu vòng lặp? (Nhập số, mặc định là 1): ").strip()
    try:
        loop_count = int(loop_count_str) if loop_count_str else 1
        if loop_count <= 0:
            print(Fore.RED + "Số vòng lặp phải lớn hơn 0. Mặc định là 1.")
            loop_count = 1
    except ValueError:
        loop_count = 1
    
    for _ in range(loop_count):
        for private_key, proxy in zip(private_keys, proxies):
            for script in selected_scripts:
                await run_script(script, private_key, proxy)
    
    print(Fore.GREEN + "\n✅ Tất cả module đã hoàn thành!\n")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\n⛔ Chương trình đã bị dừng bởi người dùng.")