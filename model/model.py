import datetime

import pandas as pd
import requests

from utils.utils import get_symbol


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

    def get_data(self):
        return self.data

    def set_choice(self, user_first_name, option):
        self.data.loc[user_first_name, option] = 1
        self.data.loc[user_first_name, 'Out'] = 0

    def get_results(self):
        times = self.data.T.apply(lambda x: ', '.join(x.loc[x == 1].index.tolist()), axis=1)
        print(times)

        return times.to_string()

    def delete_user(self, user_first_name, times_only=False):
        if times_only:
            self.data.loc[user_first_name, [col for col in self.data.columns if col != 'Out']] = 0
        else:
            self.data.loc[user_first_name, :] = 0
