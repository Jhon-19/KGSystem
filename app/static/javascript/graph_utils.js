//绘图及显示属性
const width = 800;
const height = 500;

var old_select_index = -1; //已选择的节点

var is_cleared = true; //记录是否清空了图谱

var svg = d3.select("#graph").append("svg")
    .attr("width", width).attr("height", height);

var g_root = svg.append("g").attr('id', 'g_root');
var forceSimulation;

define_arrow();

function draw_graph(g_nodes0, g_links0) {
    //创造副本，d3.js会修改原来的数组
    var g_nodes = g_nodes0.map(d => Object.create(d));
    var g_links = g_links0.map(d => Object.create(d));

    forceSimulation = d3.forceSimulation(g_nodes)
        .force("charge", d3.forceManyBody().strength(-6))
        .force("link", d3.forceLink(g_links).id(d => d.ID))
        .force("center", d3.forceCenter())
        .force("collide", d3.forceCollide().radius(12))
        .alphaTarget(0.8);

    forceSimulation.nodes(g_nodes)
        .on("tick", ticked);
    forceSimulation.force("link")
        .links(g_links)
        .distance(200);

    forceSimulation.force("center")
        .x(width / 2)
        .y(height / 2);

    var links = g_root.append("g")
        .attr('id', 'links')
        .selectAll(".link")
        .data(g_links)
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("marker-end", "url(#marker)")
        .on("click", clicked_link);

    var linksText = g_root.append("g")
        .attr('id', 'links_text')
        .selectAll(".link_text")
        .data(g_links)
        .enter()
        .append("text")
        .text(function (d) {
            return d.Type;
        })
        .attr("class", "link_text");

    var nodes = g_root.append("g")
        .attr('id', 'nodes')
        .selectAll(".node")
        .data(g_nodes)
        .enter()
        .append("circle")
        .attr("class", function (d) {
            return "node " + d.Label[0].toLowerCase();
        })
        .attr("r", 10)
        .call(d3.drag()
            .on("start", started)
            .on("drag", dragged)
            .on("end", ended)
        )
        .on("click", clicked_node);

    var nodesText = g_root.append("g")
        .attr('id', 'nodes_text')
        .selectAll(".node_text")
        .data(g_nodes)
        .enter()
        .append("text")
        .text(function (d) {
            return d.title;
        })
        .attr("class", "node_text");


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
            forceSimulation.alphaTarget(0.8).restart();
        }
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function ended(d) {
        if (!d3.event.activate) {
            forceSimulation.alphaTarget(0);
        }
        // d.fx = null;
        // d.fy = null;
    }

    //加载用户更改
    show_user_changes()
}

function update_graph(g_nodes0, g_links0) {
    //创造副本，d3.js会修改原来的数组
    var g_nodes = g_nodes0.map(d => Object.create(d));
    var g_links = g_links0.map(d => Object.create(d));

    forceSimulation.alphaTarget(0.8).restart()

    forceSimulation.nodes(g_nodes)
        .on("tick", ticked);
    forceSimulation.force("link")
        .links(g_links)
        .distance(200);

    forceSimulation.force("center")
        .x(width / 2)
        .y(height / 2);


    var update_links = g_root.select('#links')
        .selectAll(".link")
        .data(g_links);

    var links = update_links.enter()
        .append("line")
        .merge(update_links)
        .attr("class", "link")
        .attr("marker-end", "url(#marker)")
        .on("click", clicked_link);

    var update_links_text = g_root.select('#links_text')
        .selectAll(".link_text")
        .data(g_links);

    var linksText = update_links_text.enter()
        .append("text")
        .merge(update_links_text)
        .text(function (d) {
            return d.Type;
        })
        .attr("class", "link_text");

    var update_nodes = g_root.select('#nodes')
        .selectAll(".node")
        .data(g_nodes);

    var nodes = update_nodes.enter()
        .append("circle")
        .merge(update_nodes)
        .attr("class", function (d) {
            return "node " + d.Label[0].toLowerCase();
        })
        .attr("r", 10)
        .call(d3.drag()
            .on("start", started)
            .on("drag", dragged)
            .on("end", ended)
        )
        .on("click", clicked_node);

    var update_nodes_text = g_root.select('#nodes_text')
        .selectAll(".node_text")
        .data(g_nodes);

    var nodesText = update_nodes_text.enter()
        .append("text")
        .merge(update_nodes_text)
        .text(function (d) {
            return d.title;
        })
        .attr("class", "node_text");

    if (old_select_index >= 0) {
        graph_nodes.eq(old_select_index).addClass('selected')
    }

    // console.log(g_nodes);

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
            forceSimulation.alphaTarget(0.8).restart();
        }
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx = d3.event.x;
        d.fy = d3.event.y;
    }

    function ended(d) {
        if (!d3.event.activate) {
            forceSimulation.alphaTarget(0);
        }
        //d.fx不为null则
        // d.fx = null;
        // d.fy = null;
    }

    //加载用户更改
    show_user_changes()
}

function define_arrow() {
    //定义箭头
    svg.append("svg:defs")
        .append("svg:marker")
        .attr("id", "marker")
        .attr('viewBox', '0 -5 10 10')
        .attr("refX", 16)
        .attr("refY", 0)
        .attr('markerWidth', 3)
        .attr('markerHeight', 3)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr("fill", "gray");
}

function clicked_link(d) {
    console.log('clicked');
}


function clicked_node(d, i) {
    // alert(d.ID);
    neo_id = d.ID;
    graph_nodes = $('.node');
    if (old_select_index >= 0) {
        graph_nodes.eq(old_select_index).removeClass('selected')
    }
    old_select_index = i;
    graph_nodes.eq(i).addClass('selected');

    $.ajax({
        url: "/search_node_details",
        data: {"neo_id": neo_id},
        success: result => {
            // console.log(result);

            if (neo_id === result.n_ID) {
                $('#neo_id').text(neo_id);
                $('#neo_label').text(result.n_labels.join(', '))

                var details_table = $('#details_table');
                details_table.empty();
                thead = '<tr><td class="column_1">属性</td><td>属性值</td></tr>';
                details_table.append(thead);
                properties = result.n_properties;
                for (key in properties) {
                    add_details_item(key, properties[key]);
                }

                show_user_changes()
                show_changes_in_tables()

                var node_name = '';
                if (properties['name'] != null) {
                    node_name = 'name: ' + properties['name'];
                } else if (properties['title'] != null) {
                    node_name = 'title: ' + properties['title'];
                }
                $('#query_node_name').val(node_name);

            } else {
                console.log("error!")
            }
        }
    })
}

//清空图形
function bind_clear_graph() {
    $('#clear_graph').click(function () {
        //重置清除标志和选择标志
        is_cleared = true;
        old_select_index = -1;

        g_nodes0 = [];
        g_links0 = [];
        d3.selectAll('#g_root >*').remove();
        //后端清除id
        $.ajax({
            url: '/user/clear_graph',
            type: 'GET',
            success: result => {
                console.log(result)
            }
        })
    });
}