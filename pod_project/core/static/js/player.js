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
/******* VARIABLES ********/
var myPlayer;
var currentslide = '';
var timestamps = [];
var changeRes = false;
var animation_complete = true;
var list_disp = {
    '50/50': '50/50',
    '30/70': '30/70',
    '70/30': '70/30',
    '100/20': 'Pip media',
    '20/100': 'Pip video',
    '100/0': 'only video',
    '0/100': 'only media'
};
var defaultDisp = '50/50';
var slide_height = 90; //96 en fullscreen
var videozindex = 1000;
var isPlaying = false;
var increase_view_count = false;
var start;
var is_360 = false;
/* check bandwidth */
var previoustime = 0;
var previousuploaded = 0;
var mediumspeed = 0;
var intcheck = 0;
var changeResBd = false;
/******* DOC READY ********/
$(document).ready(function() {
    loadVideo();
    // Remove right click on video
    $('#player_video').bind('contextmenu', function() { return false; });
});

/******* FUNCTION ********/
function isMobile() {
    var check = false;
    (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);
    return check;
}

function loadVideo() {
    //reinitialize somes var :
    currentslide = '';
    timestamps = [];

    videojs.options.flash.swf = 'video-js.swf';
    videojs('player_video').ready(function() {
        // PLAYER READY
        myPlayer = this;
        
        //if video 360
        if(is_360) {
            window.addEventListener("resize", function () {
                var canvas = myPlayer.getChild('Canvas');
                if(canvas) canvas.handleResize();
            });
        
            var videoElement = document.getElementById("player_video");
            var width = videoElement.offsetWidth;
            var height = videoElement.offsetHeight;
            myPlayer.width(width), myPlayer.height(height);
            myPlayer.panorama({
              clickToToggle: (!isMobile()),
              clickAndDrag: true,
              autoMobileOrientation: true,
              backToVerticalCenter: false,
              backToHorizonCenter: false,
              initFov: 100,
              VREnable: false,
              NoticeMessage: (isMobile())? NoticeMessageMobile : NoticeMessageMouse,
              callback: function () {
                //if(!isMobile()) myPlayer.play();
              }
            });
        }
        //end if video 360

        myPlayer.on('loadstart', loadstart);
        myPlayer.on('loadedmetadata', loadedmetadata);
        myPlayer.on('error', error); // error log for dev
        myPlayer.on('durationchange', loadChapBar);
        myPlayer.on('progress', progress);
        myPlayer.on('timeupdate', timeupdate);
         myPlayer.on('firstplay', function(){
            $.post(
                location,
                {
                    action: 'increase_view_count'
                },
                function(data) {
                }
            );
        });
        myPlayer.on('fullscreenchange', function() {
            if ($('#player_video').hasClass('vjs-fullscreen')) {
                slide_height = 96;
                $('.vjs-slide').height( '96%' );
                $('.vjs-title').css('font-size', '8em');
            } else {
                slide_height = 90;
                $('.vjs-slide').height( '90%' );
                $('.vjs-title').css('font-size', '3em');
            }
        });

        // Load plugin
        var defsize = decodeURIComponent($.urlParam('size'));
        if (defsize != '480' && defsize != '720') {
            defsize = 240;
        }
        myPlayer.resolutionSelector({default_res : ''+defsize});

        if ($('ul#slides li[data-type!="None"]').length > 0) {
            myPlayer.displaySelector({
                default_disp: '100/0',
                list_disp: list_disp
            });
        }
        $('ul#slides').hide();

        if ($('ul#chapters li').length > 0) {
            var list_chap = {};
            $('ul#chapters li').each(function () {
                list_chap[$(this).attr('data-start')] = $(this).attr('data-title');
            });
            myPlayer.chapterSelector({
                list_chap : list_chap
            });
            $('ul#chapters').hide();
        }

        $('div.vjs-slide').hide();
        $('div.vjs-title').hide();

        myPlayer.on('changeRes', function() {
            changeRes = true;
        });
        myPlayer.on('changeDisp', function() {
            isPlaying = !myPlayer.paused();
            changeDisplay(myPlayer.getCurrentDisp());
        });

        // LOAD Z-INDEX
        $('video').css('zIndex', videozindex + 1);
        $('.vjs-slide').css('zIndex', videozindex + 2);
        $('.vjs-title').css('zIndex', videozindex + 3);
        $('.vjs-big-play-button').css('zIndex', videozindex + 5);
        $('.vjs-loading-spinner').css('zIndex', videozindex + 6);
        $('.vjs-text-track-display').css('zIndex', videozindex + 7);
        $('.vjs-control-bar').css('zIndex', videozindex + 8);

        var IS_MOBILE = /mobile|android/i.test (navigator.userAgent);
        var IS_IPHONE = (/iPhone/i).test(navigator.userAgent);
        var IS_IPAD = (/iPad/i).test(navigator.userAgent);
        var IS_IPOD = (/iPod/i).test(navigator.userAgent);
        var IS_IOS = IS_IPHONE || IS_IPAD || IS_IPOD;
        var IS_ANDROID = (/Android/i).test(navigator.userAgent);
        /*************************************************************************/
        if (is_iframe === true) {
            $('div#info_video')
                .appendTo($('#player_video'))
                .attr(
                    'style',
                    'z-index: ' + (videozindex + 3) + ';' +
                    'position: absolute;' +
                    'top: 10%;' +
                    'left: 10%;' +
                    'width: 80%;' +
                    'height: 80%;' +
                    'background-color: #fff;'
                )
                .hide();
            $('#player')
                .css('padding', 0)
                .css('overflow', 'hidden');
            $('body').attr('style', 'margin: 0;padding: 0;overflow: hidden;');
            $('#player_video').attr('style', 'position:absolute; top:0; left:0; width:100%; height:100%');
            $('#page-video')
                .height('100%')
                .css('overflow', 'hidden');
            $('.vjs-big-play-button').css('zIndex', videozindex + 4);
            videojs.Info = videojs.Button.extend({
                /** @constructor */
                init: function(player, options) {
                    videojs.Button.call(this, player, options);
                    this.on('click', this.onClick);
                }
            });

            videojs.Info.prototype.onClick = function() {
                if ($('div#info_video').is(':visible')) {
                    $('div#info_video').hide();
                } else {
                    $('div#info_video').show();
                }
            };

            // Note that we're not doing this in prototype.createEl() because
            // it won't be called by Component.init (due to name obfuscation).
            var createInfoButton = function() {
                var props = {
                    className: 'vjs-info-button vjs-control',
                    innerHTML: '<div class="vjs-control-content"><span class="vjs-control-text">' + ('Info') + '</span></div>',
                    role: 'button',
                    'aria-live': 'polite', // let the screen reader user know that the text of the button may change
                    tabIndex: 0
                  };
                return videojs.Component.prototype.createEl(null, props);
            };

            var info;
            videojs.plugin('info', function() {
                var options = {'el': createInfoButton()};
                info = new videojs.Info(this, options);
                this.controlBar.el().appendChild(info.el());
            });

            myPlayer.info({});
        }
        /*************************************************************************/
        if (isMobile()) {
            if (is_iframe === false && ($('ul#slides li[data-type!="None"]').length > 0 || $('ul#chapters li').length > 0)) {
                $('#player').after('<nav class="navbar navbar-default" role="navigation"><div class="collapse navbar-collapse" ><ul class="nav navbar-nav" id="mobile_info"></ul></div></nav>');
                if ($('ul#slides li[data-type!="None"]').length > 0) {
                    var disp_html = '<li id="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Display <b class="caret"></b></a><ul id="mobile_disp" class="dropdown-menu">';
                    for (var disp in list_disp) {
                        disp_html += '<li><a href="#'+disp+'">'+list_disp[disp]+'</a></li>';
                    }
                    disp_html += '</ul></li>';
                    $('#mobile_info').append(disp_html);

                    $('#mobile_disp a').click(function(e) {
                        e.preventDefault();
                        $('#mobile_disp a').removeClass();
                        $(this).addClass('current');
                        myPlayer.currentDisp = $(this).attr('href').replace('#', '');
                        changeDisplay($(this).attr('href').replace('#', ''));
                    });
                }
                if ($('ul#chapters li').length > 0) {
                    var chap_html = '<li id="dropdown"><a href="#" class="dropdown-toggle" data-toggle="dropdown">Chapter(s) <b class="caret"></b></a><ul id="mobile_chap" class="dropdown-menu">';
                    for (var chap in list_chap) {
                        chap_html += '<li><a href="#'+chap+'" >'+list_chap[chap]+'</a></li>';
                    }
                    chap_html += '</ul></li>';
                    $('#mobile_info').append(chap_html);
                    $('#mobile_chap a').click(function(e) {
                        e.preventDefault();
                        $('#mobile_chap a').removeClass();
                        $(this).addClass('current');
                        myPlayer.currentTime($(this).attr('href').replace('#', ''));
                    });
                }
            }
        } else {
            // On a ajoute l'overview
            if ($('.vjs-control-bar').length && overview && overview != '') {
                // Not using jquery to improve perf
                $('.vjs-control-bar').append(
                    '<div id="preview" hidden style="display:none;">' +
                        '<img src="' + overview + '" id="previewimg" style="position:absolute" />' +
                    '</div>'
                );
                $('#preview').css('zIndex', videozindex + 5);
                var pre = $('#preview').get(0);
                var preimg = $('#previewimg').get(0);
                pre.style.width = (overview_width / 100) + 'px';
                pre.style.height = overview_height + 'px';
                pre.style.top = 0 - ($('.vjs-control-bar').height() + $( '#preview' ).height()) + 'px';
                preimg.style.top = '0px';
                var progressControl = myPlayer.controlBar.progressControl;

                $('.vjs-progress-holder').mousemove(function(event) {
                    left = event.pageX || (event.clientX + document.body.scrollLeft + document.documentElement.scrollLeft);
                    // Subtract the page offset of the progress control
                    left -= progressControl.el().getBoundingClientRect().left + window.pageXOffset;
                    percent  = (left / progressControl.el().getBoundingClientRect().width) * 100;

                    left = left - (pre.offsetWidth / 2);

                    if (left < 0) {
                        left = 0;
                    } else if (left > (progressControl.el().getBoundingClientRect().width - pre.offsetWidth)) {
                        left = progressControl.el().getBoundingClientRect().width - pre.offsetWidth;
                    }
                    pre.style.left = left + 'px';
                    preimg.style.left = '-' + parseInt(percent) * overview_width / 100 + 'px';
                });
                $('.vjs-progress-holder').mouseenter(function(event) {
                    pre.hidden = false;
                    pre.style.display = 'block';
                });
                $('.vjs-progress-holder').mouseleave(function(event) {
                    pre.hidden = true;
                    pre.style.display = 'none';
                });
            }
        }
        /*************************************************************************/
        if ( player_logo_img ) {

            var logoImg = document.createElement( 'img' );

            logoImg.setAttribute( 'src', player_logo_img );
            logoImg.setAttribute( 'alt', player_logo_alt );
            logoImg.setAttribute( 'height', '90%' );
            logoImg.setAttribute( 'style', "font-size: 1.6em; line-height: 1.9em; font-weight: bold;" );

            if ( player_logo_url ) {

                var logoLink = document.createElement( 'a' );

                logoLink.setAttribute( 'href', player_logo_url );
                logoLink.setAttribute( 'target', "_blank" );
                logoLink.setAttribute( 'title', player_logo_title );
                logoLink.setAttribute( 'role', "link" );

                logoLink.appendChild( logoImg );

                myPlayer.controlBar.el( ).appendChild( logoLink );

            } else {

                myPlayer.controlBar.el( ).appendChild( logoImg );

            }
        }
        /*************************************************************************/
        start = decodeURIComponent($.urlParam('start'));
    });
}

