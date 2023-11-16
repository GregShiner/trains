from node import Path

def prompt_for_stations():

    # ask user for origin and store

    print('Enter origin: ', end='')

    user_origin = input()

    # ask user for destination and store

    print('Enter destination: ', end='')

    user_destination = input()

    return user_origin, user_destination


def display_path(user_origin, created_path):

    print(created_path)
    print(f'Stops: {created_path.cost}')
    print(f'Transfers: {len(created_path.transfers)}')

    for i, node in enumerate(created_path.path):

        if i == 0:

            print(f'Origin Station: {user_origin}')

        else:

            print(f'\nGet on line {node.line_id} line train at {node.node_id}')

        print(f'\nRide for {node.distance} stops and get off at {node.node_id}')

        
#
