# pynarrative: Transform Data Visualizations into Stories

## Overview

pynarrative is a Python library designed to transform data visualizations into engaging narratives. Built as an extension of Altair, pynarrative provides a powerful set of tools for creating interactive, narrative-driven visualizations that engage and inform your audience. The library bridges the gap between raw data visualization and storytelling by introducing narrative elements such as contextual descriptions, annotations, and interactive guidance through its main Story class and supporting NextStep functionality.

## Architecture

pynarrative is built around two main classes: Story and NextStep. The Story class serves as the core component, handling the creation and management of narrative visualizations. It extends Altair's functionality while maintaining full compatibility with its declarative API. The NextStep class complements Story by providing specialized support for interactive elements, allowing you to guide users through your data narrative in various ways.

## Installation

pynarrative can be easily installed using pip, Python's package manager. To install the library, run the following command in your terminal:

```bash
pip install pynarrative
```

The library requires Python 3.7 or later and depends on the following packages:
```bash
altair >= 4.0.0
pandas >= 1.0.0
```

These dependencies will be automatically installed if they're not already present in your environment.

## Getting Started

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
    .add_next_step(
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
    .add_next_step(
        type='line_steps',
        texts=["Phase 1", "Phase 2", "Phase 3", "Phase 4"],
        position='bottom'
    )
    .add_next_step(
        type='button',
        text="Click here",
        url="https://example.com",
        position='top',
        title="Next steps"
    )
    .add_next_step(
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
    .add_next_step(
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
    .add_next_step(
        type='line_steps',
        texts=["Phase 1", "Phase 2", "Phase 3", "Phase 4"],
        position='bottom',
        line_steps_chart_width=350,
        line_steps_chart_height=50,
        line_steps_font_size=6
    )
    # Customized button
    .add_next_step(
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
    .add_next_step(
        type='stair_steps',
        texts=["Level 1", "Level 2", "Level 3", "Level 4"],
        position='right'
    )
    # Direct use of NextStep class
    .add_next_step(
        custom_button=pn.NextStep(
            type='button',
            text='Click here',
            position='left',
            url='https://example.com'
        )
    )
    .render()
)
```

These examples demonstrate how pynarrative allows you to create rich, interactive narrative visualizations with just a few lines of code. The first example illustrates the library's basic functionality, while the second shows how you can customize every aspect of the visualization in detail.

## The Story Class

The Story class is the main interface for creating narrative visualizations. It extends Altair's functionality with methods specifically designed for storytelling. Through this class, you can add titles and subtitles, include explanatory text to provide context and insights, highlight specific data points with customizable arrows and labels, and integrate interactive guidance elements. All Story methods support method chaining, allowing for a fluid and intuitive API.

## The NextStep Class

NextStep provides specialized support for creating interactive guidance elements within your visualizations. It offers three main types of interactive elements: buttons, which provide clickable elements for basic interactions; linear steps, which create progression guides for sequential narratives; and stair steps, which display hierarchical visualizations for progressive disclosure. Each type can be fully customized with colors, fonts, sizes, and positioning to match your visualization's style.

## Documentation

Comprehensive documentation is available for pynarrative, providing detailed information about all features and capabilities. The documentation includes in-depth tutorials, complete API reference, and numerous examples showing different ways to use pynarrative for creating engaging data narratives.

The documentation is accessible on GitHub at:

[pynarrative Documentation](https://github.com/Robeonekenoby/pynarrative-doc)

## Advanced Usage

pynarrative supports sophisticated narrative techniques through its advanced features. The NextStep system allows the creation of guided narratives with multiple interaction points. Annotations can be highly customized with different arrow styles, colors, and positioning. The library also provides flexible positioning systems for all narrative elements, allowing precise control over your story's visual hierarchy.

## Contributing

pynarrative is an open-source project, and we welcome contributions from the community. Whether you're fixing bugs, adding new features, or improving documentation, your help is valuable. Please refer to our contribution guidelines in the repository for more information about how to get involved.

## License

pynarrative is released under the MIT License, allowing both personal and commercial use with minimal restrictions. See the LICENSE file in the repository for the complete license text.
