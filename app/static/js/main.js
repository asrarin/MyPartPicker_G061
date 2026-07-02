// auto close alert box after 5 seconds 

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".alert.alert-dismissible").forEach(function (el) {
        setTimeout(function () {
            var a = bootstrap.Alert.getOrCreateInstance(el);
            if (a) a.close();
        }, 5000);
    });
});
