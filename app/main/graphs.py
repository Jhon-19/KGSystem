from flask import g, Response, request
from app import graph
from . import main
from json import dumps


@main.route('/graph')
def get_graph():
    find_all = "MATCH (p: Person)-[:ACTED_IN]->(m: Movie) " \
               "RETURN collect(p.name) AS actors, m.title AS movie " \
               "LIMIT 2"
    results = graph.run(find_all).data()

    nodes = []
    links = []
    i = 0
    for record in results:
        nodes.append({"title": record["movie"], "label": "Movie"})
        target = i
        i += 1
        for name in record["actors"]:
            actor = {"title": name, "label": "Person"}
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
    pass


