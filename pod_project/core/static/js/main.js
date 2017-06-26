/*
Copyright (C) 2014 Nicolas Can
Ce programme est un logiciel libre : vous pouvez
le redistribuer et/ou le modifier sous les termes
de la licence GNU Public Licence telle que publiée
par la Free Software Foundation, soit dans la
version 3 de la licence, ou (selon votre choix)
toute version ultérieure.
Ce programme est distribué avec l'espoir
qu'il sera utile, mais SANS AUCUNE
GARANTIE : sans même les garanties
implicites de VALEUR MARCHANDE ou
D'APPLICABILITÉ À UN BUT PRÉCIS. Voir
la licence GNU General Public License
pour plus de détails.
Vous devriez avoir reçu une copie de la licence
GNU General Public Licence
avec ce programme. Si ce n'est pas le cas,
voir http://www.gnu.org/licenses/
*/
/** VARIABLES **/


var Pod = ( function ( Pod ) {

    // Used to prevent XHR video form upload when file field is empty.
    Pod.allowAjaxUpload = true;

    return Pod;

} ( Pod || { } ) );



/** DOC READY **/


$(document).ready(function() {

    // Lancement de la recherche au clic sur le bouton de recherche
    $(document.body).on(
        'click',
        '#searchBar SPAN BUTTON.submit',
        function() {
            if ($('#searchBar').find('INPUT').val() != '') {
                $(this).closest('FORM').submit();
            }
        }
    );


    /** NAVIGATION **/

    $("select.language").on('change',function(e) { $(this).parents("form").submit();});

    $('#filters input:checkbox').change(function() {
        get_ajax_url($('#filters').attr('action'), $('#filters').serialize());
    });

    $('div.list-all a').on('click',function(e) {
        if($(this).hasClass("list-all-plus")) {
            $(this).parent("div.list-all").children("a.list-all-minus").removeClass("hide");
            $(this).parents("fieldset:first").children("div.form-group").addClass("show-all");
            $(this).addClass("hide");
        } else {
            $(this).parent("div.list-all").children("a.list-all-plus").removeClass("hide");
            $(this).addClass("hide");
            $(this).parents("fieldset:first").children("div.form-group").removeClass("show-all");
        }
        return false;
    });

    setPerPage();
    setOrderBy();

    /** FIN NAVIGATION **/


    /** SELECT USER **/

    $('#ownerbox').keyup(function() {
       var valThis = $(this).val().toLowerCase();
       if(valThis == "") $('.navList>div>label>input:not(:checked)').parent("label").parent("div").hide();
       else {
           $('.navList>div>label>input:not(:checked)').each(function() { //:not(:checked)
             var text = $(this).parent("label").children("span.fullname").text().toLowerCase();
                (text.indexOf(valThis) != -1) ? $(this).parent("label").parent("div").show() : $(this).parent("label").parent("div").hide();
           });
       }
    });

    $('.navList>div>label>input:not(:checked)').parent("label").parent("div").hide();
    $(".navList>div>label>a.show-desc>span.user-description").hide();

    $('.navList>div>label>input').on('change',function(e) {
        if(!this.checked) {
             $(this).parent("label").parent("div").hide();
        }
    });


    /** FORM VIDEO **/
    $('form:not(#video_form)').on('submit', function() {
        $('form').hide();
        return true;
    });

    var initial = new Array();
    $('#id_theme option:selected').each(function () {
        initial.push($(this).val());
    });

    $('#id_theme')
        .find('option')
        .remove()
        .end();
    //$('#id_theme').append(initial);
    $("#id_channel option:selected").each(function () {
        for (var i = 0; i < themetab[$(this).val()].length; i++) {
            if($.inArray(""+themetab[$(this).val()][i][0], initial) > -1)
            $('#id_theme').append('<option selected value="'+themetab[$(this).val()][i][0]+'">'+themetab[$(this).val()][i][1]+'</option>')
            else
            $('#id_theme').append('<option value="'+themetab[$(this).val()][i][0]+'">'+themetab[$(this).val()][i][1]+'</option>')
        };
    });

    $('#id_channel').change(function() {
        var str = "";
        $('#id_theme')
            .find('option')
            .remove()
            .end();
        $("#id_channel option:selected").each(function () {
            for (var i = 0; i < themetab[$(this).val()].length; i++) {
                $('#id_theme').append('<option value="'+themetab[$(this).val()][i][0]+'">'+themetab[$(this).val()][i][1]+'</option>')
            };
        });
    });

    /** FIN FORM VIDEO **/


    /** DJANGO FILER **/

    if (typeof num != 'undefined' && name == "") {
        showRelatedObjectLookupPopup = function(triggeringLink) {
            name = triggeringLink.id.replace(/^lookup_/, '');
            var href;
            if (triggeringLink.href.search(/\?/) >= 0) {
                href = triggeringLink.href + '&_popup=1';
            } else {
                href = triggeringLink.href + '?_popup=1';
            }
            ifr = '<span id="framemessage"><p>Chargement en cours.Veuillez patienter...</p></span><iframe style="width:99%;height:1px;border:0;" id="resultFrame" src="'+href+'" onload="frameReady();" seamless="seamless"><p>Chargement en cours.Veuillez patienter...</p></iframe>';
            $("#mediabox").html(ifr);
            $('#myModal').modal({
              show: true,
              /*remote: href*/
            });
            return false;
        };

        dismissRelatedImageLookupPopup = function(win, chosenId, chosenThumbnailUrl, chosenDescriptionTxt) {
            var img_name = name + '_thumbnail_img';
            var txt_name = name + '_description_txt';
            var clear_name = name + '_clear';
            var elem = document.getElementById(name);
            document.getElementById(name).value = chosenId;
            document.getElementById(img_name).src = chosenThumbnailUrl;
            document.getElementById(txt_name).innerHTML = chosenDescriptionTxt;
            document.getElementById(clear_name).style.display = 'inline';
            //close_box();
            $('#myModal').modal('hide');
        };
    }

    /** DJANGO FILER **/

});



