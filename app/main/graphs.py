from flask import Response, request
from app import graph
from . import main
from json import dumps, loads
from .. import db
from ..models import UserNodeChange, UserLinkChange, UserLinkAdd, UserNodeAdd
from flask_login import current_user
from datetime import datetime
import math
from app.main.graph_utils import query_by_neo_id, query_by_user_id, query_by_node_name
from .graph_utils import clear_id_list, format_node_adds, format_link_adds, \
    find_user_node_by_id, find_user_link_by_id


@main.route('/graph')
def get_graph():
    return Response(query_by_neo_id(0),
                    mimetype="application/json")


@main.route("/search_node_details")
def search_node_details():
    neo_id = request.args.get("neo_id", "0")
    if int(neo_id) >= 0:
        find_id = "MATCH (n) " \
                  "WHERE ID(n) = %s " \
                  "RETURN ID(n) as node_ID, " \
                  "properties(n) as node_properties, LABELS(n) as node_labels" \
                  % neo_id
        results = graph.run(find_id).data()
    else:
        nodes = find_user_node_by_id(neo_id)
        results = []
        for node in nodes:
            results.append({
                'node_ID': node.user_node_id,
                'node_properties': {'title': node.title},
                'node_labels': node.Label
            })

    # print(results[0])
    if len(results) == 0:
        results = ['not find']

    return Response(dumps(results[0]), mimetype="application/json")


@main.route("/search_link_details")
def search_link_details():
    neo_link_id = request.args.get("neo_link_id", "0")

    if int(neo_link_id) >= 0:
        find_id = 'MATCH (n)-[rel]->(m) ' \
                  'WHERE ID(rel) = %s ' \
                  'RETURN ID(rel) AS relation_ID, ' \
                  'TYPE(rel) AS relation_type, rel AS relation' \
                  % neo_link_id

        results = graph.run(find_id).data()
    else:
        links = find_user_link_by_id(neo_link_id)
        results = []
        for link in links:
            results.append({
                'relation_ID': link.user_link_id,
                'relation_type': link.Type,
                'properties': []
            })

    if len(results) == 0:
        results = ['not find']

    return Response(dumps(results[0]), mimetype="application/json")


@main.route('/user/node_change', methods=['POST'])
def user_node_change():
    data = request.form
    data_json = loads(dumps(data))

    username = current_user.username
    neo_id = data_json['neo_id']
    property = data_json['property']
    property_value = data_json['property_value']
    time = math.floor(datetime.now().timestamp() * 1000)

    change = UserNodeChange(
        username=username,
        neo_id=neo_id,
        property=property,
        property_value=property_value,
        time=time
    )
    db.session.add(change)
    db.session.commit()

    # print(data_json)
    # print(current_user.username)

    return 'Change Saved.'


@main.route('/user/link_change', methods=['POST'])
def user_link_change():
    data = request.form
    data_json = loads(dumps(data))

    username = current_user.username
    neo_link_id = data_json['neo_link_id']
    property = data_json['property']
    property_value = data_json['property_value']
    time = math.floor(datetime.now().timestamp() * 1000)

    change = UserLinkChange(
        username=username,
        neo_link_id=neo_link_id,
        time=time,
        property=property,
        property_value=property_value
    )

    db.session.add(change)
    db.session.commit()

    # print(data_json)
    # print(current_user.username)

    return 'Change Saved.'


@main.route('/user/node_add', methods=['POST'])
def user_node_add():
    data = request.form
    data_json = loads(dumps(data))

    username = current_user.username
    user_node_id = data_json['user_node_id']
    time = math.floor(datetime.now().timestamp() * 1000)
    Label = data_json['Label']
    title = data_json['title']

    node_add = UserNodeAdd(
        username=username,
        time=time,
        user_node_id=user_node_id,
        Label=Label,
        title=title
    )

    db.session.add(node_add)
    db.session.commit()

    return 'node added.'


@main.route('/user/link_add', methods=['POST'])
def user_link_add():
    data = request.form
    data_json = loads(dumps(data))

    username = current_user.username
    user_link_id = data_json['user_link_id']
    time = math.floor(datetime.now().timestamp() * 1000)
    Type = data_json['Type']
    start_node = data_json['start_node']
    end_node = data_json['end_node']

    link_add = UserLinkAdd(
        username=username,
        time=time,
        user_link_id=user_link_id,
        Type=Type,
        start_node=start_node,
        end_node=end_node
    )

    db.session.add(link_add)
    db.session.commit()

    return 'link added.'


@main.route('/user/query_node_add')
def query_node_add():
    username = current_user.username

    node_adds = UserNodeAdd.query.filter_by(username=username).all()

    return Response(format_node_adds(node_adds), mimetype='application/json')


@main.route('/user/query_link_add')
def query_link_add():
    username = current_user.username

    link_adds = UserLinkAdd.query.filter_by(username=username).all()

    return Response(format_link_adds(link_adds), mimetype='application/json')


@main.route('/user/query_changes')
def query_user_changes():
    username = current_user.username

    changes = UserNodeChange.query.filter_by(username=username).all()

    change_list = []

    for change in changes:
        change_list.append({
            'neo_id': change.neo_id,
            'property': change.property,
            'property_value': change.property_value
        })

    result = dumps(change_list)
    # print(result)

    return Response(result, mimetype='application/json')


@main.route('/user/query_link_changes')
def query_user_link_changes():
    username = current_user.username

    changes = UserLinkChange.query.filter_by(username=username).all()

    change_list = []

    for change in changes:
        link_change = {
            'neo_link_id': change.neo_link_id,
            'property': change.property,
            'property_value': change.property_value,
        }

        change_list.append(link_change)

    result = dumps(change_list)
    # print(result)

    return Response(result, mimetype='application/json')


@main.route('/user/query_by_node')
def query_by_node():
    neo_id = request.args.get('neo_id', '')
    node_name = request.args.get('node_name', '')

    # neo_id >= 0则查询Neo4j，neo_id < 0则查询MySQL；如果neo_id为null，则按照节点名同时查询
    if len(neo_id) == 0:
        if len(node_name) == 0:
            return ''
        else:
            return Response(query_by_node_name(node_name),
                            mimetype='application/json')
    else:
        if int(neo_id) >= 0:  # neo_id>0
            return Response(query_by_neo_id(neo_id),
                            mimetype='application/json')
        else:  # neo_id<0 查询用户修改的数据库
            return Response(query_by_user_id(neo_id),
                            mimetype='application/json')


@main.route('/user/clear_graph')
def clear_graph():
    clear_id_list()
    return 'cleared graph.'
