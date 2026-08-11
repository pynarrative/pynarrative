import altair as alt
import pandas as pd

from .template import DefaultTemplate, Template

class Story:
    """
    Story class: Implements a structure for creating narrative views of data.
    
    This class extends the functionality of Altair to include narrative elements
    such as titles, contexts, and call-to-action elements. It is designed to facilitate
    the creation of more engaging and informative data visualisations.
    """

    def __init__(self, data=None, width=None, height=None, font=None, base_font_size=None, template=None, **kwargs):
        """
        Initialise a Story object.

        Parameters:
        - data: DataFrame or URL for graph data  (default: None)
        - width: Graph width in pixels (default: 600)
        - height: Height of the graph in pixels (default: 400)
        - font: Font to be used for all text elements (default: 'DejaVu Sans')
        - base_font_size: Basic font size in pixels (default: 16)
        - **kwargs: Additional parameters to be passed to the constructor of alt.Chart
        """
        if template is None:
            template = DefaultTemplate()
        elif isinstance(template, type) and issubclass(template, Template):
            template = template()
        elif not isinstance(template, Template):
            raise ValueError("template must be a Template instance or Template subclass")

        if font is not None:
            template.style.set_font(font)
        if base_font_size is not None:
            template.style.set_base_font_size(base_font_size)

        self.template = template
        self.font = template.font
        self.base_font_size = template.base_font_size
        chart_width = width if width is not None else self.chart_style_value(template, 'preferred_width', 600)
        chart_height = height if height is not None else self.chart_style_value(template, 'preferred_height', 400)

        # Initialising the Altair Chart object with basic parameters
        self.chart = alt.Chart(data, width=chart_width, height=chart_height, **kwargs)
        self.story_layers = []  # List for storing history layers
        
        # Dictionaries for the sizes and colours of various text elements
        # These values are multipliers for base_font_size
        self.style = template.style
        self.layout = template.layout
        self.font_sizes = self.style['font_sizes']
        self.colors = self.style['colors']
        self.context_box = self.style['context_box']
        self.chart_style = {**self.style, **self.layout}
        self.config = {}

    @staticmethod
    def chart_style_value(template, key, default):
        return template.layout.get(key, default)

    def __getattr__(self, name):
        """
        Special method to delegate attributes not found to the Altair Chart object.
        
        This method is crucial for maintaining compatibility with Altair, allowing
        to call Altair methods directly on the Story object.

        Parameters:
        - name: Name of the required attribute

        Returns:
        - Altair attribute if it exists, otherwise raises an AttributeError
        """
        # Search for the attribute in Altair's Chart object
        attr = getattr(self.chart, name)
        
        # If the attribute is callable (i.e. it is a method), we create a wrapper
        if callable(attr):
            def wrapped(*args, **kwargs):
                # This wrapped function is created dynamically for each Altair method
                # It is used to intercept Altair method calls and handle them correctly
                
                # Let us call Altair's original method
                result = attr(*args, **kwargs)
                
                # If the result is a new Altair Chart object
                if isinstance(result, alt.Chart):
                    # We update the chart attribute of our Story instance 
                    self.chart = result
                    # We return self (the Story instance) to allow method chaining
                    return self
                # If the result is not a Chart, we return it as it is
                return result
            
            # We return the wrapped function instead of the original method
            return wrapped
        
        # If the attribute is not callable (it is a property), we return it directly
        return attr

    def add_title(self, title, subtitle=None):
        """
        Adds a title layer (and optional subtitle) to the story.

        Parameters:
        - title: Main title text
        - subtitle: Subtitle text (optional)
        returns:
        - self, to allow method chaining
        """
        self.story_layers.append({
            'type': 'title', 
            'title': title, 
            'subtitle': subtitle
        })
        return self

    def add_context(self, text, position='left'):
        """
        Adds a context layer to the story.

        Parameters:
        - text: The context text to be added
        - position: The position of the text (default: ‘left’)
        returns:
        - self, to allow method chaining
        """
        font_size_px = self.em_to_px(self.font_sizes['context'])
        box_width, _ = self._context_box_size(position)
        wrapped_text = self._wrap_text_for_width(
            text,
            box_width=box_width,
            font_size_px=font_size_px
        )
        box_height = self._text_block_height(wrapped_text, font_size_px)
        self.story_layers.append({
            'type': 'context', 
            'text': wrapped_text, 
            'position': position,
            'box_width': box_width,
            'box_height': box_height
            
        })
        return self


    def add_next_steps(
        self,
        steps,
        position='bottom',
        title="What can we do next?"
    ):


        """
        Adds next steps as a row of boxes with a shared title.
        
        Parameters
        ---------
        steps : list[str] | str                                 Steps to display
        position : str, default=‘bottom’                        Position of the element (‘bottom’, ‘top’, ‘left’, ‘right’)
        title : str                                             Title displayed above the steps
        
        Returns
        -------
        self : Story object                                     The current instance for method chaining
        """
        if steps is None:
            raise ValueError("The parameter 'steps' is required")

        if isinstance(steps, str):
            steps = [steps]

        if not isinstance(steps, list):
            raise ValueError("The parameter 'steps' must be a list or a string")

        if len(steps) > 5:
            raise ValueError("Maximum number of steps is 5")
        if len(steps) < 1:
            raise ValueError("Must provide at least one step")

        font_family = self.font
        font_size = self.chart_style['nextstep_font_size']
        title_size = font_size + self.chart_style['nextstep_title_size_delta']
        title_color = self.colors['nextstep_title']

        gap = self.chart_style['nextstep_gap']
        text_top_padding_px = self.chart_style.get('nextstep_text_top_padding_px', max(4, font_size * 0.35))
        text_bottom_padding_px = self.chart_style.get('nextstep_text_bottom_padding_px', text_top_padding_px)
        text_side_padding_px = self.chart_style.get('nextstep_text_side_padding_px', max(6, font_size * 0.4))
        line_gap_px = self.chart_style.get('nextstep_line_gap_px', max(1.0, font_size * 0.15))
        line_height_px = font_size + line_gap_px
        layout_width = self._layout_width()
        box_width = int((layout_width - gap * (len(steps) - 1)) / len(steps))
        min_box = self.chart_style['nextstep_min_box_width']
        max_box = self.chart_style['nextstep_max_box_width']
        box_width = min(max(box_width, min_box), max_box)

        content_width = (box_width * len(steps)) + (gap * (len(steps) - 1))
        chart_width = max(layout_width, content_width)
        x_offset = max((chart_width - content_width) / 2, 0)

        box_color = self.colors['nextstep_box']
        box_border = self.colors['nextstep_border']
        text_color = self.colors['nextstep_text']

        import textwrap
        usable_width = max(box_width - (2 * text_side_padding_px), self.chart_style['text_wrap_min_width'])
        approx_char_width = max(
            font_size * self.chart_style['text_wrap_char_width_ratio'],
            self.chart_style['text_wrap_min_char_width']
        )
        max_chars = max(int(usable_width / max(approx_char_width, 1e-9)), self.chart_style['text_wrap_min_chars'])

        wrapped_steps = []
        line_counts = []
        for step in steps:
            lines = textwrap.wrap(str(step), width=max_chars, break_long_words=False, break_on_hyphens=False) or [""]
            wrapped_steps.append("\n".join(lines))
            line_counts.append(len(lines))

        box_heights = [
            (count * line_height_px) + text_top_padding_px + text_bottom_padding_px
            for count in line_counts
        ]
        uniform_box_height = max(box_heights) if box_heights else self.chart_style['nextstep_box_height']
        chart_body_height = uniform_box_height

        rows = []
        for i, step_text in enumerate(wrapped_steps):
            x_left = x_offset + i * (box_width + gap)
            rows.append({
                'x': x_left,
                'y': 0,
                'x2': x_left + box_width,
                'y2': uniform_box_height,
                'text': step_text,
                'x_mid': x_left + (box_width / 2),
                'y_text': uniform_box_height - text_top_padding_px,
            })
        df_rect = pd.DataFrame(rows)

        rect = alt.Chart(df_rect).mark_rect(
            color=box_color,
            opacity=self.chart_style['nextstep_opacity'],
            cornerRadius=self.chart_style['nextstep_corner_radius'],
            stroke=box_border,
            strokeWidth=self.chart_style['nextstep_border_width']
        ).encode(
            x=alt.X('x:Q', axis=None),
            y=alt.Y('y:Q', axis=None),
            x2='x2:Q',
            y2='y2:Q'
        ).properties(
            width=chart_width,
            height=chart_body_height + self.chart_style['nextstep_chart_height_padding']
        )

        text = alt.Chart(df_rect).mark_text(
            fontSize=font_size,
            font=font_family,
            align=self.chart_style['nextstep_text_align'],
            baseline='top',
            lineHeight=line_height_px,
            lineBreak=self.chart_style['text_line_break'],
            color=text_color,
            clip=True
        ).encode(
            text='text:N',
            x=alt.X('x_mid:Q', axis=None),
            y=alt.Y('y_text:Q', axis=None),
        )

        chart = alt.layer(rect, text)

        if title:
            chart = chart.properties(
                title=alt.TitleParams(
                    text=[title],
                    fontSize=title_size,
                    font=font_family,
                    color=title_color,
                    offset=self.chart_style['nextstep_title_offset']
                )
            )

        self.story_layers.append({
            'type': 'special_cta',
            'chart': chart,
            'position': position
        })

        return self
    
    def add_source(self, text, position='bottom', vertical=False):
        """
        Add a source layer to the story.

        Parameters:
        - text: The source text
        - position: 'bottom' (below chart), 'top' (above chart), 'left' (before left context), 'right' (after chart)
        - vertical: If True, the text will be rotated 90 degrees (default: False)

        Ritorna:
        - self, to allow the method chaining
        """
        if position not in ['bottom', 'top', 'left', 'right']:
            raise ValueError("source position must be one of: 'bottom', 'top', 'left', 'right'")
        self.story_layers.append({
            'type': 'source', 
            'text': text, 
            'position': position, 
            'vertical': vertical
            
        })
        return self

    def add_annotation(
        self,
        x=None,
        y=None,
        text=None,
        title=None,
        dx=80,
        dy=-60,
        show_subject=True,
        **kwargs
    ):
        """
        Add an annotation layer for quantitative axes.

        Parameters:
        - x, y: Subject coordinates in chart data space
        - text: Annotation body text
        - title: Optional title prepended to text
        - dx, dy: Pixel offsets from subject to box top-left corner
        - show_subject: If True, draw subject marker

        Returns:
        - self
        """
        if kwargs:
            unknown = ", ".join(sorted(kwargs.keys()))
            raise TypeError(f"Unexpected keyword argument(s): {unknown}")

        if x is None or y is None:
            raise ValueError("add_annotation requires x and y coordinates.")
        if text is None:
            raise ValueError("add_annotation requires text.")

        x_field, x_type = self._get_encoding_field_and_type('x')
        y_field, y_type = self._get_encoding_field_and_type('y')
        if x_type != 'Q' or y_type != 'Q':
            raise ValueError("add_annotation supports only quantitative ('Q') x/y axes.")

        try:
            x = float(x)
            y = float(y)
        except (TypeError, ValueError):
            raise ValueError("add_annotation requires numeric x and y values.")

        x_min, x_max = self._get_axis_range(x_field)
        y_min, y_max = self._get_axis_range(y_field)
        if x_min is None or x_max is None or y_min is None or y_max is None:
            raise ValueError("add_annotation requires valid numeric x/y ranges.")

        x_range = max(x_max - x_min, 1e-9)
        y_range = max(y_max - y_min, 1e-9)
        x_per_px = x_range / self.chart.width
        y_per_px = y_range / self.chart.height

        label_size = self.chart_style.get('annotation_label_size', self.chart_style.get('callout_label_size', 12))
        if label_size <= 6:
            label_size = self.em_to_px(label_size)
        # Derive line-height from effective font size + explicit inter-line padding.
        line_gap_px = self.chart_style.get('annotation_line_gap_px', max(1.5, label_size * 0.15))
        line_height_px = label_size + line_gap_px

        note_text = f"{title}\n{text}" if title else str(text)

        import textwrap
        max_width_px = self.chart.width * self.chart_style.get(
            'annotation_max_width_ratio',
            self.chart_style.get('callout_max_width_ratio', 0.45)
        )
        approx_char_width = max(
            label_size * self.chart_style.get(
                'annotation_char_width_ratio',
                self.chart_style.get('callout_label_char_width_ratio', 0.5)
            ),
            self.chart_style.get(
                'annotation_min_char_width',
                self.chart_style.get('callout_label_min_char_width', 6)
            )
        )
        max_chars = max(int(max_width_px / max(approx_char_width, 1e-9)), self.chart_style['text_wrap_min_chars'])
        wrapped_lines = textwrap.wrap(
            note_text,
            width=max_chars,
            break_long_words=False,
            break_on_hyphens=False
        ) or [""]
        wrapped_text = "\n".join(wrapped_lines)

        max_line_chars = max(max(len(line), 1) for line in wrapped_lines)
        box_width_px = min(max_line_chars * approx_char_width, max_width_px)
        box_height_px = max(len(wrapped_lines), 1) * line_height_px
        box_padding_px = self.chart_style.get(
            'annotation_padding',
            self.chart_style.get('padding', 6)
        )
        text_left_padding_px = self.chart_style.get('annotation_text_left_padding_px', 2.0)
        text_top_padding_px = self.chart_style.get('annotation_text_top_padding_px', 2.0)

        box_w_data = box_width_px * x_per_px
        box_h_data = (box_height_px + (2 * box_padding_px)) * y_per_px
        text_padding_h = ((box_padding_px + text_top_padding_px) * y_per_px)

        # Box and text share the same top-left anchor by design.
        box_x_left = x + (dx * x_per_px)
        box_y_top = y - (dy * y_per_px)
        box_x_right = box_x_left + box_w_data
        box_y_bottom = box_y_top - box_h_data*line_gap_px 
        text_x = box_x_left + ((box_padding_px + text_left_padding_px) * x_per_px)
        text_y = box_y_top - text_padding_h

        def connector_start_offset(dx_px, dy_px, w_px, h_px):
            if abs(dx_px) >= abs(dy_px):
                x_off = dx_px if dx_px > 0 else dx_px + w_px
                y_off = dy_px + (h_px / 2)
                return (x_off, y_off)
            if dy_px < 0:
                return (dx_px + (w_px / 2), dy_px + h_px)
            if dy_px > 0:
                return (dx_px + (w_px / 2), dy_px)
            return (dx_px + (w_px / 2), dy_px + (h_px / 2))

        conn_dx, conn_dy = connector_start_offset(dx, dy, box_width_px, box_height_px)
        connector_x = x + (conn_dx * x_per_px)
        connector_y = y - (conn_dy * y_per_px)

        tip_offset_ratio = self.chart_style.get(
            'annotation_tip_offset_ratio',
            self.chart_style.get('callout_peak_offset_ratio', 0.05)
        )
        vx = x - connector_x
        vy = y - connector_y
        tip_x = x - (vx * tip_offset_ratio)
        tip_y = y - (vy * tip_offset_ratio)

        annotation_data = pd.DataFrame({
            'subject_x': [x],
            'subject_y': [y],
            'connector_x': [connector_x],
            'connector_y': [connector_y],
            'tip_x': [tip_x],
            'tip_y': [tip_y],
            'box_x1': [box_x_left],
            'box_x2': [box_x_right],
            'box_y1': [box_y_bottom],
            'box_y2': [box_y_top],
            'text_x': [text_x],
            'text_y': [text_y],
        })

        text_color = self.colors.get('annotation_text', self.colors.get('callout_text', self.colors['context']))
        box_fill = self.colors.get('annotation_fill', self.context_box['fill'])
        box_stroke = self.colors.get('annotation_stroke', self.context_box['stroke'])
        line_color = box_stroke
        point_color = box_stroke
        point_size = self.chart_style.get('annotation_point_size', self.chart_style.get('callout_point_size', 60))
        line_width = self.chart_style.get('annotation_line_width', self.chart_style.get('callout_arrow_line_width', 2))
        box_opacity = self.chart_style.get('annotation_box_opacity', self.chart_style.get('callout_box_opacity', 1.0))
        box_border_width = self.chart_style.get('annotation_box_border_width', self.chart_style.get('callout_box_border_width', 1))

        layers = []
        if show_subject:
            layers.append(
                alt.Chart(annotation_data).mark_point(color=point_color, size=point_size).encode(
                    x=alt.X('subject_x:Q'),
                    y=alt.Y('subject_y:Q')
                ).properties(width=self.chart.width, height=self.chart.height)
            )

        layers.append(
            alt.Chart(annotation_data).mark_rule(stroke=line_color, strokeWidth=line_width).encode(
                x=alt.X('connector_x:Q'),
                y=alt.Y('connector_y:Q'),
                x2='tip_x',
                y2='tip_y'
            ).properties(width=self.chart.width, height=self.chart.height)
        )

        layers.append(
            alt.Chart(annotation_data).mark_rect(
                color=box_fill,
                opacity=box_opacity,
                cornerRadius=self.context_box['corner_radius'],
                stroke=box_stroke,
                strokeWidth=box_border_width
            ).encode(
                x=alt.X('box_x1:Q'),
                x2='box_x2',
                y=alt.Y('box_y1:Q'),
                y2='box_y2'
            ).properties(width=self.chart.width, height=self.chart.height)
        )

        layers.append(
            alt.Chart(annotation_data).mark_text(
                text=wrapped_text,
                align='left',
                baseline='top',
                font=self.font,
                fontSize=label_size,
                lineHeight=line_height_px,
                lineBreak=self.chart_style['text_line_break'],
                color=text_color
            ).encode(
                x=alt.X('text_x:Q'),
                y=alt.Y('text_y:Q')
            ).properties(width=self.chart.width, height=self.chart.height)
        )

        self.story_layers.append({'type': 'annotation', 'chart': alt.layer(*layers)})
        return self

    def add_line(self, value, orientation='horizontal'):
        """
        Adds a reference line to the story.

        Parameters:
        - value: The position of the line (x or y value)
        - orientation: 'horizontal' or 'vertical' (default: 'horizontal')

        Returns:
        - self, to allow method chaining
        """
        
        if orientation not in ['horizontal', 'vertical']:
            raise ValueError("orientation must be either 'horizontal' or 'vertical'")

        def axis_type(axis):
            if hasattr(self.chart, 'encoding') and hasattr(self.chart.encoding, axis):
                shorthand = getattr(self.chart.encoding, axis).shorthand
                if shorthand and ':' in shorthand:
                    return shorthand.split(':')[-1]
            return 'Q'

        # Crea un DataFrame con un singolo valore
        if orientation == 'horizontal':
            y_type = axis_type('y')
            data = pd.DataFrame({'y': [value]})
            encoding = {'y': f'y:{y_type}'}
        else:  # vertical
            x_type = axis_type('x')
            data = pd.DataFrame({'x': [value]})
            encoding = {'x': f'x:{x_type}'}

        # Crea la linea
        line = alt.Chart(data).mark_rule(
            color=self.chart_style['reference_line_color'],
            strokeWidth=self.chart_style['reference_line_width'],
            strokeDash=self.chart_style['reference_line_dash']
        ).encode(
            **encoding
        )

        # Aggiunge la linea ai layer della storia
        self.story_layers.append({
            'type': 'line',
            'chart': line
        })

        return self

    def add_highlight(self, category):
        """
        Highlights a single category in a bar chart and mutes the others.

        Parameters:
        - category: Category value to highlight on the categorical axis.

        Returns:
        - self, to allow method chaining
        """
        if not self._is_bar_chart():
            raise ValueError("add_highlight works only with bar charts.")
        if not isinstance(self.chart.data, pd.DataFrame):
            raise ValueError("add_highlight requires DataFrame-backed chart data.")

        x_field, x_type = self._get_encoding_field_and_type('x')
        y_field, y_type = self._get_encoding_field_and_type('y')
        category_field = None
        if x_type in ['N', 'O']:
            category_field = x_field
        elif y_type in ['N', 'O']:
            category_field = y_field

        if not category_field:
            raise ValueError("add_highlight requires a categorical axis (N or O).")
        if category_field not in self.chart.data.columns:
            raise ValueError(f"Category field '{category_field}' not found in chart data.")

        values = self.chart.data[category_field].tolist()
        category_key = str(category)
        matched_category = None
        for value in values:
            if str(value) == category_key:
                matched_category = value
                break
        if matched_category is None:
            raise ValueError(f"Category '{category}' not found in field '{category_field}'.")

        highlight_color = self.colors.get(
            'bar_highlight',
            self.chart_style.get('bar_fill_color', '#1d4ed8')
        )
        muted_color = self.colors.get(
            'bar_muted',
            self.chart_style.get('axis_tick_color', '#cbd5e1')
        )

        self.chart = self.chart.encode(
            color=alt.condition(
                alt.datum[category_field] == matched_category,
                alt.value(highlight_color),
                alt.value(muted_color),
                legend=None
            )
        )
        return self
    
        

    def em_to_px(self, em):
        """
        Converts a dimension from em to pixels.

        This function is essential for maintaining visual consistency
        between different textual elements and devices.

        Parameters:
        - em: Size in em

        Returns:
        - Equivalent size in pixels (integer)
        """
        return int(em * self.base_font_size)

    def _get_position(self, position):
        """
        Calculates the x and y co-ordinates for positioning text elements in the graph.

        This method is crucial for the correct positioning of various elements
        narrative elements such as context, call-to-action and sources.

        Parameters:
        - position: String indicating the desired position (e.g. ‘left’, ‘right’, ‘top’, etc.).
        
        Returns:
        - Tuple (x, y) representing the coordinates in pixels
        """
        # Dictionary mapping positions to coordinates (x, y)
        # Co-ordinates are calculated from the size of the graph
        positions = {
            'left': (-100, self.chart.height / 2),  # 10 pixel from the left edge, centred vertically
            'right': (self.chart.width + 20, self.chart.height / 2),  # 10 pixel from the right edge, centred vertically
            'top': (self.chart.width / 2, 80),  # Centred horizontally, 80 pixels from above
            'bottom': (self.chart.width / 2, self.chart.height + 40),  # Horizontally centred, 40 pixels from bottom
            'center': (self.chart.width / 2, self.chart.height / 2),  # Graph Centre
            'side-left': (-150, self.chart.height / 2),  # 10 pixels to the left of the border, centred vertically
            'side-right': (self.chart.width + 50, self.chart.height / 2),  # 10 pixels to the right of the border, centred vertically
        }
        
        # If the required position is not in the dictionary, use a default position
        # In this case, horizontally centred and 20 pixels from the bottom
        return positions.get(position, (self.chart.width / 2, self.chart.height - 20))

    def create_source_side_chart(self, layer):
        """
        Creates a dedicated side chart for source text on left/right positions.
        """
        position = layer.get('position', 'left')
        font_size = layer.get('font_size', self.em_to_px(self.font_sizes['source']))
        if position == 'left':
            angle = 270
            width = self.chart_style.get('source_side_vertical_width', 48)
        else:
            angle = 90
            width = self.chart_style.get('source_side_horizontal_width', 260)

        base = alt.Chart(pd.DataFrame({'_': [0]})).properties(
            width=width,
            height=self.chart.height
        )
        return base.mark_text(
            text=layer['text'],
            fontSize=font_size,
            align='center',
            baseline='middle',
            font=self.font,
            lineBreak="\n",
            angle=angle,
            color=layer.get('color', self.colors.get('source', self.colors['context']))
        ).encode(
            x=alt.value(width / 2),
            y=alt.value(self.chart.height / 2)
        )

    def create_source_top_chart(self, layer):
        """
        Creates a dedicated chart for source text above the main chart.
        """
        font_size = layer.get('font_size', self.em_to_px(self.font_sizes['source']))
        width = self._layout_width()
        height = self.chart_style.get('source_top_height', 28)
        base = alt.Chart(pd.DataFrame({'_': [0]})).properties(
            width=width,
            height=height
        )
        return base.mark_text(
            text=layer['text'],
            fontSize=font_size,
            align='center',
            baseline='middle',
            font=self.font,
            lineBreak="\n",
            angle=0,
            color=layer.get('color', self.colors.get('source', self.colors['context']))
        ).encode(
            x=alt.value(width / 2),
            y=alt.value(height / 2)
        )

    def create_title_layer(self, layer):
        """
        Creates the title layer (and subtitle if present).

        This method is responsible for visually creating the main title
        and the optional subtitle of the graphic.

        Parameters:
        - Layer: Dictionary containing the title information

        Returns:
        - Altair Chart object representing the title layer
        """
        layout_width = self._layout_width()
        base = alt.Chart(pd.DataFrame({'_': [0]})).properties(
            width=layout_width,
            height=self.chart_style['title_area_height']
        )

        title_chart = base.mark_text(
            text=layer['title'],
            fontSize=self.em_to_px(self.font_sizes['title']),
            fontWeight=self.chart_style['title_font_weight'],
            align=self.chart_style['title_align'],
            baseline=self.chart_style['title_baseline'],
            font=self.font,
            color=self.colors['title']
        ).encode(
            x=alt.value(layout_width / 2),
            y=alt.value(self.chart_style['title_y'])
        )
        
        if layer['subtitle']:
            subtitle_chart = base.mark_text(
                text=layer['subtitle'],
                fontSize=self.em_to_px(self.font_sizes['subtitle']),
                align=self.chart_style['subtitle_align'],
                baseline=self.chart_style['subtitle_baseline'],
                font=self.font,
                color=self.colors['subtitle']
            ).encode(
                x=alt.value(layout_width / 2),
                y=alt.value(self.chart_style['subtitle_y'])
            )
            return title_chart + subtitle_chart
        return title_chart

    def create_text_layer(self, layer):
        """
        Creates a generic text layer (context, next-steps, source).

        This method is used to create text layers for various narrative purposes,
        such as adding context, next-steps or data source information.

        Parameters:
        - Layer: Dictionary containing the text information to be added

        Returns:
        - Altair Chart object representing the text layer
        """
        x, y = self._get_position(layer['position'])

        # Keep source text visually separated from the chart area.
        if layer['type'] == 'source' and layer.get('position') == 'bottom':
            y += self.chart_style['source_bottom_padding']

        font_size = layer.get('font_size', self.em_to_px(self.font_sizes[layer['type']]))

        text_chart = alt.Chart(self.chart.data).mark_text(
            text=layer['text'],
            fontSize=font_size,
            align=self.chart_style['text_align'],
            baseline=self.chart_style['text_baseline'],
            font=self.font,
            lineBreak=self.chart_style['text_line_break'],
            angle=(
                270 if (layer['type'] == 'source' and layer.get('position') == 'left')
                else 90 if (layer['type'] == 'source' and layer.get('position') == 'right')
                else self.chart_style['source_vertical_angle'] if layer.get('vertical', False)
                else self.chart_style['source_horizontal_angle']
            ),
            color=layer.get('color', self.colors.get(layer['type'], self.colors['context']))
        ).encode(
            x=alt.value(x),
            y=alt.value(y)
        )

        return text_chart

    def create_context_box_chart(self, layer):
        """
        Creates a context box chart sized to the wrapped text.
        """
        font_size = layer.get('font_size', self.em_to_px(self.font_sizes['context']))
        padding = self.context_box['padding']

        box_width = layer.get('box_width')
        box_height = layer.get('box_height')
        if box_width is None or box_height is None:
            box_width, _ = self._context_box_size(layer.get('position', 'left'))
            box_height = self._text_block_height(layer.get('text', ''), font_size)

        x_center = box_width / 2
        y_center = box_height / 2

        base = alt.Chart(pd.DataFrame({'_': [0]})).properties(
            width=box_width,
            height=box_height
        )

        box = base.mark_rect(
            color=self.context_box['fill'],
            opacity=self.context_box['opacity'],
            cornerRadius=self.context_box['corner_radius'],
            stroke=self.context_box['stroke'],
            strokeWidth=self.chart_style['context_border_width']
        ).encode(
            x=alt.value(0),
            x2=alt.value(box_width),
            y=alt.value(0),
            y2=alt.value(box_height)
        )

        text = base.mark_text(
            text=layer['text'],
            fontSize=font_size,
            align=self.chart_style['context_text_align'],
            baseline=self.chart_style['context_text_baseline'],
            font=self.font,
            lineBreak=self.chart_style['text_line_break'],
            lineHeight=font_size * self.chart_style['context_line_height_ratio'],
            color=layer.get('color', self.colors['context'])
        ).encode(
            x=alt.value(padding),
            y=alt.value(padding)
        )

        return alt.layer(box, text)

    def _context_box_size(self, position):
        width = self.chart.width
        height = self.chart.height
        if position == 'right':
            return (
                width * self.chart_style['context_right_width_ratio'],
                height * self.chart_style['context_right_height_ratio']
            )
        if position == 'top':
            return (
                width * self.chart_style['context_top_width_ratio'],
                height * self.chart_style['context_top_height_ratio']
            )
        if position == 'bottom':
            return (
                width * self.chart_style['context_bottom_width_ratio'],
                height * self.chart_style['context_bottom_height_ratio']
            )
        return (
            width * self.chart_style['context_left_width_ratio'],
            height * self.chart_style['context_left_height_ratio']
        )

    def _wrap_text_for_box(self, text, box_width, box_height, font_size_px):
        import math
        import textwrap

        if text is None:
            return ""
        text = str(text).strip()
        if not text:
            return text

        padding = self.context_box['padding']
        usable_width = max(box_width - (padding * 2), self.chart_style['text_wrap_min_width'])
        usable_height = max(box_height - (padding * 2), font_size_px * self.chart_style['text_wrap_line_height_ratio'])

        approx_char_width = max(
            font_size_px * self.chart_style['text_wrap_char_width_ratio'],
            self.chart_style['text_wrap_min_char_width']
        )
        line_height = font_size_px * self.chart_style['text_wrap_line_height_ratio']

        max_chars = max(int(usable_width / approx_char_width), self.chart_style['text_wrap_min_chars'])
        max_lines = max(int(usable_height / line_height), 1)

        lines = textwrap.wrap(text, width=max_chars, break_long_words=False, break_on_hyphens=False)
        if len(lines) <= max_lines:
            return "\n".join(lines)

        # Trim to available lines and add ellipsis to the last line.
        lines = lines[:max_lines]
        last = lines[-1]
        if len(last) >= 2:
            lines[-1] = last[:max(max_chars - 1, 1)].rstrip() + "…"
        return "\n".join(lines)

    def _wrap_text_for_width(self, text, box_width, font_size_px):
        import textwrap

        if text is None:
            return ""
        if isinstance(text, list):
            text = " ".join(str(t) for t in text)
        text = str(text).strip()
        if not text:
            return text

        padding = self.context_box['padding']
        usable_width = max(box_width - (padding * 2), self.chart_style['text_wrap_min_width'])
        approx_char_width = max(
            font_size_px * self.chart_style['text_wrap_char_width_ratio'],
            self.chart_style['text_wrap_min_char_width']
        )
        max_chars = max(int(usable_width / approx_char_width), self.chart_style['text_wrap_min_chars'])
        lines = textwrap.wrap(text, width=max_chars, break_long_words=False, break_on_hyphens=False)
        return "\n".join(lines) if lines else ""

    def _text_block_height(self, text, font_size_px):
        padding = self.context_box['padding']
        line_height = font_size_px * self.chart_style['context_line_height_ratio']
        lines = (str(text).splitlines() if text is not None else [""])
        line_count = max(len(lines), 1)
        return (line_count * line_height) + (padding * 2)
    def _layout_width(self):
        width = self.chart.width
        has_left = any(
            layer.get('type') == 'context' and layer.get('position') == 'left'
            for layer in self.story_layers
        )
        has_right = any(
            layer.get('type') == 'context' and layer.get('position') == 'right'
            for layer in self.story_layers
        )
        if has_left:
            width += self.chart.width * self.chart_style['layout_context_side_width_ratio']
        if has_right:
            width += self.chart.width * self.chart_style['layout_context_side_width_ratio']
        return width

    def _arrow_angle(self, x_from, y_from, x_to, y_to):
        import math
        angle = math.degrees(math.atan2(y_to - y_from, x_to - x_from))
        return angle

    def _get_axis_range(self, field):
        if not field or self.chart.data is None:
            return (None, None)
        if not isinstance(self.chart.data, pd.DataFrame):
            return (None, None)
        if field not in self.chart.data.columns:
            return (None, None)
        series = pd.to_numeric(self.chart.data[field], errors='coerce').dropna()
        if series.empty:
            return (None, None)
        return (float(series.min()), float(series.max()))

    def _get_ordinal_domain(self, field):
        if not field or self.chart.data is None:
            return []
        if not isinstance(self.chart.data, pd.DataFrame):
            return []
        if field not in self.chart.data.columns:
            return []
        # Preserve appearance order from the source data.
        return [str(v) for v in pd.Series(self.chart.data[field]).dropna().astype(str).drop_duplicates().tolist()]

    def _get_encoding_field_and_type(self, axis):
        if not hasattr(self.chart, 'encoding') or not hasattr(self.chart.encoding, axis):
            return (None, None)
        channel = getattr(self.chart.encoding, axis)
        shorthand = getattr(channel, 'shorthand', None)
        if shorthand and ':' in shorthand:
            field, dtype = shorthand.split(':', 1)
            return (field, dtype)
        field = getattr(channel, 'field', None)
        dtype = getattr(channel, 'type', None)
        if field and dtype:
            return (field, str(dtype)[0].upper())
        return (None, None)

    def _is_line_chart(self):
        mark = getattr(self.chart, 'mark', None)
        if isinstance(mark, str):
            return mark == 'line'
        if hasattr(mark, 'type'):
            return mark.type == 'line'
        return False

    def _is_bar_chart(self):
        mark = getattr(self.chart, 'mark', None)
        if isinstance(mark, str):
            return mark == 'bar'
        if hasattr(mark, 'type'):
            return mark.type == 'bar'
        return False

    def _apply_trendline_end_labels(self, base_chart):
        """
        Replace line legend with labels near the end of each trend line.
        """
        if not self._is_line_chart():
            return base_chart
        if not isinstance(self.chart.data, pd.DataFrame):
            return base_chart

        x_field, x_type = self._get_encoding_field_and_type('x')
        y_field, y_type = self._get_encoding_field_and_type('y')
        color_field, color_type = self._get_encoding_field_and_type('color')
        if not x_field or not y_field or not color_field:
            return base_chart
        if x_field not in self.chart.data.columns or y_field not in self.chart.data.columns or color_field not in self.chart.data.columns:
            return base_chart

        labels_df = (
            self.chart.data.sort_values(x_field)
            .groupby(color_field, as_index=False)
            .tail(1)
            .copy()
        )
        if labels_df.empty:
            return base_chart

        base_no_legend = base_chart.encode(
            color=alt.Color(f'{color_field}:{color_type}', legend=None)
        )

        labels = alt.Chart(labels_df).mark_text(
            align=self.chart_style['trendline_label_align'],
            baseline=self.chart_style['trendline_label_baseline'],
            dx=self.chart_style['trendline_label_dx'],
            clip=self.chart_style['trendline_label_clip'],
            font=self.font,
            fontSize=self.chart_style['axis_label_size'],
        ).encode(
            x=alt.X(f'{x_field}:{x_type}'),
            y=alt.Y(f'{y_field}:{y_type}'),
            text=alt.Text(f'{color_field}:N'),
            color=alt.Color(f'{color_field}:{color_type}', legend=None)
        )

        return base_no_legend + labels

    def configure_view(self, *args, **kwargs):
        """
        Configure aspects of the graph view using Altair's configure_view method.

        This method allows you to configure various aspects of the chart view, such as
        the background colour, border style, internal spacing, etc.

        Parameters:
        *args, **kwargs: Arguments to pass to the Altair configure_view method.

        stores the view configuration for application during rendering.
        """
        self.config['view'] = kwargs
        return self


    def render(self):
        """
        It renders all layers of the story in a single graphic.       
        """
        def _vstack(charts):
            if not charts:
                return None
            if len(charts) == 1:
                return charts[0]
            return alt.vconcat(*charts)

        # Let's start with the basic graph
        main_chart = self._apply_trendline_end_labels(self.chart)
        
        # Create separate lists to place special graphics
        title_charts = []
        top_other_charts = []
        top_context_charts = []
        top_source_charts = []
        bottom_charts = []
        left_charts = []
        right_charts = []
        left_outer_charts = []
        right_outer_charts = []
        overlay_charts = []
        
        # Organise the layers according to their position
        for layer in self.story_layers:
            if layer['type'] == 'special_cta':
                # We take the position from the layer
                if layer.get('position') == 'top':
                    top_other_charts.append(layer['chart'])
                elif layer.get('position') == 'bottom':
                    bottom_charts.append(layer['chart'])
                elif layer.get('position') == 'left':
                    left_charts.append(layer['chart'])
                elif layer.get('position') == 'right':
                    right_charts.append(layer['chart'])
            elif layer['type'] == 'context' and layer.get('position') in ['left', 'right', 'top', 'bottom']:
                context_chart = self.create_context_box_chart(layer)
                if layer.get('position') == 'top':
                    top_context_charts.append(context_chart)
                elif layer.get('position') == 'bottom':
                    bottom_charts.append(context_chart)
                elif layer.get('position') == 'left':
                    left_charts.append(context_chart)
                elif layer.get('position') == 'right':
                    right_charts.append(context_chart)
            elif layer['type'] == 'title':
                title_charts.append(self.create_title_layer(layer))
            elif layer['type'] == 'source' and layer.get('position') in ['left', 'right']:
                source_side = self.create_source_side_chart(layer)
                if layer.get('position') == 'left':
                    left_outer_charts.append(source_side)
                else:
                    right_outer_charts.append(source_side)
            elif layer['type'] == 'source' and layer.get('position') == 'top':
                top_source_charts.append(self.create_source_top_chart(layer))
            elif layer['type'] in ['context', 'cta', 'source']:
                overlay_charts.append(self.create_text_layer(layer))
            elif layer['type'] in ['shape', 'shape_label', 'annotation']:
                overlay_charts.append(layer['chart'])
            elif layer['type'] == 'line':
                overlay_charts.append(layer['chart'])

        # Overlaying the layers on the main graph
        for overlay in overlay_charts:
            main_chart += overlay

        # Build the final layout
        left_stack = _vstack(left_charts)
        left_source_stack = _vstack(left_outer_charts)
        if left_source_stack is not None and left_stack is not None:
            # Keep left source before left context, but aligned on the same row as the chart.
            main_chart = alt.hconcat(left_source_stack, left_stack, main_chart)
        elif left_source_stack is not None:
            main_chart = alt.hconcat(left_source_stack, main_chart)
        elif left_stack is not None:
            main_chart = alt.hconcat(left_stack, main_chart)

        right_stack = _vstack(right_charts)
        right_source_stack = _vstack(right_outer_charts)
        if right_source_stack is not None and right_stack is not None:
            # Keep right source after right context.
            main_chart = alt.hconcat(main_chart, right_stack, right_source_stack)
        elif right_source_stack is not None:
            main_chart = alt.hconcat(main_chart, right_source_stack)
        elif right_stack is not None:
            main_chart = alt.hconcat(main_chart, right_stack)
        top_charts = top_context_charts + top_source_charts + top_other_charts
        if top_charts:
            main_chart = alt.vconcat(*top_charts, main_chart)
        if bottom_charts:
            main_chart = alt.vconcat(main_chart, alt.hconcat(*bottom_charts))
        if title_charts:
            main_chart = alt.vconcat(*title_charts, main_chart)

        # Apply configurations
        if 'view' in self.config:
            main_chart = main_chart.configure_view(**self.config['view'])

        # Apply default chart styling
        main_chart = main_chart.configure_view(
            strokeWidth=self.chart_style['default_view_stroke_width']
        ).configure_axis(
            grid=self.chart_style['axis_grid'],
            labelFont=self.chart_style['font'],
            labelColor=self.chart_style['label_color'],
            labelFontSize=self.chart_style['axis_label_size'],
            titleFont=self.chart_style['font'],
            titleColor=self.chart_style['title_color'],
            titleFontSize=self.chart_style['axis_title_size'],
            tickColor=self.chart_style['axis_tick_color'],
            domainColor=self.chart_style['axis_domain_color']
        ).configure_legend(
            labelFont=self.chart_style['font'],
            labelColor=self.chart_style['label_color'],
            labelFontSize=self.chart_style['legend_label_size'],
            titleFont=self.chart_style['font'],
            titleColor=self.chart_style['title_color'],
            titleFontSize=self.chart_style['legend_title_size']
        ).configure_title(
            font=self.chart_style['font'],
            color=self.chart_style['title_color'],
            fontSize=self.em_to_px(self.font_sizes['title'])
        ).configure_mark(
            strokeWidth=self.chart_style['line_stroke_width']
        ).configure_bar(
            color=self.chart_style['bar_fill_color']
        ).configure_range(
            category=self.chart_style['series_colors']
        )

        if self._is_bar_chart():
            wrap_threshold = self.chart_style['bar_label_wrap_threshold']
            main_chart = main_chart.configure_axisX(
                labelAngle=0,
                labelLineHeight=self.chart_style['bar_label_line_height'],
                labelExpr=(
                    f"length(datum.label) > {wrap_threshold} "
                    "? replace(datum.label, /\\s+/, '\\n') : datum.label"
                )
            )

        return main_chart.resolve_axis(x='independent', y='independent')
    


    

def story(data=None, **kwargs):
    """
    Utility function for creating a Story instance.

    This function simplifies the creation of a Story object, allowing
    to initialise it in a more concise and intuitive way.

    Parameters:
    - data: DataFrame or URL for chart data (default: None)
    - **kwargs: Additional parameters to be passed to the Story constructor

    Returns:
    - An instance of the Story class
    """
    return Story(data, **kwargs)
