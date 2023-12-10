from node import NodeId, Path
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


def display_path(user_origin: NodeId, created_path: Path):
    # command line separator
    print('\n-----Path from Origin to Destination-----')

    # display number of stops
    print(f'\nStops: {created_path.num_stations}')

    # display number of transfers
    print(f'\nTransfers: {created_path.num_transfers}')

    # displaying list of stations
    transfers = created_path.transfers

    print(f'\nOrigin Station: {user_origin} | Line: {created_path.path[0].line_id}')
    print('\nMiddle Stations:')

    for node in created_path.path:
        print(f'{node.node_id}', end='')
        transfer = transfers[0] if transfers else None
        if transfer and node.node_id == transfer.node_id:
            print(f'    [{transfer.from_line} > {transfer.to_line}]')
            transfers.pop(0)
        else:
            print()
    
    print(f'\nDestination Station: {created_path.path[-1].node_id} | Line: {created_path.path[-1].line_id}')
