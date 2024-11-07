"""
This module provides the NextStep class for creating next-step elements
elements in Story views. It is designed to work in conjunction with the Story class
 to create narrative data visualisations.
"""

class NextStep:
    """
    Class for creating next-step elements in Story visualisations.
    It supports three types of visualisation: button, line_steps and stair_steps.
    
    This class can be used either directly or via the
    parameters in the Story class:

    Examples:
        >>> # Using the button
        >>> story.add_next_step(
        ...     something=NextStep(
        ...         type='button',
        ...         text='Click me',
        ...         url='https://example.com'
        ...     )
        ... )
        
        >>> # Using the stairs 
        >>> story.add_next_step(
        ...     stairs=NextStep(
        ...         type='stair_steps',
        ...         texts=['Base', 'Intermedio', 'Avanzato']
        ...     )
        ... )
        
        >>> # Using the line 
        >>> story.add_next_step(
        ...     line=NextStep(
        ...         type='line_steps',
        ...         texts=['Step 1', 'Step 2', 'Step 3']
        ...     )
        ... )
    """
    
    def __init__(
        self,
        type: str,
        position: str = 'bottom',
        # Parameters for text and content
        title: str = "What can we do next?",
        texts: list = None,
        text: str = None,
        url: str = None,
        # Parameters for colours
        primary_color: str = '#80C11E',
        text_color: str = 'black',
        title_color: str = 'black',
        opacity: float = 0.2,
        # Parameters for Fonts
        font_family: str = 'Arial',
        font_size: int = 14,
        title_font_size: int = None,
        title_font_family: str = None,
        # Dimensional parameters for button
        button_width: int = 120,
        button_height: int = 40,
        button_corner_radius: int = 5,
        # Dimensional parameters for line_steps
        rect_width: int = 10,
        rect_height: int = 10,
        rect_space: int = 5,
        chart_width: int = 700,
        chart_height: int = 100,
        # Specific dimensional parameters for stair_steps
        stair_height: int = 3
    ):
        """
        Initialises a NextStep configuration.
        
        Args:
            type (str):                             Display type (‘button’, ‘line_steps’, ‘stair_steps’)
            position (str, optional):               Position of the element. Default ‘bottom’
            title (str, optional):                  Title of the visualisation. Default ‘What can we do next?’
            texts (list, optional):                 List of texts for the steps. Default None
            text (str, optional):                   Text for the button. Default None
            url (str, optional):                    URL for the button. Default None
            primary_color (str, optional):          Primary colour. Default ‘#80C11E’.
            text_color (str, optional):             Text colour. Default ‘black’.
            title_color (str, optional):            Title colour. Default ‘black’.
            opacity (float, optional):              Opacity of the elements. Default 0.2
            font_family (str, optional):            Primary font. Default ‘Arial’.
            font_size (int, optional):              Primary font size. Default 14
            title_font_size (int, optional):        Title font size. Default None
            title_font_family (str, optional):      Title font. Default None
            button_width (int, optional):           Button width. Default 120
            button_height (int, optional):          Button height. Default 40
            button_corner_radius (int, optional):   Button corner radius. Default 5
            rect_width (int, optional):             Rectangle steps width. Default 10
            rect_height (int, optional):            Height rectangles line_steps. Default 10
            rect_space (int, optional):             Space between rectangle steps. Default 5
            chart_width (int, optional):            Total chart width. Default 700
            chart_height (int, optional):           Total chart height. Default 100
            stair_height (int, optional):           Height of stair_steps. Default 3
        
        raises:
            ValueError: If the type is invalid or if mandatory parameters are missing
        """
        # Check that the type is valid
        valid_types = ['line_steps', 'button', 'stair_steps']
        if type not in valid_types:
            raise ValueError(f"Type deve essere uno tra: {', '.join(valid_types)}")
        
        # Stores basic parameters
        self.type = type
        self.position = position
        
        # Content Management
        # The title is None for the buttons since they do not use it
        self.title = None if type == 'button' else title
        self.texts = texts or []  # Lista vuota se None
        self.text = text
        self.url = url
        
        # Store style parameters
        self.primary_color = primary_color
        self.text_color = text_color
        self.title_color = title_color
        self.opacity = opacity
        
        # Font Management
        self.font_family = font_family
        self.font_size = font_size
        # If title_font_size is not specified, use a multiple of the base font_size
        self.title_font_size = title_font_size or (font_size * 1.4)
        # If title_font_family is not specified, use font_family base
        self.title_font_family = title_font_family or font_family
        
        # 
        self.dimensions = {
            # Dimensioni specifiche per i bottoni
            'button': {
                'width': button_width,
                'height': button_height,
                'corner_radius': button_corner_radius
            },
            # Dimensioni per i line_steps
            'line_steps': {
                'rect_width': rect_width,
                'rect_height': rect_height,
                'space': rect_space,
                'chart_width': chart_width,
                'chart_height': chart_height
            },
            # Dimensioni per gli stair_steps
            'stair_steps': {
                'rect_width': rect_width,
                'rect_height': stair_height,  # usa stair_height invece di rect_height
                'chart_width': chart_width,
                'chart_height': chart_height
            }
        }
        
        # Performs configuration validation
        self.validate_configuration()
    
    def validate_configuration(self):
        """
        Validates the configuration according to the selected type.
        
        Raises:
            ValueError: If configuration is not valid for the selected type
        """
        if self.type == 'button':
            # Buttons need both text and URL
            if not self.text:
                raise ValueError("The parameter ‘text’ is required for the button type")
            if not self.url:
                raise ValueError("The ‘url’ parameter is required for the button type")
        
        elif self.type in ['line_steps', 'stair_steps']:
            # A valid text list is needed for the steps
            if not self.texts:
                raise ValueError(f"A list of texts is required for {self.type}")
            if not isinstance(self.texts, list):
                raise ValueError(f"The ‘texts’ parameter must be a list for {self.type}")
            if len(self.texts) > 5:
                raise ValueError("The maximum number of steps is 5")
            if len(self.texts) < 1:
                raise ValueError("At least one step must be provided")

    def to_dict(self):
        """
        Converts the configuration into a dictionary compatible with Story.add_next_step.
        
        Returns:
            dict: Dictionary containing all parameters needed for the configuration
        """
        # Basic configuration common to all types
        config = {
            'type': self.type,
            'position': self.position,
            'title': self.title,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'title_font_size': self.title_font_size,
            'title_font_family': self.title_font_family,
            'title_color': self.title_color
        }
        
        # Adds specific configuration based on type
        if self.type == 'button':
            config.update({
                'text': self.text,
                'url': self.url,
                'button_color': self.primary_color,
                'button_text_color': self.text_color,
                'button_opacity': self.opacity,
                'button_width': self.dimensions['button']['width'],
                'button_height': self.dimensions['button']['height'],
                'button_corner_radius': self.dimensions['button']['corner_radius']
            })
        
        elif self.type == 'line_steps':
            config.update({
                'texts': self.texts,
                'line_steps_color': self.primary_color,
                'line_steps_text_color': self.text_color,
                'line_steps_opacity': self.opacity,
                'line_steps_rect_width': self.dimensions['line_steps']['rect_width'],
                'line_steps_rect_height': self.dimensions['line_steps']['rect_height'],
                'line_steps_space': self.dimensions['line_steps']['space'],
                'line_steps_chart_width': self.dimensions['line_steps']['chart_width'],
                'line_steps_chart_height': self.dimensions['line_steps']['chart_height']
            })
        
        elif self.type == 'stair_steps':
            config.update({
                'texts': self.texts,
                'stair_steps_color': self.primary_color,
                'stair_steps_text_color': self.text_color,
                'stair_steps_opacity': self.opacity,
                'stair_steps_rect_width': self.dimensions['stair_steps']['rect_width'],
                'stair_steps_rect_height': self.dimensions['stair_steps']['rect_height'],
                'stair_steps_chart_width': self.dimensions['stair_steps']['chart_width'],
                'stair_steps_chart_height': self.dimensions['stair_steps']['chart_height']
            })
        
        return config
    
    def __repr__(self):
        """
        Provides a string representation of the NextStep object.
        
        Returns:
            str: String representation of the object
        """
        return f"NextStep(type='{self.type}', position='{self.position}')"
