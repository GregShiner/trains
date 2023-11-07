from __future__ import annotations
from typing import List, NamedTuple, TypedDict, Dict, TypeAlias

NodeId = str
LineId = str

class NodeDict(TypedDict):
    node_id: NodeId
    node: Node

class LineDict(TypedDict):
    line_id: LineId
    line: List[NodeId]

class Connection(NamedTuple):
    node_id: str # node name of the connected node
    line_id: str # line name of the connection
    distance: float = 1 # distance between the nodes

class Node:
    node_id: str # node name
    connections: List[Connection] # list of connections
    def __init__(self, node_id: NodeId, connections: List[Connection] = []):
        self.node_id = node_id
        self.connections = connections
    def get_nodes_on_line(self, line_id: LineId) -> List[NodeId]:
        return [c.node_id for c in self.connections if c.line_id == line_id]
    def get_connected_nodes(self) -> List[NodeId]:
        return [c.node_id for c in self.connections]
    def get_connected_lines(self) -> List[LineId]:
        return [c.line_id for c in self.connections]
    def route_to(self, other: Node) -> List[Connection]:
        """Returns a list of connections that will take you from this node to the other node"""
        pass