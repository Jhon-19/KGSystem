var neo_id;
var neo_link_id;
var g_nodes0;
var g_links0;

var min_user_node_id = 0;
var min_user_link_id = 0;

var is_confirm_query = false; //判断查询按钮是否被按下

//扩展ajax_pro函数，使用promise,返回Promise对象的函数可以使用await
$.extend({
    'ajax_pro': (params) => {
        return new Promise((resolve, reject) => {
            $.ajax({
                url: params.url,
                type: params.type || 'get',
                dataType: 'json',
                headers: params.headers || {},
                data: params.data || {},
                success(res) {
                    resolve(res);
                },
                error(err) {
                    reject(err);
                }
            })
        })
    }
});

init_elements();

//刷新时清除后端数据
$(() => {
    $.ajax({
        url: '/user/clear_graph',
        success: () => {
            init_graph();
        }
    });
});

function init_graph() {
    $.ajax({
        url: "/graph",
        type: 'GET',
        success: result => {
            // console.log(result);
            g_nodes0 = result.nodes;
            g_links0 = result.links;

            draw_graph(g_nodes0, g_links0)
        }
    });
}

function init_elements() {
    enable_buttons([]);

    confirm_change();

    confirm_query();

    bind_clear_graph();

    bind_delete_node_link();

    bind_add_node_link();
}
