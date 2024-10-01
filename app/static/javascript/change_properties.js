var is_node_selected = true;

function enable_buttons(enable_list) {
    let button_list = [
        $('#confirm_button'),
        $('#delete_node_button'),
        $('#delete_link_button')
    ];
    for (let index = 0; index < button_list.length; index++) {
        if (enable_list.includes(index)) {
            button_list[index].removeClass('disable_click');
            button_list[index].css('background-color', '#43fffc');
            button_list[index].hover(() => {
                button_list[index].css('background-color', '#35cbc6');
            }, () => {
                button_list[index].css('background-color', '#43fffc');
            })
        } else {
            button_list[index].addClass('disable_click');
            button_list[index].css('background-color', '#e5eaff');
        }
    }
}

//处理修改事件
function add_details_item(key, value) {
    let details_table = $('#details_table');
    row = '<tr class="changeable"><td>' + key + '</td><td>' + value + '</td></tr>';
    details_table.append(row);

    bind_change();
}

function bind_change() {
    let changeable_items = $('.changeable');
    changeable_items.click(function (e) {
        //e获取的是td
        let key = $(e.target).parent().children('td').eq(0).text();
        let value = $(e.target).parent().children('td').eq(1).text();
        console.log(key + ":" + value);
        $('#property').prop('value', key);
        $('#property_value').prop('value', value);
    });
}

function confirm_change() {
    $('#confirm_button').click(function () {
        is_confirm_query = true;

        let key = $('#property').val();
        let value = $('#property_value').val();

        if (key.length === 0) {
            return;
        }

        let changeable_items = $('.changeable');

        let target_item = null;
        let old_value = null;
        changeable_items.each(function (i, e) {
            if ($(e).children('td').eq(0).text() === key) {
                target_item = $(e);
                old_value = target_item.children('td').eq(1).text();
                return false;
            }
        });
        if (old_value === value) {
            return;
        }

        if (is_node_selected) {
            //将修改存入数据库
            change_in_user_node_database(neo_id, key, value);

            change_node_tables_and_graph(target_item, neo_id, key, value);
        } else {
            change_in_user_link_database(neo_link_id, key, value);

            change_link_tables_and_graph(target_item, neo_link_id, key, value)
        }

    });
}

function change_link_tables_and_graph(target_item, neo_link_id, key, value) {
    if (key === 'Type') {
        change_link_in_graph(neo_link_id, value);
    }

    change_tables(target_item, key, value);
}


function change_node_tables_and_graph(target_item, neo_id, key, value) {
    //修改图上的显示文本
    if (key === 'name' || key === 'title') {
        change_node_in_graph(neo_id, value);
    }

    change_tables(target_item, key, value);
}

function change_tables(target_item, key, value) {
    if (target_item === null) {
        if (value.length === 0) {
            if (is_confirm_query){
                alert('没有找到指定节点或边');
            }
        } else {
            //增加属性值
            add_details_item(key, value);
        }
    } else {
        if (key === 'Label') {
            $('#neo_label').text(value);
        } else {
            if (value.length === 0) {
                //删除属性
                target_item.remove();
            } else {
                //修改属性
                target_item.children('td').eq(1).text(value);
            }
        }
    }
    is_confirm_query = false;
}

function change_link_in_graph(neo_link_id, value) {
    let node;
    node = d3.selectAll('.link_text').filter(function (d, i) {
        if (d.ID === neo_link_id) {
            return true;
        }
    });
    node.text(value);
}

function change_node_in_graph(neo_id, value) {
    let node;
    node = d3.selectAll('.node_text').filter(function (d, i) {
        if (d.ID === neo_id) {
            return true;
        }
    });
    node.text(value);
}

function change_in_user_node_database(neo_id, key, value) {
    $.ajax({
        url: '/user/node_change',
        data: {'neo_id': neo_id, 'property': key, 'property_value': value},
        type: 'POST',
        success: function (result) {
            console.log(result);
        }
    });
}

function change_in_user_link_database(neo_link_id, key, value) {
    $.ajax({
        url: '/user/link_change',
        data: {
            'neo_link_id': neo_link_id,
            'property': key,
            'property_value': value
        },
        type: 'POST',
        success: function (result) {
            console.log(result);
        }
    });
}