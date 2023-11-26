def prompt_for_stations():

    # command line separator

    print('\n-----Enter stations below-----')

    # ask user for origin and store

    print('\nEnter origin: ', end='')

    user_origin = input()

    # ask user for destination and store

    print('Enter destination: ', end='')

    user_destination = input()

    # returning tuple of origin and destination for route creation

    return user_origin, user_destination


def display_path(user_origin, created_path):

    # command line separator

    print('\n-----Path from Origin to Destination-----')

    # display number of stops

    print(f'\nStops: {created_path.cost}')

    # display number of transfers

    print(f'\nTransfers: {len(created_path.transfers)}')

    # displaying list of stations

    transfers = created_path.transfers

    for i, node in enumerate(created_path.path):

        if i == 0:

            print(f'\nOrigin Station: {user_origin} | Line: {node.line_id}')

        if i == 0 and len(created_path.path) > 1:

            print('\nMiddle Stations:')

            if transfers:

                transfer = transfers[0]

                if node.node_id is transfer.node_id:

                    print(f'{node.node_id}   [{transfer.from_line} > {transfer.to_line}]')

                    del transfer

            else:

                print(f'{node.node_id}')

        else:

            if i == len(created_path.path)-1:

                print(f'\nDestination Station: {node.node_id}')

            else:

                print(f'{node.node_id}')
