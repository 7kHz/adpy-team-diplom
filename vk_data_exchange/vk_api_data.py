import configparser
from time import sleep
import vk
# from vk_data_exchange.vk_config import vk_user_token, vk_version, vk_host


config_vk = configparser.ConfigParser()
config_vk.read("settings.ini")
vk_user_token = config_vk["settings"]["vk_user_token"]
vk_version = config_vk["settings"]["vk_version"]
vk_host = config_vk["settings"]["vk_host"]


class VKAPI:

    def __init__(self):
        self.vk_api_session = vk.API(access_token=vk_user_token)
        self.vk_version = vk_version
        self.vk_host = vk_host

    def search_candidates(self, age: int, sex: int, city: str):
        """
        :param city: city of the candidate
        :param sex: sex of the candidate
        :param age: age of the candidate
        """
        counter = 0

        while True:
            response = self.vk_api_session.users.search(
                v=self.vk_version,
                offset=counter,
                count=1,
                sex=sex,
                age_from=age,
                age_to=age,
                city_id=self.get_city_id(city))

            if len(response['items']) == 0:
                break
            else:
                candidate = response['items'][0]
                counter += 1
                sleep(0.8)
                if not candidate['is_closed'] \
                        or candidate['can_access_closed']:
                    yield {
                        'id': candidate['id'],
                        'first_name': candidate['first_name'],
                        'last_name': candidate['last_name'],
                        'link': f'https://vk.com/id{candidate["id"]}',
                        'photos_ids': self.get_photos_ids(candidate['id'])
                        }

    def get_photos_ids(self, user_id) -> list:

        result = []
        response = self.vk_api_session.photos.get(
            v=self.vk_version,
            offset=0,
            count=1000,
            album_id='profile',
            extended=1,
            owner_id=user_id,
        )

        photos_to_sort = map(self.photo_data_to_dict, response["items"])
        min_likes = {}
        result_dict = {}
        for item in photos_to_sort:
            if len(result_dict) > 2:
                if min_likes['likes'] < item['likes']:
                    del result_dict[min_likes['id']]
                    result_dict[item['id']] = item['likes']
                    min_likes = item
            else:
                result_dict[item['id']] = item['likes']
                if len(min_likes):
                    if min_likes['likes'] > item['likes']:
                        min_likes = item
                else:
                    min_likes = item

        return sorted(result_dict.keys(), reverse=True)

    def photo_data_to_dict(self, item):
        return {'id': item['id'],
                'likes': item['likes']['count']}

    def get_city_id(self, city):

        city_id = 0
        cities = self.vk_api_session.database.getCities(
            v=self.vk_version,
            offset=0,
            count=1000,
            q=city,
            need_all=1
        )
        if cities['count'] > 0:
            city_id = cities['items'][0]['id']
        return city_id
