jQuery(document).ready(function () {
    "use strict";

    (function ($) {
        var getCookie,
            csrftoken,
            removeStudent,
            re;

        getCookie = function (name) {
            var cookieValue = null,
                cookies,
                i,
                cookie;

            if (document.cookie && document.cookie !== '') {
                cookies = document.cookie.split(';');
                for (i = 0; i < cookies.length; i += 1) {
                    cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };

        csrftoken = getCookie("csrftoken");

        $("#invite-student").typeahead({
            source: function (query, process) {
                $.getJSON("/api/v1/user/",
                    {
                        format: "json",
                        first_name__istartswith: query,
                        last_name__istartswith: query
                    },
                    function (data, textStatus, jqXHR) {
                        process(_.map(data.objects, function (user) {
                            return user.first_name + " " + user.last_name + " (" + user.id + ")";
                        }));
                    });
            },
            minLength: 3
        });

        removeStudent = function (evt) {
            var id, row = $(evt.target).parent().parent();

            id = parseInt(row.children().eq(0).text(), 10);

            $.ajax(MOOC.basePath + "delete/" + id + "/", {
                headers: {
                    "X-CSRFToken": csrftoken
                },
                type: "DELETE",
                success: function (data, textStatus, jqXHR) {
                    row.remove();
                    $("#removed.alert-success").show();
                    setTimeout(function () {
                        $(".alert-success").hide();
                    }, MOOC.alertTime);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $("#generic.alert-error").show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                    }, MOOC.alertTime);
                }
            });
        };

        $("table .icon-remove").click(removeStudent);

        re = /\S+@\S+\.\S+/; // Very simple email validation
        $("#invite-student").next().click(function (evt) {
            evt.preventDefault();
            evt.stopPropagation();
            var data = $("#invite-student").val(),
                idxA,
                idxB;

            $("#invite-student").val("");
            if (!re.test(data)) {
                // Extract id from name
                idxA = data.lastIndexOf('(');
                idxB = data.lastIndexOf(')');
                if (idxA > 0 && idxB > 0) {
                    data = data.substring(idxA + 1, idxB);
                } else {
                    data = ""; // Invalid
                }
            }

            $.ajax(MOOC.basePath + "invite/", {
                data: {
                    data: data
                },
                headers: {
                    "X-CSRFToken": csrftoken
                },
                dataType: "json",
                type: "POST",
                success: function (data, textStatus, jqXHR) {
                    var html;
                    if (data.pending === false) {
                        html = "<tr>" +
                            "<td class='hide'>" + data.id + "</td>" +
                            "<td>" + data.gravatar + "</td>" +
                            "<td>" + data.name + "</td>" +
                            "<td class='ownership'></td>" +
                            "<td class='align-right'><span class='icon-remove pointer'></span></td>" +
                            "</tr>";
                        $("table#students_invited > tbody").append(html);
                        $("table#students_invited .icon-remove").off("click").click(removeStudent);
                    } else {
                        html = "<tr>" +
                            "<td>" + data.gravatar + "</td>" +
                            "<td>" + data.name + "</td>" +
                            "<td class='align-right'><span class='icon-remove pointer'></span></td>" +
                            "</tr>";
                        $("table#students_invited > tbody").append(html);
                        $("table#students_invited .icon-remove").off("click").click(removeStudent);
                    }

                    $("#added.alert-success").show();
                    setTimeout(function () {
                        $(".alert-success").hide();
                    }, MOOC.alertTime);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    $("#" + jqXHR.status).show();
                    setTimeout(function () {
                        $(".alert-error").hide();
                    }, MOOC.alertTime);
                }
            });
        });
    }(jQuery));
});
