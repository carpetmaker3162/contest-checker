from datetime import datetime
import pyperclip
import requests
import sys
import time

def check(url):
    r = requests.get(url)

    if r.status_code == 404:
        return 1
    elif r.status_code == 200:
        return 0
    else:
        return -1

def interact(contest, year):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    url = 'https://www.cemc.uwaterloo.ca/contests/past_contests/{}/{}{}Results.pdf'.format(year, year, contest)

    if check(url) == 1:
        print('{}: {} {} results are not out'.format(now, contest, year))
        return 1
    else:
        print('{}: \033[31mHOLY FUCKING SHIT I THINK {} {} RESULTS ARE OUT!!!\033[0m'.format(now, contest, year))
        pyperclip.copy(url)
        print('URL copied to clipboard')
        return 0

def loop(contests, delay):
    while True:
        results = []

        for contest, year in contests:
            result = interact(contest, year)
            results.append(result)

        if sum(results) != len(contests):
            break

        time.sleep(delay)
        print()

    print('[Loop ended]')

    while True:
        print(chr(7), end='')
        sys.stdout.flush()
        time.sleep(0.5)

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        year = int(sys.argv[2])
        contest = sys.argv[1]
    else:
        year = 2024
        contest = "CCC"

    interact(contest, year)
