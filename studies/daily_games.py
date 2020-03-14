from datetime import date
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

from utils.meta_info import get_meta_df


def count_games() -> Tuple[dict, dict, dict]:
    df = get_meta_df(usecols=['UTCDate', 'UTCTime'])

    day_of_week_counters = {i: {} for i in range(1, 8)}
    hourly_counters = {i: {str(h).rjust(2, '0'): 0 for h in range(0, 24)} for i in range(1, 8)}
    daily_counters = {}

    c = 0
    for row in df.itertuples(index=False):

        y, m, d = row[0].split('.')
        day_of_week = date(int(y), int(m), int(d)).isoweekday()

        if row[0] not in day_of_week_counters[day_of_week]:
            day_of_week_counters[day_of_week][row[0]] = 0
        day_of_week_counters[day_of_week][row[0]] += 1

        h = row[1].split(':')[0]
        hourly_counters[day_of_week][h] += 1

        if row[0] not in daily_counters:
            daily_counters[row[0]] = 0
        daily_counters[row[0]] += 1

        c += 1
        if not c % 100000:
            print(c)

    for h, data in hourly_counters.items():
        hourly_counters[h] = {k: v / len(day_of_week_counters[h]) for k, v in data.items()}

    for day, data in day_of_week_counters.items():
        day_of_week_counters[day] = sum(data.values()) / len(data)

    return daily_counters, day_of_week_counters, hourly_counters


def plot_day_of_week_games(day_of_week_counters: dict):
    fig, ax = plt.subplots()

    weekdays = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    y_pos = np.arange(len(weekdays))
    num_games = list(day_of_week_counters.values())

    ax.barh(y_pos, num_games, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(weekdays)
    ax.invert_yaxis()
    ax.set_xlabel('average games played')

    plt.savefig('../images/day_of_week_games.png')


def plot_daily_games(daily_counters: dict):
    fig, ax = plt.subplots()

    x = list(daily_counters.keys())
    ax.plot(x, list(daily_counters.values()))
    for i in range(1, len(x)-1):
        x[i] = ''
    ax.set_xticklabels(x)

    plt.grid(color='0.95')
    plt.ylim(bottom=0, top=1.7*1000000)
    plt.title('daily games')
    plt.savefig('../images/daily_games.png')


def plot_games_vs_utc_hours(hourly_counters: dict):
    fig, ax = plt.subplots()

    weekdays = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    for dow, data in hourly_counters.items():
        ax.plot(list(data.keys()), list(data.values()), label=weekdays[dow-1])

    plt.grid(color='0.95')
    plt.legend()
    plt.title('average games vs UTC hours')
    plt.savefig('../images/num_games_vs_utc_hours.png')


if __name__ == '__main__':
    daily_counters, day_of_week_counters, hourly_counters = count_games()

    # plot daily games
    plot_daily_games(daily_counters)

    # plot day of week games
    plot_day_of_week_games(day_of_week_counters)

    # plot games vs utc hours
    plot_games_vs_utc_hours(hourly_counters)
