# Pynarrative: Transform Data Visualizations into Stories

## Installation

Pynarrative can be easily installed using **pip**, Python's package manager. To install the library, run the following command in your terminal:

```bash
pip install pynarrative
```

## Core API Reference
**Full technical documentation [here](https://pynarrative.github.io/doc/site/api/)**

```python
Story(
    data=None,
    width=None,
    height=None,
    font=None,
    base_font_size=None,
    template=None,
    geodata=False,
    geojson_url=None,
    geojson_property=None,
    geo_property=None,
    geo_value=None,
    **kwargs
)

add_title(
    title,
    subtitle=None,
    background_color=None,
    color=None, align='center',
    img_url=None,
    img_width=80,
    x_img_offset=-300,
    y_img_offset=0
)

add_context(
    text,
    text_align='left',
    position='left',
    align='middle',
    font_weight='normal',
    font_style='normal',
    title='CONTEXT',
    title_dy=0,
    img_url=None,
    img_width=60,
    x_img_offset=-40,
    y_img_offset=0
)

add_next_steps(
    steps,
    text_align='left',
    position='bottom',
    title='NEXT STEPS',
    title_dy=0,
    title_dx=0,
    mode='horizontal',
    img_url=None,
    img_width=45,
    x_img_offset=-50,
    y_img_offset=-22.5
)

add_source(
    text,
    position='top',
    vertical=False,
    align='center'
)

add_annotation(
    x=None,
    y=None,
    text=None,
    title=None,
    dx=0,
    dy=0,
    background_color=None,
    text_color=None,
    how_subject=False,
    line_point_color=None,
    img_url=None,
    img_width=60,
    x_img_offset=0,
    y_img_offset=0
)


add_line(
    value,
    orientation='horizontal',
    math=None,
    color='',
    label_text='',
    label_dx=0,
    label_dy=0,
    label_font_size='',
    label_font_weight='normal',
    label_font_style='normal'
)


render(
    save=False,
    filename=None,
    ppi=False
)

```

## Overview

Pynarrative is a Python library designed to transform data visualizations into engaging narratives. Built as an extension of Altair, pynarrative provides a powerful set of tools for creating interactive, narrative-driven visualizations that engage and inform your audience. The library bridges the gap between raw data visualization and storytelling by introducing narrative elements such as **contextual** descriptions, **annotations** and **nextsteps**.

## Architecture

Pynarrative is built around the **Story class**: it serves as the core component, handling the creation and management of narrative visualizations. It extends Altair's functionality while maintaining full compatibility with its declarative API.

The library requires Python 3.6 or later and depends on the following packages:

```bash
altair
pandas
geopandas
```

These dependencies will be automatically installed if they're not already present in your environment.

## Getting Started
<!-- RIVEDERE -->

PyNarrative is designed to be intuitive while providing powerful narrative capabilities. Here are two comprehensive examples showcasing both basic usage and advanced features:

### Basic Example

```python
import pynarrative as pn
import pandas as pd

# Sample data creation
data = pd.DataFrame({
    'Year': range(2018, 2023),
    'Sales': [100, 120, 90, 150, 200]
})

# Creating a complete chart in a single flow
final_chart = (pn.Story(data, width=600, height=400)
    .mark_line(color='blue')
    .encode(x='Year:O', y='Sales:Q')
    .add_title(
        "Sales Trends", 
        "2018-2022", 
        title_color="#1a1a1a", 
        subtitle_color="#4a4a4a"
    )
    .add_context(
        "Steady Growth", 
        position='top', 
        color="#2ecc71"
    )
    .add_next_steps(
        "Click for details", 
        position='bottom', 
        color="#3498db"
    )
    .add_annotation(
        2020, 90, "Point of interest",
        arrow_direction='left', 
        arrow_dx=50, 
        arrow_dy=-7, 
        arrow_color='red', 
        arrow_size=75,
        label_color='darkgreen', 
        label_size=14,
        show_point=True
    )
    .add_next_steps(
        type='line_steps',
        texts=["Phase 1", "Phase 2", "Phase 3", "Phase 4"],
        position='bottom'
    )
    .add_next_steps(
        type='button',
        text="Click here",
        url="https://example.com",
        position='top',
        title="Next steps"
    )
    .add_next_steps(
        type='stair_steps',
        texts=["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"],
        position='right'
    )
    .render()
)
```

### Advanced Example with Customization

```python
import pynarrative as pn
import pandas as pd

# Sample data creation
data = pd.DataFrame({
    'Year': range(2018, 2023),
    'Sales': [100, 120, 90, 150, 200]
})

# Creating a chart with advanced customizations
customized_chart = (pn.Story(data, width=600, height=400)
    .mark_line(color='blue')
    .encode(x='Year:O', y='Sales:Q')
    .add_title(
        "Sales Trends", 
        "2018-2022", 
        title_color="#1a1a1a", 
        subtitle_color="#4a4a4a"
    )
    .add_context(
        "Steady Growth", 
        position='top', 
        color="#2ecc71"
    )
    .add_next_steps(
        "Click for details", 
        position='bottom', 
        color="#3498db"
    )
    .add_annotation(
        2020, 90, "Point of interest",
        arrow_direction='left', 
        arrow_dx=50, 
        arrow_dy=-8, 
        arrow_color='red', 
        arrow_size=75,
        label_color='darkgreen', 
        label_size=14,
        show_point=True
    )
    # Customized linear steps
    .add_next_steps(
        type='line_steps',
        texts=["Phase 1", "Phase 2", "Phase 3", "Phase 4"],
        position='bottom',
        line_steps_chart_width=350,
        line_steps_chart_height=50,
        line_steps_font_size=6
    )
    # Customized button
    .add_next_steps(
        type='button',
        text="Click here",
        url="https://example.com",
        position='top',
        title="Next steps",
        title_color='blue',
        title_font_family='Helvetica',
        title_font_size=26,
        button_width=150,
        button_height=40,
        button_color='#FF0000',
        button_opacity=0.3
    )
    # Basic stair steps
    .add_next_steps(
        type='stair_steps',
        texts=["Level 1", "Level 2", "Level 3", "Level 4"],
        position='right'
    )
    
    .render()
)
```

These examples demonstrate how pynarrative allows you to create rich, interactive narrative visualizations with just a few lines of code. The first example illustrates the library's basic functionality, while the second shows how you can customize every aspect of the visualization in detail.

## Documentation

Comprehensive documentation is available for pynarrative, providing detailed information about all features and capabilities. The documentation includes in-depth tutorials, complete API reference, and numerous examples showing different ways to use pynarrative for creating engaging data narratives.

Full documentation is accessible on GitHub at: [Pynarrative API Documentation](https://pynarrative.github.io/doc/site/api/)

## Contributing

Pynarrative is an open-source project, and we welcome contributions from the community. Whether you're fixing bugs, adding new features, or improving documentation, your help is valuable. Please refer to our contribution guidelines in the repository for more information about how to get involved.

## License

Pynarrative is released under the MIT License, allowing both personal and commercial use with minimal restrictions. See the LICENSE file in the repository for the complete license text.

## Authors

Pynarrative was implemented by Roberto Olinto Barsotti as a master's thesis project in digital humanities, under the supervision of professor Angelica Lo Duca. It was then developped by Lorenzo Ferrante as a bachelor's thesis project in digital humanities, also under the supervision of professor Lo Duca.