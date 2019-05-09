function mark_comment() {
    var mark = 0;
    var comment = '';

    Array.from($('.list').find('input')).forEach(function (input) {
        if ($(input).attr('type') === 'number' && $(input).val() !== '0') {
            var koef = parseInt($(input).val());
            var text = $($($(input).parent()).find('.label-text').eq(0)).html();
            var points = parseFloat(text.split(' ')[0]);
            mark += koef * points;
            if (koef === 1) {
                comment += text + '\n';
            } else {
                comment += koef + ' * ' + text + '\n';
            }
        } else if ($(input).attr('type') === 'checkbox' && input.checked) {
            var text = $($($(input).parent()).find('.label-text').eq(0)).html();
            var points =  parseFloat(text.split(' ')[0]);
            mark += points;
            comment += text + '\n';
        }
    });
    mark = 10 + mark;
    comment += 'Оценка: ' + mark;
    $('#id_mark').attr('value', mark);
    $('#id_comment').html(comment);
}

$(document).ready(function () {
    $('.list').on('change', 'input', mark_comment);
});