/*** DON'T TOUCH THIS ****/
function csrfSafeMethod(method) {
    // These HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // Obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
    }
});
var csrftoken = getCookie('csrftoken');



/** EVTS PERMANENT **/


/** video list **/

$(document).on('click', "#pagination .paginator a", function() {
    var newurl = $(this).attr('href');
    get_ajax_url(newurl);
    return false;
});

$(document).on('change', "#orderby", function() {
    createCookie("orderby", $(this).val(), null);
    get_ajax_url(window.location.href);
});

$(document).on('change', "#perpage", function() {
    createCookie("perpage", $(this).val(), null);
    get_ajax_url(window.location.href);
});

$(document).on('mouseenter', 'a.show-desc', function() {
    $( this ).children("span.user-description").show();
});

$(document).on('mouseleave', 'a.show-desc', function() {
    $( this ).children("span.user-description").hide();
});

/** end video list **/


/** video share embed **/

$(document).on('change', '#integration_size', function() {
    writeInFrame();
});

$(document).on('change', '#autoplay', function() {
    writeInFrame();
});

$(document).on('change', "#displaytime", function(e) {
    //$('#txtpartage').val(($('#displaytime:checked').val()) ? $('#txtpartage').val().replace(/(start=)\d+/, '$1'+parseInt(myPlayer.currentTime())) : $('#txtpartage').val().replace(/(start=)\d+/, '$10'));
    if($('#displaytime').is(':checked')){
        if($('#txtpartage').val().indexOf('start')<0){
             $('#txtpartage').val($('#txtpartage').val()+'?start='+parseInt(myPlayer.currentTime()));
             var valeur = $('#txtintegration').val();
             $('#txtintegration').val(valeur.replace('/?', '/?start=' + parseInt(myPlayer.currentTime())+'&'));
        }
        $('#txtposition').val(myPlayer.currentTime().toHHMMSS());
    }else{
         $('#txtpartage').val($('#txtpartage').val().replace(/(\?start=)\d+/, ''));
         $('#txtintegration').val($('#txtintegration').val().replace(/(start=)\d+&/, ''));
         $('#txtposition').val("");
    }
});

