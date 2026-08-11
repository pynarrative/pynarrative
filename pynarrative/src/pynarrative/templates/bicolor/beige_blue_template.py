from copy import deepcopy

from ..layout import DefaultLayout, Layout
from ..style import DefaultStyle, Style
from ..template import Template

primary_color = "#c2a46c" #highlighted bar
tab_color = "#e0d1b4"
tab_border_color = primary_color

secondary_color = "#6C8AC2" #normal bars

text_color = "#000000"
highlight_color = "#bf2626"


text_areas_background = True
if not text_areas_background:
    tab_color = "#ffffff"


class BeigeBlueStyle(Style):
    """
    Style values.
    """

    def __init__(self):
        base = DefaultStyle()
        super().__init__(deepcopy(base.data))

        self.set_font('Noto Sans')
        self.set_base_font_size(12)
        self.set_font_sizes(
            title=1.6,
            subtitle=1.3,
            context=1.3,
            source=0.95,
        )

        self.set_colors(
            #TITOLO e SOTTOTITOLO
            title = text_color,
            subtitle = text_color,

            #CONTESTO 1
            context = text_color,

            #BARRE
            bar_muted = secondary_color,
            bar_highlight = primary_color,

            #ANNOTAZIONE
            callout_text = highlight_color,
            callout_arrow = highlight_color,
            callout_point = highlight_color,

            #NEXTSTEP
            nextstep_box = tab_color,
            nextstep_border = tab_border_color,
            nextstep_text = text_color,
            nextstep_title = text_color,

            #FONTE
            source = text_color,

            #LABEL
            chart_label_color = text_color
        )

        self.set_context_box(
            #CONTESTO 
            fill = tab_color,
            stroke = tab_border_color,
            padding=10,
            corner_radius=10,
            opacity=1.0,
        )

        self.set(
            title_color=self.get_colors()['title'],
            label_color='#594a37',
            axis_tick_color='#d8c9ad',
            axis_domain_color='#d8c9ad',
            bar_fill_color = secondary_color,

            series_colors = [secondary_color, primary_color, "#348035", "#a46cc2", "#d96027"],

            reference_line_color = highlight_color, #linea orizzontale/verticale
        )


class BeigeBlueLayout(Layout):
    """
    Layout values.
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


class BeigeBlueTemplate(Template):
    """
    Custom style template.
    """

    def __init__(self):
        super().__init__(
            style=BeigeBlueStyle(),
            layout=BeigeBlueLayout(),
        )
