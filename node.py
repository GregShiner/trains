from __future__ import annotations
from typing import Dict, List, NamedTuple, Set
from networkx import MultiGraph

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
        return list(set([c.node_id for c in self.connections]))

    def get_connected_lines(self) -> List[LineId]:
        return [c.line_id for c in self.connections]
    
    def __repr__(self):
        return f'Node {self.node_id} with connections {self.connections}'


class _Network:
    def __init__(self, node_dict: Dict[NodeId, Node], line_dict: Dict[LineId, Line]):
        self.node_dict = node_dict
        self.line_dict = line_dict

    def route_to(self, start: NodeId, other: NodeId) -> Path:
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
                paths.append(path_stack.copy())
            elif next_node not in path_stack:
                path_stack.append(next_node)
                paths.extend(self._get_all_raw_paths(next_node, other, path_stack, paths))
                path_stack.pop()
        return paths

class Network(MultiGraph):
    node_dict: Dict[NodeId, Node]
    def __init__(self, node_dict: Dict[NodeId, Node]):
        super().__init__()
        self.node_dict = node_dict
        for node in self.node_dict:
            self.add_node(node, node=self.node_dict[node])
        for node_id, node in self.node_dict.items():
            for connection in node.connections:
                self.add_edge(node_id, connection.node_id, key=connection.line_id, connection=connection)
    
    def route_to(self, start: NodeId, other: NodeId) -> Path:
        """
        Returns a path of connections that will take you from this node to the other node
        Algorithm:
        1. Find every non-cyclic path from this node to the other node (ignoring lines/transfers) using a greedy algorithm
        2. For each path, find the minimum number of transfers
        3. Return the path with the minimum number of transfers (if there are multiple, return the one with the minimum distance)
        """
        # TODO: implement this
        raw_paths = self._get_all_raw_paths(start, other)
        trees = []
        for raw_path in raw_paths:
            sequence_tree = self._get_sequence_tree(raw_path)
            trees.append(sequence_tree)
        paths: List[List[Connection]] = []
        for tree in trees:
            paths.extend(self._sequence_tree_to_paths(tree))
        min_transfers = float('inf')
        min_distance = float('inf')
        min_path: List[Connection] | None = None
        for path in paths:
            # get the transfers
            transfers = self._transfers(path)
            # get the distance
            distance = sum([connection.distance for connection in path])
            # if the number of transfers is less than the minimum number of transfers
            if len(transfers) < min_transfers:
                min_path = path
                min_transfers = len(transfers)
                min_distance = distance
            # if the number of transfers is equal to the minimum number of transfers
            elif len(transfers) == min_transfers:
                # if the distance is less than the minimum distance
                if distance < min_distance:
                    min_path = path
                    min_transfers = len(transfers)
                    min_distance = distance
        return Path(min_path, min_distance, self._transfers(min_path))
    
    def _get_sequence_tree(self, raw_path: List[NodeId], tree: Dict[Connection, dict] | None = None) -> Dict[Connection, dict]: # {Connection: {Connection: {Connection: ...}}}
        """
        The raw path is a list of node IDs that represents a path from one node to another.
        It ignores lines and transfers.
        This function returns a tree of all of the possible connections and lines for the path.
        The tree is built recursively using a tree traversal.
        """
        if tree is None:
            tree = {}
        if len(raw_path) == 1:
            return tree
        # for each connection in the first node
        for connection in self.node_dict[raw_path[0]].connections:
            # if the connection is to the next node in the path
            if connection.node_id == raw_path[1]:
                # add the connection to the tree
                tree[connection] = {}
                # recursively call this function with the rest of the path
                self._get_sequence_tree(raw_path[1:], tree[connection])
        return tree
    
    def _sequence_tree_to_paths(self, sequence_tree: Dict[Connection, dict], path: List[Connection] = [], paths: List[List[Connection]] = []) -> List[List[Connection]]:
        """
        This function takes a sequence tree and returns a list of paths.
        """
        if len(sequence_tree) == 0:
            paths.append(path.copy())
            return paths
        for connection in sequence_tree:
            path.append(connection)
            self._sequence_tree_to_paths(sequence_tree[connection], path, paths)
            path.pop()
        return paths

    def _transfers(self, path: List[Connection]) -> List[Transfer]:
        """
        Returns a list of transfers that must be made to follow this path.
        """
        transfers = []
        for i in range(len(path) - 1):
            if path[i].line_id != path[i + 1].line_id:
                transfers.append(Transfer(path[i].node_id, path[i].line_id, path[i + 1].line_id))
        return transfers
    
    def _get_all_raw_paths(self, start: NodeId, end: NodeId, visited: Dict[NodeId, bool] | None = None, paths: Set[List[NodeId]] | None = None, path: List[NodeId] = []) -> List[List[NodeId]]:
        """
        Returns a list of all possible paths from start to end, ignoring lines/transfers
        """
        if visited is None:
            visited = {node_id: False for node_id in self.node_dict}

        if paths is None:
            paths = set()
    
        # Mark the current node as visited and store in path
        visited[start] = True
        path.append(start)
 
        # If current vertex is same as destination, then add path
        if start == end:
            paths.add(tuple(path))
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for node in self.node_dict[start].get_connected_nodes():
                if visited[node] == False:
                    paths.update(tuple(self._get_all_raw_paths(node, end, visited, paths, path)))

        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[start] = False
        return paths
