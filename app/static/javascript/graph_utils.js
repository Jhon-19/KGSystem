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

function init_force_simulation(g_nodes, g_links) {
    forceSimulation = d3.forceSimulation(g_nodes)
        .force("charge", d3.forceManyBody().strength(-6))
        .force("link", d3.forceLink(g_links).id(d => d.ID))
        .force("center", d3.forceCenter())
        .force("collide", d3.forceCollide().radius(12))
        .alphaTarget(0.8);

    forceSimulation.force("center")
        .x(width / 2)
        .y(height / 2);

    return init_g_nodes_links(g_nodes, g_links);
}

function init_g_nodes_links(g_nodes, g_links) {
    // console.log(g_nodes);
    // console.log(g_links);

    forceSimulation.nodes(g_nodes);
    forceSimulation.force("link")
        .links(g_links)
        .distance(200);
}

function add_attrs(links, links_text, nodes, nodes_text) {
    links.attr("class", "link")
        .attr("marker-end", "url(#marker)")
        .on("click", clicked_link);

    links_text.text(function (d) {
        return d.Type;
    })
        .attr("class", "link_text");

    nodes.attr("class", function (d) {
        return "node " + d.Label.toLowerCase();
    })
        .attr("r", 10)
        .call(d3.drag()
            .on("start", started)
            .on("drag", dragged)
            .on("end", ended))
        .on("click", clicked_node);

    nodes_text.text(function (d) {
        return d.title;
    })
        .attr("class", "node_text");

    forceSimulation.on('tick', ticked);

    //动态改变的属性
    function ticked() {
        links.attr("x1", function (d) {
            return d.source.x;
        }).attr("y1", function (d) {
            return d.source.y;
        }).attr("x2", function (d) {
            return d.target.x;
        }).attr("y2", function (d) {
            return d.target.y;
        }).attr('d', function (d) {
            return 'M' + d.source.x + ' ' + d.source.y + ' Q'
                + (d.source.x + d.target.x + 100 * (d.link_order - 1)) / 2 +
                ' ' + (d.source.y + d.target.y + 100 * (d.link_order - 1)) / 2
                + ', ' + d.target.x + ' ' + d.target.y;
        });

        nodes.attr("cx", function (d) {
            return d.x;
        }).attr("cy", function (d) {
            return d.y;
        });

        links_text.attr("transform", function (d) {
            return "translate(" + (d.source.x + d.target.x + 50 * (d.link_order - 1)) / 2 +
                "," + (d.source.y + d.target.y + 50 * (d.link_order - 1)) / 2 + ")";
        });

        nodes_text.attr("transform", function (d) {
            return "translate(" + (d.x + 10) + "," + d.y + ")";
        });
    }
}

async function draw_graph(g_nodes0, g_links0) {
    await query_user_adds();

    //创造副本，d3.js会修改原来的数组
    let g_nodes = g_nodes0.concat(g_nodes0_user).map(d => Object.create(d));
    let g_links = g_links0.concat(g_links0_user).map(d => Object.create(d));

    init_force_simulation(g_nodes, g_links);

    let links = g_root.append("g")
        .attr('id', 'links')
        .selectAll(".link")
        .data(g_links)
        .enter()
        .append("path");

    let links_text = g_root.append("g")
        .attr('id', 'links_text')
        .selectAll(".link_text")
        .data(g_links)
        .enter()
        .append("text");

    let nodes = g_root.append("g")
        .attr('id', 'nodes')
        .selectAll(".node")
        .data(g_nodes)
        .enter()
        .append("circle");

    let nodes_text = g_root.append("g")
        .attr('id', 'nodes_text')
        .selectAll(".node_text")
        .data(g_nodes)
        .enter()
        .append("text");

    add_attrs(links, links_text, nodes, nodes_text);

    //加载用户更改
    show_user_node_changes();
    show_user_link_changes();

    is_cleared = false; //将图谱未清除的标志置为false
}

function define_arrow() {
    //定义箭头
    svg.append("svg:defs")
        .append("svg:marker")
        .attr("id", "marker")
        .attr('viewBox', '0 0 12 12')
        .attr("refX", 13)
        .attr("refY", 6)
        .attr('markerWidth', 5)
        .attr('markerHeight', 5)
        .attr('orient', 'auto')
        .append('svg:path')
        .attr('d', 'M2,2 L10,6 L2,10 L6,6 L2,2')
        .attr("fill", "#5f00ff");

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

function clicked_link(d) {
    neo_link_id = d.ID;
    graph_links = $('.link');

    enable_buttons([0, 2]);
    is_node_selected = false;

    $.ajax({
        url: '/search_link_details',
        type: 'GET',
        data: {'neo_link_id': neo_link_id},
        success: result => {
            console.log(result);

            if (neo_link_id === result.relation_ID) {
                $('#neo_id').text(neo_link_id);
                $('#label_or_type').text('Type');
                $('#neo_label').text(result.relation_type);

                let properties = result.relation;
                add_node_link_details(properties);

                //加载用户对关系的更改
                show_user_link_changes();
            } else {
                console.log('error!')
            }
        }
    });
}

function clicked_node(d, i) {
    // alert(d.ID);
    neo_id = d.ID;
    let graph_nodes = $('.node');
    if (old_select_index >= 0) {
        graph_nodes.eq(old_select_index).removeClass('selected')
    }
    old_select_index = i;
    graph_nodes.eq(i).addClass('selected');

    enable_buttons([0, 1]);
    is_node_selected = true;

    $.ajax({
        url: "/search_node_details",
        data: {"neo_id": neo_id},
        success: result => {
            // console.log(result);

            if (neo_id === result.node_ID) {
                $('#neo_id').text(neo_id);
                $('#label_or_type').text('Label');
                $('#neo_label').text(result.node_labels);

                let properties = result.node_properties;

                add_node_link_details(properties);

                // show_user_node_changes();

                let node_name = '';
                if (properties['name'] != null) {
                    node_name = properties['name'];
                } else if (properties['title'] != null) {
                    node_name = properties['title'];
                }
                $('#query_node_name').val(node_name);

            } else {
                console.log("error!")
            }
        }
    })
}

function add_node_link_details(properties) {
    let details_table = $('#details_table');
    details_table.empty();
    thead = '<tr><td class="column_1">属性</td><td>属性值</td></tr>';
    details_table.append(thead);
    for (let key in properties) {
        add_details_item(key, properties[key]);
    }

}

//清空图形
function bind_clear_graph() {
    $('#clear_graph').click(clear);
}

function clear() {
    clearRecords();
    clearGraph();
    clearServer().then().catch((err) => {});
}

function clearRecords() {
    //重置清除标志和选择标志
    neo_id = '';
    is_cleared = true;
    old_select_index = -1;

    g_nodes0 = [];
    g_links0 = [];
    g_nodes0_user = [];
    g_links0_user = [];
}

function clearGraph() {
    d3.selectAll('#g_root >*').remove();
}

function clearServer() {
    //后端清除id
    return $.ajax_pro({
        url: '/user/clear_graph', type: 'GET'
    })
}