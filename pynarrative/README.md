# pynarrative

`pynarrative` extends Altair with narrative components for data storytelling.

## Install

```bash
pip install pynarrative
```

## Quick Start

```python
import altair as alt
import pandas as pd
from pynarrative import Story

data = pd.DataFrame({
    'month': [1, 2, 3, 4, 5, 6],
    'sales': [12, 14, 17, 21, 26, 32],
})

story = Story(data, width=700, height=420)
story = story.mark_line()
story = story.encode(
    x=alt.X('month:Q', title='Month'),
    y=alt.Y('sales:Q', title='Sales')
)
story = story.add_title('Basic Line Story', 'Monthly trend')
story = story.add_context('Sales grow steadily over the observed months.', position='left')
story = story.add_source('Source: Internal dataset', position='bottom')
chart = story.render()

chart.save('basic_line_story.html')
```

Rendered chart:
- [`pynarrative/examples/basic_line_story/basic_line_story.html`](pynarrative/examples/basic_line_story/basic_line_story.html)

## Examples

All examples are listed here:
- [`pynarrative/examples/README.md`](pynarrative/examples/README.md)

## Core API

- `Story(data=None, width=None, height=None, template=None, ...)`
- `add_title(title, subtitle=None)`
- `add_context(text, position='left')` where `position` is `left|right|top|bottom`
- `add_annotation(x, y, text, title=None, dx=80, dy=-60, show_subject=True)`
- `add_line(value, orientation='horizontal')`
- `add_highlight(category)` for bar charts only
- `add_next_steps(steps, position='bottom', title='What can we do next?')`
- `add_source(text, position='bottom', vertical=False)` where `position` is `bottom|top|left|right`
- `render()`

## Templates

- `DefaultTemplate`
- `HistoricalTemplate`
- `EnvironmentalTemplate`
- `MinimalTemplate`

## Notes

- For bar charts, labels are horizontal and long labels are wrapped.

## Credits

`pynarrative` originated from an idea by Angelica Lo Duca, was first developed as Roberto Barsotti’s thesis project in version 1.0, and was fully revised in version 2.0 by Angelica Lo Duca.
