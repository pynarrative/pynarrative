import altair as alt
import pandas as pd

class Story:
    """
    Story class: Implements a structure for creating narrative views of data.
    
    This class extends the functionality of Altair to include narrative elements
    such as titles, contexts, call-to-action and annotations. It is designed to facilitate
    the creation of more engaging and informative data visualisations.
    """

    def __init__(self, data=None, width=600, height=400, font='Arial', base_font_size=16, **kwargs):
        """
        Initialise a Story object.

        Parameters:
        - data: DataFrame or URL for graph data  (default: None)
        - width: Graph width in pixels (default: 600)
        - height: Height of the graph in pixels (default: 400)
        - font: Font to be used for all text elements (default: 'Arial')
        - base_font_size: Basic font size in pixels (default: 16)
        - **kwargs: Additional parameters to be passed to the constructor of alt.Chart
        """
        # Initialising the Altair Chart object with basic parameters
        self.chart = alt.Chart(data, width=width, height=height, **kwargs)
        self.font = font
        self.base_font_size = base_font_size
        self.story_layers = []  # List for storing history layers
        
        # Dictionaries for the sizes and colours of various text elements
        # These values are multipliers for base_font_size
        self.font_sizes = {
            'title': 2,        # The title will be twice as big as the basic font
            'subtitle': 1.5,   # The subtitle will be 1.5 times bigger
            'context': 1.2,    # The context text will be 1.2 times larger
            'nextstep': 1.3,   # Next-Step text will be 1.3 times larger
            'source': 1        # The source text will have the basic size
        }
        # Predefined colours for various text elements
        self.colors = {
            'title': 'black',
            'subtitle': 'gray',
            'context': 'black',
            'nextstep': 'black',
            'source': 'gray'
        }
        self.config = {}

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

    def add_title(self, title, subtitle=None, title_color=None, subtitle_color=None, title_font_size=None, subtitle_font_size=None, dx=None, dy=None, s_dx=None, s_dy=None):
        """
        Adds a title layer (and optional subtitle) to the story.

        Parameters:
        - title: Main title text
        - subtitle: Subtitle text (optional)
        - title_color: Custom colour for the title (optional)
        - subtitle_color: Custom colour for the subtitle (optional)
        - title_font_size: Custom font size for title in pixels (optional)
        - subtitle_font_size: Custom font size for subtitle in pixels (optional)
        - dx: Horizontal offset of the title in pixels (optional)
        - dy: Vertical offset of the title in pixels (optional)
        - s_dx: Horizontal offset of the subtitle in pixels (optional)
        - s_dy: Vertical offset of the subtitle in pixels (optional)

        returns:
        - self, to allow method chaining
        """
        self.story_layers.append({
            'type': 'title', 
            'title': title, 
            'subtitle': subtitle,
            'title_color': title_color or self.colors['title'],
            'subtitle_color': subtitle_color or self.colors['subtitle'],
            'title_font_size': title_font_size or self.em_to_px(self.font_sizes['title']),
            'subtitle_font_size': subtitle_font_size or self.em_to_px(self.font_sizes['subtitle']),
            'dx': dx or 0,
            'dy': dy or 0,
            's_dx': s_dx or 0,
            's_dy': s_dy or 0
        })
        return self

    def add_context(self, text, position='left', color=None, dx=0, dy=0, font_size=None):
        """
        Adds a context layer to the story.

        Parameters:
        - text: The context text to be added
        - position: The position of the text (default: ‘left’)
        - colour: Custom text colour (optional)
        - dx: Horizontal offset in pixels from the base position (default: 0)
        - dy: Vertical offset in pixels from the base position (default: 0)
        - font_size: Custom font size in pixels (optional)

        returns:
        - self, to allow method chaining
        """
        self.story_layers.append({
            'type': 'context', 
            'text': text, 
            'position': position,
            'color': color or self.colors['context'],
            'dx': dx,
            'dy': dy,
            'font_size' : font_size or self.em_to_px(self.font_sizes['context'])
            
        })
        return self


    def add_next_steps(self, 
        #Basic parameters
        text=None,
        position='bottom',
        mode=None,
        title="What can we do next?",        
    
        # General styling parameters (used as fallback)
        color=None,             # general color of elements
        font_family='Arial',
        font_size=14,
        text_color=None,
        opacity=None,
        width=None,
        height=None,
        chart_width=None,
        chart_height=None,
        space=None,
        
        # List of texts for steps
        texts=None,
        
        # Parameters per button
        url=None,
        button_width=120,
        button_height=40,
        button_color='#80C11E',
        button_opacity=0.2,
        button_corner_radius=5,
        button_text_color='black',
        button_font_family=None,    # If None, use font_family
        button_font_size=None,      # If None, use font_size
        
        # Parameters for line_steps
        line_steps_rect_width=10,
        line_steps_rect_height=10,
        line_steps_space=5,
        line_steps_chart_width=700,
        line_steps_chart_height=100,
        line_steps_color='#80C11E',
        line_steps_opacity=0.2,
        line_steps_text_color='black',
        line_steps_font_family=None,  # If None, use font_family
        line_steps_font_size=None,    # If None, use font_size
        
        # Parameters for stair_steps
        stair_steps_rect_width=10,
        stair_steps_rect_height=3,
        stair_steps_chart_width=700,
        stair_steps_chart_height=300,
        stair_steps_color='#80C11E',
        stair_steps_opacity=0.2,
        stair_steps_text_color='black',
        stair_steps_font_family=None,  # If None, use font_family
        stair_steps_font_size=None,    # If None, use font_size
        
        # Title Parameters
        title_color='black',
        title_font_family=None,     # If None, use font_family
        title_font_size=None,       # If None, use font_size * 1.4
        **kwargs):


        """
        Adds a next-step element to the visualisation with multiple customisation options.
        
        Parameters
        ---------
        text : str                                              Text for the basic version or for the button
        position : str, default=‘bottom’                        Position of the element (‘bottom’, ‘top’, ‘left’, ‘right’)
        type : str, optional                                    Display type (‘line_steps’, ‘button’, ‘stair_steps’)
        title : str, default="What can we do next?’             Title for special visualisations
        colour : str, optional                                  Text colour for the basic version
        font_family : str, default=‘Arial’                      Default font
        font_size : int, default=14                             Default font size
        texts : list of str                                     List of texts for line_steps and stair_steps
        url : str                                               URL for the button
        
        Parameters for Button
        ------------------
        button_width : int, default=120                         Button width
        button_height : int, default=40                         Height of the button
        button_color : str, default=‘#80C11E’                   Background colour of the button
        button_opacity : float, default=0.2                     Opacity of the button
        button_corner_radius : int, default=5                   Corner radius of the button
        button_text_color : str, default=‘black’                Button text colour
        button_font_family : str, optional                      Font specific to the button
        button_font_size : int, optional                        Font size for the button
        
        Parameters for Line Steps
        ----------------------
        line_steps_rect_width : int, default=10                 Rectangle width
        line_steps_rect_height : int, default=10                Height of rectangles
        line_steps_space : int, default=5                       Space between rectangles
        line_steps_chart_width : int, default=700               Total width of the chart
        line_steps_chart_height : int, default=100              Total chart height
        line_steps_color : str, default=‘#80C11E’               Colour of rectangles
        line_steps_opacity : float, default=0.2                 Opacity of rectangles
        line_steps_text_colour : str, default=‘black’           Text colour
        line_steps_font_family : str, optional                  Font specific to line steps
        line_steps_font_size : int, optional                    Font size for line steps
        
        Parameters for Stair Steps
        -----------------------
        stair_steps_rect_width : int, default=10                Width of steps
        stair_steps_rect_height : int, default=3                Height of steps
        stair_steps_chart_width : int, default=700              Total width of the chart
        stair_steps_chart_height : int, default=300             Total height of the chart
        stair_steps_color : str, default=‘#80C11E’              Colour of the steps
        stair_steps_opacity : float, default=0.2                Opacity of the steps
        stair_steps_text_colour : str, default=‘black’          Text colour
        stair_steps_font_family : str,                          Font specific to stair steps
        stair_steps_font_size : int, optional                   Font size for stair steps
        
        Title parameters
        ----------------------
        title_color : str, default=‘black’                      Title colour
        title_font_family : str, optional                       Specific font for the title
        title_font_size : int, optional                         Font size for the title
        
        Returns
        -------
        self : Story object                                     The current instance for method chaining
        """
 
 
        # Apply general parameters to specific parameters if not set
        # Colors and styling
        button_color = button_color or color
        button_opacity = button_opacity or opacity
        button_text_color = button_text_color or text_color
        button_width = button_width or width
        button_height = button_height or height
        
        line_steps_color = line_steps_color or color
        line_steps_opacity = line_steps_opacity or opacity
        line_steps_text_color = line_steps_text_color or text_color
        line_steps_rect_width = line_steps_rect_width or width
        line_steps_rect_height = line_steps_rect_height or height
        line_steps_space = line_steps_space or space
        line_steps_chart_width = line_steps_chart_width or chart_width
        line_steps_chart_height = line_steps_chart_height or chart_height
        
        stair_steps_color = stair_steps_color or color
        stair_steps_opacity = stair_steps_opacity or opacity
        stair_steps_text_color = stair_steps_text_color or text_color
        stair_steps_rect_width = stair_steps_rect_width or width
        stair_steps_rect_height = stair_steps_rect_height or height
        stair_steps_chart_width = stair_steps_chart_width or chart_width
        stair_steps_chart_height = stair_steps_chart_height or chart_height
        
        title_color = title_color or text_color       

    
      
        # Basic version (text only)
        if mode is None:
            if text is None:
                raise ValueError("The parameter ‘text’ is required for the basic version")
            self.story_layers.append({
                'type': 'cta', 
                'text': text, 
                'position': position,
                'color': color or self.colors['cta']
            })
            return self

        # Mode validation
        valid_types = ['line_steps', 'button', 'stair_steps']
        if mode not in valid_types:
            raise ValueError(f"Invalid type. Use one of: {', '.join(valid_types)}")

        # Chart creation by mode
        if mode == 'button':
            if text is None:
                raise ValueError("The parameter ‘text’ is required for the button type")
            if url is None:
                raise ValueError("The ‘url’ parameter is required for the button type")
            
            # Button chart creation
            df = pd.DataFrame([{
                'text': text,
                'url': url,
                'x': 0,
                'y': 0
            }])
            
            base = alt.Chart(df).encode(
                x=alt.X('x:Q', axis=None),
                y=alt.Y('y:Q', axis=None)
            ).properties(
                width=button_width,
                height=button_height
            )
            
            button_bg = base.mark_rect(
                color=button_color,
                opacity=button_opacity,
                cornerRadius=button_corner_radius,
                width=button_width,
                height=button_height
            ).encode(
                href='url:N'
            )
            
            button_text = base.mark_text(
                fontSize=button_font_size or font_size,
                font=button_font_family or font_family,
                align='center',
                baseline='middle',
                color=button_text_color
            ).encode(
                text='text'
            )
            
            chart = alt.layer(button_bg, button_text)
            
        elif mode == 'line_steps':
            if not texts or not isinstance(texts, list):
                raise ValueError("It is necessary to provide a list of texts for line_steps")
            if len(texts) > 5:
                raise ValueError("Maximum number of steps is 5")
            if len(texts) < 1:
                raise ValueError("Must provide at least one step")
                
            # Create DataFrame for rectangles and text
            N = len(texts)
            x = [i*(line_steps_rect_width+line_steps_space) for i in range(N)]
            y = [0 for _ in range(N)]
            x2 = [(i+1)*line_steps_rect_width+i*line_steps_space for i in range(N)]
            y2 = [line_steps_rect_height for _ in range(N)]
            
            df_rect = pd.DataFrame({   
                'x': x, 'y': y, 'x2': x2, 'y2': y2, 'text': texts
            })
            
            # Create rectangles
            rect = alt.Chart(df_rect).mark_rect(
                color=line_steps_color,
                opacity=line_steps_opacity
            ).encode(
                x=alt.X('x:Q', axis=None),
                y=alt.Y('y:Q', axis=None),
                x2='x2:Q',
                y2='y2:Q'
            ).properties(
                width=line_steps_chart_width,
                height=line_steps_chart_height
            )
            
            # Add text labels
            text = alt.Chart(df_rect).mark_text(
                fontSize=line_steps_font_size or font_size,
                font=line_steps_font_family or font_family,
                align='left',
                dx=10,
                lineHeight=18,
                color=line_steps_text_color
            ).encode(
                text='text:N',
                x=alt.X('x:Q', axis=None),
                y=alt.Y('y_half:Q', axis=None),
            ).transform_calculate(
                y_half='datum.y2/2'
            )
            
            if N > 1:
                df_line = pd.DataFrame({   
                    'x': [line_steps_rect_width*i+line_steps_space*(i-1) for i in range(1,N)],
                    'y': [line_steps_rect_height/2 for _ in range(N-1)],
                    'x2': [(line_steps_rect_width+line_steps_space)*i for i in range(1,N)],
                    'y2': [line_steps_rect_height/2 for _ in range(N-1)]
                })
                
                line = alt.Chart(df_line).mark_line(
                    point=True,
                    strokeWidth=2
                ).encode(
                    x=alt.X('x:Q', axis=None),
                    y=alt.Y('y:Q', axis=None),
                    x2='x2:Q',
                    y2='y2:Q'
                )
                
                chart = alt.layer(rect, line, text)
            else:
                chart = alt.layer(rect, text)
                
        elif mode == 'stair_steps':
            if not texts or not isinstance(texts, list):
                raise ValueError("You must provide a list of texts for stair_steps")
            if len(texts) > 5:
                raise ValueError("Maximum number of steps is 5")
            if len(texts) < 1:
                raise ValueError("Must provide at least one step")
                
            # Create DataFrame for rectangles and text
            N = len(texts)
            x = [i*stair_steps_rect_width for i in range(N)]
            y = [i*stair_steps_rect_height for i in range(N)]
            x2 = [(i+1)*stair_steps_rect_width for i in range(N)]
            y2 = [(i+1)*stair_steps_rect_height for i in range(N)]
            
            df_rect = pd.DataFrame({   
                'x': x, 'y': y, 'x2': x2, 'y2': y2, 'text': texts
            })
            
            # Create rectangles
            rect = alt.Chart(df_rect).mark_rect(
                color=stair_steps_color,
                opacity=stair_steps_opacity
            ).encode(
                x=alt.X('x:Q', axis=None),
                y=alt.Y('y:Q', axis=None, scale=alt.Scale(domain=[0, N*stair_steps_rect_height])),
                x2='x2:Q',
                y2='y2:Q'
            ).properties(
                width=stair_steps_chart_width,
                height=stair_steps_chart_height
            )
            
            # Add text labels
            text = alt.Chart(df_rect).mark_text(
                fontSize=stair_steps_font_size or font_size,
                font=stair_steps_font_family or font_family,
                align='left',
                dx=10,
                dy=0,
                color=stair_steps_text_color
            ).encode(
                text=alt.Text('text'),
                x=alt.X('x:Q', axis=None),
                y=alt.Y('y_mid:Q', axis=None),
            ).transform_calculate(
                y_mid='(datum.y + datum.y2)/2'
            )
            
            if N > 1:
                line_data = []
                for i in range(N-1):
                    line_data.append({
                        'x': x2[i],
                        'y': y2[i],
                        'x2': x[i+1],
                        'y2': y[i+1]
                    })
                
                df_line = pd.DataFrame(line_data)
                
                line = alt.Chart(df_line).mark_line(
                    point=True,
                    strokeWidth=2
                ).encode(
                    x=alt.X('x:Q', axis=None),
                    y=alt.Y('y:Q', axis=None),
                    x2='x2:Q',
                    y2='y2:Q'
                )
                
                chart = alt.layer(rect, line, text)
            else:
                chart = alt.layer(rect, text)

        # Addition of title with customisable font
        if title:
            chart = chart.properties(
                title=alt.TitleParams(
                    text=[title],
                    fontSize=title_font_size or (font_size * 1.4),
                    font=title_font_family or font_family,
                    color=title_color,
                    offset=10
                )
            )

        # Addition to layer
        self.story_layers.append({
            'type': 'special_cta',
            'chart': chart,
            'position': position
        })
        
        return self
    
    def add_source(self, text, position='bottom', vertical=False, color=None, dx=None, dy=None, font_size=None):
        """
        Add a source layer to the story.

        Parameters:
        - text: The source text
        - position: The position of the text (default: 'bottom')
        - vertical: If True, the text will be rotated 90 degrees (default: False)
        - color: Custom text color (optional)
        - dx: Horizontal movement of the text (optional)
        - dy: Vertical movement of the text (optional)
        - font_size: Custom font size (optional)

        Ritorna:
        - self, to allow the method chaining
        """
        self.story_layers.append({
            'type': 'source', 
            'text': text, 
            'position': position, 
            'vertical': vertical,
            'color': color or self.colors['source'],
            'dx': dx or 0,
            'dy': dy or 0,
            'font_size': font_size or self.em_to_px(self.font_sizes['source'])
            
        })
        return self

    def add_annotation(self, x_point, y_point, annotation_text="Point of interest", 
                                     arrow_direction='right', arrow_color='blue', arrow_size=40,
                                     label_color='black', label_size=12,
                                     show_point=True, point_color='red', point_size=60,
                                     arrow_dx=0, arrow_dy=-45,
                                     label_dx=37, label_dy=-37):
        """
        Create an arrow annotation on the graph.
        
        This method is essential for highlighting specific points in the graph and adding
        contextual explanations. It is particularly useful for data narration, allowing
        to guide the observer's attention to relevant aspects of the visualisation.

        Parameters:
        - x_point, y_point: Coordinates of the point to be annotated
        - annotation_text: Text of the annotation (default: ‘Point of interest’)
        - arrow_direction: Direction of the arrow (default: ‘right’)
        - arrow_color, arrow_size: Arrow colour and size
        - label_colour, label_size: Colour and size of the annotation text
        - show_point: If True, shows a point at the annotation location
        - point_color, point_size: Colour and size of the point
        - arrow_dx, arrow_dy: Distances in pixels to be added to the arrow position (default:0, -45)
        - label_dx, label_dy: Distances in pixels to be added to the label position (default:37, -37)

        returns:
        - self, to allow method chaining
        """
        
        # Dictionary that maps arrow directions to corresponding Unicode symbols
        arrow_symbols = {
            'left': '←', 'right': '→', 'up': '↑', 'down': '↓',
            'upleft': '↖', 'upright': '↗', 'downleft': '↙', 'downright': '↘',
            'leftup': '↰', 'leftdown': '↲', 'rightup': '↱', 'rightdown': '↳',
            'upleftcurve': '↺', 'uprightcurve': '↻'
        }

        # Check that the direction of the arrow is valid
        if arrow_direction not in arrow_symbols:
            raise ValueError(f"Invalid arrow direction. Use one of: {', '.join(arrow_symbols.keys())}")

        # Select the appropriate arrow symbol
        arrow_symbol = arrow_symbols[arrow_direction]
        
        # checks whether the encoding has already been defined
        if not hasattr(self.chart, 'encoding')or not hasattr(self.chart.encoding, 'x'):
            # If encoding is not defined use of default values
            x_type = 'Q'
            y_type = 'Q'
        else:
            # If encoding is defined, we extract the data types for the x and y axes
            x_type = self.chart.encoding.x.shorthand.split(':')[-1]
            y_type = self.chart.encoding.y.shorthand.split(':')[-1]

        # Explanation of data type extraction:
        # 1. We first check whether the encoding has been defined. This is important because
        # the user may call this method before defining the encoding of the graph.
        # (The encoding in Altair defines how the data is mapped to the visual properties of the graph).
        # 2. If encoding is not defined, we use ‘Q’ (Quantitative) as the default data type
        # for both axes. This allows the method to work even without a defined encoding.
        # 3. If the encoding is defined, we proceed with the data type extraction as before:
        # - self.chart.encoding.x.shorthand: accesses the shorthand of the x-axis
        # .shorthand: In Altair, ‘shorthand’ is a concise notation for specifying the encoding.
        # Example of shorthand: ‘column:Q’ where ‘column’ is the name of the data column
        # and ‘Q’ is the data type (in this case, Quantitative).
        # - split(‘:’)[-1]: splits the shorthand at ‘:’ and takes the last element (the data type)
        # Example: If shorthand is ‘price:Q’, split(‘:’) will return [‘price’, ‘Q’].
        # 4. The extracted data type will be one of:
        # - ‘Q’: Quantitative (continuous numeric)
        # - ‘O’: Ordinal (ordered categories)
        # N': Nominal (unordered categories)
        # T': Temporal (dates or times)
        
        # Important: This operation is essential to ensure that the annotations
        # added to the graph are consistent with the original axis data types.
        # Without this match, annotations may be positioned
        # incorrectly or cause rendering errors.

        # Create a DataFrame with a single point for the annotation
        annotation_data = pd.DataFrame({'x': [x_point], 'y': [y_point]})
        
        # Internal function to create the correct encoding based on the data type
        def create_encoding(field, dtype):
            """
            Creates the appropriate encoding for Altair based on the data type.
            This function is crucial to ensure that the annotation is
            consistent with the original chart data type.
            
            Parameters:
            - field: str - The field name to encode ('x' or 'y')
            - dtype: str - The data type to use for encoding. Can be:
                        'O' for Ordinal (ordered categories)
                        'N' for Nominal (unordered categories) 
                        'T' for Temporal (dates/times)
                        'Q' for Quantitative (default, continuous numeric)

            Returns:
            - alt.X or alt.Y encoding object configured with the specified field and data type
                 
            """
            
            if dtype == 'O':  # Ordinal
                return alt.X(field + ':O', title='') if field == 'x' else alt.Y(field + ':O', title='')
            elif dtype == 'N':  # Nominal
                return alt.X(field + ':N', title='') if field == 'x' else alt.Y(field + ':N', title='')
            elif dtype == 'T':  # Temporal
                return alt.X(field + ':T', title='') if field == 'x' else alt.Y(field + ':T', title='')
            else:  # Quantity (default)
                return alt.X(field + ':Q', title='') if field == 'x' else alt.Y(field + ':Q', title='')

        # Initialises the list of annotation layers
        layers = []

        # Adds full stop if required
        if show_point:
            point_layer = alt.Chart(annotation_data).mark_point(
                color=point_color,
                size=point_size
            ).encode(
                x=create_encoding('x', x_type),
                y=create_encoding('y', y_type)
            )
            layers.append(point_layer)

        # Adds the arrow
        # We use mark_text to draw the arrow using a Unicode character
        arrow_layer = alt.Chart(annotation_data).mark_text(
            text=arrow_symbol, 
            fontSize=arrow_size,
            dx=arrow_dx,  # Horizontal offset to position the arrow                   was 22
            dy=arrow_dy,  # Vertical offset to position the arrow                     was -22
            color=arrow_color
        ).encode(
            x=create_encoding('x', x_type),
            y=create_encoding('y', y_type)
        )
        layers.append(arrow_layer)

        # Adds text label
        label_layer = alt.Chart(annotation_data).mark_text(
            align='left',
            baseline='top',
            dx= label_dx,  # Horizontal offset to position text                     was 37
            dy= label_dy,  # Vertical offset to position text                       was -37
            fontSize=label_size,
            color=label_color,
            text=annotation_text
        ).encode(
            x=create_encoding('x', x_type),
            y=create_encoding('y', y_type)
        )
        layers.append(label_layer)

        # Combine all layers into a single annotation
        annotation = alt.layer(*layers)

        # Adds annotation to history layers
        self.story_layers.append({
            'type': 'annotation',
            'chart': annotation
        })

        # Note on flexibility and robustness:
        # This approach makes the add_annotation method more flexible,
        # as it can automatically adapt to different types of graphs without
        # requiring manual input on the axis data type. In addition, using
        # the Altair shorthand, the code automatically adapts even if the user
        # has specified the encoding in different ways (e.g., using alt.X(‘column:Q’)
        # or alt.X(‘column’, type=‘quantitative’)).


        return self  # Return self to allow method chaining
    
    
    def add_line(self, value, orientation='horizontal', color='red', stroke_width=2, stroke_dash=[]):
        """
        Adds a reference line to the story.

        Parameters:
        - value: The position of the line (x or y value)
        - orientation: 'horizontal' or 'vertical' (default: 'horizontal')
        - color: Color of the line (default: 'red')
        - stroke_width: Width of the line in pixels (default: 2)
        - stroke_dash: Pattern for dashed line, e.g. [5,5] (default: [] for solid line)

        Returns:
        - self, to allow method chaining
        """
        
        if orientation not in ['horizontal', 'vertical']:
            raise ValueError("orientation must be either 'horizontal' or 'vertical'")

        # Crea un DataFrame con un singolo valore
        if orientation == 'horizontal':
            data = pd.DataFrame({'y': [value]})
            encoding = {'y': 'y:Q'}
        else:  # vertical
            data = pd.DataFrame({'x': [value]})
            encoding = {'x': 'x:Q'}
        
        # definizione dei parametri della line
        mark_params = {
            'color': color,
            'strokeWidth': stroke_width,
        }
        
        # Viene aggiunto stokeDash solo se è specificato un pattern
        if stroke_dash:
            mark_params['strokeDash'] = stroke_dash

        # Crea la linea
        line = alt.Chart(data).mark_rule(
            color=color,
            strokeWidth=stroke_width,
            strokeDash=stroke_dash
        ).encode(
            **encoding
        )

        # Aggiunge la linea ai layer della storia
        self.story_layers.append({
            'type': 'line',
            'chart': line
        })

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
        title_chart = alt.Chart(self.chart.data).mark_text(
            text=layer['title'],
            fontSize=layer['title_font_size'],
            fontWeight='bold',
            align='center',
            font=self.font,
            color=layer['title_color']
        ).encode(
            x=alt.value(self.chart.width / 2 + layer.get('dx', 0)),  # Centre horizontally
            y=alt.value(-50 + layer.get('dy', 0))  # Position 20 pixels from above
        )
        
        if layer['subtitle']:
            subtitle_chart = alt.Chart(self.chart.data).mark_text(
                text=layer['subtitle'],
                fontSize=layer['subtitle_font_size'],
                align='center',
                font=self.font,
                color=layer['subtitle_color']
            ).encode(
                x=alt.value(self.chart.width / 2 + layer.get('s_dx', 0)),  # Centre horizontally
                y=alt.value(-20 + layer.get('s_dy', 0))  # Position 50 pixels from the top (below the title)
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
        
        # Apply offsets if they exist (for context layers)
        if layer['type'] in ['context', 'source']:
            x += layer.get('dx', 0)
            y += layer.get('dy', 0)
        
        return alt.Chart(self.chart.data).mark_text(
            text=layer['text'],
            fontSize=layer.get('font_size', self.em_to_px(self.font_sizes[layer['type']])),
            align='center',
            baseline='middle',
            font=self.font,
            angle=270 if layer.get('vertical', False) else 0,  #  Rotate text if ‘vertical’ is True
            color=layer['color']
        ).encode(
            x=alt.value(x),
            y=alt.value(y)
        )

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
        # Let's start with the basic graph
        main_chart = self.chart
        
        # Create separate lists to place special graphics
        top_charts = []
        bottom_charts = []
        left_charts = []
        right_charts = []
        overlay_charts = []
        
        # Organise the layers according to their position
        for layer in self.story_layers:
            if layer['type'] == 'special_cta':
                # We take the position from the layer
                if layer.get('position') == 'top':
                    top_charts.append(layer['chart'])
                elif layer.get('position') == 'bottom':
                    bottom_charts.append(layer['chart'])
                elif layer.get('position') == 'left':
                    left_charts.append(layer['chart'])
                elif layer.get('position') == 'right':
                    right_charts.append(layer['chart'])
            elif layer['type'] == 'title':
                overlay_charts.append(self.create_title_layer(layer))
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
        if left_charts:
            main_chart = alt.hconcat(alt.vconcat(*left_charts), main_chart)
        if right_charts:
            main_chart = alt.hconcat(main_chart, alt.vconcat(*right_charts))
        if top_charts:
            main_chart = alt.vconcat(alt.hconcat(*top_charts), main_chart)
        if bottom_charts:
            main_chart = alt.vconcat(main_chart, alt.hconcat(*bottom_charts))

        # Apply configurations
        if 'view' in self.config:
            main_chart = main_chart.configure_view(**self.config['view'])

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

