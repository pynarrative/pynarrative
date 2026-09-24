import altair as alt
import pandas as pd
import geopandas as gpd
import re
import os
import warnings
import numpy as np
import textwrap
import math


from .templates.template import DefaultTemplate, Template

class Story:
    def __init__(
            self,
            data=None,
            width=None,
            height=None,
            font=None,
            base_font_size=None,
            template=None,
            geodata = False,
            geojson_url = None,
            geojson_property = None,
            geo_property = None,
            geo_value = None,
            **kwargs
        ):
        
        """Story class: Implements a structure for creating narrative views of data.
            
            This class extends the functionality of Altair to include narrative elements
            such as titles, contexts, and call-to-action elements. It is designed to facilitate
            the creation of more engaging and informative data visualisations.
            

        Args:
            data (pandas.DataFrame | str, optional): DataFrame or URL/path containing
                the chart data. Defaults to None.
            width (int, optional): Graph width in pixels. If omitted or None, uses the
                preferred width from the template (if used), falling back to 600. Defaults to None.
            height (int, optional): Graph height in pixels. If omitted or None, uses the
                preferred height from the template (if used), falling back to 400. Defaults to None.
            font (str, optional): Font family to be applied to all text elements.
                If omitted or None, uses the value from the template (if used), falling back to
                Times New Roman for the title (if used) and Noto Sans for all the rest.
                Defaults to None.
            base_font_size (int | float, optional): Base font size in pixels.
                If omitted or None, uses the value from the template (if used)
                Defaults to None.
            template (Template | type[Template], optional): Instance or subclass of
                `Template` for styling. If omitted or None, uses `DefaultTemplate()`.
                Defaults to None.
            geodata (bool, optional): Indicates whether the chart handles spatial data.
                Defaults to False.
            geojson_url (str, optional, required if `geodata=True`): File path or URL to the GeoJSON file.
                Required if `geodata=True`. Defaults to None.
            geojson_property (str, optional, required if `geodata=True`): Key property name in the GeoJSON used for
                merging. Required if `geodata=True`. Defaults to None.
            geo_property (str, optional, required if `geodata=True`): DataFrame column name matching `geojson_property`.
                Required if `geodata=True`. Defaults to None.
            geo_value (str, optional, required if `geodata=True`): DataFrame column name containing the numerical or
                categorical values to map spatially. Required if `geodata=True`.
                Defaults to None.
            **kwargs: Additional keyword arguments passed directly to the `alt.Chart`
                constructor.

        Raises:
            ValueError: If `template` is neither an instance nor a subclass of `Template`.
            ValueError: If `geodata=True` and any required spatial arguments
                (`geojson_url`, `geojson_property`, `geo_property`, `geo_value`) are missing.
            ValueError: If `geojson_url` does not have a `.json` or `.geojson` extension.
            ValueError: If `geo_property` or `geo_value` are not valid columns in `data`.
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

        #Managing geographical data
        if geodata and None in [geojson_url, geojson_property, geo_property, geo_value]:
            raise ValueError("if `geodata=True`, 'geojson_url', 'geojson_property', 'geo_property', 'geo_value' are required arguments")
        if geodata:
            if geojson_url: #Checking extension
                if os.path.splitext(geojson_url)[1] not in [".geojson", ".json"]:
                    raise ValueError("'geojson_url' must be a .geojson or .json file")
            if geo_property not in data.columns:
                raise ValueError(f"'{geo_property}' must be a column in your dataframe")
            if geo_value not in data.columns:
                    raise ValueError(f"'{geo_value}' must be a column in your dataframe")

        if geodata:
            geo_dataframe = gpd.read_file(geojson_url)
            geo_dataframe = geo_dataframe.merge(data, left_on = geojson_property, right_on = geo_property, how = "left")
            geo_dataframe[geo_value] = geo_dataframe[geo_value].fillna(0)
            data = geo_dataframe


        self.template = template
        self.font = template.font
        self.base_font_size = template.base_font_size
        chart_width = width if width is not None else self.chart_style_value(template, 'preferred_width', 600)
        self.chart_width = chart_width

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
        """Retrieves a configuration value from the template's layout settings.

        Args:
            template (Template): The template instance containing layout definitions.
            key (str): The parameter key to look up.
            default (Any): The fallback value to return if `key` is not found.

        Returns:
            Any: The layout configuration value if present; otherwise, `default`.
        """
        return template.layout.get(key, default)

    def __getattr__(self, name):
        """Delegates missing attributes dynamically to the underlying `alt.Chart` object.

        Allows standard Altair methods to be invoked directly on the `Story` instance
        while maintaining method-chaining behavior.

        Args:
            name (str): The name of the attribute or method requested.

        Returns:
            Any: The attribute value if non-callable, or a wrapper function that updates
            the internal chart reference and returns `self` if the invoked Altair method
            returns a new `alt.Chart` instance.

        Raises:
            AttributeError: If the attribute does not exist on either `Story` or `alt.Chart`.
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

    def add_title(
            self,
            title,
            subtitle=None,
            background_color = None,
            color = None,
            align = "center",

            img_url = None,
            img_width = 80,
            x_img_offset = -300,
            y_img_offset = 0

            ):
        """Adds a main title layer and an optional subtitle to the story.

        Args:
            title (str): Main title text to display.
            subtitle (str, optional): Subtitle text to display below the title.
                Defaults to None.
            background_color (str, optional): Background color for the title block.
                If omitted or None, falls back to the `title_background_color` defined
                in the template. Defaults to None.
            color (str, optional): Text color for the title and subtitle.
                If omitted or None, falls back to the `title` defined
                in the template. Defaults to None.
            align (str, optional): Horizontal text alignment. Must be one of
                `'left'`, `'center'`, or `'right'`. Defaults to "center".
            img_url (str, optional): URL or path to an optional image/logo to display
                alongside the title. Defaults to None.
            img_width (int | float, optional): Width of the image in pixels.
                Defaults to 80.
            x_img_offset (int | float, optional): Horizontal offset for the image position
                relative to the title block in pixels. Defaults to -300.
            y_img_offset (int | float, optional): Vertical offset for the image position
                relative to the title block in pixels. Defaults to 0.

        Returns:
            Story: The current instance (`self`) to enable method chaining.

        Raises:
            TypeError: If `title` is not a string.
            ValueError: If `align` is not one of `'left'`, `'center'`, or `'right'`.
            ValueError: If `img_width` is less than or equal to 0 when `img_url` is provided.
        """

        #GESTIONE ERRORI
        if align not in ["left", "center", "right"]:
            raise ValueError(f"Invalid 'align' value: '{align}'. Must be one of: 'left', 'center', 'right'")

        if img_url is not None and img_width <= 0:
            raise ValueError("'img_width' must be a positive number")

        background_color = background_color if background_color else self.colors["title_background_color"]
        color = color if color else self.colors["title"]
        
        self.story_layers.append({
            'type': 'title', 
            'title': title, 
            'subtitle': subtitle,
            "align": align,
            "color": color,
            "background_color": background_color,
            "img_url": img_url,
            "img_width": img_width,
            "x_img_offset": x_img_offset,
            "y_img_offset": y_img_offset
        })
        return self

    def add_context(
            self,
            text,
            text_align = "left",
            position='left',
            align = "middle",
            font_weight = "normal",
            font_style = "normal",
            title = "CONTEXT",
            title_dy = 0,
            img_url = None,
            img_width = 60,
            x_img_offset = -40,
            y_img_offset = 0
        ):
        """Adds a context box layer to the story.

        Args:
            text (str): The body text to be displayed within the context box.
            text_align (str, optional): Horizontal alignment of the text inside the box.
                Must be one of `'left'`, `'center'`, or `'right'`. Defaults to "left".
            position (str, optional): Position of the context box relative to the chart.
                Must be one of `'left'`, `'right'`, `'top'`, or `'bottom'`. Defaults to "left".
            align (str, optional): Vertical alignment relative to the chart when `position` is
                `'left'` or `'right'`. Must be one of `'top'`, `'middle'`, or `'bottom'`.
                Defaults to "middle".
            font_weight (str, optional): Font weight for the context text.
                Must be one of `'normal'` or `'bold'`. Defaults to "normal".
            font_style (str, optional): Font style for the context text.
                Must be one of `'normal'` or `'italic'`. Defaults to "normal".
            title (str, optional): Title header displayed above the context text.
                Defaults to "CONTEXT".
            title_dy (int | float, optional): Vertical offset in pixels for the title relative
                to its default position. Defaults to 0.
            img_url (str, optional): File path or URL to an image/icon displayed alongside
                the context block. Defaults to None.
            img_width (int | float, optional): Width of the context image in pixels.
                Defaults to 60.
            x_img_offset (int | float, optional): Horizontal offset in pixels for the context image.
                Defaults to -40.
            y_img_offset (int | float, optional): Vertical offset in pixels for the context image.
                Defaults to 0.

        Returns:
            Story: The current instance (`self`) to enable method chaining.

        Raises:
            TypeError: If `text` or `title` is not a string.
            ValueError: If `text_align` is not one of `'left'`, `'center'`, or `'right'`.
            ValueError: If `position` is not one of `'left'`, `'right'`, `'top'`, or `'bottom'`.
            ValueError: If `align` is specified with `position` set to `'top'` or `'bottom'`.
            ValueError: If `align` is not one of `'top'`, `'middle'`, or `'bottom'`.
            ValueError: If `font_weight` is not one of `'normal'` or `'bold'`.
            ValueError: If `font_style` is not one of `'normal'` or `'italic'`.
            ValueError: If `img_width` is less than or equal to 0 when `img_url` is provided.
        """

        #GESTIONE ERRORI

        if not isinstance(text, str):
            raise TypeError(f"'text' must be a string, got {type(text).__name__}")
        if title is not None and not isinstance(title, str):
            raise TypeError(f"'title' must be a string, got {type(title).__name__}")
        if text_align not in ["left", "center", "right"]:
            raise ValueError(f"Invalid 'text_align' value: '{text_align}'. Must be one of: 'left', 'center', 'right'")
        if position not in ['bottom', 'top', 'left', 'right']:
            raise ValueError(f"Invalid 'position' value: '{position}'. Must be one of: 'bottom', 'top', 'left', 'right'")
        if position in ["top", "bottom"] and align != "middle":
            raise ValueError("Vertical alignment ('align') cannot be customized when 'position' is 'top' or 'bottom'")
        if align not in ["top", "middle", "bottom"]:
            raise ValueError(f"Invalid 'align' value: '{align}'. Must be one of: 'top', 'middle', 'bottom'")
        if font_weight not in ["normal", "bold"]:
            raise ValueError(f"Invalid 'font_weight' value: '{font_weight}'. Must be one of: 'normal', 'bold'")
        if font_style not in ["normal", "italic"]:
            raise ValueError(f"Invalid 'font_style' value: '{font_style}'. Must be one of: 'normal', 'italic'")
        if img_url is not None and img_width <= 0:
            raise ValueError("'img_width' must be a positive number")
        
        font_size_px = self.em_to_px(self.font_sizes['context']) 

        box_width, _ = self._context_box_size(position)
        wrapped_text = self._wrap_text_for_width(
            text,
            box_width=box_width,
            font_size_px=font_size_px,
        )
        box_height = self._text_block_height(wrapped_text, font_size_px, block_type = "context")
        self.story_layers.append({
            'type': 'context', 
            'text': wrapped_text,
            "text_align" : text_align,
            'position': position,
            'box_width': box_width,
            'box_height': box_height,
            "align" : align,
            "font_weight" : font_weight,
            "font_style" : font_style,
            "title" : title,
            "title_dy" : title_dy,
            "img_url": img_url,
            "img_width": img_width,
            "x_img_offset": x_img_offset,
            "y_img_offset": y_img_offset
        })

        return self
    

    def add_next_steps(
        self,
        steps,
        text_align = "left",
        position='bottom',
        title="NEXT STEPS",
        title_dy = 0,
        title_dx = 0,
        mode = "horizontal",
        img_url = None,
        img_width = 45,
        x_img_offset = -50,
        y_img_offset = -22.5
    ):

        """Adds next steps as a row or column of styled boxes with a shared title.

        Args:
            steps (list[str] | str): Sequence of step descriptions to display.
                A single string will be automatically converted into a one-element list.
            text_align (str, optional): Horizontal alignment of the text inside each step box.
                Must be one of `'left'`, `'center'`, or `'right'`. Defaults to "left".
            position (str, optional): Position of the entire element relative to the chart.
                Must be one of `'bottom'`, `'top'`, `'left'`, or `'right'`. Defaults to "bottom".
            title (str, optional): Main title header displayed above the next steps.
                Defaults to "NEXT STEPS".
            title_dy (int | float, optional): Vertical offset in pixels for the title.
                If omitted or 0, falls back to the `nextstep_title_offset` defined in the template.
                Defaults to 0.
            title_dx (int | float, optional): Horizontal offset in pixels for the title.
                Defaults to 0.
            mode (str, optional): Layout orientation for displaying the step boxes.
                Must be either `'horizontal'` or `'vertical'`. Defaults to "horizontal".
            img_url (str | list[str], optional): URL/path or list of URLs/paths for icons
                associated with each step. If a list is provided, its length must match `steps`.
                Defaults to None.
            img_width (int | float, optional): Width and height of the step icons in pixels.
                Defaults to 45.
            x_img_offset (int | float, optional): Horizontal offset in pixels for icon positioning.
                Defaults to -50.
            y_img_offset (int | float, optional): Vertical offset in pixels for icon positioning.
                Defaults to -22.5.

        Returns:
            Story: The current instance (`self`) to enable method chaining.

        Raises:
            TypeError: If `steps` is not a string or a list of strings.
            TypeError: If `img_url` is provided but is neither a string nor a list.
            ValueError: If `steps` is empty or contains more than 5 elements.
            ValueError: If `position` is not one of `'bottom'`, `'top'`, `'left'`, or `'right'`.
            ValueError: If `text_align` is not one of `'left'`, `'center'`, or `'right'`.
            ValueError: If `mode` is not `'horizontal'` or `'vertical'`.
            ValueError: If `img_url` as a list does not match the length of `steps`.
            ValueError: If `img_width` is less than or equal to 0 when `img_url` is provided.
        """
        if steps is None:
            raise ValueError("The parameter 'steps' is required")
        if isinstance(steps, str):
            steps = [steps]
        if not isinstance(steps, list) or not all(isinstance(s, str) for s in steps):
            raise TypeError("'steps' must be a string or a list of strings")
        if len(steps) < 1:
            raise ValueError("Must provide at least one step")
        if len(steps) > 5:
            raise ValueError("Maximum number of steps is 5")
        if position not in ["bottom", "top", "left", "right"]:
            raise ValueError(f"Invalid 'position' value: '{position}'. Must be one of: 'bottom', 'top', 'left', 'right'")
        if text_align not in ["left", "center", "right"]:
            raise ValueError(f"Invalid 'text_align' value: '{text_align}'. Must be one of: 'left', 'center', 'right'")
        if mode not in ["horizontal", "vertical"]:
            raise ValueError(f"Invalid 'mode' value: '{mode}'. Must be one of: 'horizontal', 'vertical'")

        if img_url is not None:
            if not isinstance(img_url, (list, str)):
                raise TypeError("'img_url' must be a list or a string")
            elif len(img_url) != len(steps):
                    raise ValueError(f"Length of 'img_url' list ({len(img_url)}) must match length of 'steps' ({len(steps)})")

        if img_width <= 0:
            raise ValueError("'img_width' must be a positive number")

        font_family = self.font
        font_size = self.em_to_px(self.font_sizes["nextstep"])
        title_color = self.colors['nextstep_title']

        gap = self.chart_style['nextstep_gap']
        text_top_padding_px = self.chart_style.get('nextstep_text_top_padding_px', max(4, font_size * 0.35))
        text_bottom_padding_px = self.chart_style.get('nextstep_text_bottom_padding_px', text_top_padding_px)
        text_side_padding_px = self.chart_style.get('nextstep_text_side_padding_px', max(6, font_size * 0.4))
        line_gap_px = self.chart_style.get('nextstep_line_gap_px', max(1.0, font_size * 0.15))
        line_height_px = font_size + line_gap_px
        layout_width = self._layout_width()
        min_box = self.chart_style['nextstep_min_box_width']
        max_box = self.chart_style['nextstep_max_box_width']

        # NUOVO
        if mode == "horizontal":
            box_width = int((layout_width - gap * (len(steps) - 1)) / len(steps))
            box_width = min(max(box_width, min_box), max_box)
            content_width = (box_width * len(steps)) + (gap * (len(steps) - 1))
            chart_width = max(layout_width, content_width)
        else: #vertical
            box_width, _ = self._context_box_size(position) #Il calcolo della larghezza utilizza lo stesso metodo del box di contesto per questioni di uniformità grafica
            chart_width = box_width
            
        box_color = self.colors['nextstep_box']
        box_border = self.colors['nextstep_border']
        text_color = self.colors['nextstep_text']

        wrapped_steps = []
        box_heights = []
        for step in steps:
            wrapped = self._wrap_text_for_width( #uniformazione alla gestione dei box di contesto
                str(step),
                box_width = box_width,
                font_size_px = font_size,
            )
            wrapped_steps.append(wrapped)
            box_heights.append(self._text_block_height(wrapped, font_size, block_type = "nextsteps"))  #uniformazione alla gestione dei box di contesto

        uniform_box_height = max(box_heights) if box_heights else self.chart_style['nextstep_box_height']
        chart_body_height = uniform_box_height

        rows = []

        text_align = text_align if text_align is not None else self.chart_style['nextstep_text_align']
        if mode == "horizontal":
            uniform_box_height = max(box_heights) if box_heights else self.chart_style['nextstep_box_height']
            chart_body_height = uniform_box_height
            for i, step_text in enumerate(wrapped_steps):
                x_left = i * (box_width + gap)
                if text_align == "left":
                    x_mid = x_left +  (box_width / 10)
                elif text_align == "center":
                    x_mid = x_left +  (box_width / 2)
                else: #right
                    x_mid = x_left + box_width - 10
                rows.append({
                    'x': x_left,
                    'y': 0,
                    'x2': x_left + box_width,
                    'y2': uniform_box_height,
                    'text': step_text,
                    'x_mid': x_mid,
                    'y_text': uniform_box_height - text_top_padding_px,
            })
        else: #vertical
            total_body_height = sum(box_heights) + (gap * (len(steps) - 1))
            chart_body_height = total_body_height

            current_top = total_body_height
            for i, step_text in enumerate(wrapped_steps):
                h_i = box_heights[i]
                y_bottom = current_top - h_i
                if text_align == "left":
                    x_mid = text_side_padding_px
                elif text_align == "center":
                    x_mid = box_width / 2
                else: #right
                    x_mid = box_width - text_side_padding_px
                rows.append({
                    'x': 0,
                    'y': y_bottom,
                    'x2': box_width,
                    'y2': current_top,
                    'text': step_text,
                    'x_mid': x_mid,
                    'y_text': current_top - text_top_padding_px,
                })
                current_top = y_bottom - gap

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
            width = chart_width,
            height = chart_body_height + self.chart_style['nextstep_chart_height_padding']
        )

        text = alt.Chart(df_rect).mark_text(
            color = text_color,
            font = font_family,
            fontSize = font_size,
            align = text_align,
            baseline = "top",
            lineBreak = self.chart_style['text_line_break'],
            lineHeight = font_size * self.chart_style['context_line_height_ratio'], #uniformazione alla gestione dei box di contesto
        ).encode(
            text = "text:N",
            x = alt.X('x_mid:Q', axis=None),
            y = alt.Y('y_text:Q', axis=None),
        )

        if img_url:
            df_rect["img_url"] = img_url
            img_layer = alt.Chart(df_rect).mark_image(
                width = img_width,
                height = img_width,
                baseline = "bottom",
                xOffset = x_img_offset,
                yOffset = y_img_offset
            ).encode(
                x = alt.X('x:Q', axis=None),
                y = alt.Y('y:Q', axis=None),
                url = "img_url:N",
            )
            chart = alt.layer(rect, text, img_layer)
        else:
            chart = alt.layer(rect, text)

        title_dy = title_dy if title_dy else self.chart_style["nextstep_title_offset"]
        if title:
            dx = title_dx
            if img_url:
                dx = x_img_offset + title_dx
            chart = chart.properties(
                title=alt.TitleParams(
                    text = [title],
                    fontSize = self.em_to_px(self.font_sizes["nextstep"]) + 5,
                    font = font_family,
                    color = title_color,
                    fontWeight = "bold",
                    align = "center",
                    baseline = "top",
                    dx = dx,
                    offset = title_dy,
                )
            )


        self.story_layers.append({
            'type': 'special_cta',
            'chart': chart,
            'position': position
        })

        return self


    
    def add_source(self, text, position='top', vertical=False, align = "center"):
        """Adds a source (or credits) attribution layer to the story.

        Args:
            text (str): The source text or attribution to display.
            position (str, optional): Position of the source relative to the chart.
                Must be one of `'top'`, `'bottom'`, `'left'`, or `'right'`.
                Defaults to "top".
            vertical (bool, optional): Whether to rotate the text 90 degrees.
                Defaults to False.
            align (str, optional): Horizontal text alignment when `position` is `'top'` or
                `'bottom'`. Must be one of `'left'`, `'center'`, or `'right'`.
                Defaults to "center".

        Returns:
            Story: The current instance (`self`) to enable method chaining.

        Raises:
            TypeError: If `text` is not a string.
            TypeError: If `vertical` is not a boolean.
            ValueError: If `position` is not one of `'top'`, `'bottom'`, `'left'`, or `'right'`.
            ValueError: If `align` is specified (other than default `'center'`) when `position`
                is `'left'` or `'right'`.
            ValueError: If `align` is not one of `'left'`, `'center'`, or `'right'`.
        """

        #GESTIONE ERRORI
        if not isinstance(text, str):
            raise TypeError(f"'text' must be a string, got {type(text).__name__}")
        if not isinstance(vertical, bool):
            raise TypeError(f"'vertical' must be a boolean, got {type(vertical).__name__}")
        if position not in ['bottom', 'top', 'left', 'right']:
            raise ValueError(f"Invalid 'position' value: '{position}'. Must be one of: 'top', 'bottom', 'left', 'right'")
        if position in ["left", "right"] and align != "center":
            raise ValueError("Horizontal alignment ('align') cannot be customized when 'position' is 'left' or 'right'")
        if align not in ["left", "center", "right"]:
            raise ValueError(f"Invalid 'align' value: '{align}'. Must be one of: 'left', 'center', 'right'")
        
        self.story_layers.append({
            'type': 'source', 
            'text': text, 
            'position': position, 
            'vertical': vertical,
            "align": align
        })

        return self
    

    def add_annotation(
        self,
        x=None,
        y=None,
        text=None,
        title=None,
        dx=0,
        dy=0,
        background_color = None,
        text_color = None,
        show_subject = False,
        line_point_color = None,
        img_url = None,
        img_width = 60,
        x_img_offset = 0,
        y_img_offset = 0,
    ):
        """Adds an annotation layer anchored to quantitative (x, y) coordinates.

        Args:
            x (int | float): Subject X-coordinate in chart data space.
            y (int | float): Subject Y-coordinate in chart data space.
            text (str, optional): Main annotation body text. Required if `img_url` is None.
                Defaults to None.
            title (str, optional): Title header prepended above the text. Defaults to None.
            dx (int | float, optional): Horizontal pixel offset from the subject point
                to the annotation box corner. Defaults to 0.
            dy (int | float, optional): Vertical pixel offset from the subject point
                to the annotation box corner. Defaults to 0.
            background_color (str, optional): Background color for the annotation box.
                If omitted or None, falls back to the `annotation_fill` defined in the
                template or the context box fill setting. Defaults to None.
            text_color (str, optional): Text color for the annotation label.
                If omitted or None, falls back to the `annotation_text` defined in the
                template or context color settings. Defaults to None.
            show_subject (bool, optional): If True, draws a point marker at (x, y) and
                a connecting line to the annotation box, that slightly shifts. Defaults to False.
            line_point_color (str, optional): Custom color for the connecting line and
                subject point marker. If omitted or None, falls back to `text_color`.
                Defaults to None.
            img_url (str, optional): URL or file path for an image/icon inside the annotation.
                Required if `text` is None. Defaults to None.
            img_width (int | float, optional): Width and height of the annotation image in pixels.
                Defaults to 60.
            x_img_offset (int | float, optional): Horizontal pixel offset for the image position.
                Defaults to 0.
            y_img_offset (int | float, optional): Vertical pixel offset for the image position.
                Defaults to 0.
            **kwargs: Unused keyword arguments.

        Returns:
            Story: The current instance (`self`) to enable method chaining.

        Raises:
            TypeError: If `show_subject` is not a boolean.
            ValueError: If both `x` and `y` are not provided, or are non-numeric.
            ValueError: If both `text` and `img_url` are missing.
            ValueError: If either the X or Y chart axes are not quantitative ('Q').
            ValueError: If axis numeric ranges cannot be resolved.
            ValueError: If `img_width` is less than or equal to 0 when `img_url` is provided.
        """

        if x is None or y is None:
            raise ValueError("add_annotation requires x and y coordinates.")
        if text is None and img_url is None:
            raise ValueError("add_annotation requires at least 'text' or 'img_url'.")
        if not isinstance(show_subject, bool):
            raise TypeError(f"'show_subject' must be a boolean, got {type(show_subject).__name__}")

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

        box_w_data = (box_width_px + 5 * (box_padding_px + text_left_padding_px)) * x_per_px
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

        text_color = text_color if text_color else self.colors.get('annotation_text', self.colors.get('callout_text', self.colors['context']))
        box_fill = background_color if background_color else self.colors.get('annotation_fill', self.context_box['fill'])
        box_stroke = self.colors.get('annotation_stroke', self.context_box['stroke'])
        line_color = line_point_color if line_point_color else text_color
        point_color = line_color
        point_size = self.chart_style.get('annotation_point_size', self.chart_style.get('callout_point_size', 60))
        line_width = self.chart_style.get('annotation_line_width', self.chart_style.get('callout_arrow_line_width', 2))
        box_opacity = self.chart_style.get('annotation_box_opacity', self.chart_style.get('callout_box_opacity', 1.0))
        box_border_width = self.chart_style.get('annotation_box_border_width', self.chart_style.get('callout_box_border_width', 1))

        layers = []
        if show_subject == True:
            dx = -50
            dy = -50
            layers.append(
                alt.Chart(annotation_data).mark_point(color=point_color, size=point_size).encode(
                    x=alt.X('subject_x:Q'),
                    y=alt.Y('subject_y:Q'),
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

        if text is not None:
            layers.append(
                alt.Chart(annotation_data).mark_rect(
                    color=box_fill,
                    opacity=box_opacity,
                    cornerRadius=self.context_box['corner_radius'],
                    stroke=box_stroke,
                    strokeWidth=box_border_width,
                    dx = dx,
                    dy = dy

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
                    color=text_color,
                ).encode(
                    x=alt.X('text_x:Q'),
                    y=alt.Y('text_y:Q')
                ).properties(width=self.chart.width, height=self.chart.height)
            )

        if img_url:
            y_img_offset = x_img_offset if x_img_offset != 0 else (-50 if text is not None else 0)
            y_img_offset = y_img_offset if y_img_offset != 0 else (50 if text is not None else 0)
            layers.append(
                alt.Chart(annotation_data)
                    .mark_image(
                        width = img_width,
                        height = img_width,
                        baseline = "middle",
                        xOffset = x_img_offset,
                        yOffset = y_img_offset
                    ).encode(
                        x=alt.X('text_x:Q'),
                        y=alt.Y('text_y:Q'),
                        url = alt.value(img_url)
                    )
            )

        self.story_layers.append({'type': 'annotation', 'chart': alt.layer(*layers)})
        return self
    

    def add_line(
            self,
            value,
            orientation='horizontal',
            math = None,
            color = "",
            label_text = "",
            label_dx = 0,
            label_dy = 0,
            label_font_size = "",
            label_font_weight = "normal",
            label_font_style = "normal",
            ):
        """Adds a reference line (horizontal or vertical) with an optional label to the story.

        Args:
            value (int | float | list | pandas.Series): Position of the reference line.
                If `math` is specified, must be a list or `pandas.Series` of numbers.
                Otherwise, must be a single numeric value (`int` or `float`).
            orientation (str, optional): Line orientation relative to axes. Must be either
                `'horizontal'` or `'vertical'`. Defaults to "horizontal".
            math (str, optional): Automatic aggregation function to calculate `value`.
                Must be one of `'mean'`, `'median'`, `'min'`, or `'max'`. Defaults to None.
            color (str, optional): Line and label text color. If omitted or None, falls back to
                the `reference_line_color` defined in the template layout settings.
                Defaults to None.
            label_text (str, optional): Custom text displayed alongside the line. If None,
                defaults to the formatted calculated value (e.g., "Mean 12.5" or "12.5").
                Set to `""` (empty string) to hide the label entirely. Defaults to None.
            label_dx (int | float, optional): Horizontal pixel offset for the label position.
                Defaults to 0.
            label_dy (int | float, optional): Vertical pixel offset for the label position.
                Defaults to 0.
            label_font_size (int | float, optional): Font size of the label text in pixels.
                If omitted or None, falls back to the `line_label` size defined in the template.
                Defaults to None.
            label_font_weight (str, optional): Font weight of the label text.
                Must be one of `'normal'` or `'bold'`. Defaults to "normal".
            label_font_style (str, optional): Font style of the label text.
                Must be one of `'normal'` or `'italic'`. Defaults to "normal".

        Returns:
            Story: The current instance (`self`) to enable method chaining.

        Raises:
            TypeError: If `value` type does not match the requirements of `math`.
            TypeError: If `label_font_size` is provided but is not an integer or float.
            ValueError: If `orientation` is not `'horizontal'` or `'vertical'`.
            ValueError: If `math` is not one of `'mean'`, `'median'`, `'min'`, `'max'`, or None.
            ValueError: If `label_font_weight` is not `'normal'` or `'bold'`.
            ValueError: If `label_font_style` is not `'normal'` or `'italic'`.
        """

        if orientation not in ['horizontal', 'vertical']:
            raise ValueError(f"Invalid 'orientation' value: '{orientation}'. Must be either 'horizontal' or 'vertical'")
        if label_font_weight not in ["normal", "bold"]:
            raise ValueError("label_font_weight must be one of: 'normal', 'bold'")
        if label_font_style not in ["normal", "italic"]:
            raise ValueError("label_font_style must be one of: 'normal', 'italic'")

        def axis_type(axis):
            if hasattr(self.chart, 'encoding') and hasattr(self.chart.encoding, axis):
                shorthand = getattr(self.chart.encoding, axis).shorthand
                if shorthand and ':' in shorthand:
                    return shorthand.split(':')[-1]
            return 'Q'


        #Math
        if math not in ["mean", "median", "min", "max", None]:
            raise ValueError(f"Invalid 'math' value: '{math}'. Must be one of: 'mean', 'median', 'min', 'max', or None")
        if math is not None:
            if not isinstance(value, (list, pd.Series)):
                raise ValueError("When 'math' is specified, 'value' must be a list or a pandas Series. Try something as: 'value = dataframe['value_column']' or 'value = dataframe['value_column'].tolist()")
            
            if len(value) == 0:
                raise ValueError("Cannot perform 'math' calculation on an empty sequence.")
            
            clean_values = [v for v in value if pd.notna(v)]

            if math == "mean": #Media
                line_value = round(sum(clean_values) / len(clean_values), 2)
                print(f"Mean = {line_value}")

            elif math == "median": #Mediana
                line_value = round(float(np.median(clean_values)), 2)
                print(f"Median = {line_value}")

            elif math == "min": #Minimo
                line_value = round(float(min(clean_values)), 2)
                print(f"Min = {line_value}")

            elif math == "max": #Massimo
                line_value = round(float(max(clean_values)), 2)
                print(f"Max = {line_value}")
        else:
            if value is None or not isinstance(value, (int, float, np.number)):
                raise ValueError("When 'math' is None, 'value' must be a numeric integer or float.")
            line_value = float(value)
            print(f"Single value = {line_value}")


        # Crea un DataFrame con un singolo valore
        if orientation == 'horizontal':
            y_type = axis_type('y')
            data = pd.DataFrame({'y': [line_value]})
            encoding = {'y': f'y:{y_type}'}
        else:  # vertical
            x_type = axis_type('x')
            data = pd.DataFrame({'x': [line_value]})
            encoding = {'x': f'x:{x_type}'}


        # Crea la linea
        line_color = color if color else self.chart_style["reference_line_color"]

        line = alt.Chart(data).mark_rule(
            color = line_color,
            strokeWidth=self.chart_style['reference_line_width'],
            strokeDash=self.chart_style['reference_line_dash']
        ).encode(
            **encoding,
        )

        data_label = data.copy()
        if label_text is None:
            if math == "mean":
                label_text = f"Mean {str(line_value)}"
            elif math == "median":
                label_text = f"Median {str(line_value)}"
            else:
                label_text = str(line_value) #etichetta di default col valore numerico
        else:
            label_text = str(label_text)

        if orientation == 'horizontal':
            data_label['label_x'] = 0 
            y_offset = self.chart_width + 10
            label_encoding = {**encoding, 'x': alt.value(y_offset)}
        else:  # vertical
            data_label['label_y'] = 0
            x_offset = -10
            label_encoding = {**encoding, 'y': alt.value(x_offset)}

        if label_font_size == "":
            font_size = self.em_to_px(self.font_sizes["line_label"])

        else:
            if not isinstance(label_font_size, (int, float)):
                raise TypeError("'label_font_size' must be an integer or float.")
            #else
            font_size = label_font_size

        label = alt.Chart(data_label).mark_text(
            color = line_color,
            fontSize = font_size,
            align = "left",
            dx = label_dx,
            dy = label_dy,
            fontWeight = label_font_weight,
            fontStyle = label_font_style,
        ).encode(
            **label_encoding,
            text = alt.value(label_text),
        )

        line = line + label

        # Aggiunge la linea ai layer della storia
        self.story_layers.append({
            'type': 'line',
            'chart': line
        })

        return self

    def add_highlight(
            self,
            category,
            highlight_color = None,
            img_url = None,
            img_width = 35,
            x_img_offset = 0,
            y_img_offset = -25,
            text_label = None,
            label_font_size = 20,
            label_text_angle = 90,
            label_text_color = "black",
            label_text_dx = 100,
            label_text_dy = 0,
            label_font_weight = "bold"
            ):
        """Highlights one or more target categories in a bar chart while muting the remaining bars.

            Optionally adds image markers or custom text callouts anchored to the highlighted bars.
            Supports nominal (`:N`), ordinal (`:O`), and quantitative/discrete (`:Q`) target axes.

            Args:
                category (str | int | float | list | tuple | set): The category value or list of
                    category values to highlight on the target chart axis.
                highlight_color (str, optional): Custom fill color for highlighted bars. If omitted or
                    None, falls back to `bar_highlight` or `bar_fill_color` in theme settings.
                    Defaults to None.
                img_url (str, optional): URL or local file path for an image icon placed over
                    the highlighted bar(s). Defaults to None.
                img_width (int | float, optional): Width and height of the overlay image in pixels.
                    Defaults to 35.
                x_img_offset (int | float, optional): Horizontal pixel offset for the overlay image.
                    Defaults to 0.
                y_img_offset (int | float, optional): Vertical pixel offset for the overlay image.
                    Defaults to -25.
                text_label (str, optional): Text annotation label displayed over the highlighted bar.
                    Defaults to None.
                label_font_size (int | float, optional): Font size of the text label in pixels.
                    Defaults to 20.
                label_text_angle (int | float, optional): Rotation angle of the text label in degrees.
                    Defaults to 90.
                label_text_color (str, optional): Text color for the annotation label.
                    Defaults to "black".
                label_text_dx (int | float, optional): Horizontal pixel offset for the text label.
                    Defaults to 100.
                label_text_dy (int | float, optional): Vertical pixel offset for the text label.
                    Defaults to 0.
                label_font_weight (str, optional): Font weight of the text label. Must be one of
                    `'normal'` or `'bold'`. Defaults to "bold".

            Returns:
                Story: The current instance (`self`) to enable method chaining.

            Raises:
                TypeError: If numerical parameters (`img_width`, `label_font_size`, offsets) are non-numeric.
                ValueError: If the chart is not a bar chart or lacks a DataFrame source.
                ValueError: If no nominal, ordinal, or quantitative axis is found.
                ValueError: If the target axis field is missing from DataFrame columns.
                ValueError: If none of the specified `category` values exist in the target field.
                ValueError: If `label_font_weight` is not `'normal'` or `'bold'`.
                ValueError: If `img_width` is less than or equal to 0 when `img_url` is provided.
        """


        if not self._is_bar_chart():
            raise ValueError("add_highlight works only with bar charts.")
        if not isinstance(self.chart.data, pd.DataFrame):
            raise ValueError("add_highlight requires DataFrame-backed chart data.")

        if label_font_weight not in ["normal", "bold"]:
            raise ValueError(f"Invalid 'label_font_weight' value: '{label_font_weight}'. Must be 'normal' or 'bold'")

        try:
            img_width = float(img_width)
            x_img_offset = float(x_img_offset)
            y_img_offset = float(y_img_offset)
            label_font_size = float(label_font_size)
            label_text_angle = float(label_text_angle)
            label_text_dx = float(label_text_dx)
            label_text_dy = float(label_text_dy)
        except (TypeError, ValueError):
            raise TypeError("Image offsets, font size, angles, and dimensions must be numeric.")

        if img_url is not None and img_width <= 0:
            raise ValueError("'img_width' must be a positive number")

        x_field, x_type = self._get_encoding_field_and_type('x')
        y_field, y_type = self._get_encoding_field_and_type('y')
        
        category_field = None
        category_type = None

        #Accetta anche ':Q' per supportare assi temporali/numerici discreti(zzati)
        if x_type in ['N', 'O', 'Q']:
            category_field, category_type = x_field, x_type
        elif y_type in ['N', 'O', 'Q']:
            category_field, category_type = y_field, y_type

        if not category_field:
            raise ValueError("add_highlight requires a categorical (:N or :O) or quantitative axis (:Q).")
        if category_field not in self.chart.data.columns:
            raise ValueError(f"Category field '{category_field}' not found in chart data.")

        def _normalize(val):
            if pd.isna(val):
                return None
            if isinstance(val, (int, float)):
                if float(val).is_integer():
                    return int(val)
                return float(val)
            return str(val).strip()

        # attrs storage
        if not hasattr(self, '_highlighted_categories') or self._highlighted_categories is None:
            self._highlighted_categories = []
        if not hasattr(self, '_highlight_color_map') or self._highlight_color_map is None:
            self._highlight_color_map = {}
        if not hasattr(self, '_overlays') or self._overlays is None:
            self._overlays = []

        if isinstance(category, (list, tuple, set)):
            categories_list = list(category)
        else:
            categories_list = [category]

        target_norms = {_normalize(c) for c in categories_list}
        
        matched_categories = []
        for val in self.chart.data[category_field]:
            norm_val = _normalize(val)
            if norm_val in target_norms:
                if not any(_normalize(mc) == norm_val for mc in matched_categories):
                    matched_categories.append(val)

        if not matched_categories:
            raise ValueError(f"None of the requested categories '{category}' were found in field '{category_field}'.")


        if len(categories_list) > len(matched_categories):
            matched_norms = {_normalize(mc) for mc in matched_categories}
            for cat in categories_list:
                if _normalize(cat) not in matched_norms:
                    warnings.warn(f"Value '{cat}' was not found in field '{category_field}'.", UserWarning,)

        chosen_color = highlight_color if highlight_color else self.colors.get(
            'bar_highlight',
            self.chart_style.get('bar_fill_color', '#1d4ed8')
        )

        for val in matched_categories:
            norm_val = _normalize(val)
            if not any(_normalize(m) == norm_val for m in self._highlighted_categories):
                self._highlighted_categories.append(val)
            native_val = val.item() if hasattr(val, 'item') else val
            self._highlight_color_map[native_val] = chosen_color


        native_matched_global = [c.item() if hasattr(c, 'item') else c for c in self._highlighted_categories]
        global_condition_clause = alt.FieldOneOfPredicate(
            field = category_field,
            oneOf = native_matched_global
        )

        native_matched_local = [c.item() if hasattr(c, 'item') else c for c in matched_categories]
        local_condition_clause = alt.FieldOneOfPredicate(
            field = category_field,
            oneOf = native_matched_local
        )

        has_series, _ = self._get_encoding_field_and_type("color")
        if has_series is not None:
            self.chart = self.chart.encode(
                opacity=alt.condition(
                    global_condition_clause,
                    alt.value(1.0),
                    alt.value(0.5)
                )
            )
        else:
            muted_color = self.colors.get(
                'bar_muted',
                self.chart_style.get('axis_tick_color', '#cbd5e1')
            )

            domain = list(self._highlight_color_map.keys())
            range_colors = list(self._highlight_color_map.values())

            self.chart = self.chart.encode(
                color=alt.condition(
                    global_condition_clause,
                    alt.Color(
                        f"{category_field}:{category_type}",
                        scale = alt.Scale(domain = domain, range = range_colors),
                        legend = None
                    ),
                    alt.value(muted_color)
                )
            )

        # Overlays
        if img_url:
            img_overlay = (
                alt.Chart(self.chart.data)
                .transform_filter(local_condition_clause)
                .mark_image(
                    width = img_width,
                    height = img_width,
                    baseline = "bottom",
                    xOffset = x_img_offset,
                    yOffset = y_img_offset
                ).encode(
                    x = f"{x_field}:{x_type}",
                    y = f"{y_field}:{y_type}",
                    url = alt.value(img_url),
                )
            )
            self._overlays.append(img_overlay)

        if text_label:
            text_overlay = (
                alt.Chart(self.chart.data)
                .transform_filter(local_condition_clause)
                .mark_text(
                    text = text_label,
                    fontSize = label_font_size,
                    fontWeight = label_font_weight,
                    angle = label_text_angle,
                    dx = label_text_dx,
                    dy = label_text_dy,
                    color = label_text_color
                )
                .encode(
                    x = f"{x_field}:{x_type}",
                    y = f"{y_field}:{y_type}",
                )
            )
            self._overlays.append(text_overlay)

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
    

    def create_source_anchored_layer(self, layer):
        """
        Creates a text layer for the source, anchored directly to the main chart's coordinate space.

        This ensures precise horizontal and vertical alignment of the source box relative to 
        the core chart area, preventing alignment issues caused by external layout elements 
        such as side context boxes.
        """
        font_size = layer.get('font_size', self.em_to_px(self.font_sizes['source']))
        position = layer.get('position', 'bottom')
        align_mode = layer.get("align")
        main_chart_width = self.chart.width
        main_chart_heigth = self.chart.height

        #calcolo dell'allineamento orizzontale della source rispetto al grafico principale
        if align_mode == "left":
            x_pos = 10 #piccolo rientro
            text_align = "left"
        elif align_mode == "right":
            x_pos = main_chart_width - 10 #piccolo rientro
            text_align = "right"
        else:  # center, default
            x_pos = (main_chart_width / 2)
            text_align = "center"


        if position == 'bottom':
            padding = self.chart_style.get('source_bottom_padding', 60)
            y_pos = main_chart_heigth + padding
            baseline = 'top'
        else:  # top
            padding = self.chart_style.get('source_top_padding', 20)
            y_pos = -padding
            baseline = 'bottom'


        source_chart = alt.Chart(pd.DataFrame({'_': [0]})).mark_text(
            text=layer['text'],
            fontSize=font_size,
            align=text_align,
            baseline=baseline,
            font=self.font,
            lineBreak=self.chart_style['text_line_break'],
            color=layer.get('color', self.colors.get('source', self.colors['context']))
        ).encode(
            x=alt.value(x_pos),
            y=alt.value(y_pos)
        )

        return source_chart


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
            height=self.chart_style['title_area_height'],
        )

        align_mode = layer.get("align", "center") #default center

        if align_mode == "left":
            x_position = 10
        elif align_mode == "right":
            x_position = layout_width - 10
        else: #default, center
            x_position = layout_width/2

        # NUOVO
        title_background = base.mark_rect(
            color = layer.get("background_color", "transparent"), #default transparent
        )
        
        title_chart = base.mark_text(
            text=layer['title'],
            font=self.chart_style["title_font"],
            fontSize=self.em_to_px(self.font_sizes['title']),
            fontWeight=self.chart_style['title_font_weight'],
            align = align_mode,
            baseline=self.chart_style['title_baseline'],
            color=layer.get("color", self.colors["title"])
        ).encode(
            x = alt.value(x_position),
            y = alt.value(self.chart_style['title_y'])
        )

        final_chart = title_background + title_chart
        
        if layer['subtitle']:
            subtitle_chart = base.mark_text(
                text=layer['subtitle'],
                fontSize=self.em_to_px(self.font_sizes['subtitle']),
                align = align_mode,
                baseline=self.chart_style['subtitle_baseline'],
                font=self.font,
                color=self.colors['subtitle']
            ).encode(
                x = alt.value(x_position),
                y = alt.value(self.chart_style['subtitle_y'])
            )
            final_chart += subtitle_chart

        if layer["img_url"]:
            image_layer = base.mark_image(
                width = layer["img_width"],
                height = layer["img_width"],
                baseline = "middle",
                xOffset = layer["x_img_offset"],
                yOffset = layer["y_img_offset"]
            ).encode(
                x = alt.value(x_position),
                y = alt.value(self.chart_style['subtitle_y'] - self.chart_style['title_y']), #Centers
                url = alt.value(layer["img_url"])
            )
            final_chart += image_layer
        
        return final_chart


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
        font_weight = layer.get("font_weight", "normal")
        font_style = layer.get("font_style", "normal")

        box_width = layer.get('box_width')
        box_height = layer.get('box_height')
        if box_width is None or box_height is None:
            box_width, _ = self._context_box_size(layer.get('position', 'left'))
            box_height = self._text_block_height(layer.get('text', ''), font_size, block_type = "context")


        position_side = layer.get("position")
        side_context_count = sum(
            1 for l in self.story_layers 
            if l.get('type') == 'context' and l.get('position') == position_side
        )

        #Gestione dell'allineamento verticale del blocco di testo rispetto al grafico
        chart_height = box_height
        if position_side in ["left", "right"]:
            align_mode = layer.get("align")
            # Soltanto un context box
            if side_context_count == 1:
                if align_mode == "top":
                    y_start = 0
                    y_end = box_height
                    text_y_position = padding

                elif align_mode == "bottom":
                    y_start = self.height - box_height
                    y_end = self.height
                    text_y_position = y_start + padding

                else: #middle
                    remaining_space = self.height - box_height
                    y_start = remaining_space / 2
                    y_end = y_start + box_height
                    text_y_position = y_start + padding
            # Più di un context box
            else:
                y_start = 0
                y_end = box_height
                text_y_position = padding
            
        else: #fallback per position top o bottom
            y_start = 0
            y_end = box_height
            text_y_position = padding


        base = alt.Chart(pd.DataFrame({'_': [0]})).properties(
            width=box_width,
            height=chart_height
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
            y=alt.value(y_start),
            y2=alt.value(y_end)
        )

        text_align =  self.chart_style['context_text_align']
        if layer["text_align"] is not None:
            text_align =  layer["text_align"]

        if text_align == "left":
            x_text = padding
        elif text_align == "center":
            x_text =  (box_width / 2)
        else: #right
            x_text = box_width - padding

        text = base.mark_text(
            text=layer['text'],
            fontSize=font_size,
            # align=self.chart_style['context_text_align'],
            align = text_align,
            baseline=self.chart_style['context_text_baseline'],
            font=self.font,
            lineBreak=self.chart_style['text_line_break'],
            lineHeight=font_size * self.chart_style['context_line_height_ratio'],
            color=layer.get('color', self.colors['context']),
            fontWeight = font_weight,
            fontStyle = font_style,
        ).encode(
            x=alt.value(x_text),
            y=alt.value(text_y_position)
        )


        final_chart = box + text

        title = layer.get("title")
        if title:
            title_layer = base.mark_text(
                text=title,
                fontSize=self.em_to_px(self.font_sizes["context"]) + 5,
                font=self.font,
                color=self.colors["context"],
                fontWeight="bold",
                align = "center",
                baseline="bottom",
                dy = layer["title_dy"]
            ).encode(
                x=alt.value(box_width / 2),
                y=alt.value(y_start - 5)
            )

            final_chart += title_layer

        if layer["img_url"]:
            if position_side in ["left", "right"]:
                y_encoding = box_height
            else:
                y_encoding = 0
            image_layer = base.mark_image(
                width = layer["img_width"],
                height = layer["img_width"],
                baseline = "top",
                xOffset = layer["x_img_offset"],
                yOffset = layer["y_img_offset"]
            ).encode(
                x = alt.value(0),
                y = alt.value(y_encoding),
                url = alt.value(layer["img_url"])
            )
            final_chart += image_layer

        return final_chart


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

        #NUOVO
        paragraphs = text.split("\n")
        all_lines = []

        for paragraph in paragraphs:
            if not paragraph.strip():
                all_lines.append("")
            else:
                lines = textwrap.wrap(
                    paragraph, 
                    width=max_chars,
                    break_long_words=False, 
                    break_on_hyphens=False,
                    replace_whitespace=False,
                )
                
                all_lines.extend(lines if lines else [paragraph])
        
        return "\n".join(all_lines) if all_lines else ""

    def _text_block_height(self, text, font_size_px, block_type):
        if block_type == "context":
            padding = 2 * self.context_box['padding']
        elif block_type == "nextsteps":
            padding = self.chart_style["nextstep_text_top_padding_px"] + self.chart_style["nextstep_text_bottom_padding_px"]
        line_height = font_size_px * self.chart_style['context_line_height_ratio']
        lines = (str(text).splitlines() if text is not None else [""])
        line_count = max(len(lines), 1)
        return (line_count * line_height) + padding
    def _layout_width(self):
        width = self.chart.width
        width += self.chart.width * self.chart_style['layout_context_side_width_ratio']
        return width

    def _arrow_angle(self, x_from, y_from, x_to, y_to):
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
    

    def add_labels_chart(self,
                         values = None,
                         color = None,
                         orientation = "horizontal",
                         angle=0,
                         dx=0,
                         dy=0,
                         font_size=11,
                         font_weight="normal",
                         geodata = False,
                         geodata_label = None
                         ):
        """Adds custom text labels to an existing chart layer or map visualization.

        Creates an Altair `mark_text` layer positioned relative to existing chart encodings
        or geodata centroids. Supports custom orientations, offsets, and fonts.

        Args:
            values (str | list | pandas.Series, optional): Column name or explicit list of values
                to display as labels. If None, automatically defaults to the Y-axis encoding field.
                Defaults to None.
            color (str, optional): Custom fill color for the label text. If omitted or None,
                falls back to the `chart_label_color` defined in the template style settings.
                Defaults to None.
            orientation (str, optional): Preset label layout orientation. Must be one of
                `'horizontal'`, `'vertical_left'` (angle=90), or `'vertical_right'` (angle=270).
                For custom rotations, use `'horizontal'` and set `angle` directly.
                Defaults to "horizontal".
            angle (int | float, optional): Label rotation angle in degrees. Must be between 0 and 360.
                Cannot be combined with preset orientations other than `'horizontal'`.
                Defaults to 0.
            dx (int | float, optional): Horizontal pixel offset for text positioning.
                Defaults to 0.
            dy (int | float, optional): Vertical pixel offset for text positioning.
                Defaults to 0.
            font_size (int | float, optional): Font size of the text labels in pixels.
                Defaults to 11.
            font_weight (str, optional): Font weight for the label text. Must be one of
                `'normal'` or `'bold'`. Defaults to "normal".
            geodata (bool, optional): Whether the target chart represents geographic map data.
                If True, labels are placed on spatial geometry centroids. Defaults to False.
            geodata_label (str, optional): The column name containing text labels when `geodata=True`.
                Required if `geodata` is True. Defaults to None.

        Returns:
            Story: The current instance (`self`) to enable method chaining.

        Raises:
            TypeError: If numerical parameters (`angle`, `dx`, `dy`, `font_size`) receive boolean or non-numeric types.
            TypeError: If `geodata` is not a boolean.
            ValueError: If used on multi-series charts without enabling `geodata=True`.
            ValueError: If `angle` is not between 0 and 360 degrees.
            ValueError: If `orientation` is not one of `'horizontal'`, `'vertical_left'`, or `'vertical_right'`.
            ValueError: If a non-zero `angle` is combined with `'vertical_left'` or `'vertical_right'`.
            ValueError: If `font_weight` is not `'normal'` or `'bold'`.
            ValueError: If `geodata=True` but `geodata_label` is omitted.
            ValueError: If no Y-axis encoding or explicit `values` can be resolved.
        """

        if not isinstance(geodata, bool):
            raise TypeError(f"'geodata' must be a boolean, got {type(geodata).__name__}")

        if isinstance(angle, bool) or not isinstance(angle, (int, float)):
            raise TypeError(f"'angle' must be a numeric integer or float, got {type(angle).__name__}")

        if not (0 <= angle <= 360):
            raise ValueError(f"Value of 'angle' must be between 0 and 360, got {angle}")

        if isinstance(dx, bool) or not isinstance(dx, (int, float)):
            raise TypeError(f"'dx' must be a numeric integer or float, got {type(dx).__name__}")

        if isinstance(dy, bool) or not isinstance(dy, (int, float)):
            raise TypeError(f"'dy' must be a numeric integer or float, got {type(dy).__name__}")

        if isinstance(font_size, bool) or not isinstance(font_size, (int, float)) or font_size <= 0:
            raise TypeError(f"'font_size' must be a positive number, got {type(font_size).__name__}")

        if font_weight not in ["normal", "bold"]:
            raise ValueError(f"Invalid 'font_weight' value: '{font_weight}'. Must be 'normal' or 'bold'")

        has_series, _ = self._get_encoding_field_and_type("color")
        if has_series is not None and not geodata:
            raise ValueError(
                "add_labels_chart cannot be used on charts with multiple series. "
                "For geographical data, set 'geodata = True'."
            )

        
        preset_orientations = ["horizontal", "vertical_left", "vertical_right"]
        if orientation not in preset_orientations:
            raise ValueError(
                f"Invalid 'orientation' value: '{orientation}'. Must be one of {preset_orientations}. "
                "For custom layouts, use 'horizontal' with explicit angle, dx, and dy settings."
            )

        if orientation != "horizontal" and angle != 0:
            raise ValueError(
                f"Cannot specify a custom angle ({angle}) when using orientation '{orientation}'. "
                "Use orientation 'horizontal' when specifying custom angles."
            )
        
        if orientation == "vertical_left":
            angle = 90
        if orientation == "vertical_right":
            angle = 270

        
        mark_color = color if color else self.colors.get("chart_label_color", "#000000")

        if geodata:
            if geodata_label is None:
                raise ValueError("When 'geodata=True', you must specify 'geodata_label'.")
            else:
                values = self.data.copy()
                centroids = values.geometry.to_crs(epsg=3035).centroid.to_crs(epsg=4326)
                values["lon"] = centroids.x
                values["lat"] = centroids.y
                self.label_layer = alt.Chart(values[values[geodata_label].notna()]).mark_text(
                    align = "center",
                    dx = dx,
                    dy = dy,
                    lineBreak="\n",
                    angle = angle,
                    color = mark_color,
                    fontSize = font_size,
                    fontWeight = font_weight
                ).encode(
                    longitude = "lon:Q",
                    latitude = "lat:Q",
                    text=f"{geodata_label}:N",
                )

                return self


        y_enc = self.encoding.get("y") if isinstance(self.encoding, dict) else getattr(self.encoding, "y", None)
        
        if y_enc is not None:
            shorthand = getattr(y_enc, "shorthand", str(y_enc))
            field_name = shorthand.split(":")[0] if ":" in shorthand else shorthand
            labels = f"{field_name}:Q"
        else:
            labels = None

        if values is not None and len(values) > 0:
            if not isinstance(values, (str, list, pd.Series)):
                raise TypeError("'values' must be a column name (str), a list, or a pandas Series.")

            if isinstance(values, str):
                if ":" in values:
                    labels = values
                else:
                    if values in self.data.columns and pd.api.types.is_numeric_dtype(self.data[values]):
                        labels = f"{values}:Q"
                    else:
                        labels = f"{values}:N"

            elif isinstance(values, (list, pd.Series)):
                first_elem = values[0] if isinstance(values, list) else values.iloc[0]
                data_type = "Q" if isinstance(first_elem, (int, float, np.number)) else "N"
                
                chart_data = self.data.copy()
                chart_data["_custom_label"] = values
                self.data = chart_data
                labels = f"_custom_label:{data_type}"

        if not labels:
            raise ValueError(
                "Could not resolve labels: ensure self.encoding['y'] is set "
                "or provide a valid 'values' parameter."
            )

        text_encoding = alt.Text(labels)

        self.label_layer = alt.Chart(self.data).encode(
            x=self.encoding['x'],
            y=self.encoding['y'],
            text=text_encoding
        ).mark_text(
            align = "center",
            dx = dx,
            dy = dy,
            lineBreak="\n",
            angle = angle,
            color = mark_color,
            fontSize = font_size,
            fontWeight = font_weight
            )

        return self


    def render(self, save = False, filename = None, ppi = False):
        """Renders all elements, overlays, and structural layers of the story into a single compound chart.

        Optionally exports the final visualization to a file in the `export/` directory in SVG,
        PNG, or PDF format.

        Args:
            save (str | bool, optional): Target output format for saving the chart.
                Must be one of `'svg'`, `'png'`, `'pdf'`, or `False` to skip saving.
                If an invalid string format is provided, a warning is raised and it falls
                back to `'svg'`. Defaults to False.
            filename (str | bool, optional): Custom filename for export (without extension).
                If `False` or empty, falls back to the story's title text (formatted as snake_case)
                or `'no_name_chart'` if no title exists. Defaults to None.
            ppi (int | float, optional): Pixels per inch resolution setting for PNG exports.
                Higher values increase render accuracy and image size. Defaults to 150.

        Returns:
            alt.TopLevelSpec: The complete, stylized Altair chart specification.

        Raises:
            TypeError: If `ppi` is provided and is not a positive integer or float.
            TypeError: If `filename` is provided (and not False) but is not a string.
        """

        if save not in ["svg", "png", "pdf", False]:
            warnings.warn(
                f"Unsupported export format '{save}'. Supported formats are 'svg', 'png', 'pdf'. "
                "Falling back to 'svg'.",
                UserWarning,
            )
            save = "svg"

        if filename is not None and not isinstance(filename, str):
            raise TypeError(f"'filename' must be a string or False, got {type(filename).__name__}")

        if save == "png":
            if not isinstance(ppi, (int, float)) or ppi <= 0:
                raise TypeError("'ppi' must be a positive number.")
            if ppi > 500:
                warnings.warn(
                    f"A high ppi value ({ppi}) was provided. This may significantly slow down chart rendering.",
                    UserWarning,
                )
        elif ppi is False or ppi is None:
            ppi = 150
            

        def _vstack(charts, spacing = 1):
            if not charts:
                return None
            if len(charts) == 1:
                return charts[0]
            return alt.vconcat(*charts, spacing = spacing)

        # Let's start with the basic graph
        main_chart = self._apply_trendline_end_labels(self.chart)

        if hasattr(self, "label_layer"): #NUOVO (gestione labels)
            main_chart = alt.layer(main_chart, self.label_layer)
        
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
            elif layer['type'] == 'source' and layer.get('position') in ["top", "bottom"]:
                overlay_charts.append(self.create_source_anchored_layer(layer)) #MODIFICATO

                
            elif layer['type'] in ['context', 'cta', 'source']:
                overlay_charts.append(self.create_text_layer(layer))
            elif layer['type'] in ['shape', 'shape_label', 'annotation']:
                overlay_charts.append(layer['chart'])
            elif layer['type'] == 'line':
                overlay_charts.append(layer['chart'])

        #Overlaying management in add_highlight() method
        if hasattr(self, '_overlays') and self._overlays:
            overlay_charts.extend(self._overlays)

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
            main_chart = alt.vconcat(*top_charts, main_chart, center = True) #MODIFICATO
        if bottom_charts:
            main_chart = alt.vconcat(main_chart, alt.hconcat(*bottom_charts, center = True), center = True) #MODIFICATO
        if title_charts:
            main_chart = alt.vconcat(*title_charts, main_chart, center = True)

        # Apply configurations
        if 'view' in self.config:
            main_chart = main_chart.configure_view(**self.config['view'])

        #NUOVO
        mark_info = getattr(self.chart, "mark", None) #tipo di grafico
        mark_type = mark_info.type if hasattr(mark_info, "type") else mark_info
        if mark_type == "point":
            point_size = 150
            point_color = self.chart_style["series_colors"][0]
        elif mark_type == "line":
            point_size = 80
            point_color = self.chart_style["series_colors"][1]
        else:
            point_color = "#000000"
            point_size = 75

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
        ).configure_line( #NUOVO: prende il primo colore della serie
            color=self.chart_style["series_colors"][0]
        ).configure_point(
            size = point_size,
            filled = True,
            color = point_color
        ).configure_range(
            category = self.chart_style["series_colors"]
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

        #SAVE
        if not filename: #default
            filename = "no_name_chart"
            for layer in self.story_layers:
                if layer["type"] == "title":
                    filename = layer["title"]
            filename = filename.lower()
            filename = re.sub(" ", "_", filename)
        
        if save is not False:
            os.makedirs("export", exist_ok = True) #crea la cartella export se non esiste
            export_path = f"export/{filename}.{save}"

            if save == "png":
                try:
                    main_chart.save(export_path, ppi = ppi)
                except TypeError:
                    main_chart.save(export_path)
            else:
                main_chart.save(export_path)

            print(f"Your file '{filename}.{save}' was successfully exported to the 'export/' directory.")

        return main_chart.resolve_axis(x="shared", y="shared")  



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