$(document).on('click', "#share a", function() {
    var src = $(this).attr("href");
    if(src.indexOf("javascript")==-1) {
        window.open(src,'popup_1', config='height=400, width=600, toolbar=no, menubar=no, scrollbars=yes, resizable=yes' );
        return false;
    }
    return true;
});

/** end video share embed **/


$(document).on('click', 'button#button_video_report', function(event) {
    event.preventDefault();
    if($(this).parent('form').length==0){
        alert($(this).children('span.sr-only').text());
    } else {
        if(expiration_date_second > 5) {
            //show modal box with comment input and save/cancel buttons
            $("#modal_report_form").modal({
              show: true,
            });
        } else {
            alert(expiredsession);
            location.reload();
        }
    }
    return false;
});


/*

    Creates & shows BS alert boxes w close button

*/
function show_messages( msgText, msgClass, loadUrl ) {

    var $msgContainer = $( '#show_messages' );
    var closeButton = "";

    msgClass = typeof msgClass !== 'undefined' ? msgClass : 'warning';
    loadUrl = typeof loadUrl !== 'undefined' ? loadUrl : false;

    if ( loadUrl === false ) {

        closeButton = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>';
    }

    var $msgBox = $( "<div>", {
        // "fade in" class means the alert box will fade out when the close icon is clicked (!)
        'class': "alert alert-" + msgClass + " alert-dismissable fade in",
        'role': "alert",
        'html': closeButton + msgText,
    } );

    $msgContainer.html( $msgBox );

    if ( loadUrl !== false ) {

        $msgBox.delay( 4000 ).fadeOut( function( ) {

            if ( loadUrl === true ) {

                window.location.reload( );

            } else {

                window.location.assign( loadUrl );
            }
        } );

    } else if ( msgClass === "info" || msgClass === "success" ) {

        $msgBox.delay( 3000 ).fadeOut( function( ) {

            $msgBox.remove( );
        } );
    }

}

/** END EVTS PERMANENT **/



/** FUNCTIONS **/

Number.prototype.toHHMMSS = function() {
    var seconds = Math.floor(this),
        hours = Math.floor(seconds / 3600);
    seconds -= hours*3600;
    var minutes = Math.floor(seconds / 60);
    seconds -= minutes*60;

    if (hours   < 10) {hours   = "0"+hours;}
    if (minutes < 10) {minutes = "0"+minutes;}
    if (seconds < 10) {seconds = "0"+seconds;}
    return hours+':'+minutes+':'+seconds;
};

// Edit the iframe and share link code
function writeInFrame() {
    // Iframe
    var str = $('#txtintegration').val();
    // Video size
    var $integration_size_option = $('#integration_size').find('OPTION:selected');
    var width = $integration_size_option.attr('data-width');
    var height = $integration_size_option.attr('data-height');
    var size = $integration_size_option.attr('value');
    str = str.replace(/(width=)\S+/, '$1' + '\"' + width +'\"');
    str = str.replace(/(height=)\S+/, '$1' + '\"' + height +'\"');
    str = str.replace(/(size=)\d+/, '$1' + size);
    // Autoplay
    if ($('#autoplay').is(':checked')) {
            if(str.indexOf('autoplay=true') < 0){
                str = str.replace('is_iframe=true', 'is_iframe=true&autoplay=true');
            }
    } else if (str.indexOf('autoplay=true') > 0) {
        str = str.replace('&autoplay=true', '');
    }
    $('#txtintegration').val(str);

    // Share link
    var link = $('#txtpartage').val();
    link = link.replace(/(size=)\d+/, '$1' + size);
    // Autoplay
    if ($('#autoplay').is(':checked')) {
        if(link.indexOf('autoplay=true') <0){
                link = link.replace('is_iframe=true', 'is_iframe=true&autoplay=true');
            }

    } else if (link.indexOf('autoplay=true') >0) {
       link = link.replace('&autoplay=true', '');
    }
    $('#txtpartage').val(link);
}

