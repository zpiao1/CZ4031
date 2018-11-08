def init():
    global NODE_TYPES
    global KEY_PROPERTY

    '''
    Only consider following nodes so far, full list of nodes please consult source code 
    https://github.com/postgres/postgres/blob/master/src/backend/commands/explain.c#L814
    '''
    NODE_TYPES = ['LIMIT', 'SORT', 'NESTED LOOP', 'MERGE JOIN', 'HASH', 'HASH JOIN', 'AGGREGATE', 'HASHAGGREGATE',
                  'SEQ SCAN', 'INDEX SCAN', 'INDEX ONLY SCAN', 'BITMAP HEAP SCAN', 'BITMAP INDEX SCAN', 'CTE SCAN']

    '''
    Key attribute in a node that will help to identify which SQL query correspond to this node
    '''
    KEY_PROPERTY = {'LIMIT': 'Plan Rows', 'SORT': 'Sort Key', 'NESTED LOOP': None, 'MERGE JOIN': 'Merge Cond',
                    'HASH': None, 'HASH JOIN': 'Hash Cond', 'AGGREGATE': 'Group Key', 'HASHAGGREGATE': 'Group Key',
                    'SEQ SCAN': 'Relation Name', 'INDEX SCAN': 'Index Cond', 'INDEX ONLY SCAN': 'Index Cond',
                    'BITMAP HEAP SCAN': 'Recheck Cond', 'BITMAP INDEX SCAN': 'Index Cond', 'CTE SCAN': 'Index Cond'}

    '''
    Possible keywords that indicate a new operation
    '''
    PREFIX_KEYWORD = ['SELECT', '(SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'GROUP BY', 'HAVING', 'INNER JOIN',
                      'LEFT OUTER JOIN', 'RIGHT OUTER JOIN', 'FULL OUTER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN',
                      'JOIN', 'LIMIT', 'OFFSET']