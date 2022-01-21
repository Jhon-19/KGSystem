from flask import Response, request
from app import graph
from . import main
from json import dumps, loads
from .. import db
from ..models import UserNodeChange, UserLinkChange
from flask_login import current_user
from datetime import datetime
import math
from app.main.graph_utils import query_by_neo_id, query_by_user_id, query_by_node_name
from .graph_utils import clear_id_list

@main.route('/graph')
def get_graph():
    # find_all = "MATCH (p: Person)-[:ACTED_IN]->(m: Movie) " \
    #            "RETURN collect(p.name) AS actors," \
    #            " m.title AS movie, collect(ID(p)) AS actorsID, ID(m) as movieID " \
    #            "LIMIT 2"
    # results = graph.run(find_all).data()
    #
    # nodes = []
    # links = []
    # i = 0
    # for record in results:
    #     movie = {"title": record["movie"], "label": ["Movie"], "ID": record["movieID"]}
    #     nodes.append(movie)
    #     target = i
    #     i += 1
    #     for name in record["actors"]:
    #         index = record["actors"].index(name)
    #         actor = {"title": name, "label": ["Person"], "ID": record["actorsID"][index]}
    #         try:
    #             source = nodes.index(actor)
    #         except ValueError:
    #             nodes.append(actor)
    #             source = i
    #             i += 1
    #         links.append({"source": source, "target": target})

    # print(dumps({"nodes": nodes, "links": links}))

    return Response(query_by_neo_id(0),
                    mimetype="application/json")


@main.route("/search_node_details")
def search_node_details():
    neo_id = request.args.get("neo_id", "0")
    find_id = "MATCH (n) " \
              "WHERE ID(n) = %s " \
              "RETURN ID(n) as n_ID, " \
              "properties(n) as n_properties, LABELS(n) as n_labels" \
              % neo_id
    results = graph.run(find_id).data()

    # print(results[0])

    return Response(dumps(results[0]), mimetype="application/json")


@main.route('/user/change', methods=['POST'])
def user_change():
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


@main.route('/user/query_by_node', methods=['GET'])
def query_by_node():
    neo_id = request.args.get('neo_id', 'null')
    node_name = request.args.get('node_name', '')

    # neo_id >= 0则查询Neo4j，neo_id < 0则查询MySQL；如果neo_id为null，则按照节点名同时查询
    if neo_id == 'null':
        if len(node_name) == 0:
            return
        else:
            return Response(query_by_node_name(node_name),
                            mimetype='application/json')
    else:
        if int(neo_id) >= 0: #neo_id>0
            # print(query_by_neo_id(neo_id))
            return Response(query_by_neo_id(neo_id),
                            mimetype='application/json')
        else: #neo_id<0 查询用户修改的数据库
            return Response(query_by_user_id(neo_id),
                            mimetype='application/json')

@main.route('/user/clear_graph')
def clear_graph():
    clear_id_list()
    return 'cleared graph.'



