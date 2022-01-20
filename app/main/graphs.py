from flask import g, Response, request
from app import graph
from . import main
from json import dumps, loads
from .. import db
from ..models import UserChange
from flask_login import current_user
from datetime import datetime
import math

@main.route('/graph')
def get_graph():
    find_all = "MATCH (p: Person)-[:ACTED_IN]->(m: Movie) " \
               "RETURN collect(p.name) AS actors," \
               " m.title AS movie, collect(ID(p)) AS actorsID, ID(m) as movieID " \
               "LIMIT 2"
    results = graph.run(find_all).data()

    nodes = []
    links = []
    i = 0
    for record in results:
        movie = {"title": record["movie"], "label": "Movie", "ID": record["movieID"]}
        nodes.append(movie)
        target = i
        i += 1
        for name in record["actors"]:
            index = record["actors"].index(name)
            actor = {"title": name, "label": "Person", "ID": record["actorsID"][index]}
            try:
                source = nodes.index(actor)
            except ValueError:
                nodes.append(actor)
                source = i
                i += 1
            links.append({"source": source, "target": target})
    return Response(dumps({"nodes": nodes, "links": links}),
                    mimetype="application/json")


@main.route("/search")
def get_search():
    neo_id = request.args.get("neo_id", "0")
    find_id = "MATCH (n) "\
              "WHERE ID(n) = %s "\
              "RETURN ID(n) as n_ID, " \
              "properties(n) as n_properties, LABELS(n) as n_labels"\
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
    time = math.floor(datetime.now().timestamp()*1000)

    change = UserChange(
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

    changes = UserChange.query.filter_by(username=username).all()

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




