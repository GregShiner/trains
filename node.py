from __future__ import annotations
from typing import Dict, List, NamedTuple, Set
from networkx import MultiGraph
import json

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


class Network(MultiGraph):
    node_dict: Dict[NodeId, Node]

    
    def __init__(self, node_dict: Dict[NodeId, Node]):
        # Call the MultiGraph constructor
        super().__init__()
        self.node_dict = node_dict
        # Add the nodes to the MultiGraph
        for node in self.node_dict:
            self.add_node(node, node=self.node_dict[node])
        # Add the edges to the MultiGraph
        for node_id, node in self.node_dict.items():
            for connection in node.connections:
                self.add_edge(node_id, connection.node_id, key=connection.line_id, connection=connection)
    

    def route_to(self, start: NodeId, other: NodeId) -> Path:
        """
        Returns a path of connections that will take you from this node to the other node
        Algorithm:
        1. Find every non-cyclic path from this node to the other node (ignoring lines/transfers) using a greedy algorithm
        2. For each path, find the sequence tree of all of the possible connections and lines
        3. For each sequence tree, find all of the possible paths
        4. Return the path with the minimum number of transfers (if there are multiple, return the one with the minimum distance)
        """
        # Step 1: Get all of the raw paths
        raw_paths = self._get_all_raw_paths(start, other)

        # Step 2: Find the sequence trees
        # Get the sequence trees
        trees = []
        # For each raw path
        for raw_path in raw_paths:
            # Get the sequence tree
            trees.append(self._get_sequence_tree(raw_path))

        # Step 3: Convert the sequence trees to paths
        # Get the paths from the sequence trees
        paths: List[List[Connection]] = []
        for tree in trees:
            paths.extend(self._sequence_tree_to_paths(other, tree))

        for path in paths:
            print(path)
        
        # Find the path with the minimum number of transfers (if there are multiple, return the one with the minimum distance)
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
    

    def _get_sequence_tree(self, raw_path: List[NodeId], tree: Dict[Connection, dict] | None = None, linesVisited: Set[LineId] = set(), currentLine: LineId|None = None) -> Dict[Connection, dict]: # {Connection: {Connection: {Connection: ...}}}
        """
        The raw path is a list of node IDs that represents a path from one node to another.
        It ignores lines and transfers.
        This function returns a tree of all of the possible connections and lines for the path.
        The tree is built recursively using a tree traversal.
        """
        # God I hate python so much (why are sets passed by reference but dicts aren't)
        linesVisitedCopy = linesVisited.copy()
        # Sets the tree to an empty dict on initial call
        if tree is None:
            tree = {}
            '''linesVisited = set()
            currentLine = None'''
        
        # if the path is empty, return the tree (base case)
        if len(raw_path) == 1:
            return tree
        # for each connection in the first node
        for connection in self.node_dict[raw_path[0]].connections:
            # if the connection is to the next node in the path and is not transferring to a previously used line
            if connection.node_id == raw_path[1] and (currentLine == None or connection.line_id == currentLine or connection.line_id not in linesVisitedCopy):
                # add the line to the set of lines visited
                linesVisitedCopy.add(connection.line_id)
                # add the connection to the tree
                tree[connection] = {}
                # recursively call this function with the rest of the path
                self._get_sequence_tree(raw_path[1:], tree[connection], linesVisitedCopy, connection.line_id)
                linesVisitedCopy = linesVisited.copy()
        return tree
    

    def _sequence_tree_to_paths(self, destination_id: NodeId, sequence_tree: Dict[Connection, dict], path: List[Connection] = [], paths: List[List[Connection]] = []) -> List[List[Connection]]:
        """
        This function takes a sequence tree and returns a list of paths.
        """
        # if the sequence tree is empty, return the paths (base case)
        if len(sequence_tree) == 0:
            if path[-1].node_id == destination_id:
                paths.append(path.copy())
            return paths
        # for each connection in the sequence tree
        for connection in sequence_tree:
            # add the connection to the path
            path.append(connection)
            # recursively call this function with the rest of the sequence tree
            self._sequence_tree_to_paths(destination_id, sequence_tree[connection], path, paths)
            # remove the connection from the path
            path.pop()
        return paths


    def _transfers(self, path: List[Connection]) -> List[Transfer]:
        """
        Returns a list of transfers that must be made to follow this path.
        """
        transfers = []
        # for each connection in the path
        for i in range(len(path) - 1):
            # if the line ID of the current connection is not the same as the line ID of the next connection
            if path[i].line_id != path[i + 1].line_id:
                # add a transfer to the list of transfers
                transfers.append(Transfer(path[i].node_id, path[i].line_id, path[i + 1].line_id))
        return transfers
    

    def _get_all_raw_paths(self, start: NodeId, end: NodeId, visited: Dict[NodeId, bool] | None = None, paths: Set[List[NodeId]] | None = None, path: List[NodeId] = []) -> List[List[NodeId]]:
        """
        Returns a list of all possible paths from start to end, ignoring lines/transfers
        """
        # Mark all the vertices as not visited on initial call
        if visited is None:
            visited = {node_id: False for node_id in self.node_dict}
        
        # Initialize paths on initial call
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
    
    @staticmethod
    def from_line_file(file_name: str) -> Network:
        """
        Returns a Network object from a line file.
        """
        with open(file_name, 'r') as f:
            line_dict: Dict[LineId,Line] = json.load(f)
        return Network.from_line_dict(line_dict)
    
    @staticmethod
    def from_line_dict(line_dict: Dict[LineId,Line]) -> Network:
        """
        Returns a Network object from a line dictionary.
        """
        node_dict: Dict[NodeId, Node] = {}
        nodes = set()
        line_ids = line_dict.keys()
        lines = line_dict.values()
        for line in lines:
            nodes.update(line)
        for node in nodes:
            connection_list = []
            for line_id in line_ids:
                for i in range(len(line_dict[line_id])):
                    if line_dict[line_id][i] == node:
                        if i == 0:
                            connection_list.append(Connection(line_dict[line_id][i+1], line_id))
                        elif i == len(line_dict[line_id])-1:
                            connection_list.append(Connection(line_dict[line_id][i-1], line_id))
                        else:
                            connection_list.append(Connection(line_dict[line_id][i-1], line_id))
                            connection_list.append(Connection(line_dict[line_id][i+1], line_id))
            node_dict[node] = Node(node, connection_list)
        return Network(node_dict)
