from collections import UserDict


class Style(UserDict):
    """
    Visual styling container (fonts, colors, strokes, text styles).
    """

    def set(self, **kwargs):
        self.data.update(kwargs)
        return self

    @property
    def font(self):
        return self.data['font']

    @font.setter
    def font(self, value):
        self.data['font'] = value

    @property
    def base_font_size(self):
        return self.data['base_font_size']

    @base_font_size.setter
    def base_font_size(self, value):
        self.data['base_font_size'] = value

    @property
    def font_sizes(self):
        return self.data['font_sizes']

    @property
    def colors(self):
        return self.data['colors']

    @property
    def context_box(self):
        return self.data['context_box']

    def get_font(self):
        return self.font

    def set_font(self, font):
        self.font = font
        return self

    @property
    def title_font(self):
        return self.data.get('title_font', self.font)

    @title_font.setter
    def title_font(self, value):
        self.data['title_font'] = value

    def get_title_font(self):
        return self.title_font

    def set_title_font(self, title_font):
        self.title_font = title_font
        return self

    def get_base_font_size(self):
        return self.base_font_size

    def set_base_font_size(self, base_font_size):
        self.base_font_size = base_font_size
        return self

    def get_font_sizes(self):
        return self.font_sizes

    def set_font_sizes(self, **kwargs):
        self.font_sizes.update(kwargs)
        return self

    def get_colors(self):
        return self.colors

    def set_colors(self, **kwargs):
        self.colors.update(kwargs)
        return self

    def get_context_box(self):
        return self.context_box

    def set_context_box(self, **kwargs):
        self.context_box.update(kwargs)
        return self


class DefaultStyle(Style):
    """
    Default visual style values (fonts, colors, stroke/text settings).
    """
    def __init__(self):
        super().__init__({
            'font': 'Noto Sans',
            'title_font':"Noto Sans",

            'base_font_size': 12,
            'font_sizes': {
                'title': 1.6,
                'subtitle': 1.2,
                'context': 1,
                'nextstep': 1,
                'cta': 1,
                'source': 0.9,
                "line_label" : 1.5
            },
            'colors': {
                'title': '#000000',
                "title_background_color": "transparent",
                'subtitle': '#000000',
                'context': '#000000',
                'bar_highlight': '#A88A7C',
                'bar_muted': '#7C9AA8',
                'callout_text': '#000000',
                'callout_arrow': '#CBB9B1',
                'callout_point': '#CBB9B1',
                'nextstep': '#CBB9B1',
                'nextstep_box': '#CBB9B1',
                'nextstep_border': '#CBB9B1',
                'nextstep_text': '#000000',
                'nextstep_title': '#000000',
                'source': '#000000',
                'chart_label_color': "#000000",
                'annotation_fill': "#CBB9B185",
                'annotation_stroke': '#CBB9B1',
            },
            'context_box': {
                'fill': '#CBB9B1',
                'stroke': '#CBB9B1',
                'opacity': 1.0,
                'padding': 15,
                'corner_radius': 16,
            },
            'label_color': '#334e68',
            'title_color': '#0b1f3a',
            'axis_label_size': 13,
            'axis_title_size': 14,
            'legend_label_size': 12,
            'legend_title_size': 12,
            'axis_tick_color': '#c7d2fe',
            'axis_domain_color': '#c7d2fe',
            'axis_grid': False,
            'default_view_stroke_width': 0,
            'line_stroke_width': 2.5,
            'bar_fill_color': '#1d4ed8',
            'series_colors': ['#1d4ed8', '#3b82f6', '#60a5fa', '#93c5fd'],
            'reference_line_color': '#BF2626',
            'reference_line_width': 2,
            'reference_line_dash': [6, 4],
            'nextstep_font_size': 13,
            'nextstep_title_size_delta': 5,
            'nextstep_corner_radius': 8,
            'nextstep_border_width': 2,
            'nextstep_opacity': 1.0,
            'nextstep_line_height': 18,
            'nextstep_text_align': 'center',
            'nextstep_text_baseline': 'middle',
            'nextstep_text_top_padding_px': 15,
            'nextstep_text_bottom_padding_px': 15,
            'nextstep_text_side_padding_px': 15,
            'nextstep_line_gap_px': 2,
            'callout_arrow_size': 40,
            'callout_label_size': 12,
            'callout_text_padding': 6,
            'callout_point_size': 60,
            'callout_arrow_line_width': 2,
            'callout_arrow_head_scale': 2.2,
            'callout_box_border_width': 2,
            'callout_max_width_ratio': 0.45,
            'callout_max_height_ratio': 0.22,
            'callout_label_line_height_ratio': 1.3,
            'callout_extra_height_lines': 0.5,
            'callout_vertical_split_ratio': 0.55,
            'callout_label_vertical_offset_ratio': 0.40,
            'callout_peak_offset_ratio': 0.05,
            'callout_label_char_width_ratio': 0.6,
            'callout_label_min_char_width': 6,
            'callout_text_align': 'left',
            'callout_text_baseline': 'top',
            'callout_text_line_break': '\n',
            'callout_box_opacity': 1.0,
            'callout_shape': 'triangle',
            'callout_filled': True,
            'callout_clip': True,
            'title_font_weight': 'bold',
            'title_align': 'center',
            'title_baseline': 'top',
            'subtitle_align': 'center',
            'subtitle_baseline': 'top',
            'text_align': 'center',
            'text_baseline': 'middle',
            'text_line_break': '\n',
            'source_vertical_angle': 270,
            'source_horizontal_angle': 0,
            'context_border_width': 2,
            'context_text_align': 'left',
            'context_text_baseline': 'top',
            'context_line_height_ratio': 1.3,
            'text_wrap_line_height_ratio': 1.2,
            'text_wrap_char_width_ratio': 0.45,
            'text_wrap_min_char_width': 6,
            'text_wrap_min_chars': 12,
            'trendline_label_align': 'left',
            'trendline_label_baseline': 'middle',
            'trendline_label_clip': False,
            'bar_label_line_height': 14,
            'annotation_line_width': 2,
            'annotation_arrow_size': 40,
            'annotation_point_size': 60,
            'annotation_lateral_ratio': 1.2,
            'annotation_y_similarity_ratio': 0.03,
            'annotation_tip_offset_ratio': 0.05,
            'annotation_label_size': 12,
            'annotation_line_height_ratio': 1.3,
            'annotation_padding': 10,
            'annotation_text_left_padding_px': 5,
            'annotation_text_top_padding_px': 5,
            'annotation_char_width_ratio': 0.5,
            'annotation_min_char_width': 6,
            'annotation_line_gap_px':1.5,
            'annotation_box_opacity': 1,
            'annotation_box_border_width': 2.0,
            'annotation_box_height_multiplier_base': 1.0,
            'annotation_box_height_multiplier_per_line': 0.0,
        })
