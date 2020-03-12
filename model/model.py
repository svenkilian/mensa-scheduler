import datetime
import math

import pandas as pd
import numpy as np
import requests

from utils.utils import get_symbol, pretty_print_table, prettify_table


class Mensa:
    """
    Wrapper class for the OpenMensa API
    See https://doc.openmensa.org/api/v2/ for more infos.
    """

    base_url = 'https://openmensa.org/api/v2/'  # Specify base URL for REST API

    def __init__(self, mensa_id=31):
        """
        Constructor for Mensa instance

        :param mensa_id: Mensa ID (defaults to 31 for KIT Mensa)
        """
        self.id = mensa_id
        self.mensa_name = requests.get(f'{self.base_url}canteens/{self.id}').json().get('name')

    def get_info(self) -> dict:
        """
        Get full mensa info as dict

        :return: Mensa info as json
        """
        return requests.get(f'{self.base_url}canteens/{self.id}').json()

    def print_formatted_info(self) -> None:
        for key, value in self.get_info().items():
            print(f'{key}: {value}')

    def get_days(self) -> list:
        """
        Get info about closed days

        :return:
        """
        return requests.get(f'{self.base_url}canteens/{self.id}/days', params={'start': datetime.date.today()}).json()

    def get_daily_menu(self, offset=0) -> dict:
        """
        Get today's menu

        :return: Today's menu as json
        """

        return requests.get(
            f'{self.base_url}canteens/{self.id}/days/{datetime.date.today() + datetime.timedelta(days=offset)}/meals').json()

    def meal_data(self, offset=0, mains_only=True) -> pd.DataFrame:
        """
        Return DataFrame containing today's menu

        :return:
        """
        df = pd.DataFrame.from_records(self.get_daily_menu(offset=offset), index='category')
        # df.set_index(['category', 'name'], inplace=True)

        if mains_only:
            df = df.loc[df['prices'].apply(lambda x: x.get('students')) > 1.0]

        df['price'] = df['prices'].apply(
            lambda x: '{:4.2f}'.format(float(x.get('students'))) + ' €' if x.get(
                'students') is not None else '-')  # Extract student prices

        df['symbol'] = df.apply(lambda x: get_symbol(x['name'], x['notes']), axis=1)
        df.set_index('name', append=True, inplace=True)

        df.drop(columns=['id', 'prices'], inplace=True)

        print(df)

        return df

    def meal_data_lines(self, offset=0):
        return self.meal_data(offset=offset).groupby(level=0, sort=False)


class PollData:
    def __init__(self, option_list):
        self.data = pd.DataFrame(columns=option_list, dtype='int8')
        self.data.index.name = 'user_id'
        self.active = True

    def get_data(self):
        return self.data

    def set_choice(self, user_first_name, option):
        self.data.loc[user_first_name, option] = 1
        self.data.loc[user_first_name, 'Out'] = 0

    def calculate_stats(self):
        times = self.data.T.apply(lambda x: ', '.join(x.loc[x == 1].index.tolist()), axis=1). \
            rename('attendees',
                   inplace=True).to_frame()
        times['total'] = self.data.T.apply(lambda x: int(np.sum(x)) if not np.isnan(np.sum(x)) else 0, axis=1)

        max_votes = times['total'].max()
        times['is_choice'] = times['total'].apply(lambda x: x == max_votes if max_votes != 0 else False)
        times.loc['Out', 'is_choice'] = None
        unique_max = np.sum(times['is_choice']) == 1
        shared_max = np.sum(times['is_choice']) > 1
        print(times)
        print(f'Unique max: {unique_max}')
        print(f'Shared max: {shared_max}')
        times.reset_index(inplace=True)
        times.columns = ['time', 'attendees', 'total', 'is_choice']

        return times, unique_max, shared_max

    def get_results(self):
        times, unique_max, shared_max = self.calculate_stats()
        times['time'] = times.apply(lambda x: str(f'{x["time"]} ({x["total"]}):'), axis=1)
        times['attendees'] = times.apply(
            lambda x: str(f'{x["attendees"]} ✔') if (x['is_choice'] == 1 and unique_max) else
            f'{x["attendees"]} ❎' if (x['is_choice'] == 1 and shared_max)
            else x['attendees'], axis=1)

        times.set_index('time', inplace=True)
        times.drop(columns=['total', 'is_choice'], inplace=True)
        print(prettify_table(times, show_index=True, tablefmt='simple'))
        return prettify_table(times, show_index=True, tablefmt='simple')

        # 'plain', 'simple', 'grid', 'pipe', 'orgtbl', 'rst', 'mediawiki', 'latex', 'latex_raw' and 'latex_booktabs

    def get_final_choice(self):
        result = None
        text = None
        times, unique_max, shared_max = self.calculate_stats()
        if unique_max:
            result = times.loc[times['is_choice'] == 1].iloc[0]
            print(result['time'])
            text = f'Chosen time: {result["time"]}\n' \
                   f'Attendees: {result["attendees"]}'
        elif shared_max:
            result = prettify_table(times.loc[times['is_choice'] == 1].set_index('time')[['attendees']],
                                    show_index=True, tablefmt='simple')
            text = f'Options:\n\n' \
                   f'{result}'

        return text

    def delete_user(self, user_first_name, times_only=False):
        if times_only:
            self.data.loc[user_first_name, [col for col in self.data.columns if col != 'Out']] = 0
        else:
            self.data.loc[user_first_name, :] = 0

    def checkall_user(self, user_first_name):
        self.data.loc[user_first_name, [col for col in self.data.columns if col != 'Out']] = 1
        self.data.loc[user_first_name, 'Out'] = 0