function changeDisplay(disp, duration) {
    duration = (typeof duration == 'undefined' ? 500 : duration);
    vid_width = parseInt(disp.split('/')[0]);
    slide_width = parseInt(disp.split('/')[1]);

    if (animation_complete === true) {
        animation_complete = false;
        if (vid_width == 100 && slide_width > 0) {
            $('video').css('zIndex', videozindex + 1);
            $('.vjs-slide').css('zIndex', videozindex + 2);

            $('.video-js .vjs-tech').animate(
                {
                    width: vid_width + '%',
                    height: '100%',
                    left: '0%'
                },
                duration
            );
            $('.video-js .vjs-slide').animate(
                {
                    width: slide_width + '%',
                    height: slide_width + '%',
                    left: (100 - slide_width) + '%'
                },
                duration,
                function() {
                    animation_complete = true;
                    if($('.vjs-slide article img').length) {
                        var top = parseInt(($('.vjs-slide article').height()-$('.vjs-slide article img').height())/2);
                        $('.vjs-slide article img').attr("style","top:"+top+"px;position:relative;");
                    }
                }
            );
        } else {
            if (slide_width == 100 && vid_width > 0) {
                $('video').css('zIndex', videozindex + 2);
                $('.vjs-slide').css('zIndex', videozindex + 1);
                $('.video-js .vjs-tech').animate(
                    {
                        width: vid_width + '%',
                        height: vid_width + '%',
                        left: '0%'
                    },
                    duration
                );
                $('.video-js .vjs-slide').animate(
                    {
                        width: slide_width + '%',
                        height: slide_height + '%',
                        left: (100 - slide_width) + '%'
                    },
                    duration,function() {
                        animation_complete = true;
                        if($('.vjs-slide article img').length) {
                            var top = parseInt(($('.vjs-slide article').height()-$('.vjs-slide article img').height())/2);
                            $('.vjs-slide article img').attr("style","top:"+top+"px;position:relative;");
                        }
                    }
                );
            } else {
                $('.video-js .vjs-tech').animate(
                    {
                        width: vid_width + '%',
                        height: '100%',
                        left: '0%'
                    },
                    duration
                );
                $('.video-js .vjs-slide').animate(
                    {
                        width: slide_width + '%',
                        height: slide_height + '%',
                        left: (100 - slide_width) + '%'
                    },
                    duration,
                    function() {
                        animation_complete = true;
                        if($('.vjs-slide article img').length) {
                            var top = parseInt(($('.vjs-slide article').height()-$('.vjs-slide article img').height())/2);
                            $('.vjs-slide article img').attr("style","top:"+top+"px;position:relative;");
                        }
                    }
                );
            }
        }
        if (isPlaying) {
            myPlayer.play();
        } else {
            myPlayer.pause();
        }
    }
}

