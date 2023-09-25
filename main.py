import requests
import bs4 as bs
import pandas as pd
import json
from io import StringIO  # StringIO를 추가합니다.


def get_id():
    HAS_html = requests.get('https://www.acmicpc.net/school/ranklist/804', headers={'User-Agent': 'Mozilla/5.0'})
    HAS = bs.BeautifulSoup(HAS_html.text, 'html.parser')

    # 테이블에서 모든 행을 찾아냅니다.
    table = HAS.find('table')

    # DataFrame을 직접 생성
    df = pd.read_html(StringIO(str(table)), header=0)[0]  # StringIO로 감싸 문자열을 전달합니다.

    id_list = df['아이디'].tolist()
    return id_list


def get_contest_rank(id: int):
    contest_json = requests.get('https://www.acmicpc.net/contest/board/{}/info.json'.format(id),
                                headers={'User-Agent': 'Mozilla/5.0'})
    contest_json = json.loads(contest_json.text)

    # DataFrame을 직접 생성
    teams_df = pd.DataFrame({'rank': range(1, len(contest_json['teams']) + 1),
                             'name': [team['team'] for team in contest_json['teams']]})

    # print(teams_df)

    return teams_df


def get_contest_title(id: int):
    contest_json = requests.get('https://www.acmicpc.net/contest/board/{}/info.json'.format(id),
                                headers={'User-Agent': 'Mozilla/5.0'})
    contest_json = json.loads(contest_json.text)
    return contest_json['title']


def get_current_contest_id():
    contest_html = requests.get('https://www.acmicpc.net/contest/official/list/1',
                                headers={'User-Agent': 'Mozilla/5.0'})
    contest = bs.BeautifulSoup(contest_html.text, 'html.parser')
    a = contest_html.text.find('href="/contest/view/')
    return int(contest_html.text[a + 20:a + 24])


def main():
    current_contest_id = get_current_contest_id()

    contests = []
    id_list = get_id()

    for i in range(738, current_contest_id):
        # print(i)
        if requests.get('https://www.acmicpc.net/contest/board/{}/info.json'.format(i),
                        headers={'User-Agent': 'Mozilla/5.0'}).status_code != 200:
            continue

        contest_teams_df = get_contest_rank(i)

        # id_list를 DataFrame으로 변환
        id_df = pd.DataFrame({'아이디': id_list})

        # 공통된 아이디를 찾을 때 'name' 열로 참조
        common_ids = pd.merge(id_df, contest_teams_df, left_on='아이디', right_on='name', how='inner')
        if common_ids.empty:
            continue
        print('=' * 40)
        print(get_contest_title(i))
        print(common_ids)
        contests.append(common_ids)


if __name__ == '__main__':
    main()
