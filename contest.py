import pyperclip
import requests
import sys

if len(sys.argv) >= 3:
    year = int(sys.argv[2])
    contest = sys.argv[1]
else:
    year = 2024
    contest = "CCC"

url = 'https://www.cemc.uwaterloo.ca/contests/past_contests/{}/{}{}Results.pdf'.format(year, year, contest)

r = requests.get(url)

if r.status_code == 404:
    print('{} {} results are not out'.format(contest, year))
elif r.status_code == 200:
    print('\033[31mHOLY FUCKING SHIT I THINK {} {} RESULTS ARE OUT!!!\033[0m'.format(contest, year))
    pyperclip.copy(url)
    print('URL copied to clipboard')
else:
    print('Code {} (weird, shouldn\'t happen)'.format(r.status_code))
