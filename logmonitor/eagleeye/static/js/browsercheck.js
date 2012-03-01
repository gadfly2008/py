$(document).ready(function() {
    if (!($.browser.webkit || $.browser.mozilla || $.browser.safari)) {
        $("#wrap").css('min-height', '480px');
        var html = "<div id='browser'>"
                        +"<div id='tips'><h3>为了大力推广HTML5和CSS3的使用，我们将只支持以下同学!</h3></div>"
                        +"<div id='example'><img src='/static/images/chrome.png'>"
                        +"<img src='/static/images/safari.png'>"
                        +"<img src='/static/images/firefox.png'></div>"
                  +"</div>";
        $("#wrap").html(html);
    }
});

