from pathlib import Path

#part 2's utils are reachable from here too
#as utils.nve and utils.mongo
__path__.append(str(Path(__file__).resolve().parents[2] / "project2" / "utils"))
