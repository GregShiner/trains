from __future__ import annotations
from dataclasses import dataclass
from sys import maxsize
from typing import Dict, List, NamedTuple, Set, Tuple
from networkx import MultiGraph
import json

NodeId = str
LineId = str
Line = List[NodeId]


class Connection(NamedTuple):
    """
    A connection represents a connection between two nodes, including the line that the connection is on and the distance between the nodes.
    """
    node_id: NodeId  # node name of the connected node
    line_id: LineId  # line name of the connection
    distance: float = 1  # distance between the nodes


class Transfer(NamedTuple):
    """
    A transfer represents a connection between two lines that a user must take to get from one line to another.
    """
    node_id: NodeId
    from_line: LineId
    to_line: LineId

@dataclass(eq=False)
class Path:
    """
    A path represents a route from one node to another, including the cost of the path and the transfers that must be made.
    """
    path: List[Connection]
    distance: float
    num_stations: int
    num_transfers: int
    transfers: List[Transfer]

    """
    Comparisons for Path objects
    A path is less than another path if it has fewer transfers
    A path is greater than another path if it has more transfers
    If the paths have the same number of transfers, the path with the shorter distance is less than the other path
    """ 
    def __lt__(self, __value: Path) -> bool:
        if self.num_transfers < __value.num_transfers:
            return True
        elif self.num_transfers > __value.num_transfers:
            return False
        else:
            return self.distance < __value.distance
    

    def __eq__(self, __value: Path) -> bool:
        return self.num_transfers == __value.num_transfers and self.distance == __value.distance
    

    def append(self, value: Connection) -> None:
        """
        Appends a connection to the path.
        Automatically updates the distance and transfers.
        """
        self.path.append(value)
        self.distance += value.distance
        self.num_stations += 1
        if len(self.path) >= 2 and value.line_id != self.path[-2].line_id:
            self.transfers.append(Transfer(self.path[-2].node_id, self.path[-2].line_id, value.line_id))
            self.num_transfers += 1


    def pop(self) -> Connection:
        """
        Removes the last connection from the path.
        Automatically updates the distance and transfers.
        """
        self.distance -= self.path[-1].distance
        self.num_stations -= 1
        if len(self.path) >= 2 and self.path[-1].line_id != self.path[-2].line_id:
            self.transfers.pop()
            self.num_transfers -= 1
        return self.path.pop()
    

    def set_self(self, value: Path) -> None:
        """
        Sets this path to the value of another path.
        Note: This is an absolutely horrible abuse of sharing memory.
        """
        self.path = value.path.copy()
        self.distance = value.distance
        self.num_stations = value.num_stations
        self.num_transfers = value.num_transfers
        self.transfers = value.transfers.copy()


class Node:
    node_id: NodeId  # node name
    connections: List[Connection]  # list of connections


    def __init__(self, node_id: NodeId, connections: List[Connection] = []):
        self.node_id = node_id
        self.connections = connections


    def get_connected_nodes(self) -> List[NodeId]:
        """
        Gets a list of all of the nodes that this node is connected to.
        """
        # the list comprehension gets the node_id of every connection in the list of connections
        # the set() removes duplicates (some nodes are connected to each other multiple times if they share multiple lines)
        # it is then converted back to a list
        return list(set([c.node_id for c in self.connections]))


    def get_connected_lines(self) -> List[LineId]:
        """
        Gets a list of all of the lines that this node is connected to.
        """
        # the list comprehension gets the line_id of every connection in the list of connections
        return [c.line_id for c in self.connections]
    
    
    def __repr__(self):
        """
        Debugging representation of the node.
        """
        return f'Node {self.node_id} with connections {self.connections}'
    

