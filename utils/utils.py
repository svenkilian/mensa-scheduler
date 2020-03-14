from typing import Union

import pandas as pd
from tabulate import tabulate


def pretty_print_table(df: pd.DataFrame, headers='keys', tablefmt='fancy_grid', show_index=True):
    """
    Print out DataFrame in tabular format.

    :param show_index:
    :type headers: list or string
    :param df: DataFrame to print
    :param headers: Table headers
    :param tablefmt: Table style
    :return: None

    """
    print(tabulate(df, headers, tablefmt=tablefmt, showindex=show_index, floatfmt='.2f'))


def prettify_table(df: pd.DataFrame, headers='keys', tablefmt='fancy_grid', show_index=False):
    # 'plain', 'simple', 'grid', 'pipe', 'orgtbl', 'rst', 'mediawiki', 'latex', 'latex_raw' and 'latex_booktabs
    return tabulate(df, tablefmt=tablefmt, showindex=show_index, floatfmt='.2f', numalign='decimal', stralign='left')


def get_symbol(meal_name: str, note_list: list) -> str:
    symbol_dict = {'vegan': u'🍃', 'vegetarisch': u'🥕', 'fleisch': u'🥩', 'steak': u'🥩', 'wurst': u'🥩',
                   'hnchen': u'🐔', 'schwein': u'🐖', 'rinder': u'🐄'}

    if len(note_list) == 0:
        note_string = ''
    else:
        note_string = note_list[0].lower()

    key = None

    for key in symbol_dict.keys():
        if key in note_string:
            print(f'Key {key} in note_string.')
            symbol = symbol_dict.get(key)
            print(symbol)
            return symbol
    else:
        print(f'{key} not found in first')
        for key in symbol_dict.keys():
            if key in meal_name:
                print(f'Key {key} in meal_name.')
                symbol = symbol_dict.get(key)
                print(symbol)
                return symbol
        else:
            symbol = ''
            print(f'{key} not found in second')
            return symbol


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
