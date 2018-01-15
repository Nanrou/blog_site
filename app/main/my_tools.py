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


month_dict = {'1': '一月打机',
              '2': '二月大力',
              '3': '三月减肥',
              '4': '四月失败',
              '5': '五月干嘛',
              '6': '六月过半',
              '7': '七月**',
              '8': '八月',
              '9': '九月布鲁',
              '10': '十月图强',
              '11': '十一月太迟',
              '12': '十二月明年见',
              }
another_month_dict = {'一月打机': 1,
                      '二月大力': 2,
                      '三月减肥': 3,
                      '四月失败': 4,
                      '五月干嘛': 5,
                      '六月过半': 6,
                      '七月**': 7,
                      '八月': 8,
                      '九月布鲁': 9,
                      '十月图强': 10,
                      '十一月太迟': 11,
                      '十二月明年见': 12,
                      }


@main.app_context_processor
def product_month(month=None, flag=None):
    """
    生成目标月份的文章列表结果的html，现在只做了月份判断，并未做年份判断
    :param month:
    :param flag:
    :return:
    """
    now_ = datetime.now()
    month = month or now_.month
    if flag == 'last_year':
        year = now_.year - 1
    elif flag == 'next_year':
        year = now_.year + 1
    else:
        year = now_.year

    rv = cache.get('month_content_{}'.format(month))
    if rv is None:
        cc = Calendar(firstweekday=6)
        month_html = ''
        for week in cc.monthdatescalendar(now_.year, month):
            week_html = ''
            for day in week:
                if day.month == month:
                    dh = datetime(year=year, month=month, day=day.day, hour=23, minute=59, second=59)
                    dm = datetime(year=year, month=month, day=day.day)
                    _count = Post.select(Post.timestamp).where(Post.timestamp.between(dm, dh)).count()
                    if not bool(_count):
                        _class = ''
                        content = '不宜写作,{}'.format(day)
                        action = 'javascript:void(0);'
                    elif _count > 1:
                        _class = ' class="more"'
                        content = '哇！这天有{}篇'.format(_count)
                        action = '/search?date={:%Y-%m-%d}'.format(dm)
                    else:
                        _class = ' class="less"'
                        content = '好像有东西,{}'.format(day)
                        action = '/search?date={:%Y-%m-%d}'.format(dm)
                    day_html = '<td{class_}><a href="{action}" data-toggle="tooltip" data-original-title="{content}"><div style="width: 100%; height:100%;"></div></a></td>'\
                        .format(class_=_class, action=action, content=content)
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
            month=month_dict[str(month)], td=month_html).replace('\n', '').replace('    ', ''))
        cache.set('month_content_{}'.format(month), rv, timeout=5 * 60)
    return rv


if __name__ == '__main__':
    print('i in my tools')
