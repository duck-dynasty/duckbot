import sys
import os

# allow for importing modules in the tests directory
sys.path.append(os.path.dirname(__file__))

# unify the module import scheme between src and tst
sys.path.insert(0, os.path.abspath(os.path.join("..", "duckbot", "duckbot")))
