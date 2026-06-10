from copy import deepcopy

from .layout import DefaultLayout, Layout
from .style import DefaultStyle, Style
from .template import Template


class EnvironmentalStyle(Style):
    """
    Environmental style values.
    """

    def __init__(self):
        base = DefaultStyle()
        super().__init__(deepcopy(base.data))

        self.set_font('Helvetica')
        self.set_base_font_size(16)
        self.set_colors(
            title='#163b2d',
            subtitle='#2a5d49',
            context='#173a2d',
            bar_highlight='#2e7d32',
            bar_muted='#c9dece',
            callout_text='#173a2d',
            callout_arrow='#2e7d32',
            callout_point='#2e7d32',
            nextstep_box='#e7f4ea',
            nextstep_border='#b8dfbf',
            nextstep_text='#173a2d',
            nextstep_title='#163b2d',
            source='#4f6e60',
        )

        self.set_context_box(
            fill='#f3fbf4',
            stroke='#cfe8d1',
            padding=10,
            corner_radius=10,
            opacity=1.0,
        )

        self.set(
            title_color=self.get_colors()['title'],
            label_color='#355f4f',
            axis_tick_color='#c9dece',
            axis_domain_color='#c9dece',
            bar_fill_color='#2e7d32',
            series_colors=['#2e7d32', '#66bb6a', '#8d6e63', '#00796b'],
            reference_line_color='#2e7d32',
        )


class EnvironmentalLayout(Layout):
    """
    Environmental layout values.
    """

    def __init__(self):
        base = DefaultLayout()
        super().__init__(deepcopy(base.data))
        self.set(
            preferred_width=980,
            preferred_height=560,
        )


class EnvironmentalTemplate(Template):
    """
    Environmental style template for plant/ecosystem narratives.
    """

    def __init__(self):
        super().__init__(
            style=EnvironmentalStyle(),
            layout=EnvironmentalLayout(),
        )
