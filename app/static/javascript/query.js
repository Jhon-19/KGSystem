//按照节点查询

function confirm_query() {
    $('#confirm_query').click(function () {
        node_name = $('#query_node_name').val();//val()读取表单元素的值
        if (node_name.length > 0) {
            query_by_node(neo_id, node_name);
        }
    });
}

function query_by_node(neo_id, node_name) {
    $.ajax({
        url: '/user/query_by_node',
        type: 'GET',
        data: {'neo_id': neo_id, 'node_name': node_name},
        success: result => {
            // console.log(result);
            g_nodes0 = g_nodes0.concat(result.nodes);
            g_links0 = g_links0.concat(result.links);

            if (is_cleared) {
                draw_graph(g_nodes0, g_links0);
            } else {
                update_graph(g_nodes0, g_links0);
            }


        }
    });
}