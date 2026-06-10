from copy import deepcopy

from .layout import DefaultLayout, Layout
from .style import DefaultStyle, Style
from .template import Template


class HistoricalStyle(Style):
    """
    Historical style values.
    """

    def __init__(self):
        base = DefaultStyle()
        super().__init__(deepcopy(base.data))

        self.set_font('Garamond')
        self.set_base_font_size(16)
        self.set_font_sizes(
            title=1.6,
            subtitle=1.2,
            context=1.3,
            source=0.95,
        )

        self.set_colors(
            title='#3b2f1f',
            subtitle='#5f4f3a',
            context='#2f271b',
            bar_highlight='#8a6237',
            bar_muted='#d8c9ad',
            callout_text='#2f271b',
            callout_arrow='#7c5c33',
            callout_point='#7c5c33',
            nextstep_box='#efe3ce',
            nextstep_border='#d1bd97',
            nextstep_text='#2f271b',
            nextstep_title='#3b2f1f',
            source='#6b5b45',
        )

        self.set_context_box(
            fill='#efe1c2',
            stroke='#c7ab7a',
            padding=10,
            corner_radius=10,
            opacity=1.0,
        )

        self.set(
            title_color=self.get_colors()['title'],
            label_color='#594a37',
            axis_tick_color='#d8c9ad',
            axis_domain_color='#d8c9ad',
            bar_fill_color='#8a6237',
            series_colors=['#8a6237', '#b08a5b', '#6f7d4e', '#6a4b33'],
            reference_line_color='#8a6237',
        )


class HistoricalLayout(Layout):
    """
    Historical layout values.
    """

    def __init__(self):
        base = DefaultLayout()
        super().__init__(deepcopy(base.data))

        self.set(
            title_area_height=58,
            title_y=4,
            subtitle_y=30,
            preferred_width=760,
            preferred_height=560,
            context_left_height_ratio=1.0,
            context_right_height_ratio=1.0,
        )


class HistoricalTemplate(Template):
    """
    Historical style template.
    """

    def __init__(self):
        super().__init__(
            style=HistoricalStyle(),
            layout=HistoricalLayout(),
        )
