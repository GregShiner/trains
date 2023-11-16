from parser import load_json, line_dict_to_node_dict

LIST_DICT = load_json("data.json")

NODE_DICT = line_dict_to_node_dict(LIST_DICT)

print(NODE_DICT)