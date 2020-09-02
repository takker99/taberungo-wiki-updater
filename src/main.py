import requests
import datetime
import os
from pyquery import PyQuery as pq


def getUserNameFromId(userId):
    url = f'https://www.nicovideo.jp/user/{str(userId)}'
    dom = pq(url)
    result = dom('head').find(
        'meta[property="profile:username"]').attr['content']
    return result


def getVideoURL(id: str):
    return f'https://www.nicovideo.jp/watch/{id}'


def getVideoInfo(response_data):
    '''
    APIから返ってきた配列から必要な情報を取り出す
    '''
    return {'userName': getUserNameFromId(response_data['userId']),
            'title': response_data['title'],
            'thumbnailUrl': f'{response_data["thumbnailUrl"]}.L',
            'videoUrl': getVideoURL(response_data['contentId']),
            'postTime': datetime.datetime.
            fromisoformat(response_data['startTime']).strftime('%Y-%m-%d')}


def getVideoList(start: datetime.datetime, end: datetime.datetime):
    '''
    指定した期間内の動画に関する情報を取得し、text fileに書き込むscript

    取得する情報
    - 動画名
    - Thumbnail image URL
    - 動画URL
    - 投稿者名
    - 投稿日
    '''
    # niconico contents search APIに投げるparameter
    options = {
        'q': 'たべるんごのうた',
        'targets': 'tagsExact',
        'fields': 'userId,title,contentId,startTime,thumbnailUrl',
        '_sort': '-startTime',
        '_context': 'taberungo-wiki-updater',
    }
    temp = []
    for j in range(16):
        data_range = {'_limit': 100,
                      'filters[startTime][gte]': start.isoformat(),
                      'filters[startTime][lt]': end.isoformat(),
                      '_offset': j*100}
        print(f'getting data: [{j*100}, {j*100+99}[')
        response = requests.get(
            'https://api.search.nicovideo.jp/api/v2/video/contents/search',
            params={**options, **data_range})
        # 全て取得し終えたら終了する
        if (response.json()['data'] == []):
            break
        print('Adding data to List...')
        temp += [getVideoInfo(item) for item in response.json()['data']]
    print('Finish loading all data')
    # 取得結果の確認
    for item in temp:
        print(f'title = {item["title"]}'
              f'\n\tcreator = {item["userName"]}'
              f'\n\tthumbnail URL = {item["thumbnailUrl"]}'
              f'\n\tvideo URL = {item["videoUrl"]}'
              f'\n\tposted on {item["postTime"]}')

    print('Writing to the text file...')
    # fileに書き込む
    os.makedirs('dist', exist_ok=True)
    with open('dist/taberungo-list.txt', encoding='utf-8', mode='w') as file:
        for item in temp:
            file.writelines([item["title"],
                             f'\n[{item["videoUrl"]} {item["thumbnailUrl"]}#.png]',
                             '\n',
                             f'\n 投稿者: [{item["userName"]}]',
                             f'\n投稿日: [{item["postTime"]}]\n'])
    print('Successfully finished!')


if __name__ == "__main__":
    getVideoList(datetime.datetime.fromisoformat(
        '2020-07-27T00:00:00+09:00'), datetime.datetime.now())
