from datetime import date
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

from utils.meta_info import get_meta_df


def count_games() -> Tuple[dict, dict]:
    df = get_meta_df(usecols=['UTCDate', 'UTCTime'])

    day_of_week_counters = {i: 0 for i in range(1, 8)}
    hourly_counters = {i: {str(h).rjust(2, '0'): 0 for h in range(0, 24)} for i in range(1, 8)}

    c = 0

    for row in df.itertuples(index=False):

        y, m, d = row[0].split('.')
        day_of_week = date(int(y), int(m), int(d)).isoweekday()

        day_of_week_counters[day_of_week] += 1

        h = row[1].split(':')[0]
        hourly_counters[day_of_week][h] += 1

        c += 1
        if not c % 1000:
            print(c)
    return day_of_week_counters, hourly_counters


def plot_daily_games(day_of_week_counters: dict):
    fig, ax = plt.subplots()

    weekdays = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    y_pos = np.arange(len(weekdays))
    num_games = list(day_of_week_counters.values())
    num_games_pct = [n / sum(num_games) * 100 for n in num_games]

    ax.barh(y_pos, num_games_pct, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(weekdays)
    ax.invert_yaxis()
    ax.set_xlabel('% of all games played')

    plt.savefig('../images/day_of_week_games.png')


def plot_games_vs_utc_hours(hourly_counters: dict):
    fig, ax = plt.subplots()

    weekdays = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    for dow, data in hourly_counters.items():
        ax.plot(list(data.keys()), list(data.values()), label=weekdays[dow-1])

    ax.set_yticklabels([])
    plt.grid(color='0.95')
    plt.legend()
    plt.title('num. games vs UTC hours')
    plt.savefig('../images/num_games_vs_utc_hours.png')


if __name__ == '__main__':
    day_of_week_counters, hourly_counters = count_games()
    
    # plot daily games
    plot_daily_games(day_of_week_counters)

    # plot games vs utc hours
    plot_games_vs_utc_hours(hourly_counters)