$(document).on(
    'click',
    'button#button_video_note',
    function (event) {
        event.preventDefault();
        if (expiration_date_second > 5) {
            var jqxhr = $.post(
                $( '#video_note_form' ).attr('action'),
                $( '#video_note_form' ).serialize(),
                function(data) {
                    var alert_text =
                        '<div class="alert alert-info" id="myAlert">' +
                            '<a href="#" class="close" data-dismiss="alert">&times;</a>' +
                            data +
                        '</div>';
                    $('body').append(alert_text);
                    $('#myAlert').on('closed.bs.alert', function () {
                        $(this).remove();
                    });
                    $('#myAlert').alert();
                    window.setTimeout(function() { $('#myAlert').alert('close'); }, 3000);
                }
            );
            jqxhr.fail(function(data) {
                alert('Error '+data);
            });
        } else {
            alert(expiredsession);
            location.reload();
        }
    }
);

function timeupdate(event) {
    var t = myPlayer.currentTime();
    var all = timestamps.length;
    var slide = false;
    var change_slide = false;
    var current_slide_type = 'None';

    var i = 0;
    for (i; i < all; i++) {
        if (t >= timestamps[i].start && t <= timestamps[i].end) {
            slide = true;

            if (currentslide != $(timestamps[i].elm).attr('data-id')) {
                if ($(timestamps[i].elm).data('stop-video') == 'True') {
                    myPlayer.pause();
                }
                isPlaying = !myPlayer.paused();

                if ($(timestamps[i].elm).data('type') != 'None') {
                    if(!$('.vjs-slide').is(':visible')) {
                        $('.vjs-slide').show();
                        // performClick
                        $('div.vjs-disp-button').find('li.vjs-menu-item:contains(' + defaultDisp + ')').trigger('click');
                        if ((myPlayer.currentDisp == defaultDisp) == false) {
                            myPlayer.currentDisp = defaultDisp;
                            changeDisplay(defaultDisp);
                        }
                    }
                }

                timestamps[i].elm.addClass('current');
                change_slide = true;
                currentslide = $(timestamps[i].elm).attr('data-id');
                current_slide_type = $(timestamps[i].elm).attr('data-type');
                $('.vjs-slide').html('&nbsp;');
                if (current_slide_type != 'None') {
                    var noscriptContents = $($(timestamps[i].elm).find('noscript').text());
                    $('.vjs-slide').html('<article>&nbsp;</article>');
                    $('.vjs-slide article').append(noscriptContents);
                }

                // Show title on overlay
                $('.vjs-title')
                    .text($(timestamps[i].elm).attr('data-title'))
                    .fadeIn('slow')
                    .delay(3000)
                    .fadeOut('slow');
                break;
            }
        } else {
            timestamps[i].elm.removeClass('current');
        }
    }

    if (slide == true && change_slide == true ) {
        isPlaying = !myPlayer.paused();
        if (current_slide_type != 'None') {
            changeDisplay(myPlayer.getCurrentDisp(), 1000);
        } else {
            changeDisplay('100/0');
        }
    }
    if (currentslide != '' && slide == false ){
        for (i = 0; i < all; i++) {
            if (t < timestamps[i].start) {
                break;
            }
        }
        isPlaying = !myPlayer.paused();
        currentslide = '';
        $('.vjs-slide').html('&nbsp;');
        $('.vjs-title').text('').hide();
        if (i == all || timestamps[i].start-parseInt(t) > 2) {
            changeDisplay('100/0', 1000);
        }
    }

}

