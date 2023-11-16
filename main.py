from typing import Dict
from node import Node, Connection, NodeId, LineId, Line, Network
from parser import load_json, line_dict_to_node_dict
import ui

NODE_DICT: Dict[NodeId, Node] = {
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

LINE_DICT: Dict[LineId, Line] = {
    'red': ['D', 'A', 'B'],
    'blue': ['F', 'A', 'B'],
    'green': ['E', 'A', 'C', 'B'],
}

network = Network(NODE_DICT)
for node in network.nodes:
    print(node)
    for connection in NODE_DICT[node].connections:
        print(f'\t{connection.node_id} on line {connection.line_id}')

for edge in network.edges:
    print(edge)

#draw(network, with_labels=True)
#plt.show()

user_stations = ui.prompt_for_stations()

# example is from F to C

user_path = network.route_to(user_stations[0], user_stations[1])

ui.display_path(user_stations[0], user_path)
