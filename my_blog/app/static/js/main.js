
// Navigation Scripts to Show Header on Scroll-Up
jQuery(document).ready(function($) {
    var MQL = 768;

    //primary navigation slide-in effect
    if ($(window).width() > MQL) {
        var headerHeight = $('#mainNav').height();
        $(window).on('scroll', {
                previousTop: 0
            },
            function() {
                var currentTop = $(window).scrollTop();
                //check if user is scrolling up
                if (currentTop < this.previousTop) {
                    //if scrolling up...
                    if (currentTop > 0 && $('#mainNav').hasClass('is-fixed')) {
                        $('#mainNav').addClass('is-visible');
                        $('#to_top').addClass('is-unvisible');
                    } else {
                        $('#mainNav').removeClass('is-visible is-fixed');
                        
                    }
                } else if (currentTop > this.previousTop) {
                    //if scrolling down...
                    $('#mainNav').removeClass('is-visible');
                    $('#to_top').removeClass('is-unvisible');
                    if (currentTop > headerHeight && !$('#mainNav').hasClass('is-fixed')){
                        $('#mainNav').addClass('is-fixed');
                        
                    }
                }
                this.previousTop = currentTop;
            });
    };
    $("#to_top").click(function() {
        $("html,body").animate({"scrollTop":0}, 200);
    });
    
    var _comment_btn = true;
    
    $("#main_comment_btn").click(function() {
        if (_comment_btn) {
            $("#main_comment_form").slideDown("middle");
            $("#main_comment_btn").text("收起");
            _comment_btn = false; 
        } else {
            $("#main_comment_form").slideUp("middle");
            $("#main_comment_btn").text("说点什么罗");
            _comment_btn = true; 
        }
        
    });
    
    $("#submit").click(function() {  // 要改成对应的form的响应
        $('#main_comment_message').fadeIn();
    });
    
});

NProgress.configure({ showSpinner: false });

$(document).ready(function(){
    NProgress.start();
});
$(window).on('load', function(){   // jQuery1.8后移除了load，要用on
    NProgress.done();
    //$(login_form).attr("onsubmit", "return PostData()");
});  

function PostData() {
    var _data = $('#login_form').serialize();
        $.ajax({
            type: "POST",
            url: "",
            data : _data,
            success: function(msg) {
                $('#login_message_p').text(msg.error_msg);
                $('#login_message').fadeIn();
            }
        });
        return false;
    }

function getCalendar (s) {
    if (typeof($("#btn_next").attr("disable"))!="undefined") {
        return
    }
    
    var month = $('.month:first').text();
    var prev = true;
    
    $('#calendar').mLoading('show');
    
    if (s == 'next') {
        prev = false;
    }
    var _data = {'month': month, 'prev': prev,}
    $.ajax({
        type: "POST",
        url: "/getcalendar",
        data : _data,
        success: function(msg) {
            $('#calendar').html(msg.calendar.product_calendar);
            
            $('#calendar').mLoading('hide');
        },
        error: function(msg) {
            $('#calendar').mLoading('hide');
            $('#calendar_message').fadeIn();
            $('#btn_prev, #btn_next').attr('disable', 'true');
            setTimeout("$('#btn_prev, #btn_next').removeAttr('disable');", 5000);
        }
    });
};