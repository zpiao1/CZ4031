import os
import json
import node_types
from pglast import Node, parse_sql, prettify
from anytree import AnyNode, RenderTree
import sqlparse


def main():
    node_types.init()

    plan_path = './sample.json'
    query_path = './sample4a.sql'

    # plan_path = str(input("Query Plan (in JSON) path: "))
    # query_path = str(input("SQL query path: "))

    plan_file = open(plan_path, 'r')
    plan_json = json.loads(plan_file.read())

    query_file = open(query_path, 'r')
    query_text = query_file.read()

    #root = build_tree([plan_json[0]["Plan"]])[0]
    #print(RenderTree(root))
    query_string = query_text.replace('\n', ' ')
    print(sqlparse.format(query_string, reindent=True, keyword_case='upper'))
    #root = Node(parse_sql(query_string))
    #print(root)
    # for node in root.traverse():
    #     print(node)
    relation = {}


def build_tree(plans_list, parent=None):
    result_list = []
    for plan in plans_list:
        node_type = plan["Node Type"].upper()
        if parent is None:
            node = AnyNode(id=node_type)
        else:
            node = AnyNode(id=node_type, parent=parent)

        if node_type in node_types.KEY_PROPERTY:
            key_property = node_types.KEY_PROPERTY[node_type]
            if key_property in plan:
                setattr(node, key_property, plan[key_property])
        if "Output" in plan:
            setattr(node, "Output", plan["Output"])
        if "Plans" in plan:
            setattr(node, "Plans", build_tree(plan["Plans"], node))
        if "Filter" in plan:
            setattr(node, "Filter", plan["Filter"])
        if "Partial Mode" in plan:
            setattr(node, "Partial Mode", plan["Partial Mode"])
        if "Index Name" in plan:
            setattr(node, "Index Name", plan["Index Name"])
        if "Relation Name" in plan:
            setattr(node, "Relation Name", plan["Relation Name"])
        if "Alias" in plan:
            setattr(node, "Alias", plan["Alias"])
        #setattr(node, "Data", plan)
        result_list.append(node)
    return result_list


'''
Build relation between plan and query by running BFS on plan tree
'''
def build_relation(plan, query):
    return


if __name__ == "__main__": main()