class Network(MultiGraph):
    """
    A network represents a graph of stations and connections between them.
    """
    node_dict: Dict[NodeId, Node] # Mapping of node IDs to node objects

    
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
    

    def route_to(self, start: NodeId, other: NodeId) -> Path:#type: ignore
        """
        Returns a path of connections that will take you from this node to the other node
        Algorithm:
        1. Find every non-cyclic path from this node to the other node (ignoring lines/transfers) using a greedy algorithm
        2. For each path, find the sequence tree of all of the possible connections and lines
        3. For each sequence tree, find the best path
            a. Stop traversing the tree if the path is longer than the best path
            b. Share the current best path between all of the trees
        Time complexity:
        let V be the number of nodes in the graph
        let N be the number of raw paths (see below)
        There are 3 complex parts to this algorithm:
        1. Finding all of the raw paths O(2^V)
        2. Sorting the raw paths O(V!logV)
        3. Finding the best path O(V!*(2^V))
        Since these happen sequentially, the total time complexity is O(V!*(2^V))
        """
        # Step 1: Get all of the raw paths
        # O(2^V) where V is the number of nodes in the graph
        raw_paths = self._get_all_raw_paths(start, other, self._find_needed_lines(start, other))
        """
        The number of raw paths in the worst case is (V-2)!e
        Where V is the number of nodes in the graph and e is euler's number (Hey that's pretty cool that e shows up here)
        Source: https://math.stackexchange.com/questions/2406920/total-number-paths-between-two-nodes-in-a-complete-graph
        When dealing with time complexity, we ignore constants and lower order terms
        Therefore, the asymptotic number of raw paths is O(V!)
        """

        # Sort the raw paths by length
        # This should make step 3 find more min paths faster
        """
        The time complexity of this sort is O(NlogN) where N is the number of raw paths
        Substituting in the asymptotic number of raw paths, we get O(V!log(V!))
        O(log(V!)) can be simplified using Stirling's approximation to O(VlogV)
        Sources: https://stackoverflow.com/questions/8118221/what-is-ologn-on-and-stirlings-approximation
            https://en.wikipedia.org/wiki/Stirling%27s_approximation
        Substituting this back gives us O(V*V!logV)
        This simplifies to O(V!logV)
        While this seems like a horrendous time complexity, 
        In practice, the number of raw paths is very small, and the sort is very fast
        This is because our graph is far from fully connected
        """
        raw_paths_sorted = sorted(raw_paths, key=lambda path: len(path))
        # Initialize the min path
        min_path = Path([], float('inf'), 0, maxsize, [])
        # Step 2-3: For each sequence tree, find the best path
        """
        This loop runs O(N) or O(V!) times where N is the number of raw paths (see above)
        The complexity of this loop as a whole is O(V!*(2^V+2^V))
        This simplifies to O(V!*2^V)
        """
        for raw_path in raw_paths_sorted:
            # O(2^V) where V is the number of nodes in the tree
            tree = self._get_sequence_tree(raw_path)
            # O(2^V) where V is the number of nodes in the tree
            self._get_best_path(other, tree, min_path)
        return min_path

    def _get_best_path(self, destination_id: NodeId, tree: Dict[Connection, dict], min_path: Path, path: Path | None = None) -> None:
        """
        This function takes a sequence tree and returns the best path.
        Algorithm:
        1. Recurse through the tree, keeping track of the current path, the number of transfers, and the distance
            a. If the current path has more transfers than the minimum path, stop traversing the tree
            b. If the current path has the same transfers as the min path, but is longer, stop traversing the tree
            c. Else, continue traversing the tree
        2. At the end of the tree, if the current path is better than the min path, set the min path to the current path
        Time complexity: O(2^V) where V is the number of nodes in the tree
        """
        # Initialize the path on initial call
        if not path:
            path = Path([], 0, 0, 0, [])
        # If the tree is empty, if the path is better than the min path, set the min path to the path and return it
        if len(tree) == 0:
            if (path.path[-1].node_id == destination_id) and (path < min_path):
                min_path.set_self(path)
            return

        # For each connection in the tree
        for connection in tree:
            # Add the connection to the path
            path.append(connection)
            # Recursively call this function with the rest of the tree
            if path < min_path:
                self._get_best_path(destination_id, tree[connection], min_path, path)
            # Remove the connection from the path
            path.pop()


    def _get_sequence_tree(self, raw_path: Tuple[NodeId], tree: Dict[Connection, dict] | None = None, linesVisited: Set[LineId] = set(), currentLine: LineId|None = None) -> Dict[Connection, dict]: # {Connection: {Connection: {Connection: ...}}}
        """
        The raw path is a list of node IDs that represents a path from one node to another.
        It ignores lines and transfers.
        This function returns a tree of all of the possible connections and lines for the path.
        The tree is built recursively using a tree traversal.
        Time complexity: O(2^V) where V is the number of nodes in the graph
        The worst case is that we have a fully connected graph, and the raw path traverses every node.
        In this case, the for loop will run V times, and the recursive call will run V times.
        Becaue the for loop and recursive call are nested, the time complexity is O(2^V).
        """
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
        Algorithm:
        1. Recurse through the tree, keeping track of the current path
        2. At the end of the tree, if the current path ends at the destination, add the path to the list of paths
        Time complexity: O(2^V) where V is the number of nodes in the tree
        """
        # if the sequence tree is empty, return the paths (base case)
        if len(sequence_tree) == 0:
            # if the path ends at the destination, add the path to the list of paths
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
        Algorithm:
        1. For each connection in the path, 
            if the line ID of the current connection is not the same as the line ID of the next connection, 
                add a transfer to the list of transfers
        Time complexity: O(V) where V is the number of connections in the path
        """
        transfers = []
        # for each connection in the path
        for i in range(len(path) - 1):
            # if the line ID of the current connection is not the same as the line ID of the next connection
            if path[i].line_id != path[i + 1].line_id:
                # add a transfer to the list of transfers
                transfers.append(Transfer(path[i].node_id, path[i].line_id, path[i + 1].line_id))
        return transfers
    

    def _get_all_raw_paths(self, start: NodeId, end: NodeId, needed: Set[LineId], visited: Dict[NodeId, bool] | None = None, paths: Set[Tuple[NodeId]] | None = None, path: List[NodeId] = []) -> Set[Tuple[NodeId]]:
        """
        Returns a list of all possible paths from start to end, ignoring lines/transfers
        Algorithm:
        1. Mark all the vertices as not visited
        2. Create an empty path
        3. Visit the start node and add it to the path
        4. If the current node is the destination, add the path to the list of paths
        5. Else, for each node adjacent to the current node, if the node is not visited, 
            recursively call this function with the node as the start node
        6. Remove the current node from the path and mark it as unvisited
        7. Return the list of paths
        Time complexity: O(2^V) where V is the number of nodes in the graph
        The worst case is that we have a fully connected graph
        The for loop will run V times, and the inside loop will run V times
        However, the recursive call is nested inside the first for loop, and that causes the time complexity to be O(2^V)
        This outweighs the O(V) time of the inside loop
        """
        # Mark all the vertices as not visited and determine unneeded lines on initial call 
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
            paths.add(tuple(path)) # type: ignore
        # If current vertex is not destination
        else:
            # Recur for all the vertices adjacent to this vertex
            for node in self.node_dict[start].get_connected_nodes(): # O(V) because in a fully connected graph, every node is connected to every other node
                connections_checked = 0 # Keep track of how many connections have been checked
                for connection in self.node_dict[start].connections:  # O(V) ditto
                    # If the connection is not needed, skip it
                    if connection.line_id in needed:
                        break
                    connections_checked += 1
                # If all of the connections have been checked, and none of them are needed, skip this node
                if connections_checked == len(self.node_dict[start].connections):
                    continue
                # If the node is not visited, recursively call this function with the node as the start node
                if visited[node] == False:
                    self._get_all_raw_paths(node, end, needed, visited, paths, path) # O(V) recursive call happens V times per loop

        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[start] = False
        return paths
    

    def _find_needed_lines(self, start_Node: NodeId, end_Node: NodeId) -> Set[LineId]:
        """
        Finds the set of lines that might be needed to travel from the start node to the end node.

        Args:
            start_Node (NodeId): The ID of the start node.
            end_Node (NodeId): The ID of the end node.

        Returns:
            Set[LineId]: The set of lines needed to travel from the start node to the end node.
        """
        #create a graph of all lines connected to each other
        line_graph:Dict[LineId, Set[LineId]] = {}
        for node in self.nodes:
            #if the node is a junction
            if len(self.node_dict[node].connections) > 1:
                connections_to_current_line = set()
                #create a set of all lines that the current node is connected to
                for connection in self.node_dict[node].connections:
                    #add line as a key to the line_graph if it is not already present
                    if connection.line_id not in line_graph:
                        line_graph[connection.line_id] = set()
                    connections_to_current_line.add(connection.line_id)
                #update every key in line_graph present in the node with all other lines in the current node
                for line in connections_to_current_line:
                    line_graph[line].update(connections_to_current_line)
        #remove every line from its own set
        for key in line_graph:
            line_graph[key].remove(key)
        #get the lines of the start and end nodes
        start_lines = self.node_dict[start_Node].get_connected_lines()
        end_lines = self.node_dict[end_Node].get_connected_lines()
        shortest_path = maxsize
        possibles = set()
        startend = set()
        #find the shortest path between the start and end nodes using any combination of start/end lines
        for start in start_lines:
            #redoing this but like less bad and more good
            #"MARK" is added into the queue after each depth, tracks the length of the path
            startend.add(start)
            for end in end_lines:
                startend.add(end)
                visited = set()
                incremental_visited = set()
                queue = []
                queue.append(start)
                queue.append("MARK")
                visited.add(start)
                length = 1
                while queue:
                    current_line = queue.pop(0)
                    if current_line == "MARK":
                        length += 1
                        queue.append("MARK")
                        incremental_visited = visited.copy()
                        continue
                    for line in line_graph[current_line]:
                        if line == end:
                            queue = []
                            break
                        elif line not in visited:
                            queue.append(line)
                            visited.add(line)
                if length < shortest_path:
                    shortest_path = length
                    possibles = incremental_visited
                elif length == shortest_path:
                    possibles.update(incremental_visited)
        
        possibles.update(startend)
        return possibles
    
    @staticmethod
    def from_line_file(file_name: str) -> Network:
        """
        Returns a Network object from a line file.
        """
        # The json file is a dictionary of line IDs to lines (lists of node IDs)
        with open(file_name, 'r') as f:
            line_dict: Dict[LineId,Line] = json.load(f)
        return Network.from_line_dict(line_dict)
    
    @staticmethod
    def from_line_dict(line_dict: Dict[LineId,Line]) -> Network:
        """
        Builds a Network object from a line dictionary.
        """
        node_dict: Dict[NodeId, Node] = {} # Mapping of node IDs to node objects
        nodes = set() # Set of all nodes
        line_ids = line_dict.keys() # Set of all line IDs
        lines = line_dict.values() # Set of all lines
        # Add all of the nodes to the set of nodes
        for line in lines:
            nodes.update(line)
        # Create a dictionary of nodes
        # Each node is mapped to a list of connections
        for node in nodes:
            # Reset the connection list for each node
            connection_list = []
            # For each line, if the node is on the line, add the node's connections to the connection list
            for line_id in line_ids:
                # for each node on the line
                for i in range(len(line_dict[line_id])):
                    # if the node is on the line
                    if line_dict[line_id][i] == node:
                        # if the node is the first node on the line, add the next node to the connection list
                        if i == 0:
                            connection_list.append(Connection(line_dict[line_id][i+1], line_id))
                        # if the node is the last node on the line, add the previous node to the connection list
                        elif i == len(line_dict[line_id])-1:
                            connection_list.append(Connection(line_dict[line_id][i-1], line_id))
                        # otherwise, add the previous and next nodes to the connection list
                        else:
                            connection_list.append(Connection(line_dict[line_id][i-1], line_id))
                            connection_list.append(Connection(line_dict[line_id][i+1], line_id))
            # Add the node to the node dictionary
            node_dict[node] = Node(node, connection_list)
        return Network(node_dict)
