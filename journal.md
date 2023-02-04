# Journal

## Initial commit
Copy the code from Jetbrain's trivia repository, write a README and begin the refactoring journal.

## Code format and first CI workflow
The first obvious way to improve the readability of a codebase is to use a code formatter.
I choose the uncompromising opinionated [black](https://github.com/psf/black).

Code formatting is important to ensure a consistent style across the entire code base for all the project's life.
The simple quoted strings have been replaced by double-quoted ones for example.

In order to unsure the code formatter is going to be used systematically before each commit,
I install [pre-commit](https://pre-commit.com/).

I also add a [Github Actions](https://docs.github.com/en/actions)
workflow to unsure each pushed commit is correctly formatted.
## First tests
Since the goal of refactoring is to preserve the existing behaviour,
we must have some data that define the desired behaviour we want to preserve. In our case, in the main
script, we have an example of a randomized interactions with a Game object.

Let us say these runs are the behaviours we want to preserve.
After each iteration of refactor, we want to reproduce the runs and verify they didn't change.

Let us defined each run as a scenario. Each scenario is an ordered list of steps,
at each step we call a method of Game. To reproduce a scenario, we must record the name of the called method,
the arguments we called it with and the returned value.

However, there is an important missing data: the printed text: Each method call prints texts and this
printed text, even though it is not part of the returned value, is in important part of what defines the behaviour of Game.

For now, we don't bother with recording the printed text. For now, we just want to record some scenarios and to replay
them in tests.

Three scenarios with two, three and four players are constituted. They can be rerun in our test suite.
Our test suite is integrated to our CI. If the test suite is broken, it means our refactor broke the behaviour of the Game class.

Later, the test suite will be enriched with the printed text.
### Technologies and read more
Tests are written and run using [pytest](https://docs.pytest.org/).

You can find [here](https://docs.pytest.org/) an example of running pytest in Github Actions.

On the concept of CI (Continuous Integration) you can read the classic [book by Paul Duvall](https://www.amazon.fr/Continuous-Integration-Improving-Software-Reducing/dp/0321336380)

## Capture side effects
This is the first time we are going to touch the code of the class Game since the automatic reformatting.
Our goal at this iteration is simply to capture the printed text for each method call.

We want must be very careful in changing the code base of Game since as long they don't check the printed texts, our tests fail in guaranteeing our changes do not alter the functional behaviour.

Before each method calling the built-in function "print", we redefine print as referring to a protected method. Instead of printing is STDIN (the terminal in our case), it will print in a provided buffer we can inspect.

In order not to alter too much the code of Game, we delegate the printing responsibility to another class: Printer. This class prints the text in file using the built-in print.

We also define a subclass ou print whose role
is to log the text to be printed in a buffer. We add a method to capture the printed lines and to reinitialize the buffer.
This BufferingPrinter act as a [test double](https://martinfowler.com/bliki/TestDouble.html).

So now we update our database of scenarios with the printed lines and use this extra data to enrich our tests and ensure our behaviour is preserved.

## First refactor
Once we have confidence in our tests, we can start refactor our Game class. The first bold step is to stop redefining the python built-in "print"
and use the printer each time we want to print.

## Fix and clarify meaning
Did player win? The answer should be true if the current player won the game so the function '_did_player_win' is not correctly implemented. Its functions using it must be adapted once fixed.

## Standardize string interpolation
This code use two methods to [interpolate strings](https://en.wikipedia.org/wiki/String_interpolation), the '%' operator and the string concatenation with '+'. I prefer the f-strings so I replaced
both '%' and '+' strings by f-strings.

## Generalize method
The method creating rock question can be generalized to create a question of any category. It is a class method since it is not specific to an instance and is protected since it is not use outside the
class itself.

Categories' names can be extracted as constants.

## Better names
The property how_many_players that returns an integer should be names nb_players. Since it is not used outside the class, it should be protected (prefixed by a underscore).

## Property extraction and encapsulation
[Properties](https://realpython.com/python-property/) are one of the most useful features. It disguises function calls as attributes access update. So no more setters and getters.

Extract property is a pythonic version of the [Extract function](https://refactoring.com/catalog/extractFunction.html) pattern.

## Not a refactor
This commit is a bug fix. A little one but a bug fix nonetheless. So this is the first case where the test data
need to be updated to reflect the bug fix.
