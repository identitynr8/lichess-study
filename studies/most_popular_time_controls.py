from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np

from utils.meta_info import get_meta_df


def count_time_controls() -> Tuple[List, List]:
    """
    Counts top-10 time controls for players under 2000 rating, and for players with 2000+ rating.
    """
    df = get_meta_df(usecols=['WhiteElo', 'BlackElo', 'TimeControl'])

    u2000_controls = {}
    u2000_counter = 0
    above2000_controls = {}
    above2000_counter = 0

    for row in df.itertuples(index=False):
        time_control = row[2]

        if row[0] < 2000 or row[1] < 2000:
            if time_control not in u2000_controls:
                u2000_controls[time_control] = 0
            u2000_controls[time_control] += 1
            u2000_counter += 1

        if row[0] >= 2000 or row[1] >= 2000:
            if time_control not in above2000_controls:
                above2000_controls[time_control] = 0
            above2000_controls[time_control] += 1
            above2000_counter += 1

    u2000_list = list(u2000_controls.items())
    u2000_list.sort(key=lambda el: el[1], reverse=True)

    a2000_list = list(above2000_controls.items())
    a2000_list.sort(key=lambda el: el[1], reverse=True)

    return [(v[0], v[1]/u2000_counter*100) for v in u2000_list[0:10]],\
           [(v[0], v[1]/above2000_counter*100) for v in a2000_list[0:10]]


def plot_time_controls(u2000: list, a2000: list):
    fig, ax = plt.subplots(figsize=(12, 8))

    x = np.arange(len(u2000))
    width = 0.45

    rects1 = ax.bar(x - width / 2, [v[1] for v in u2000], width, label='Under 2000')
    rects2 = ax.bar(x + width / 2, [v[1] for v in a2000], width, label='2000+')

    for bars, labels in ((rects1, [v[0] for v in u2000]), (rects2, [v[0] for v in a2000])):
        for bar, label in zip(bars, labels):
            height = bar.get_height()
            ax.annotate(label,
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    ax.legend()
    ax.set_xticklabels([])
    ax.set_ylabel('% of all games played in a group')
    plt.title('Most popular time controls')

    fig.tight_layout()
    plt.savefig('../images/most_popular_time_controls.png')


if __name__ == '__main__':
    u2000, a2000 = count_time_controls()

    # plot most popular time controls
    plot_time_controls(u2000, a2000)
