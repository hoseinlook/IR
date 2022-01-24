import os

from pathlib import Path
ABSOLUTE_DATA_PATH = str(Path(__file__).parent.joinpath('data'))
print(ABSOLUTE_DATA_PATH)