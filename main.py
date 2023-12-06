from node import Network
import ui
from iterfzf import iterfzf

network = Network.from_line_file("manhattan.json")
"""
for node in network.nodes:
    print(node)
    for connection in network.node_dict[node].connections:
        print(f'\t{connection.node_id} on line {connection.line_id}')

for edge in network.edges:
    print(edge)
"""
nodes = network.node_dict.keys()
start_node = iterfzf(nodes, multi=False, prompt='Start station: ')
end_node = iterfzf(nodes, multi=False, prompt='End station: ')
print(f'Start station: {start_node}')
print(f'End station: {end_node}')

#user_stations = ui.prompt_for_stations()
#user_stations = ('215th Street (1)', '57th Street (M)')

user_path = network.route_to(start_node, end_node) # type: ignore
#user_path = network.route_to(*user_stations)

ui.display_path(start_node, user_path) # type: ignore
#ui.display_path(user_stations[0], user_path)
