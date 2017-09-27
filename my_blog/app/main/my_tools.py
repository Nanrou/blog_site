import re
from calendar import Calendar
from datetime import datetime, date

from playhouse.flask_utils import PaginatedQuery

from . import main
from ..models import Post
from app import cache


@main.add_app_template_filter
def my_html_truncate(s, length=255, killwords=False, end='...'):
    assert length >= len(end), 'expected length >= %s, got %s' % (len(end), length)
    if len(s) <= length:
        return s
    if killwords:
        return s[:length - len(end)] + end
    result = s[:length - len(end)].rsplit(' ', 1)[0].rsplit('<', 1)[0]
    return re.sub(re.compile(r'</?.*?>'), '', result) + end


@main.add_app_template_filter
def my_time_format(timestamp, verbose=False):
    _timestamp = date(timestamp.year, timestamp.month, timestamp.day)
    _now = date.today()
    _timedelta = (_now - _timestamp).days
    if _timedelta < 1:
        _format = '{:%H:%M}'
    elif _timedelta < 2:
        _format = '昨天 {:%H:%M}'
    elif _timedelta < 3:
        _format = '前天 {:%H:%M}'
    else:
        _format = '{:%y/%m/%d %H:%M}'
    return _format.format(timestamp)


class MyPaginatedQuery(PaginatedQuery):
    """
    就是增加了一个可以手动指定页数的功能
    """
    def get_page(self):
        try:
            return int(self.page_var)
        except TypeError:
            super().get_page()


month_dict = {'9': '九月布鲁'}


@main.app_context_processor
def product_month():
    rv = cache.get('month_content')
    if rv is None:
        cc = Calendar(firstweekday=6)
        now_ = datetime.now()
        month_html = ''
        for week in cc.monthdatescalendar(now_.year, now_.month):
            week_html = ''
            for day in week:
                if day.month == now_.month:
                    dh = datetime(year=now_.year, month=now_.month, day=day.day, hour=23, minute=59, second=59)
                    dm = datetime(year=now_.year, month=now_.month, day=day.day)
                    _count = Post.select(Post.timestamp).where(Post.timestamp.between(dm, dh)).count()
                    if not bool(_count):
                        _class = ''
                        content = '不宜写作,{}'.format(day)
                    elif _count > 1:
                        _class = ' class="more"'
                        content = '哇！这天有{}篇'.format(_count)
                    else:
                        _class = ' class="less"'
                        content = '好像有东西,{}'.format(day)
                    day_html = '<td{class_}><a href="#" data-toggle="tooltip" data-original-title="{content}"><div style="width: 100%; height:100%;"></div></a></td>'\
                        .format(class_=_class, content=content)
                else:
                    day_html = '<td class="noday"></td>'
                week_html += day_html
            week_html = '<tr>' + week_html + '</tr>'
            month_html += week_html

        ss = '''<table class="calendar"><tbody><tr><th class="month" colspan="7">{month}</th></tr>
    <tr>
        <th class="sun">Sun</th>
        <th class="mon">Mon</th>
        <th class="tue">Tue</th>
        <th class="wed">Wed</th>
        <th class="thu">Thu</th>
        <th class="fri">Fri</th>
        <th class="sat">Sat</th>
    </tr>
    {td}
    </tbody>
</table>'''
        rv = dict(product_calendar=ss.format(
            month=month_dict[str(now_.month)], td=month_html).replace('\n', '').replace('    ', ''))
        cache.set('month_content', rv, timeout=5 * 60)
    return rv


if __name__ == '__main__':
    print('i in my tools')
