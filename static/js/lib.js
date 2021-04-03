var cartSum = 0;
var deliverySum = 0;
var totalSum = 0;
var minOrderSum = 0;
var itemList = [];
var priceList = {};
var items = {};
var cart = {};

function normalize(x) {
    return (+x).toFixed(2).toString().replace('.', ',').replace(/(\d{1,3}(?=(\d{3})+(?:\.\d|\b)))/g, "$1" + ('\u202F'));
}

function getItemPrice(item, count) {
    if (!(item in priceList)) {
        console.log('error: there no such item');
        return 0;
    }

    var mxLower = -1;
    var price = 0;
    for (key in priceList[item]) {
        if ((+key) <= count && mxLower < (+key)) {
            mxLower = (+key);
            price = +priceList[item][key];
        }
    }
    return price;
}


function getQuantityInCart(item) {
    if (!(item in cart)) {
        return 0;
    }
    return +cart[item];
}


function updateCartSum(f) {
    $.post("/getcartsum", {},
        function (data, status) {
            cartSum = +data;
            $("#cartSum").text(normalize(cartSum));
            if (f == undefined) {

            } else {
                f(data, status);
            }
        });
}

function updateDeliverySum(f) {
    $.post("/getdelivery", {},
        function (data, status) {
            cartSum = +data;
            $("#deliverySum").text(normalize(deliverySum));
            if (f == undefined) {

            } else {
                f(data, status);
            }
        });
}

function updateTotalSum(f) {
    $.post("/gettotal", {},
        function (data, status) {
            totalSum = +data;
            if (f == undefined) {

            } else {
                f(data, status);
            }
        });
}

function updateCart(async) {
    if (async == undefined) {
        async = true;
    }
    console.log(async);
    $.ajax({
        url: "/getcartsum", async: async, type: "POST", success: function (result) {
            cartSum = +result;
            $("#cartSum").text(normalize(cartSum));
        }
    });
    $.ajax({
        url: "/getdelivery", async: async, type: "POST", success: function (result) {
            deliverySum = +result;
            $("#deliverySum").text(normalize(deliverySum));
        }
    });
    $.ajax({
        url: "/gettotal", async: async, type: "POST", success: function (result) {
            totalSum = +result;
        }
    });
    $.ajax({
        url: "/getcart", async: async, type: "POST", success: function (result) {
            cart = JSON.parse(result);
        }
    });
}


function setInCart(item, quantity, f) {
    $.post("/setincart",
        {
            "item": item,
            "quantity": quantity
        },
        function (data, status) {
            updateCart();
            if (f == undefined) {

            } else {
                f(data, status);
            }
        });
}


function addToCart(item, quantity, f) {
    $.post("/addtocart",
        {
            "item": item,
            "quantity": quantity
        },
        function (data, status) {
            updateCart();
            if (f == undefined) {

            } else {
                f(data, status);
            }
        });
}


function updateAll() {
    updateCart();
}


function loadItems() {
    $.ajax({
        url: "/getitems", async: false, type: "POST", success: function (result) {
            console.log('getitems:');
            console.log(result);
            items = JSON.parse(result);
        }
    });
    $.ajax({
        url: "/getitemarray", async: false, type: "POST", success: function (result) {
            itemList = JSON.parse(result);
        }
    });
    $.ajax({
        url: "/getitemprices", async: false, type: "POST", success: function (result) {
            // /console.log(result);
            priceList = JSON.parse(result);
        }
    });
}


function notifyId(id, text) {
    console.log(id, text);
    $(id).attr("data-content", text);
    $(id).popover("show");
    setTimeout(function () { $(id).popover("hide"); $(id).attr("data-content", ""); }, 4000);
}


function notifyCart(text) {
    notifyId("#cartlink", text);
}


$(document).ready(function () {
    // script for csrf from https://djbook.ru/rel1.7/ref/contrib/csrf.html#how-to-use-it
    var csrftoken = $.cookie('csrftoken');
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    // end of script

    //$('[data-toggle="popover"]').popover({ trigger: "hover" });
    $('[data-toggle="tooltip"]').tooltip();

    $.ajax({
        url: "/getminordersum", async: false, type: "POST", success: function (result) {
            minOrderSum = +result;
        }
    });

    loadItems();
    updateCart(false);
});
