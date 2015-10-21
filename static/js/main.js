var cart = null;

function get_cart(callback) {
    if (!callback) {
        callback = function(data) {
            cart = data;
        }
    }
    //$.blockUI();
    var cart_id = localStorage.getItem('cart_id');
    if (cart_id == null) {
        $.getJSON("/ajax/get_cart/", function(data) {
            console.log(data);
            localStorage.setItem('cart_id', data.id);
            update_cart_ui(data);
            callback(data);
        });
    } else {
        $.getJSON("/ajax/get_cart/", function(data) {
            update_cart_ui(data);
            callback(data);
        });
    }
    //$.getJSON(api_endpoint + "carts/get_cart/", callback);
}

function is_odd(number) {
    return number % 2;
}

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function update_cart_ui(cart) {
    console.log(cart);
    var cart_body = $("#cart-body");
    var item_table = $("#item-table");
    $("#item-table tr").remove();

    var row_counter = 1;
    var item_counter = 0;
    cart.items.forEach(function(item) {
        var item_row = "";

        item_counter += item.quantity;

        if (is_odd(row_counter)) {
            item_row += "<tr class='odd'>";
        } else {
            item_row += "<tr class='even'>";
        }

        product_price_total = item.product.retail_price * item.quantity;
        item_row += "<td>" + item.quantity + " x " + item.product.name + "</td>";
        item_row += "<td style='text-align: right;'>$" + product_price_total.toFixed(2) + "</td>";
        //console.log(item);
        row_counter++;
        item_row += "<tr>";
        item_table.append(item_row);
    });
    var item_row = "";
    if (is_odd(row_counter)) {
        item_row += "<tr class='odd' style='border-top: 1px #000 solid;'>";
    } else {
        item_row += "<tr class='even' style='border-top: 1px #000 solid;'>";
    }
    item_row += "<td></td>";
    item_row += "<td style='text-align: right;'>$" + cart.subtotal_price_field.toFixed(2) + "</td>";
    //console.log(item);
    row_counter++;
    item_row += "<tr>";
    item_table.append(item_row);


    $("#num-items").html("Your cart contains " + item_counter + " items for $" + numberWithCommas(cart.subtotal_price_field.toFixed(2)));
    //$("#cart-total").html("$" + cart.subtotal_price_field.toFixed(2));
}

var cart_changes = [];

build_cart_page = function (cart) {
    var cart_table = $("#cart-items");
    //var cart_body = $("#cart-items tbody");
    cart_table.empty();

    var item_counter = 1;
    var subtotal = 0;
    cart.items.forEach(function (item) {
        var item_total_price = item.product.retail_price * item.quantity;
        subtotal += item_total_price;
        var child = "";
        if (is_odd(item_counter)) {
            child += "<tr>";
        } else {
            child += "<tr>";
        }
        child += "<td>" + item.product.name + "</td><td class='quantity-value'><input class='quantity-input' id='quantity-" + item.product.id + "' type='text' value=" + item.quantity + " size=3 style='text-align: center' /></td><td>$" + item.product.retail_price + "</td><td>$" + item_total_price.toFixed(2) + "</td>";
        child += "</tr>";
        if (item.product.products.length > 0) {
            child += "<tr><td colspan='4'><table>";
            item.product.products.forEach(function (sub_item) {
                child += "<tr>";
                child += "<td style='padding-left: 25px;'>" + (sub_item.quantity * item.quantity) + " x " + sub_item.product.name + "</td>";
                child += "</tr>";
            });
            child += "</table></td></tr>";
        }
        cart_table.append(child);
        item_counter++;
    });
    var child = "";
    if (is_odd(item_counter)) {
        child += "<tr style='border-top: 1px #000 solid;'>";
    } else {
        child += "<tr style='border-top: 1px #000 solid;'>";
    }
    child += "<td></td><td class='quantity-value'></td><td></td><td>$" + subtotal.toFixed(2) + "</td>";
    child += "</tr>";
    cart_table.append(child);

    $(".quantity-input").keyup(function() {
        var pieces = $(this).attr("id").split("-");
        var item_id = pieces[1];

        cart_changes.push({id: item_id, quantity: $(this).val()});
        //console.log(cart_changes);
        //console.log($(this).attr("id"));
    });
};
