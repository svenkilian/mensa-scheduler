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
