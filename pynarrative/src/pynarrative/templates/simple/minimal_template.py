from copy import deepcopy

from ..layout import DefaultLayout, Layout
from ..style import DefaultStyle, Style
from ..template import Template


class MinimalStyle(Style):
    """
    Minimal style values.
    """

    def __init__(self):
        base = DefaultStyle()
        super().__init__(deepcopy(base.data))

        self.set_font('Helvetica')
        self.set_font_sizes(
            title=1.6,
            subtitle=1.3,
            context=1.3,
            source=0.95,
        )
        self.set_base_font_size(12)
        self.set_context_box(
            fill='#ffffff',
            stroke='#ffffff',
            opacity=0.0,
            padding=4,
            corner_radius=0,
        )
        self.set(
            callout_box_opacity=0.0,
            callout_box_border_width=0,
            context_border_width=0,
            series_colors = ["#27A0D9", "#348035", "#c2a46c", "#a46cc2", "#d96027"],
            axis_grid=False,
        )


class MinimalLayout(Layout):
    """
    Minimal layout values.
    """

    def __init__(self):
        base = DefaultLayout()
        super().__init__(deepcopy(base.data))
        self.set(
            preferred_width=960,
            preferred_height=540,
        )


class MinimalTemplate(Template):
    """
    Minimal template: no background boxes for context and annotations.
    """

    def __init__(self):
        super().__init__(
            style=MinimalStyle(),
            layout=MinimalLayout(),
        )
