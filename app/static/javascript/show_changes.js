var node_changes_list;
var link_changes_list;

async function show_user_node_changes() {
    node_changes_list = await $.ajax_pro({
        url: '/user/query_changes'
    });
    //用来修改图上的文本，修改查询的属性值
    show_node_changes_in_graph(node_changes_list);
    show_node_changes_in_tables(node_changes_list);
}

async function show_user_link_changes() {
    link_changes_list = await $.ajax_pro({
        url: '/user/query_link_changes'
    });
    //用来修改图上的文本，修改查询的属性值
    show_link_changes_in_graph(link_changes_list);
    show_link_changes_in_tables(link_changes_list);
}

function show_link_changes_in_graph(link_changes_list) {
    $(link_changes_list).each(function (index, change) {
        let key = change['property'];
        let value = change['property_value'];
        let current_id = change['neo_link_id'];

        //修改图上的显示文本
        if (key === 'Type') {
            change_link_in_graph(current_id, value);
        }

        //删除边
        if (key === 'ID' && value === '') {
            delete_link_in_graph(current_id);
        }

    });
}

function show_node_changes_in_graph(node_changes_list) {
    $(node_changes_list).each(function (index, change) {
        let key = change['property'];
        let value = change['property_value'];
        let current_id = change['neo_id'];

        //修改图上的显示文本
        if (key === 'name' || key === 'title') {
            change_node_in_graph(current_id, value);
        }

        //删除节点
        if (key === 'ID' && value === '') {
            delete_node_in_graph(current_id);
        }


    });
}

function show_link_changes_in_tables(link_changes_list) {
    $(link_changes_list).each(function (index, change) {
        let current_id = change['neo_link_id'];
        if (current_id === neo_link_id) {
            let key = change['property'];
            let value = change['property_value'];

            //修改属性值表
            let target_item = null;
            $('.changeable').each(function (i, e) {
                if ($(e).children('td').eq(0).text() === key) {
                    target_item = $(e);
                    return false;
                }
            });

            change_tables(target_item, key, value);
        }
    });
}

function show_node_changes_in_tables(node_changes_list) {
    $(node_changes_list).each(function (index, change) {
        let current_id = change['neo_id'];
        if (current_id === neo_id) {
            let key = change['property'];
            let value = change['property_value'];

            //修改属性值表
            let target_item = null;
            $('.changeable').each(function (i, e) {
                if ($(e).children('td').eq(0).text() === key) {
                    target_item = $(e);
                    return false;
                }
            });

            change_tables(target_item, key, value);
        }
    });
}