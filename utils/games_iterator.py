from typing import Iterator, Optional

import chess.pgn
from chess.pgn import Game


def games_iterator(event: Optional[str] = None,
                   min_time_control: Optional[int] = None,
                   min_elo: Optional[int] = None,
                   max_elo: Optional[int] = None) -> Iterator[Game]:
    with open('../games/lichess_db_standard_rated_2020-02.pgn') as games_file:
        while True:
            game = chess.pgn.read_game(games_file)
            if game is None:
                return

            if event is not None:
                if game.headers['Event'] != event:
                    continue

            if min_elo is not None or max_elo is not None:
                white_elo = int(game.headers['WhiteElo'])
                black_elo = int(game.headers['BlackElo'])

                if min_elo is not None and (white_elo < min_elo or black_elo < min_elo):
                    continue
                if max_elo is not None and (white_elo > max_elo or black_elo > max_elo):
                    continue

            if min_time_control is not None:
                time_control = game.headers['TimeControl']

                if time_control == '-':
                    continue

                if int(time_control.split('+')[0]) < min_time_control:
                    continue

            yield game
