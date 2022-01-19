const width = 800;
const height = 500;

var margins = {top: 0, bottom: 0, left: 0, right: 0}
var svg = d3.select("#graph").append("svg")
    .attr("width", width).attr("height", height);
var g = svg.append("g").attr("transform", "translate(" + margins.top + "," + margins.left + ")");

var data;
var link;

d3.json("/graph").then(function (graph) {
    var g_nodes = graph.nodes;
    var g_links = graph.links;

    data = g_nodes;
    link = g_links;

    var forceSimulation = d3.forceSimulation(g_nodes)
        .force("charge", d3.forceManyBody())
        .force("link", d3.forceLink(g_links))
        .force("center", d3.forceCenter());

    forceSimulation.nodes(g_nodes)
        .on("tick", ticked);
    forceSimulation.force("link")
        .links(g_links)
        .distance(200);

    forceSimulation.force("center")
        .x(width / 2)
        .y(height / 2);

    //define arrow
    svg.append("svg:defs")
        .append("svg:marker")
        .attr("id", "marker")
        .attr('viewBox', '0 -5 10 10')
        .attr("refX", 20)
        .attr("refY", 0)
        .attr('markerWidth', 10)
        .attr('markerHeight', 10)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr("fill", "gray");

    var links = g.append("g")
        .selectAll(".link")
        .data(g_links)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("marker-end", "url(#marker)");

    var linksText = g.append("g")
        .selectAll("text")
        .data(g_links)
        .enter()
        .append("text")
        .text("ACTED_IN")
        .attr("class", "text");

    var nodes = g.append("g")
        .selectAll(".node")
        .data(g_nodes)
        .enter()
        .append("circle")
        .attr("class", function (d) {
            return "node " + d.label.toLowerCase();
        })
        .attr("r", 10)
        .call(d3.drag()
            .on("start", started)
            .on("drag", dragged)
            .on("end", ended)
        );

    var nodesText = g.append("g")
        .selectAll("text")
        .data(g_nodes)
        .enter()
        .append("text")
        .text(function (d) {
            return d.title;
        })
        .attr("class", function (d) {
            return "text " + d.label;
        });

    function ticked() {
        links.attr("x1", function (d) {
            return d.source.x;
        }).attr("y1", function (d) {
            return d.source.y;
        }).attr("x2", function (d) {
            return d.target.x;
        }).attr("y2", function (d) {
            return d.target.y;
        });

        nodes.attr("cx", function (d) {
            return d.x;
        }).attr("cy", function (d) {
            return d.y;
        });

        linksText.attr("transform", function (d) {
            return "translate(" + (d.source.x + d.target.x) / 2 +
                "," + (d.source.y + d.target.y) / 2 + ")";
        });

        nodesText.attr("transform", function (d) {
            return "translate(" + (d.x + 10) + "," + d.y + ")";
        });
    }

    function started(d) {
        if (!d3.event.activate) {
            forceSimulation.alphaTarget(0.3).restart();
        }
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function ended(d) {
        if (d3.event.activate) {
            forceSimulation.alphaTarget(0);
        }
        d.fx = null;
        d.fy = null;
    }
})