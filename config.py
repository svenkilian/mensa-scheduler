import pandas as pd
import os

pd.set_option('precision', 6)
pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 40)
pd.set_option('max_colwidth', 80)
pd.set_option('mode.sim_interactive', True)
pd.set_option('expand_frame_repr', True)
pd.set_option('large_repr', 'truncate')

pd.set_option('colheader_justify', 'left')
pd.set_option('display.width', 800)
pd.set_option('display.html.table_schema', False)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CURRENT_POLL = None
CURRENT_POLL_ID = None
CHAT_ID = None

