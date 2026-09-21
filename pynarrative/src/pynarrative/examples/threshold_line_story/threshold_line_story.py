import altair as alt
import pandas as pd

from pynarrative import Story


def build_story():
    data = pd.DataFrame({
        'month': [1, 2, 3, 4, 5, 6],
        'conversion_rate': [0.58, 0.62, 0.67, 0.71, 0.69, 0.74]
    })

    story = Story(data, width=620, height=380)
    story.mark_line().encode(
        x=alt.X('month:Q', title='Month'),
        y=alt.Y('conversion_rate:Q', title='Conversion Rate')
    )

    story.add_title(
        'Conversion Rate vs Target',
        subtitle='Horizontal threshold highlights the KPI objective'
    )
    story.add_context(
        'The target threshold is 0.70. Values above the line meet the monthly objective.',
        position='left'
    )
    story.add_line(0.70, orientation='horizontal')
    story.add_source('Source: Product analytics KPI dashboard', position='bottom')

    return story.render()


def main():
    chart = build_story()
    output_path = 'threshold_line_story.html'
    chart.save(output_path)
    print(f'Saved: {output_path}')


if __name__ == '__main__':
    main()
