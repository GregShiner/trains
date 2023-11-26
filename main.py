from node import Network
import ui

network = Network.from_line_file("data.json")
for node in network.nodes:
    print(node)
    for connection in network.node_dict[node].connections:
        print(f'\t{connection.node_id} on line {connection.line_id}')

for edge in network.edges:
    print(edge)

user_stations = ui.prompt_for_stations()

user_path = network.route_to(user_stations[0], user_stations[1])

ui.display_path(user_stations[0], user_path)
