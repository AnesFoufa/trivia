import pathlib
import json
from .main import Game, BufferPrinter


def test_first_scenario():
    scenario = load_scenario(file_name="first_scenario.json")
    run_game_with_scenario(scenario)


def test_second_scenario():
    scenario = load_scenario(file_name="second_scenario.json")
    run_game_with_scenario(scenario)


def test_third_scenario():
    scenario = load_scenario(file_name="third_scenario.json")
    run_game_with_scenario(scenario)


def load_scenario(file_name):
    path_to_data = pathlib.Path().absolute() / "data"
    with open(path_to_data / file_name) as f:
        scenario = json.load(f)
    return scenario


def run_game_with_scenario(scenario):
    printer = BufferPrinter()
    game = Game(printer=printer)
    for step in scenario:
        method = {
            "add": game.add,
            "roll": game.roll,
            "was_correctly_answered": game.was_correctly_answered,
            "wrong_answer": game.wrong_answer,
        }[step["method"]]
        call_args = step["args"]
        returned_value = method(*call_args)
        expected_return_value = step["return"]
        expected_printed_lines = step["printed_lines"]
        assert expected_return_value == returned_value
        assert expected_printed_lines == printer.pop_printed_lines()
