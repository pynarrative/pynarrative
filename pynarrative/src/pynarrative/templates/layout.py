from collections import UserDict


class Layout(UserDict):
    """
    Geometric/layout container (sizes, ratios, spacing, positioning).
    """

    def set(self, **kwargs):
        self.data.update(kwargs)
        return self

    def get_value(self, key, default=None):
        return self.data.get(key, default)

    def set_value(self, key, value):
        self.data[key] = value
        return self

    def get_preferred_width(self):
        return self.data['preferred_width']

    def set_preferred_width(self, value):
        self.data['preferred_width'] = value
        return self

    def get_preferred_height(self):
        return self.data['preferred_height']

    def set_preferred_height(self, value):
        self.data['preferred_height'] = value
        return self


class DefaultLayout(Layout):
    """
    Default layout values (sizes, spacing, coordinates, ratios).
    """

    def __init__(self):
        super().__init__({
            'preferred_width': 600,
            'preferred_height': 400,
            'title_area_height': 70,
            'title_y': 5,
            'subtitle_y': 40,
            'source_bottom_padding': 60,
            'source_top_padding': 20,
            'source_top_height': 28,
            'source_side_vertical_width': 48,
            'source_side_horizontal_width': 90,
            'nextstep_box_height': 86,
            'nextstep_gap': 10,
            'nextstep_min_box_width': 160,
            'nextstep_max_box_width': 340,
            'nextstep_chart_height_padding': 10,
            'nextstep_title_offset': 10,
            'layout_context_side_width_ratio': 0.73, #title block width multiplier
            'context_left_width_ratio': 0.5, #left context and nextstep block width multiplier
            'context_right_width_ratio': 0.5, #right context and nextstep block width multiplier
            'context_left_height_ratio': 1,
            'context_right_height_ratio': 1.0,
            'context_top_width_ratio': 1.8, #top context block width multiplier
            'context_bottom_width_ratio': 1.8, #bottom context block width multiplier
            'context_top_height_ratio': 1 / 3,
            'context_bottom_height_ratio': 1 / 3,
            'text_wrap_min_width': 120,
            'trendline_label_dx': 40,
            'bar_label_wrap_threshold': 12,
            'annotation_max_width_ratio': 0.45,
        })
