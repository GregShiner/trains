from typing import Dict, List
from node import Node, Connection, NodeId, LineId, Line, Network
from networkx import draw
from timeit import timeit
from parser import loadJson, lineDictToNodeDict

LIST_DICT = loadJson()

NODE_DICT = lineDictToNodeDict(LIST_DICT)

print(NODE_DICT)