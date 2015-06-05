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

function update_cart_ui(cart) {
    console.log(cart);
    var cart_body = $("#cart-body");
    var item_table = $("#item-table");
    $("#item-table tr").remove();

    var item_counter = 1;
    cart.items.forEach(function(item) {
        var item_row = "";
        if (is_odd(item_counter)) {
            item_row += "<tr class='odd'>";
        } else {
            item_row += "<tr class='even'>";
        }

        product_price_total = item.product.retail_price * item.quantity;
        item_row += "<td>" + item.quantity + " x " + item.product.name + "</td>";
        item_row += "<td style='text-align: right;'>$" + product_price_total.toFixed(2) + "</td>";
        //console.log(item);
        item_counter++;
        item_row += "<tr>";
        item_table.append(item_row);
    });
}

build_cart_page = function(cart) {
    var cart_table = $("#cart-items");

    var item_counter = 1;
    var subtotal = 0;
    cart.items.forEach(function(item) {
        var item_total_price = item.product.retail_price * item.quantity;
        subtotal += item_total_price;
        var child = "";
        if (is_odd(item_counter)) {
            child += "<tr class='odd'>";
        } else {
            child += "<tr class='even'>";
        }
        child += "<td>" + item.product.name + "</td><td class='quantity-value'><input type='text' value=" + item.quantity + " size=3 style='text-align: center' /></td><td>$" + item.product.retail_price + "</td><td>$" + item_total_price.toFixed(2) + "</td>";
        child += "</tr>";
        cart_table.append(child);
        item_counter++;
    });
    var child = "";
    if (is_odd(item_counter)) {
        child += "<tr class='odd'>";
    } else {
        child += "<tr class='even'>";
    }
    child += "<td></td><td class='quantity-value'></td><td></td><td>$" + subtotal.toFixed(2) + "</td>";
    child += "</tr>";
    cart_table.append(child);
};