$.urlParam = function(name) {
    var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null){
       return null;
    } else {
       return results[1] || 0;
    }
};

function loadstart() {
    if (changeRes == true) {
        changeRes = false;
        myPlayer.play();
    } else {
        if (start && start != 'null' && start !=0) {
            myPlayer.play();
        } else if (typeof is_chaptering != 'undefined' && is_chaptering == true) {
            myPlayer.play();
        }
    }
}

function loadedmetadata() {
    if (changeRes == false && start && start != 'null' && start != 0) {
        myPlayer.currentTime(start);
    }
}


function loadChapBar() {
    if ($('ul#slides').length != 0) {
        $('div.vjs-title').appendTo($('#player_video'));
        $('div.vjs-slide').appendTo($('#player_video'));

        if ($('.vjs-chapbar-holder').length == 0) {
            if ($('div.vjs-progress-holder').length == 0) {
                $('#player_video').append(
                    '<div class="vjs-chapbar"><div class="vjs-chapbar-holder"></div></div>'
                );
            } else {
                $('div.vjs-progress-holder').append(
                    '<div class="vjs-chapbar"><div class="vjs-chapbar-holder"></div></div>'
                );
            }
        } else {
            $('.vjs-chapbar-holder').html('');
        }

        if (myPlayer.duration() != 0) {
            var duration_vid = myPlayer.duration();
            $('ul#slides li').each(function() {
                var chapbar_left = (parseInt($(this).data('start')) / duration_vid) * 100;
                var chapbar_width = ((parseInt($(this).data('end')) / duration_vid) * 100) - chapbar_left;
                var data_id = $(this).data('id');
                $('.vjs-chapbar-holder').append(
                    '<div ' +
                        'class="vjs-chapbar-chap" ' +
                        'style="left:' + chapbar_left + '%;width:' + chapbar_width + '%;" ' +
                        'data-id="' + data_id + '"' +
                    '></div>'
                );
                if ($(this).attr('data-start')) {
                    timestamps.push({
                        start : +$(this).attr('data-start'),
                        end : +$(this).attr('data-end'),
                        elm : $(this)
                    });
                }
            });
            /*
            if (typeof is_chaptering != 'undefined' && is_chaptering == true) {
                $('.vjs-chapbar-chap').on('click', function(e) {
                    chapbar($(this));
                });
            }
            */
        }
    }
}

