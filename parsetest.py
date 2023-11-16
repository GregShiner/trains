from parser import loadJson, lineDictToNodeDict

LIST_DICT = loadJson("data.json")

NODE_DICT = lineDictToNodeDict(LIST_DICT)

print(NODE_DICT)