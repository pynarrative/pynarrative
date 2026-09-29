from collections import UserDict

from .layout import DefaultLayout, Layout
from .style import DefaultStyle, Style


class Template(UserDict):
    """
    Template composes a Style and a Layout.
    """

    def __init__(self, style, layout):
        if not isinstance(style, Style):
            raise ValueError("style must be an instance of Style")
        if not isinstance(layout, Layout):
            raise ValueError("layout must be an instance of Layout")
        super().__init__({'style': style, 'layout': layout})

    @property
    def style(self):
        return self.data['style']

    @style.setter
    def style(self, value):
        if not isinstance(value, Style):
            raise ValueError("style must be an instance of Style")
        self.data['style'] = value

    @property
    def layout(self):
        return self.data['layout']

    @layout.setter
    def layout(self, value):
        if not isinstance(value, Layout):
            raise ValueError("layout must be an instance of Layout")
        self.data['layout'] = value

    @property
    def font(self):
        return self.style.font

    @font.setter
    def font(self, value):
        self.style.font = value

    @property
    def base_font_size(self):
        return self.style.base_font_size

    @base_font_size.setter
    def base_font_size(self, value):
        self.style.base_font_size = value

    def get_style(self):
        return self.style

    def set_style(self, style):
        self.style = style
        return self



class DefaultTemplate(Template):
    """
    Default template: composes DefaultStyle and DefaultLayout.
    """

    def __init__(self):
        super().__init__(
            style=DefaultStyle(),
            layout=DefaultLayout(),
        )
