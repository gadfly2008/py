$(document).ready(function() {
    $(document).ajaxStart(function() {
        $("#contents").mask("Loading......");
    });
    
    $(document).ajaxStop(function() {
        $("#contents").unmask();
    });
});

function searchFocusSet(elem, content) {
    var value = elem.value;
    if (value == content) {
        $("input[type='text'][value="+ content +"]").removeClass('search_font_style');
        $("input[type='text'][value="+ content +"]").attr('value','');
    }
    else if (value != content) {
        $("input[type='text'][value="+ value +"]").removeClass('search_font_style');
    }
}

function searchBlurSet(elem, content) {
    var value = elem.value;
    if (value == '') {
        $("input[type='text'][value=]").addClass('search_font_style');
        $("input[type='text'][value=]").attr('value',content);
    }
    else if (value == content) {
        $("input[type='text'][value="+ content +"]").addClass('search_font_style');
    }
}