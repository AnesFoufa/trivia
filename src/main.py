import json
import pathlib
import sys
from io import StringIO


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
    def __init__(self, printer=None):
        self.players = []
        self.places = [0] * 6
        self.purses = [0] * 6
        self.in_penalty_box = [0] * 6

        self.pop_questions = []
        self.science_questions = []
        self.sports_questions = []
        self.rock_questions = []

        self.current_player = 0
        self.is_getting_out_of_penalty_box = False

        for i in range(50):
            self.pop_questions.append("Pop Question %s" % i)
            self.science_questions.append("Science Question %s" % i)
            self.sports_questions.append("Sports Question %s" % i)
            self.rock_questions.append(self.create_rock_question(i))

        if printer is None:
            self._printer = Printer(file=sys.stdout)
        else:
            self._printer = printer

    def create_rock_question(self, index):
        return "Rock Question %s" % index

    def is_playable(self):
        return self.how_many_players >= 2

    def add(self, player_name):
        self.players.append(player_name)
        self.places[self.how_many_players] = 0
        self.purses[self.how_many_players] = 0
        self.in_penalty_box[self.how_many_players] = False

        self._printer.print(player_name + " was added")
        self._printer.print("They are player number %s" % len(self.players))

        return True

    @property
    def how_many_players(self):
        return len(self.players)

    def roll(self, roll):
        self._printer.print(
            "%s is the current player" % self.players[self.current_player]
        )
        self._printer.print("They have rolled a %s" % roll)

        if self.in_penalty_box[self.current_player]:
            if roll % 2 != 0:
                self.is_getting_out_of_penalty_box = True

                self._printer.print(
                    "%s is getting out of the penalty box"
                    % self.players[self.current_player]
                )
                self.places[self.current_player] = (
                    self.places[self.current_player] + roll
                )
                if self.places[self.current_player] > 11:
                    self.places[self.current_player] = (
                        self.places[self.current_player] - 12
                    )

                self._printer.print(
                    self.players[self.current_player]
                    + "'s new location is "
                    + str(self.places[self.current_player])
                )
                self._printer.print("The category is %s" % self._current_category)
                self._ask_question()
            else:
                self._printer.print(
                    "%s is not getting out of the penalty box"
                    % self.players[self.current_player]
                )
                self.is_getting_out_of_penalty_box = False
        else:
            self.places[self.current_player] = self.places[self.current_player] + roll
            if self.places[self.current_player] > 11:
                self.places[self.current_player] = self.places[self.current_player] - 12

            self._printer.print(
                self.players[self.current_player]
                + "'s new location is "
                + str(self.places[self.current_player])
            )
            self._printer.print("The category is %s" % self._current_category)
            self._ask_question()

    def _ask_question(self):
        if self._current_category == "Pop":
            self._printer.print(self.pop_questions.pop(0))
        if self._current_category == "Science":
            self._printer.print(self.science_questions.pop(0))
        if self._current_category == "Sports":
            self._printer.print(self.sports_questions.pop(0))
        if self._current_category == "Rock":
            self._printer.print(self.rock_questions.pop(0))

    @property
    def _current_category(self):
        if self.places[self.current_player] == 0:
            return "Pop"
        if self.places[self.current_player] == 4:
            return "Pop"
        if self.places[self.current_player] == 8:
            return "Pop"
        if self.places[self.current_player] == 1:
            return "Science"
        if self.places[self.current_player] == 5:
            return "Science"
        if self.places[self.current_player] == 9:
            return "Science"
        if self.places[self.current_player] == 2:
            return "Sports"
        if self.places[self.current_player] == 6:
            return "Sports"
        if self.places[self.current_player] == 10:
            return "Sports"
        return "Rock"

    def was_correctly_answered(self):
        if self.in_penalty_box[self.current_player]:
            if self.is_getting_out_of_penalty_box:
                self._printer.print("Answer was correct!!!!")
                self.purses[self.current_player] += 1
                self._printer.print(
                    self.players[self.current_player]
                    + " now has "
                    + str(self.purses[self.current_player])
                    + " Gold Coins."
                )

                winner = self._did_player_win()
                self.current_player += 1
                if self.current_player == len(self.players):
                    self.current_player = 0

                return winner
            else:
                self.current_player += 1
                if self.current_player == len(self.players):
                    self.current_player = 0
                return True

        else:
            self._printer.print("Answer was corrent!!!!")
            self.purses[self.current_player] += 1
            self._printer.print(
                self.players[self.current_player]
                + " now has "
                + str(self.purses[self.current_player])
                + " Gold Coins."
            )

            winner = self._did_player_win()
            self.current_player += 1
            if self.current_player == len(self.players):
                self.current_player = 0

            return winner

    def wrong_answer(self):
        self._printer.print("Question was incorrectly answered")
        self._printer.print(
            self.players[self.current_player] + " was sent to the penalty box"
        )
        self.in_penalty_box[self.current_player] = True

        self.current_player += 1
        if self.current_player == len(self.players):
            self.current_player = 0
        return True

    def _did_player_win(self):
        return not (self.purses[self.current_player] == 6)


from random import randrange


def capture_interaction(file_name, players):
    not_a_winner = False
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
