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


class Player:
    def __init__(self, name, printer):
        self._name = name
        self._printer = printer
        self._place = 0
        self._purse = 0
        self._in_penalty_box = False

    def move(self, roll):
        self._place = (self._place + roll) % 12
        self._printer.print(f"{self._name}'s new location is {str(self._place)}")

    def answer_correctly(self):
        self._printer.print("Answer was correct!!!!")
        self._purse += 1
        self._printer.print(f"{self._name} now has {self._purse} Gold Coins.")

    def answer_incorrectly(self):
        self._printer.print("Question was incorrectly answered")
        self._printer.print(f"{self.name} was sent to the penalty box")
        self._in_penalty_box = True

    @property
    def name(self):
        return self._name

    @property
    def place(self):
        return self._place

    @property
    def purse(self):
        return self._purse

    @property
    def in_penalty_box(self):
        return self._in_penalty_box


class Game:
    _ROCK = "Rock"
    _SPORTS = "Sports"
    _SCIENCE = "Science"
    _POP = "Pop"

    def __init__(self, printer=None):
        self._players = []
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

    def add(self, player_name):
        self._players.append(Player(name=player_name, printer=self._printer))
        self._printer.print(f"{player_name} was added")
        self._printer.print(f"They are player number {self._nb_players}")
        return True

    def roll(self, roll):
        self._printer.print(f"{self._current_player_name} is the current player")
        self._printer.print(f"They have rolled a {roll}")

        if self._current_player_in_penalty_box:
            self._update_penalty_box_status(roll)

        if self._current_player_out_of_penalty_box:
            self._move_current_player(roll)
            self._ask_question()

    def was_correctly_answered(self):
        there_is_no_winner = True

        if self._current_player_out_of_penalty_box:
            self._current_player.answer_correctly()
            there_is_no_winner = not self._did_player_win()

        self._update_current_player()
        return there_is_no_winner

    def wrong_answer(self):
        self._current_player.answer_incorrectly()
        self._update_current_player()
        return True

    @classmethod
    def _create_question(cls, index, category):
        return f"{category} Question {index}"

    @property
    def _nb_players(self):
        return len(self._players)

    @property
    def _current_player(self) -> Player:
        return self._players[self._i_current_player]

    @property
    def _current_player_in_penalty_box(self):
        return self._current_player.in_penalty_box

    def _update_penalty_box_status(self, roll):
        if roll % 2 != 0:
            self._is_getting_out_of_penalty_box = True
            self._printer.print(
                f"{self._current_player_name} is getting out of the penalty box"
            )
        else:
            self._printer.print(
                f"{self._current_player_name} is not getting out of the penalty box"
            )
            self._is_getting_out_of_penalty_box = False

    def _move_current_player(self, roll):
        self._current_player.move(roll)

    @property
    def _current_player_name(self):
        return self._current_player.name

    def _ask_question(self):
        self._printer.print(f"The category is {self._current_category}")
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
        return self._current_player.place

    @property
    def _current_player_out_of_penalty_box(self):
        return (
            not self._current_player_in_penalty_box
            or self._is_getting_out_of_penalty_box
        )

    def _update_current_player(self):
        self._i_current_player = (self._i_current_player + 1) % self._nb_players

    @property
    def _current_player_purse(self):
        return self._current_player.purse

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
