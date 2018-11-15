import json
import re
import node_types
import copy
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
        start = key[0]
        end = key[1]
        print('=====================')
        print('Token - ' + query_formatted[start:end])
        print('Nodes - ' + str(value))

    match_dict = build_invert_relation(query_formatted, root)
    for key, value in match_dict.items():
        print('+++++++++++++++++++++')
        print('Node = ' + str(key))
        for pos in value:
            start = pos[0]
            end = pos[1]
            print('tokens - ' + query_formatted[start:end] + '@' + str(start) + ':' + str(end))


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
        raw_json = copy.deepcopy(plan)
        if "Plans" in plan:
            build_tree(plan["Plans"], node)  # Build sub tree
            raw_json.pop("Plans")   # Don't put the entire subtree in the raw json
        if "Partial Mode" in plan:
            setattr(node, "Partial Mode", plan["Partial Mode"])
        if "Index Name" in plan:
            setattr(node, "Index Name", plan["Index Name"])
        setattr(node, "raw_json", raw_json)
        result_list.append(node)
    return result_list


'''
Build relation between plan and query by iterating the tree
Match a given token to all nodes that contain this token
'''
def build_relation(query_formatted, tree):
    match_dict = {}   # {(start index of token, end): [list of matched nodes]}
    tokens = tokenize_query(query_formatted)
    for token, position in tokens.items():
        match_dict[(position[0], position[1])] = search_tree(token, tree)

    return match_dict


'''
Build relation between plan and query by iterating the tree
Match a given node to all tokens that correlate
'''
def build_invert_relation(query_formatted, tree):
    match_dict = {}  # Has structure {node object : [list of tuples of index]}
    tokens = tokenize_query(query_formatted)
    for node in PreOrderIter(tree):
        if getattr(node, 'id') not in node_types.KEY_PROPERTY:
            continue
        else:
            for field in node_types.KEY_PROPERTY[getattr(node, 'id')]:
                if not hasattr(node, field):
                    continue
                value = getattr(node, field)
                matched_pos = search_query(value, tokens, query_formatted)
                if matched_pos is not None:
                    if node in match_dict:
                        match_dict[node] = match_dict[node] + matched_pos
                    else:
                        match_dict[node] = matched_pos
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


'''
Do full text search on query
Return a list of index tuple of matched query tokens or None if no token matched
'''
def search_query(value, tokens, query_formatted):
    matched_pos = []
    if isinstance(value, list):
        for v in value:
            regex_matches = re.finditer(v, query_formatted)
            for match in regex_matches:
                matched_pos.append((match.start(), match.end()))
    else:
        regex_matches = re.finditer(str(value).strip('()'), query_formatted)
        for match in regex_matches:
            matched_pos.append((match.start(), match.end()))

    # for token, position in tokens.items():  # position is a tuple of (start idx, end idx)
    #
    #     # Assume value can be either a list of string or a string. Could it also be dict?
    #     if isinstance(value, list):  # value is a list of string
    #         for v in value:
    #             if token in v:
    #                 matched_pos.append(position)
    #                 break
    #     else:  # value is string
    #         if token in str(value):
    #             matched_pos.append(position)

    if len(matched_pos) == 0:
        return None
    else:
        return matched_pos


'''
Tokenize query, return a dictionary with structure {token: (start index in query, end index..)}
No keyword included in the result
'''
def tokenize_query(query_formatted):
    tokens = {}
    lines = query_formatted.splitlines()  # Process query line by line
    processed_lines_len = 0
    for i in range(len(lines)):
        if i > 0:
            # +1 because of newline character has length 1
            processed_lines_len += len(lines[i - 1]) + 1

        tokenized_line = re.split(' |\(|\)|,', lines[i])
        print('tokenized line: ' + str(tokenized_line))
        for token in tokenized_line:
            token = token.strip(';')
            if token.upper() is not '' and token.upper() not in node_types.KEYWORDS:
                regex_matches = re.finditer(r'( |\(|,)'+token+'($| |\)|,)', lines[i])
                for matched in regex_matches:
                    tokens[token] = (matched.start() + processed_lines_len, matched.end() + processed_lines_len)
                    print('appending token: ' + token + ', pos: ' + str(tokens[token]))
                #index_in_query = lines[i].index(token) + processed_lines_len
                #tokens[token] = (index_in_query, index_in_query+len(token))

    print('Tokens:' + str(tokens))
    return tokens


if __name__ == "__main__": main()