import json
from node import Line, LineId, Node, NodeId, Connection
from typing import Dict


def load_json(file_name: str) -> Dict[LineId,Line]:
    with open(file_name, 'r') as f:
        line_dict: Dict[LineId,Line] = json.load(f)
        return line_dict


def line_dict_to_node_dict(line_dict: Dict[LineId, Line]) -> Dict[NodeId, Node]:
    node_dict: Dict[NodeId, Node] = {}
    nodes = set()
    line_ids = line_dict.keys()
    lines = line_dict.values()
    # create a set of all nodes
    for line in lines:
        nodes.update(line)
    ''' iterate through each node, finding its location in every line
      then creating a connection with the node before and after it in the list '''
    #iterate through each node
    for node in nodes:
        connection_list = []
        #iterate through each line
        for line_id in line_ids:
            #find the current node in the line (if present)
            for i in range(len(line_dict[line_id])):
                if line_dict[line_id][i] == node:
                    #create a connection with the node before & after in the list (checking if node is start/end of line)
                    if i == 0:
                        connection_list.append(Connection(line_dict[line_id][i+1], line_id))
                    elif i == len(line_dict[line_id])-1:
                        connection_list.append(Connection(line_dict[line_id][i-1], line_id))
                    else:
                        connection_list.append(Connection(line_dict[line_id][i-1], line_id))
                        connection_list.append(Connection(line_dict[line_id][i+1], line_id))
        node_dict[node] = Node(node, connection_list)
    return node_dict