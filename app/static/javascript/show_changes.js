//用来修改图上的文本，修改查询的属性值

var changes_list;

function show_user_changes() {
    $.ajax({
        url: '/user/query_changes',
        success: function (result) {
            // console.log(result);
            changes_list = result;
            show_changes_in_graph()
        }
    })
}

function show_changes_in_graph() {
    $(changes_list).each(function (index, change) {
        key = change['property'];
        value = change['property_value'];
        current_id = change['neo_id'];
        //修改图上的显示文本
        if (key === 'name' || key === 'title') {
            change_in_graph(current_id, value);
        }
    });
}

function show_changes_in_tables() {
    $(changes_list).each(function (index, change) {
        current_id = change['neo_id'];
        if (current_id === neo_id) {
            key = change['property'];
            value = change['property_value'];

            //修改属性值表
            var target_item = null;
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