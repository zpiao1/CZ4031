import json
import re
import node_types
from anytree import AnyNode, RenderTree, PreOrderIter
import sqlparse


def main():
    node_types.init()

    plan_path = './samplebig.json'
    query_path = './samplebig_q.sql'

    # plan_path = str(input("Query Plan (in JSON) path: "))
    # query_path = str(input("SQL query path: "))

    plan_file = open(plan_path, 'r')
    plan_json = json.loads(plan_file.read())

    query_file = open(query_path, 'r')
    query_text = query_file.read()

    root = build_tree([plan_json[0]["Plan"]])[0]
    print(RenderTree(root))
    query_string = query_text.replace('\n', ' ')
    query_formatted = sqlparse.format(query_string, reindent=True, keyword_case='upper')
    print(query_formatted)

    match_dict = build_relation(query_formatted, root)
    print(match_dict)

    # Pretty printing match_dict
    for key, value in match_dict.items():
        start = key
        end = key
        while query_formatted[end] not in ' ()\n,' and end < len(str(query_formatted))-1:
            end += 1

        print('=====================')
        print('Token - ' + query_formatted[start:end])
        print('Nodes - ' + str(value))


'''
Build tree recursively, Some operations are commented out for making result looks clearer while testing.
Currently using Node Type as node id and it is not unique. If needed can use a unique identifier for id.
'''
def build_tree(plans_list, parent=None):
    result_list = []
    for plan in plans_list:
        node_type = plan["Node Type"].upper()
        if parent is None:
            node = AnyNode(id=node_type, node_type=node_type)
        else:
            node = AnyNode(id=node_type, node_type=node_type, parent=parent)

        # Setting the key attributes that are going to be used for searching later
        if node_type in node_types.KEY_PROPERTY:
            key_properties = node_types.KEY_PROPERTY[node_type]
            for key_property in key_properties:
                if key_property in plan:
                    setattr(node, key_property, plan[key_property])

        # if "Output" in plan:
        #     setattr(node, "Output", plan["Output"])
        if "Plans" in plan:
            # Build sub tree
            build_tree(plan["Plans"], node)
            # setattr(node, "Plans", build_tree(plan["Plans"], node))
        if "Partial Mode" in plan:
            setattr(node, "Partial Mode", plan["Partial Mode"])
        if "Index Name" in plan:
            setattr(node, "Index Name", plan["Index Name"])
        #setattr(node, "Data", plan)
        result_list.append(node)
    return result_list


'''
Build relation between plan and query by iterating the tree
'''
def build_relation(query_formatted, tree):
    match_dict = {}   # {index of token: [list of matched nodes]}
    lines = query_formatted.splitlines()    # Process query line by line
    processed_lines_len = 0
    for i in range(len(lines)):
        if i > 0:
            # +1 because of newline character has length 1
            processed_lines_len += len(lines[i-1]) + 1

        tokenized_line = re.split(' |\(|\)|,', lines[i])
        print('tokenized line: ' + str(tokenized_line))
        for token in tokenized_line:
            #token = token.strip(' ,()')
            if token.upper() is not '' and token.upper() not in node_types.KEYWORDS:
                index_in_query = lines[i].index(token) + processed_lines_len
                match_dict[index_in_query] = search_tree(token, tree)

    return match_dict


'''
Do the search by using built-in pre-order iteration
Return a list of matched nodes or None if no node matched
'''
def search_tree(token, root):
    matched_pos = []
    for node in PreOrderIter(root):
        # If a node is not defined in our searchable list, skip it
        if getattr(node, 'id') not in node_types.KEY_PROPERTY:
            continue
        else:
            for field in node_types.KEY_PROPERTY[getattr(node, 'id')]:
                if not hasattr(node, field):
                    continue
                value = getattr(node, field)
                if token in str(value):
                    matched_pos.append(node)

    if len(matched_pos) == 0:
        return None
    else:
        return matched_pos


if __name__ == "__main__": main()