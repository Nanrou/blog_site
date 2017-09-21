import re

from . import main


@main.add_app_template_filter
def my_html_truncate(s, length=255, killwords=False, end='...'):
    assert length >= len(end), 'expected length >= %s, got %s' % (len(end), length)
    if len(s) <= length:
        return s
    if killwords:
        return s[:length - len(end)] + end
    result = s[:length - len(end)].rsplit(' ', 1)[0].rsplit('<', 1)[0]
    return re.sub(re.compile(r'</?.*?>'), '', result) + end


if __name__ == '__main__':
    print('i in my filter')