function setPerPage() {
    $("#perpage").prop('selected', false);
    cperpage = getCookie("perpage");
    if(cperpage!=null) {
        $("#perpage").val(cperpage);
        $("#perpage option").each(function() {
            if ($(this).attr("value") == cperpage) {
                $(this).attr("selected",true);
            } else {
                $(this).removeAttr("selected");
            }
        });
    }
}

function setOrderBy() {
    $("#orderby").prop('selected', false);
    corderby = getCookie("orderby");
    if(corderby==null) corderby="order_by_-date_added"
    if(corderby!=null) {
        $("#orderby").val(corderby);
        $("#orderby option").each(function() {
            if ($(this).attr("value") == corderby) {
                $(this).attr("selected",true);
            } else {
                $(this).removeAttr("selected");
            }
        });
    }
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function createCookie(name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    } else var expires = "";
    document.cookie = escape(name)+"="+escape(value)+expires+"; path=/";
}

function get_ajax_url(newurl, attrs) {
    $("#objects_list").css("height",$("#objects_list").height());
    //$(".mainToolbar").hide();
    var filter_is_visible = $('#filters').is(":visible")
    $('#filters').hide();
    $( "#objects_list" ).fadeOut("fast", function() {
        $( "#objects_list" ).html( ajax_image ).fadeIn("fast", function() {
            $.get( newurl, attrs, function( data ) {
                $( "#objects_list" ).fadeOut("fast", function() {
                    $( "#objects_list" ).html( data.json_videols );
                    setOrderBy();
                    $("a.show-desc span").hide();
                    $( "#objects_list" ).fadeIn("fast");
                    $("#objects_list").css("height","auto");
                });
                $( "#toolbar" ).fadeOut("fast", function() {
                    $( "#toolbar" ).html( data.json_toolbar );
                    setOrderBy();
                    setPerPage();
                    $( "#toolbar" ).fadeIn("fast");
		});

                if(attrs){
                    if (window.history && window.history.pushState) {
                       history.replaceState(null, null, location.protocol + '//' + location.host + location.pathname +"?"+ attrs);
                     }
                } else {
                    if (window.history && window.history.pushState) {
                        if(newurl.indexOf("?")==0)
                            history.replaceState(null, null, location.protocol + '//' + location.host + location.pathname + newurl);
                        else
                            history.replaceState(null, null, newurl);
                    }
                }
                setPerPage();

                if(filter_is_visible) $('#filters').show();
            }).fail(function() { alert( "error" ); });
        });
    });
}

function frameReady() {
    //alert('frameready');
    $("#framemessage").hide();
    $("#resultFrame").height("450px");
    var el = document.getElementById('resultFrame');
    getIframeWindow(el).opener = window;
}

function getIframeWindow(iframe_object) {
    var doc;

    if (iframe_object.contentWindow) {
    return iframe_object.contentWindow;
    }

    if (iframe_object.window) {
    return iframe_object.window;
    }

    if (!doc && iframe_object.contentDocument) {
    doc = iframe_object.contentDocument;
    }

    if (!doc && iframe_object.document) {
    doc = iframe_object.document;
    }

    if (doc && doc.defaultView) {
    return doc.defaultView;
    }

    if (doc && doc.parentWindow) {
    return doc.parentWindow;
    }

    return undefined;
}

function linkTo_UnCryptMailto( s ) {
    location.href="mailto:"+window.atob(s);
}