/**
 * Calcule de manière automatique la résolution la plus optimisée pour le débit de la connexion de l'utilisateur
 */
function progress() {
    if (typeof myPlayer.availableRes != 'undefined' && myPlayer.availableRes.length > 0 && changeResBd == false) {
        var howMuchIsDownloaded = myPlayer.bufferedPercent();
        var seconds = Math.round(Date.now() / 1000);
        var filesize = myPlayer.currentSrc().indexOf('video/mp4') != -1 ? videosize_mp4 : videosize_webm;

        if (seconds != previoustime && howMuchIsDownloaded < 1) {
            intcheck++;
            var lapstime = seconds - previoustime;
            if(previoustime==0) lapstime = 1;
            var downloaded = filesize * howMuchIsDownloaded;
            var laspdl = downloaded - previousuploaded;
            mediumspeed = mediumspeed + Math.round((laspdl / lapstime) / 1000);

            if (intcheck % 4 == 0) {
                mediumspeed = mediumspeed / 4;
                if (mediumspeed > 2200 && typeof myPlayer.availableRes['1080'] != 'undefined') {
                    $('div.vjs-res-button').find('li:contains("1080p")').trigger('click');
                    changeResBd = true;
                } else {
                    if (mediumspeed > 1200 && typeof myPlayer.availableRes['720'] != 'undefined') {
                        $('div.vjs-res-button').find('li:contains("720p")').trigger('click');
                        changeResBd = true;
                    } else {
                        if (mediumspeed > 700 && typeof myPlayer.availableRes['480'] != 'undefined') {
                            $('div.vjs-res-button').find('li:contains("480p")').trigger('click');
                            changeResBd = true;
                        }
                    }
                }
            } else if (howMuchIsDownloaded == 1) {
                $($('div.vjs-res-button li').get(1)).trigger('click'); // 0 is quality so 1 is the highest resolution
                changeResBd = true;
            }

            previoustime = seconds;
            previousuploaded = downloaded;
        } else if (howMuchIsDownloaded == 1) {
            $($('div.vjs-res-button li').get(1)).trigger('click'); // 0 is quality so 1 is the highest resolution
            changeResBd = true;
        }
    }
}

function error(err) {
    // prints the name of the error
    // alert(err.name);
    // prints the description that is also shown in the error console
    console.log(err.message);
    // this works only in some browsers
    // line and stack are not supported by all vendors
    console.log(err.line, err.stack);
}
