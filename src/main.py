import json
import pathlib
import sys
from io import StringIO
from random import randrange


class Printer:
    def __init__(self, file):
        self.file = file

    def print(self, text):
        print(text, file=self.file)


class BufferPrinter(Printer):
    def __init__(self):
        super().__init__(file=StringIO())

    def pop_printed_lines(self):
        res = self.file.getvalue().splitlines()
        self.__init__()
        return res


class Game:
    _ROCK = "Rock"
    _SPORTS = "Sports"
    _SCIENCE = "Science"
    _POP = "Pop"

    def __init__(self, printer=None):
        self._players_names = []
        self._places = [0] * 6
        self._purses = [0] * 6
        self._in_penalty_box = [0] * 6

        self._i_current_player = 0
        self._is_getting_out_of_penalty_box = False

        pop_questions = []
        science_questions = []
        sports_questions = []
        rock_questions = []

        for i in range(50):
            pop_questions.append(self._create_question(i, self._POP))
            science_questions.append(self._create_question(i, self._SCIENCE))
            sports_questions.append(self._create_question(i, self._SPORTS))
            rock_questions.append(self._create_question(i, self._ROCK))

        self._questions_by_category = {
            self._POP: pop_questions,
            self._ROCK: rock_questions,
            self._SCIENCE: science_questions,
            self._SPORTS: sports_questions,
        }

        if printer is None:
            self._printer = Printer(file=sys.stdout)
        else:
            self._printer = printer

    @classmethod
    def _create_question(cls, index, category):
        return f"{category} Question {index}"

    def is_playable(self):
        return self._nb_players >= 2

    def add(self, player_name):
        self._players_names.append(player_name)
        self._places[self._nb_players] = 0
        self._purses[self._nb_players] = 0
        self._in_penalty_box[self._nb_players] = False

        self._printer.print(f"{player_name} was added")
        self._printer.print(f"They are player number {len(self._players_names)}")

        return True

    @property
    def _nb_players(self):
        return len(self._players_names)

    def roll(self, roll):
        self._printer.print(f"{self._current_player_name} is the current player")
        self._printer.print(f"They have rolled a {roll}")

        if self._in_penalty_box[self._i_current_player]:
            if roll % 2 != 0:
                self._is_getting_out_of_penalty_box = True

                self._printer.print(
                    f"{self._current_player_name} is getting out of the penalty box"
                )
                self._move_current_player(roll)

                self._printer.print(
                    f"{self._current_player_name}'s new location is {str(self._current_player_place)}"
                )
                self._printer.print(f"The category is {self._current_category}")
                self._ask_question()
            else:
                self._printer.print(
                    f"{self._current_player_name} is not getting out of the penalty box"
                )
                self._is_getting_out_of_penalty_box = False
        else:
            self._move_current_player(roll)

            self._printer.print(
                f"{self._current_player_name}'s new location is {self._current_player_place}"
            )
            self._printer.print(f"The category is {self._current_category}")
            self._ask_question()

    def _move_current_player(self, roll):
        self._current_player_place = (self._current_player_place + roll) % 12

    @property
    def _current_player_name(self):
        return self._players_names[self._i_current_player]

    def _ask_question(self):
        current_category_questions = self._questions_by_category[self._current_category]
        self._printer.print(current_category_questions.pop(0))

    @property
    def _current_category(self):
        current_player_place_mod_4 = self._current_player_place % 4
        return {
            0: self._POP,
            1: self._SCIENCE,
            2: self._SPORTS,
            3: self._ROCK,
        }[current_player_place_mod_4]

    @property
    def _current_player_place(self):
        return self._places[self._i_current_player]

    @_current_player_place.setter
    def _current_player_place(self, place):
        self._places[self._i_current_player] = place

    def was_correctly_answered(self):
        if self._in_penalty_box[self._i_current_player]:
            if self._is_getting_out_of_penalty_box:
                self._printer.print("Answer was correct!!!!")
                self._current_player_purse += 1
                self._printer.print(
                    f"{self._current_player_name} now has {self._purses[self._i_current_player]} Gold Coins."
                )
                there_is_no_winner = not self._did_player_win()
                self._update_current_player()
                return there_is_no_winner
            else:
                self._update_current_player()
                return True

        else:
            self._printer.print("Answer was correct!!!!")
            self._current_player_purse += 1
            self._printer.print(
                f"{self._current_player_name} now has {self._current_player_purse} Gold Coins."
            )

            there_is_no_winner = not self._did_player_win()
            self._update_current_player()

            return there_is_no_winner

    def _update_current_player(self):
        self._i_current_player = (self._i_current_player + 1) % self._nb_players

    @property
    def _current_player_purse(self):
        return self._purses[self._i_current_player]

    @_current_player_purse.setter
    def _current_player_purse(self, purse):
        self._purses[self._i_current_player] = purse

    def wrong_answer(self):
        self._printer.print("Question was incorrectly answered")
        self._printer.print(f"{self._current_player_name} was sent to the penalty box")
        self._in_penalty_box[self._i_current_player] = True
        self._update_current_player()
        return True

    def _did_player_win(self):
        return self._current_player_purse == 6


def capture_interaction(file_name, players):
    printer = BufferPrinter()
    game = Game(printer)
    scenario = []
    for player in players:
        add_res = game.add(player)
        printed_lines = printer.pop_printed_lines()
        scenario.append(
            {
                "method": "add",
                "args": [player],
                "return": add_res,
                "printed_lines": printed_lines,
            }
        )
    while True:
        roll_arg = randrange(5) + 1
        game.roll(roll_arg)
        printed_lines = printer.pop_printed_lines()
        scenario.append(
            {
                "method": "roll",
                "args": [roll_arg],
                "return": None,
                "printed_lines": printed_lines,
            }
        )

        if randrange(9) == 7:
            not_a_winner = game.wrong_answer()
            printed_lines = printer.pop_printed_lines()
            scenario.append(
                {
                    "method": "wrong_answer",
                    "args": [],
                    "return": not_a_winner,
                    "printed_lines": printed_lines,
                }
            )
        else:
            not_a_winner = game.was_correctly_answered()
            printed_lines = printer.pop_printed_lines()
            scenario.append(
                {
                    "method": "was_correctly_answered",
                    "args": [],
                    "return": not_a_winner,
                    "printed_lines": printed_lines,
                }
            )

        if not not_a_winner:
            break
    path_to_data = pathlib.Path().absolute() / "data"
    with open(path_to_data / file_name, "w") as f:
        json.dump(scenario, f)


if __name__ == "__main__":
    capture_interaction("first_scenario.json", players=["Chet", "Pat", "Sue"])
    capture_interaction("second_scenario.json", players=["Chet", "Pat", "Sue", "Jim"])
    capture_interaction("third_scenario.json", players=["Chet", "Pat"])
