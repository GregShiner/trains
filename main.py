from node import Node, Connection, NodeDict, LineDict

NODE_DICT: NodeDict = {
    'A': Node('A', [Connection('B', 'red'), 
                Connection('B', 'blue'),
                Connection('C', 'green'),
                Connection('D', 'red'),
                Connection('E', 'green'),
                Connection('F', 'blue'),]),
    'B': Node('B', [Connection('A', 'red'),
                Connection('A', 'blue'),
                Connection('C', 'green'),]),
    'C': Node('C', [Connection('A', 'green'),
                Connection('B', 'green'),]),
    'D': Node('D', [Connection('A', 'red'),]),
    'E': Node('E', [Connection('A', 'green'),]),
    'F': Node('F', [Connection('A', 'blue'),]),
}

LINE_DICT: LineDict = {
    'red': ['D', 'A', 'B',],
    'blue': ['F', 'A', 'B'],
    'green': ['E', 'A', 'C', 'B'],
}

def get_node(node_name: str) -> Node:
    return NODE_DICT[node_name]