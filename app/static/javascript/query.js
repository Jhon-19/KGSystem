var g_nodes0_user = [];
var g_links0_user = [];

async function query_user_adds() {
    await query_user_add_nodes();
    await query_user_add_links();
}

async function query_user_add_nodes() {
    let result = await $.ajax_pro({
        url: '/user/query_node_add'
    });
    $(result).each((i, e) => {
        if (e.ID < min_user_node_id) {
            min_user_node_id = e.ID;
        }
    });
    g_nodes0_user = g_nodes0_user.concat(result);

    // console.log(result);
    return 'OK';
}

async function query_user_add_links() {
    let result = await $.ajax_pro({
        url: '/user/query_link_add'
    });
    $(result).each((i, e) => {
        if (e.ID < min_user_link_id) {
            min_user_link_id = e.ID;
        }
    });
    g_links0_user = g_links0_user.concat(result);

    return 'OK';
}


//按照节点查询
function confirm_query() {
    $('#confirm_query').click(function () {
        node_name = $('#query_node_name').val();//val()读取表单元素的值
        if (node_name.length > 0) {
            query_by_node(neo_id, node_name);
        }
    });
}

function confirm_query_triple() {
    document.getElementById('confirm_query_triple').addEventListener('click', () => {
        let head = document.getElementById('query_head').value;
        let relation = document.getElementById('query_relation').value;
        let tail = document.getElementById('query_tail').value;
        if (relation.length > 0) {
            query_by_triple(head, relation, tail);
        }
    })
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

            draw_or_update_graph();
        }
    });
}

function query_by_triple(head, relation, tail) {
    clearRecords();
    clearGraph();
    const promise = clearServer();
    promise.then(() => {
    }).catch((err) => {
        // console.log(err);
    }).finally(() => {
        $.ajax({
            url: '/user/query_by_triple',
            type: 'GET',
            data: {head, relation, tail},
            success: (result) => {
                // console.log(result);
                g_nodes0 = g_nodes0.concat(result.nodes);
                g_links0 = g_links0.concat(result.links);

                draw_or_update_graph();
            }
        })
    })
}

function draw_or_update_graph() {
    if (is_cleared) {
        draw_graph(g_nodes0, g_links0);
    } else {
        clearGraph();
        draw_graph(g_nodes0, g_links0);
    }

}