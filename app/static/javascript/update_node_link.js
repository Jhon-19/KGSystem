function bind_delete_node_link() {
    $('#delete_link_button').click(function () {
        delete_link_in_graph(neo_link_id);

        $.ajax({
            url: '/user/link_change',
            type: 'POST',
            data: {
                'neo_link_id': neo_link_id,
                'property': 'ID',
                'property_value': '',
            },
            success: (result) => {
                console.log(result);
            }
        });
    });

    $('#delete_node_button').click(function () {
        delete_node_in_graph(neo_id);

        $.ajax({
            url: '/user/node_change',
            type: 'POST',
            data: {
                'neo_id': neo_id,
                'property': 'ID',
                'property_value': ''
            },
            success: (result) => {
                console.log(result);
            }
        })
    });
}

function bind_add_node_link() {
    $('.close_panel_label').click(() => {
        $('.add_node_link_panel').slideUp();
        $('#mask').hide();
    });

    $('#add_node_button').click(() => {
        $('#node_details_ID').text(min_user_node_id - 1);//负数表示用户自定义的节点

        $('.add_node_link_panel').eq(0).slideDown();
        $('#mask').show();
    });

    $('#add_link_button').click(() => {
        $('#link_details_ID').text(min_user_link_id - 1);//负数表示用户自定义的节点边

        $('.add_node_link_panel').eq(1).slideDown();
        $('#mask').show();
    });

    $('#node_details_confirm').click(async () => {
        let ID = $('#node_details_ID').text();
        let Label = $('#node_details_Label').val();
        let title = $('#node_details_title').val();

        $('.add_node_link_panel').eq(0).slideUp();

        $('#mask').hide();
        console.log('node saved.');

        await save_node_add(ID, Label, title);

        draw_or_update_graph();
    });

    $('#link_details_confirm').click(async () => {
        let ID = $('#link_details_ID').text();
        let Type = $('#link_details_Type').val();
        let start_node = $('#link_details_source').val();
        let end_node = $('#link_details_target').val();

        $('.add_node_link_panel').eq(1).slideUp();

        $('#mask').hide();
        console.log('link saved.');

        await save_link_add(ID, Type, start_node, end_node);

        draw_or_update_graph();
    });
}

function save_node_add(user_node_id, Label, title) {
    return $.ajax({
        url: '/user/node_add',
        type: 'POST',
        data: {
            'user_node_id': user_node_id,
            'Label': Label,
            'title': title
        },
    })
}

function save_link_add(user_link_id, Type, start_node, end_node) {
    return $.ajax({
        url: '/user/link_add',
        type: 'POST',
        data: {
            'user_link_id': user_link_id,
            'Type': Type,
            'start_node': start_node,
            'end_node': end_node
        }
    })
}

function delete_link_in_graph(neo_link_id) {
    let index = -1;
    d3.selectAll('.link').filter((d, i) => {
        if (d.ID === neo_link_id) {
            index = i;
            return false;
        }
    });
    if (index !== -1) {
        delete_links_by_index_list([index]);
    }
}

function delete_node_in_graph(neo_id) {
    let index = -1;
    d3.selectAll('.node').filter((d, i) => {
        if (d.ID === neo_id) {
            index = i;
            return true;
        }
    });
    if (index !== -1) {
        delete_node_by_index(index);
        let link_index_list = [];
        //去掉与节点相关联的边
        d3.selectAll('.link').filter((d, i) => {
            // console.log(d);
             //d3.js为source和target添加了node中的信息，故需要访问node的ID才是原来的source的ID
            if (d.source.ID === neo_id || d.target.ID === neo_id) {
                link_index_list.push(i);
                return true;
            }
        });

        delete_links_by_index_list(link_index_list);
    }
}

function delete_node_by_index(index) {
    let node = d3.selectAll('.node').filter((d, i) => {
        if (i === index) {
            return true;
        }
    });
    node.style('display', 'none');

    let node_text = d3.selectAll('.node_text').filter((d, i) => {
        if (i === index) {
            return true;
        }
    });
    node_text.style('display', 'none');
}

function delete_links_by_index_list(index_list) {
    let link = d3.selectAll('.link').filter((d, i) => {
        if (index_list.includes(i)) {
            return true;
        }
    });
    link.style('display', 'none');

    let link_text = d3.selectAll('.link_text').filter((d, i) => {
        if (index_list.includes(i)) {
            return true;
        }
    });
    link_text.style('display', 'none');
}