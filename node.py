from __future__ import annotations
from typing import Dict, List, NamedTuple, Tuple

NodeId = str
LineId = str
Line = List[NodeId]


class Connection(NamedTuple):
    """
    A connection represents a connection between two nodes, including the line that the connection is on and the distance between the nodes.
    """
    node_id: str  # node name of the connected node
    line_id: str  # line name of the connection
    distance: float = 1  # distance between the nodes

class Transfer(NamedTuple):
    """
    A transfer represents a connection between two lines that a user must take to get from one line to another.
    """
    node_id: NodeId
    from_line: LineId
    to_line: LineId

class Path(NamedTuple):
    """
    A path represents a route from one node to another, including the cost of the path and the transfers that must be made.
    """
    path: List[Connection]
    cost: float
    transfers: List[Transfer]

class Node:
    node_id: str  # node name
    connections: List[Connection]  # list of connections

    def __init__(self, node_id: NodeId, connections: List[Connection] = []):
        self.node_id = node_id
        self.connections = connections

    def get_nodes_on_line(self, line_id: LineId) -> List[NodeId]:
        return [c.node_id for c in self.connections if c.line_id == line_id]

    def get_connected_nodes(self) -> List[NodeId]:
        return [c.node_id for c in self.connections]

    def get_connected_lines(self) -> List[LineId]:
        return [c.line_id for c in self.connections]


class Network:
    def __init__(self, node_dict: Dict[NodeId, Node], line_dict: Dict[LineId, Line]):
        self.node_dict = node_dict
        self.line_dict = line_dict

    def route_to(self, start: NodeId, other: NodeId) -> Path:#type: ignore
        """
        Returns a path of connections that will take you from this node to the other node
        Algorithm:
        1. Find every non-cyclic path from this node to the other node (ignoring lines/transfers) using a greedy algorithm
        2. For each path, find the minimum number of transfers
        3. Return the path with the minimum number of transfers (if there are multiple, return the one with the minimum distance)
        """
        # TODO: implement this
        pass

    def _get_all_raw_paths(self, start: NodeId, other: NodeId, path_stack: List[NodeId]=[], paths: List[List[NodeId]]=[]) -> List[List[NodeId]]:
        """
        Returns a list of all possible paths from start to other, ignoring lines/transfers
        """
        if path_stack == []:
            path_stack = [start]
        for next_node in self.node_dict[start].get_connected_nodes():
            if next_node == other:
                """
                node_stack = []
                for node in path_stack:
                    node_stack.append(node)
                paths.append(node_stack.copy())
                """
                paths.append(path_stack.copy())
            elif next_node not in path_stack:
                path_stack.append(next_node)
                paths = self._get_all_raw_paths(next_node, other, path_stack, paths)
                path_stack.pop()
        return paths
