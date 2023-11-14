import json
from node import Line, LineId, Node, NodeId, Connection
from typing import Dict

def loadJson():
    f = open('data.json')
    linedict: Dict[LineId,Line] = json.load(f)
    return linedict

def lineDictToNodeDict(linedict):
    nodedict: Dict[NodeId, Node] = {}
    nodes = set()
    lineIds = linedict.keys()
    lines = linedict.values()
    for line in lines:
        nodes.update(line)
    for node in nodes:
        connectionList = []
        for lineId in lineIds:
            for i in range(len(linedict[lineId])):
                if linedict[lineId][i] == node:
                    if i == 0:
                        connectionList.append(Connection(linedict[lineId][i+1], lineId))
                    elif i == len(linedict[lineId])-1:
                        connectionList.append(Connection(linedict[lineId][i-1], lineId))
                    else:
                        connectionList.append(Connection(linedict[lineId][i-1], lineId))
                        connectionList.append(Connection(linedict[lineId][i+1], lineId))
        nodedict[node] = Node(node, connectionList)
    return nodedict