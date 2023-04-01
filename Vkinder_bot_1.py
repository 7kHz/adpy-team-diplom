import os
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv, find_dotenv
import re


load_dotenv(find_dotenv())
token = os.getenv('ACCESS_TOKEN')
user_ids = int(input())

def write_msg(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)})


vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)

write_msg(user_ids, 'Добро пожаловать в Vkinder!\n\nВведите ваши данные в формате:\nВозраст, пол, город')


def new_message():
    data_list = []
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text
                check_len_request = request.split(',')
                if len(check_len_request) == 3:
                    data_list.append(request.title().strip())
                    return data_list
                else:
                    write_msg(event.user_id, 'Введен неверный формат данных! Повторите попытку:')


def formatting_data(data_list_):
    join_data_list = ','.join(data_list_)
    pattern_data_list = r'(\d+)\s*\W*([Муж|Жен]+)\w+\W*(\w+)'
    substitution_data_list = r'\1,\2,\3'
    format_data_list = re.sub(pattern_data_list, substitution_data_list, join_data_list, re.A)
    split_format_data_list = format_data_list.split(',')
    split_format_data_list[0] = int(split_format_data_list[0])
    if split_format_data_list[1] == 'Жен':
        split_format_data_list[1] = 1
    else:
        split_format_data_list[1] = 2
    data_dict = {'age': split_format_data_list[0],
                 'sex': split_format_data_list[1],
                 'city': split_format_data_list[2]}
    return data_dict

print(formatting_data(new_message()))
