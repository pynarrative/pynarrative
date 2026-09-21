import pandas as pd
import altair as alt

from pynarrative import Story


def build_story():
    data = pd.DataFrame({
        'month': [1, 2, 3, 4, 5, 6] * 2,
        'sales': [12, 14, 17, 21, 26, 32, 10, 11, 12, 13, 14, 15],
        'product': ['A'] * 6 + ['B'] * 6,
    })
    story = Story(data, width=600, height=400)

    story.mark_line().encode(
        x='month:Q',
        y='sales:Q',
        color=alt.Color('product:N', legend=alt.Legend(title='Product'))
    )
    story.add_title(
        "Product A Outpaces Product B",
        subtitle="Six-month sales trend comparison"
    )
    story.add_context(
        "Product A shows a steeper growth trend, while Product B remains mostly flat. "
        "The gap widens over time, suggesting B needs targeted improvements to catch up "
        "in the next quarter."
        "Product A shows a steeper growth trend, while Product B remains mostly flat. "
        "The gap widens over time, suggesting B needs targeted improvements to catch up "
        "in the next quarter.",
        position='top'
    )
    story.add_next_steps(
        steps=[
            "Refresh B's pricing & bundles",
            "Boost B's visibility with campaigns",
            "Improve B's features via feedback",
            "Boost B's visibility with campaigns",
            "Improve B's features via feedback"
        ],
        position='bottom'
    )
    story.add_source("Source: Internal sales dataset", position='bottom')

    return story.render()


def main():
    chart = build_story()
    output_path = 'basic_line_story.html'
    chart.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == '__main__':
    main()
