var neo_id;
var g_nodes0;
var g_links0;

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

confirm_change();

confirm_query();

bind_clear_graph();
