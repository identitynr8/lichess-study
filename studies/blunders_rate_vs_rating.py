from random import randint

import chess.engine
import matplotlib.pyplot as plt

from utils.games_iterator import games_iterator


time_controls = ['60+0', '180+0', '300+3', '600+0']
rating_bands = [(i, i+199) for i in range(1000, 2400, 200)]


def prepare_data():
    engine = chess.engine.SimpleEngine.popen_uci("../stockfish/stockfish_20011801_x64_bmi2")
    engine.configure({"Threads": 4, 'Contempt': 0})
    blunders_counter = {tc: {} for tc in time_controls}
    all_moves_counter = {tc: {} for tc in time_controls}

    current_tc_ix = 0
    current_rating_band_ix = 0

    num_games_studied = 0
    for game in games_iterator():
        if game.headers['TimeControl'] != time_controls[current_tc_ix]:
            continue

        board = game.board()
        moves = list(game.mainline_moves())
        if len(moves) < 5:
            continue

        move_ix = randint(2, len(moves) - 1)

        for curr_move_ix, move in enumerate(moves):
            if curr_move_ix + 1 < move_ix:
                board.push(move)
                continue

            info = engine.analyse(board, chess.engine.Limit(time=2))
            theoretical_score = info['score']
            theoretical_move = info['pv'][0]

            elo = int(game.headers['WhiteElo'])
            if theoretical_score.turn == chess.BLACK:
                elo = int(game.headers['BlackElo'])

            for move_rating_band_ix, band in enumerate(rating_bands):
                if band[0] <= elo <= band[1]:
                    break

            if move_rating_band_ix not in all_moves_counter[game.headers['TimeControl']]:
                all_moves_counter[game.headers['TimeControl']][move_rating_band_ix] = 0
            all_moves_counter[game.headers['TimeControl']][move_rating_band_ix] += 1

            board.push(move)
            if move == theoretical_move:
                # player did the best move, this can't be blunder
                break

            info = engine.analyse(board, chess.engine.Limit(time=2))
            actual_score = chess.engine.PovScore(-info['score'].relative, theoretical_score.turn)

            if theoretical_score.relative.score() is not None and actual_score.relative.score() is not None:

                if theoretical_score.relative.score() - actual_score.relative.score() > 200:
                    if move_rating_band_ix not in blunders_counter[game.headers['TimeControl']]:
                        blunders_counter[game.headers['TimeControl']][move_rating_band_ix] = 0
                    blunders_counter[game.headers['TimeControl']][move_rating_band_ix] += 1

            break

        num_games_studied += 1

        current_tc_ix += 1
        current_tc_ix = current_tc_ix % len(time_controls)

        print(num_games_studied)
        print(blunders_counter)
        print(all_moves_counter)

    engine.quit()

    return blunders_counter, all_moves_counter


def plot_graph(blunders: dict, all_moves: dict):
    fig, ax = plt.subplots()
    for tc, data in blunders.items():
        l = [(k, v / all_moves[tc][k] * 100) for k, v in data.items()]
        l.sort(key=lambda el: el[0])
        if l:
            ax.plot([rating_bands[d[0]][0] for d in l], [d[1] for d in l], label=tc)

    ax.set_xlim([rating_bands[0][0], rating_bands[-1][0]])
    ax.set_ylim([0, 20])
    ax.set_xlabel('rating')
    ax.set_ylabel('blunders rate, %')
    ax.legend()
    ax.grid(color='0.95')
    ax.set_xticklabels(['{0}-{1}'.format(*rb) for rb in rating_bands])

    fig.tight_layout()
    plt.savefig('../images/blunders_vs_time_and_tier.png')


if __name__ == '__main__':
    # blunders, all_moves = prepare_data()
    # data collected from 44241 games

    blunders = {'60+0': {6: 119, 2: 202, 5: 192, 4: 282, 3: 289, 0: 73, 1: 158},
                '180+0': {1: 155, 4: 282, 3: 253, 2: 185, 6: 91, 5: 182, 0: 85},
                '300+3': {2: 270, 3: 228, 0: 237, 1: 280, 4: 116, 6: 2, 5: 35},
                '600+0': {1: 257, 4: 189, 2: 311, 3: 289, 0: 176, 5: 50, 6: 5}}
    all_moves = {'60+0': {2: 1566, 3: 2051, 1: 947, 6: 1115, 5: 1843, 4: 2278, 0: 470},
                 '180+0': {2: 1513, 3: 2219, 4: 2540, 1: 1025, 5: 1908, 6: 903, 0: 471},
                 '300+3': {1: 2322, 2: 2524, 3: 2141, 0: 1588, 4: 1437, 5: 414, 6: 34},
                 '600+0': {4: 1914, 2: 2613, 3: 2760, 1: 1861, 5: 612, 0: 950, 6: 83}}
    plot_graph(blunders, all_moves)

# 44241
# {'60+0': {6: 119, 8: 34, 2: 202, 7: 44, 5: 192, 4: 282, 3: 289, 0: 73, 1: 158}, '180+0': {1: 155, 4: 282, 3: 253, 2: 185, 6: 91, 5: 182, 8: 20, 0: 85, 7: 28}, '300+3': {2: 270, 3: 228, 0: 237, 1: 280, 8: 104, 4: 116, 6: 2, 5: 35, 7: 1}, '600+0': {1: 257, 4: 189, 2: 311, 3: 289, 0: 176, 5: 50, 8: 57, 6: 5, 7: 1}}
# {'60+0': {2: 1566, 3: 2051, 1: 947, 6: 1115, 5: 1843, 4: 2278, 0: 470, 8: 330, 7: 461}, '180+0': {2: 1513, 3: 2219, 4: 2540, 7: 320, 1: 1025, 5: 1908, 8: 161, 6: 903, 0: 471}, '300+3': {1: 2322, 2: 2524, 3: 2141, 0: 1588, 4: 1437, 8: 597, 5: 414, 6: 34, 7: 3}, '600+0': {4: 1914, 2: 2613, 3: 2760, 1: 1861, 5: 612, 8: 259, 0: 950, 6: 83, 7: 8}}
