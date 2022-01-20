//处理修改事件
function add_details_item(key, value) {
    var details_table = $('#details_table');
    row = '<tr class="changeable"><td>' + key + '</td><td>' + value + '</td></tr>';
    details_table.append(row);

    bind_change();
}

function bind_change() {
    var changeable_items = $('.changeable');
    changeable_items.click(function (e) {
        //e获取的是td
        var key = $(e.target).parent().children('td').eq(0).text();
        var value = $(e.target).parent().children('td').eq(1).text();
        // console.log(key+":"+value);
        $('#property').prop('value', key);
        $('#property_value').prop('value', value);
    });
}

function confirm_change() {
    $('#confirm_button').click(function () {
        key = $('#property').val();
        value = $('#property_value').val();

        if (key.length === 0) {
            return;
        }

        var changeable_items = $('.changeable');

        var target_item = null;
        var old_value = null;
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

        //将修改存入数据库
        change_in_user_database(neo_id, key, value);

        change_tables_and_graph(target_item, neo_id, key, value)
    });
}

function change_tables_and_graph(target_item, neo_id, key, value) {
    //修改图上的显示文本
    if (key === 'name' || key === 'title') {
        change_in_graph(neo_id, value);
    }

    change_tables(target_item, key, value);
}

function change_tables(target_item, key, value){
    if (target_item === null) {
        if (value.length === 0) {
            //删除属性
            alert('没有找到需要删除的节点');
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
}

function change_in_graph(neo_id, value) {
    node = d3.selectAll('.text').filter(function (d, i) {
        if (d.ID === neo_id) {
            return true;
        }
    });
    node.text(value);
}

function change_in_user_database(neo_id, key, value) {
    $.ajax({
        url: '/user/change',
        data: {'neo_id': neo_id, 'property': key, 'property_value': value},
        type: 'POST',
        success: function (result) {
            console.log(result);
        }
    })
}