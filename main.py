from node import Network
from argparse import ArgumentParser
from iterfzf import iterfzf
from os.path import isfile
import ui

parser = ArgumentParser()
parser.add_argument('-s', "--start", action='store')
parser.add_argument('-e', "--end", action='store')
parser.add_argument('-i', '--input', action='store', default='manhattan.json')

args = parser.parse_args()
if not isfile(args.input):
    print(f"File does not exist: {args.input}")
    exit(2)

network = Network.from_line_file(args.input)
nodes = network.node_dict.keys()

if args.start:
    if args.start not in nodes:
        print(f"Invalid station name: {args.start}")
        exit(1)

    start_station = args.start

else:
    start_station = iterfzf(nodes, prompt='Start station: ')


if args.end:
    if args.end not in nodes:
        print(f"Invalid station name: {args.end}")
        exit(1)

    end_station = args.end

else:
    end_station = iterfzf(nodes, prompt='End station: ')

print(f'Start station: {start_station}')
print(f'End station: {end_station}')

user_path = network.route_to(start_station, end_station) # type: ignore

ui.display_path(start_station, user_path)  # type: ignore

