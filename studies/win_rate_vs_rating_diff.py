import matplotlib.pyplot as plt

from utils.meta_info import get_meta_df


bands = ((1000, 2000), (2000, 3000))


def get_win_rates() -> dict:
    """
    Calculates win rate vs rating diff in different rating bands, and separately for blacks/whites.
    Games with time control shorter than 3 minutes are not included.
    """
    min_time_control = 3 * 60

    df = get_meta_df(usecols=['WhiteElo', 'BlackElo', 'TimeControl', 'Result'])

    data = {i: {'black': {}, 'white': {}} for i in range(len(bands))}

    for row in df.itertuples(index=False):
        if row.Result == '*':
            # the game is not finished yet
            continue

        time_control = row.TimeControl

        if time_control == '-':
            # this is correspondence game, assume it's long enough to pass our threshold
            time_control = '3000+0'

        if int(time_control.split('+')[0]) < min_time_control:
            continue

        diff = abs(row.BlackElo - row.WhiteElo)
        if diff > 400:
            continue

        if row.WhiteElo >= row.BlackElo:
            for ix, band in enumerate(bands):
                if band[0] <= row.BlackElo <= band[1]:
                    if diff not in data[ix]['black']:
                        data[ix]['black'][diff] = {'1-0': 0, '1/2-1/2': 0, '0-1': 0}
                    data[ix]['black'][diff][row.Result] += 1

        if row.WhiteElo <= row.BlackElo:
            for ix, band in enumerate(bands):
                if band[0] <= row.WhiteElo <= band[1]:
                    if diff not in data[ix]['white']:
                        data[ix]['white'][diff] = {'1-0': 0, '1/2-1/2': 0, '0-1': 0}
                    data[ix]['white'][diff][row.Result] += 1

    return data


def plot_bands(data: dict):
    fig, axes = plt.subplots(nrows=len(bands), figsize=(8, 10))

    for band_ix, d in data.items():
        white_data = d['white']
        black_data = d['black']

        white_data = [(diff, counters['1-0']/(counters['1-0'] + counters['1/2-1/2'] + counters['0-1'])*100) for diff, counters in white_data.items()]
        black_data = [(diff, counters['0-1']/(counters['1-0'] + counters['1/2-1/2'] + counters['0-1'])*100) for diff, counters in black_data.items()]

        white_data.sort(key=lambda el: el[0])
        black_data.sort(key=lambda el: el[0])

        axes[band_ix].plot([d[0] for d in white_data], [d[1] for d in white_data], label='as white')
        axes[band_ix].plot([d[0] for d in black_data], [d[1] for d in black_data], label='as black')
        axes[band_ix].set_ylim([0, 50])
        axes[band_ix].set_xlim([0, 400])
        axes[band_ix].grid(True)

        axes[band_ix].legend()
        axes[band_ix].set_xlabel('rating diff')
        axes[band_ix].set_ylabel('win rate')
        axes[band_ix].set_title('user rating {0} - {1}'.format(*bands[band_ix]))
    plt.savefig('../images/win_rates.png')


if __name__ == '__main__':
    data = get_win_rates()

    # plot win rates
    plot_bands(data)
