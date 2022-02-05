from app import graph
from json import dumps, loads
from ..models import Node, Link, UserNodeAdd, UserLinkAdd
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


def format_node_adds(node_adds):
    node_list = []
    format_node_add_list(node_adds, node_list)
    return dumps(node_list)


def format_link_adds(link_adds):
    link_list = []
    for link_add in link_adds:
        current_id = link_add.user_link_id
        if is_link_available(link_add):
            link = Link(
                current_id,
                link_add.Type,
                link_add.start_node,
                link_add.end_node,
                link_list
            ).get_dict()
            link_list.append(link)
            user_link_id_list.append(current_id)

    return dumps(link_list)


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
            node1 = Node(
                id1,
                record['target_node_label'],
                record_node=record['target_node']
            ).get_dict()
            node_id_list.append(id1)
            node_list.append(node1)

        id2 = record['neighbor_ID']
        if id2 not in node_id_list:
            node2 = Node(
                id2,
                record['neighbor_label'],
                record_node=record['neighbor']
            ).get_dict()
            node_id_list.append(id2)
            node_list.append(node2)

        id_link = record['link_ID']
        if id_link not in link_id_list:
            link = Link(
                id_link,
                record['link'],
                record['start_node_ID'],  # d3.js中的id默认为节点数组中的下标
                record['end_node_ID'],
                link_list
            ).get_dict()
            link_id_list.append(id_link)
            link_list.append(link)

    return dumps({'nodes': node_list, 'links': link_list})


def query_by_user_id(user_id):
    node_list = []
    link_list = []

    query_user_nodes_links(node_list, link_list, node_id=user_id)

    return dumps({'nodes': node_list, 'links': link_list})


def query_by_node_name(node_name):
    node_list = []
    link_list = []
    # 查询用户数据库
    query_user_nodes_links(node_list, link_list, node_name=node_name)

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

    for record in results_json:
        id1 = record['target_node_ID']
        if id1 not in node_id_list:
            node1 = Node(
                id1,
                record['target_node_label'],
                record_node=record['target_node']
            ).get_dict()
            node_id_list.append(id1)
            node_list.append(node1)

        id2 = record['neighbor_ID']
        if id2 not in node_id_list:
            node2 = Node(
                id2,
                record['neighbor_label'],
                record_node=record['neighbor']
            ).get_dict()
            node_id_list.append(id2)
            node_list.append(node2)

        id_link = record['link_ID']
        if id_link not in link_id_list:
            link = Link(
                id_link,
                record['link'],
                record['start_node_ID'],
                record['end_node_ID'],
                link_list
            ).get_dict()
            link_id_list.append(id_link)
            link_list.append(link)
    return dumps({'nodes': node_list, 'links': link_list})

def query_one_by_neo_id(neo_id):
    find_one_node = 'MATCH (n) WHERE ID(n) = %s ' \
                    'RETURN ID(n) AS target_node_ID,' \
                    ' n AS target_node, LABELS(n) AS target_node_label' \
                    % neo_id
    results = graph.run(find_one_node).data()

    # print(dumps(results[0]))

    results_json = loads(dumps(results[0]))

    target_node = Node(
        results_json['target_node_ID'],
        results_json['target_node_label'],
        record_node=results_json['target_node']
    ).get_dict()

    return target_node

def query_user_nodes_links(node_list, link_list, node_name=None, node_id=None):
    # 查询用户数据库
    user_nodes = []
    if node_name != None:
        user_nodes = find_user_node_by_name(node_name)
    elif node_id != None:
        user_nodes = find_user_node_by_id(node_id)

    user_links = UserLinkAdd.query.filter_by(
        username=current_user.username,
    ).all()

    format_node_add_list(user_nodes, node_list) #整理成dict列表的形式(类似于json数组)

    if len(node_list) == 0:
        return

    target_node_id = node_list[0]['ID']

    for user_link in user_links:
        current_id = user_link.user_link_id
        if is_related_link(user_link, target_node_id):
            link = Link(
                current_id,
                user_link.Type,
                user_link.start_node,
                user_link.end_node,
                link_list
            ).get_dict()
            link_id_list.append(current_id)
            link_list.append(link)

            if user_link.start_node == target_node_id:
                current_node_id = user_link.end_node
            else:
                current_node_id = user_link.start_node

            if int(current_node_id) >= 0 and current_node_id not in node_id_list:
                node_list.append(query_one_by_neo_id(current_node_id))
                node_id_list.append(current_node_id)
            elif int(current_node_id) < 0 and current_node_id not in user_node_id_list:
                format_node_add_list(find_user_node_by_id(current_node_id), node_list)


def format_node_add_list(user_nodes, node_list):
    for user_node in user_nodes:
        current_id = user_node.user_node_id
        if current_id not in user_node_id_list:
            node = Node(
                current_id,
                [user_node.Label],
                title=user_node.title
            ).get_dict()
            user_node_id_list.append(current_id)
            node_list.append(node)


def find_user_link_by_id(link_id):
    return UserLinkAdd.query.filter_by(
        username=current_user.username,
        user_link_id=link_id
    ).all()


def find_user_node_by_id(node_id):
    return UserNodeAdd.query.filter_by(
        username=current_user.username,
        user_node_id=int(node_id)
    ).all()


def find_user_node_by_name(node_name):
    return UserNodeAdd.query.filter_by(
        username=current_user.username,
        title=node_name
    ).all()


def is_related_link(user_link, target_node_id):
    return (user_link.user_link_id not in user_link_id_list) and \
           (user_link.start_node == target_node_id or
            user_link.end_node == target_node_id)


def is_link_available(link):
    return (link.user_link_id not in user_link_id_list) and \
           (link.start_node in user_node_id_list
            and link.end_node in user_node_id_list) or \
           (link.start_node in user_node_id_list
            and link.end_node in node_id_list) or \
           (link.start_node in node_id_list
            and link.end_node in user_node_id_list) or \
           (link.start_node in node_id_list
            and link.end_node in node_id_list)


def is_node_in_list(target_node_id, id_list):
    if target_node_id in id_list:
        return True
