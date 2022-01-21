from app import graph
from json import dumps, loads
from ..models import UserNodeChange, UserLinkChange
from flask_login import current_user

# 用来防止添加重复的节点
# 边和节点的id不一样
node_id_list = []
link_id_list = []
user_node_id_list = []
user_link_id_list = []

def clear_id_list():
    global node_id_list, link_id_list, user_node_id_list, user_link_id_list
    node_id_list = []
    link_id_list = []
    user_node_id_list = []
    user_link_id_list = []

def add_node_title(record_node):
    title = ''
    if 'title' in record_node:
        title = record_node['title']
    elif 'name' in record_node:
        title = record_node['name']
    return title

def query_by_neo_id(neo_id):
    find_node = 'MATCH (n)-[rel]-(m) ' \
                'WHERE ID(n) = %s ' \
                'RETURN ID(n) AS target_node_ID, ' \
                'n AS target_node, ' \
                'LABELS(n) AS target_node_label , ' \
                'ID(rel) AS link_ID, TYPE(rel) AS link, ' \
                'ID(m) AS neighbor_ID, m AS neighbor, ' \
                'LABELS(m) AS neighbor_label, ' \
                'ID(STARTNODE(rel)) AS start_node_ID, ' \
                'ID(ENDNODE(rel)) AS end_node_ID' \
                % neo_id
    results = graph.run(find_node).data()

    # print(dumps(results[0]))

    results_json = loads(dumps(results))

    node_list = []
    link_list = []

    for record in results_json:
        id1 = record['target_node_ID']
        if id1 not in node_id_list:
            node1 = {
            'ID': id1,
            'Label': record['target_node_label'],
            'title': add_node_title(record['target_node'])
            }
            node_id_list.append(id1)
            node_list.append(node1)

        id2 = record['neighbor_ID']
        if id2 not in node_id_list:
            node2 = {
                'ID': id2,
                'Label': record['neighbor_label'],
                'title': add_node_title(record['neighbor'])
            }
            node_id_list.append(id2)
            node_list.append(node2)

        id_link = record['link_ID']
        if id_link not in link_id_list:
            link = {
                'ID': id_link,
                'Type': record['link'],
                'source': record['start_node_ID'],  #d3.js中的id默认为节点数组中的下标
                'target': record['end_node_ID']
            }
            link_id_list.append(id_link)
            link_list.append(link)
    return dumps({'nodes': node_list, 'links': link_list})

def query_by_user_id(user_id):
    username = current_user.username
    node_change_list = UserNodeChange.query.filter_by(username=username).all()
    link_change_list = UserLinkChange.query.filter_by(username=username).all()

    node_result_list = []
    link_result_list = []
    for change in node_change_list:
        if change.neo_id == user_id:
            node_result_list.append(change)
    for change in link_change_list:
        if change.start_node == user_id or change.end_node == user_id:
            link_result_list.append(change)

    node_list = []
    link_list = []

    if user_id not in user_node_id_list:
        query_one_by_user_id(user_id, node_result_list, node_list)

    start_end_node_list = []
    for change in link_result_list:
        neo_id = change.neo_id
        if neo_id not in user_link_id_list:
            user_link_id_list.append(neo_id)
            start_node = change.start_node
            end_node = change.end_node
            link = {
                'ID': neo_id,
                'Type': find_link_type(neo_id, link_result_list),
                'source': start_node,
                'target': end_node
            }
            start_end_node_list.extend([start_node, end_node])
            link_list.append(link)

    for node_id in start_end_node_list:
        if node_id < 0:
            if node_id not in user_node_id_list:
                query_one_by_user_id(user_id, node_result_list, node_list)
        else:
            if node_id not in node_id_list:
                node = query_one_by_neo_id(node_id)
                node_id_list.append(node_id)
                node_list.append(node)

    return dumps({'nodes': node_list, 'links': link_list})

def query_by_node_name(node_name):
    find_node = 'MATCH (n)-[rel]-(m) ' \
                'WHERE n.name = "%s" OR n.title = "%s" ' \
                'RETURN ID(n) AS target_node_ID, ' \
                'n AS target_node, ' \
                'LABELS(n) AS target_node_label , ' \
                'ID(rel) AS link_ID, TYPE(rel) AS link, ' \
                'ID(m) AS neighbor_ID, m AS neighbor, ' \
                'LABELS(m) AS neighbor_label, ' \
                'ID(STARTNODE(rel)) AS start_node_ID, ' \
                'ID(ENDNODE(rel)) AS end_node_ID' \
                % (node_name, node_name)
    results = graph.run(find_node).data()

    # print(dumps(results[0]))

    results_json = loads(dumps(results))

    node_list = []
    link_list = []

    for record in results_json:
        id1 = record['target_node_ID']
        if id1 not in node_id_list:
            node1 = {
                'ID': id1,
                'Label': record['target_node_label'],
                'title': add_node_title(record['target_node'])
            }
            node_id_list.append(id1)
            node_list.append(node1)

        id2 = record['neighbor_ID']
        if id2 not in node_id_list:
            node2 = {
                'ID': id2,
                'Label': record['neighbor_label'],
                'title': add_node_title(record['neighbor'])
            }
            node_id_list.append(id2)
            node_list.append(node2)

        id_link = record['link_ID']
        if id_link not in link_id_list:
            link = {
                'ID': id_link,
                'Type': record['link'],
                'source': record['start_node_ID'],  # d3.js中的id默认为节点数组中的下标
                'target': record['end_node_ID']
            }
            link_id_list.append(id_link)
            link_list.append(link)
    return dumps({'nodes': node_list, 'links': link_list})

def query_one_by_user_id(user_id, node_result_list, node_list):
    node = {
        'ID': user_id,
        'Label': [],
        'title': ''
    }
    for change in node_result_list:
        if change.property == 'Label':
            node['Label'].append(change.property_value)
        elif change.property == 'title':
            node['title'] = change.property_value
    if len(node['Label']) == 0:
        node['Label'] = ''

    node_list.append(node)
    user_node_id_list.append(user_id)

def query_one_by_neo_id(neo_id):
    find_one_node = 'MATCH (n) WHERE ID(n) = %s ' \
                    'RETURN ID(n) AS target_node_ID,' \
                    ' n AS target_node, LABELS(n) AS target_node_label'\
                    %neo_id
    results = graph.run(find_one_node).data()

    # print(dumps(results[0]))

    results_json = loads(dumps(results[0]))

    target_node = {
        'ID': results_json['target_node_ID'],
        'Label': results_json['target_node_label'],
        'title': add_node_title(results_json)
    }

    return target_node



def find_link_type(target_id, link_result_list):
    type_list = []
    for change in link_result_list:
        neo_id = change.neo_id
        if neo_id == target_id and change.property == 'Type':
            type_list.append(change.property_value)
    if len(type_list) == 0:
        type_list = ''
    return type_list


def is_node_in_list(target_node_id, id_list):
    if target_node_id in id_list:
        return True
