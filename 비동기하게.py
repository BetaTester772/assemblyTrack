import asyncio
import aiohttp
import bs4 as bs
import pandas as pd
import json
from io import StringIO
import requests


def get_id():
    HAS_html = requests.get('https://www.acmicpc.net/school/ranklist/804', headers={'User-Agent': 'Mozilla/5.0'})
    HAS = bs.BeautifulSoup(HAS_html.text, 'html.parser')

    # 테이블에서 모든 행을 찾아냅니다.
    table = HAS.find('table')

    # DataFrame을 직접 생성
    df = pd.read_html(StringIO(str(table)), header=0)[0]  # StringIO로 감싸 문자열을 전달합니다.

    id_list = df['아이디'].tolist()
    return id_list


async def get_contest_rank(id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.acmicpc.net/contest/board/{id}/info.json',
                               headers={'User-Agent': 'Mozilla/5.0'}) as response:
            contest_json = await response.json()

    teams_df = pd.DataFrame({'rank': range(1, len(contest_json['teams']) + 1),
                             'name': [team['team'] for team in contest_json['teams']]})

    return teams_df


async def get_contest_title(id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.acmicpc.net/contest/board/{id}/info.json',
                               headers={'User-Agent': 'Mozilla/5.0'}) as response:
            contest_json = await response.json()

    return contest_json['title']


async def get_current_contest_id():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.acmicpc.net/contest/official/list/1',
                               headers={'User-Agent': 'Mozilla/5.0'}) as response:
            contest_html = await response.text()

    a = contest_html.find('href="/contest/view/')
    return int(contest_html[a + 20:a + 24])


async def main():
    current_contest_id = await get_current_contest_id()

    contests = []
    id_list = get_id()

    for i in range(738, current_contest_id):
        if await check_contest_exists(i):
            contest_teams_df = await get_contest_rank(i)

            id_df = pd.DataFrame({'아이디': id_list})

            common_ids = pd.merge(id_df, contest_teams_df, left_on='아이디', right_on='name', how='inner')
            if not common_ids.empty:
                print('=' * 40)
                print(await get_contest_title(i))
                print(common_ids)
                contests.append(common_ids)


async def check_contest_exists(id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.acmicpc.net/contest/board/{id}/info.json',
                               headers={'User-Agent': 'Mozilla/5.0'}) as response:
            return response.status == 200


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
