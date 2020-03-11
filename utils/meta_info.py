import csv
import os
from typing import List

import numpy as np
import pandas as pd

meta_file_path = os.path.dirname(os.path.realpath(__file__)) + '/../games/meta.csv'


def get_meta_df(usecols: List) -> pd.DataFrame:
    dtype = {}
    if 'WhiteElo' in usecols:
        dtype['WhiteElo'] = np.int32
    if 'BlackElo' in usecols:
        dtype['BlackElo'] = np.int32

    df = pd.read_csv(meta_file_path,
                     delimiter='|', dtype=dtype,
                     usecols=usecols)
    return df


if __name__ == '__main__':
    header_elements = ('Event', 'Date', 'White', 'Black', 'Result', 'UTCDate', 'UTCTime', 'WhiteElo', 'BlackElo',
                       'ECO', 'Opening', 'TimeControl', 'Termination')

    with open(meta_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter='|')
        writer.writerow(header_elements)

        with open('../games/lichess_db_standard_rated_2020-02.pgn') as games_file:
            d = {h: '' for h in header_elements}
            headers_found = False
            rows_counter = 0

            for line in games_file:
                if line.startswith('['):
                    txt = line[1:-3]
                    for h in header_elements:
                        if txt.startswith(h+' '):
                            txt = txt.replace(h + ' "', '')
                            d[h] = txt
                            headers_found = True
                            break

                if line == '\n' and headers_found:
                    writer.writerow([d[el] for el in header_elements])
                    d = {h: '' for h in header_elements}
                    headers_found = False
                    rows_counter += 1
                    print(rows_counter)
