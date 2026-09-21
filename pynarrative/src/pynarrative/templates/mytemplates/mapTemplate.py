from copy import deepcopy
from pynarrative.templates.layout import DefaultLayout, Layout
from pynarrative.templates.style import DefaultStyle, Style
from pynarrative.templates.template import Template

#Font options
font_family = "Montserrat"
title_font_family = "Montserrat"
standard_font_size = 12
title_font_size_multiplier = 1.9
subtitle_font_size_multiplier = 1.4
context_font_size_multiplier = 1.2
nextstep_font_size_multiplier = 1.2
annotation_font_size = 12

#Color options
main_color = "rgb(255, 161, 117)"
secondary_color = "rgb(215, 121, 77)"
tab_color = "rgb(255, 255, 255)"
ta_border_color = "rgb(214, 76, 76)"
ns_color = "rgb(255, 255, 255)"
ns_border_color = "rgb(214, 76, 76)"
annotation_color = "rgb(255, 255, 255)"
annotation_border_color = "rgba(0, 0, 0, 0)"
lines_color = "rgb(191, 38, 38)"
title_color = "#000000"
title_background_color = "#ffffff"
text_color = "rgb(0, 0, 0)"
context_text_color = "rgb(0, 0, 0)"
ns_text_color = "rgb(0, 0, 0)"
annotation_text_color = "rgb(0, 0, 0)"

#Border options
def remove_px(val):
    val_str = str(val).lower().replace("px", "").strip()
    return float(val_str)
ta_border_radius = "16px"
ta_border_radius = remove_px(ta_border_radius)
ta_border_stroke = "2px"
ta_border_stroke = remove_px(ta_border_stroke)

ns_border_radius = "16px"
ns_border_radius = remove_px(ns_border_radius)
ns_border_stroke = "2px"
ns_border_stroke = remove_px(ns_border_stroke)

annotation_border_radius = "16px"
annotation_border_radius = remove_px(annotation_border_radius)
annotation_border_stroke = "2px"
annotation_border_stroke = remove_px(annotation_border_stroke)

class myStyle(Style):
    def __init__(self):
        base = DefaultStyle()
        super().__init__(deepcopy(base.data))

        self.set_font(font_family)
        self.set_title_font(title_font_family)
        self.set_base_font_size(int(standard_font_size))
        self.set_font_sizes(
            title = float(title_font_size_multiplier),
            subtitle = float(subtitle_font_size_multiplier),
            context = float(context_font_size_multiplier),
            nextstep = float(nextstep_font_size_multiplier),
            source = 0.9
        )

        #COLOR OPTIONS
        self.set_colors(
            #Title and subtitle colors
            title = title_color,
            title_background_color = title_background_color,
            subtitle = title_color,

            #Context area(s) text color
            context = context_text_color,

            #Bars colors (if bar chart is used)
            bar_muted = main_color,
            bar_highlight = secondary_color, #(if .add_highlight() method is used)

            #.add_annotation() color options
            callout_text = lines_color,
            callout_arrow = lines_color,
            callout_point = lines_color,
            annotation_fill = annotation_color,
            annotation_text = annotation_text_color,
            annotation_stroke = annotation_border_color,

            #Nextstep color options
            nextstep_box = ns_color,
            nextstep_border = ns_border_color,
            nextstep_text = ns_text_color,
            nextstep_title = ns_text_color,

            #Source text color
            source = text_color,

            #Label text color
            chart_label_color = text_color
        )

        self.set_context_box(
            #Context area(s) options 
            fill = tab_color,
            stroke = ta_border_color,
            padding = 25,
            corner_radius = ta_border_radius,
            opacity = 1.0,
        )

        self.set(
            #Other general options
            bar_fill_color = main_color,
            context_border_width = ta_border_stroke,
            nextstep_corner_radius = ns_border_radius,
            nextstep_border_width = ns_border_stroke,
            annotation_label_size = annotation_font_size,
            annotation_box_border_width = annotation_border_stroke,

            series_colors = [main_color, secondary_color, "#348035", "#a46cc2", "#d96027"],

            reference_line_color = lines_color, #horizontal and vertical lines
            reference_line_dash = [5, 5], #dash type
            text_wrap_char_width_ratio = 0.55, #parameter to modify text wrapping in text areas
          
 )


class myLayout(Layout):
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
            layout_context_side_width_ratio = 0.73, #title block width multiplier
            context_right_width_ratio = 0.5, #right context block width multiplier
            context_left_width_ratio = 0.6, #left context block width multiplier
            context_top_width_ratio = 1.7, #top context block width multiplier
            context_bottom_width_ratio = 1.7, #bottom context block width multiplier
        )


class mapTemplate(Template):
    """
    Custom style template.
    """

    def __init__(self):
        super().__init__(
            style=myStyle(),
            layout=myLayout(),
        )
