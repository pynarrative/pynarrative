import pandas as pd
import altair as alt

from pynarrative import Story


def build_story():
    data = pd.DataFrame({
        'month': [1, 2, 3, 4, 5, 6],
        'sales': [10, 12, 18, 28, 16, 14]
    })

    story = Story(data, width=600, height=400)
    story.mark_line().encode(
        x=alt.X('month:Q', title='Month'),
        y=alt.Y('sales:Q', title='Sales')
    )

    story.add_title(
        "Campaign Lift and Drop",
        subtitle="Peak month highlights the campaign impact"
    )

    story.add_context(
        "Sales spike sharply in month 4 after the campaign launch, then normalize."
        " This suggests a strong but short-lived lift."
        "Sales spike sharply in month 4 after the campaign launch, then normalize.",
        position='left'
    )

    story.add_annotation(
        x=4,
        y=28,
        title="Campaign peak",
        text=(
            "Sales rise abruptly in month 4 immediately after the campaign launch, "
            "indicating a strong short-term response from the target audience. "
            "Sales rise abruptly in month 4 immediately after the campaign launch, "
            "indicating a strong short-term response from the target audience. "
        ),
        dx=-100,
        dy=100,
        show_subject=False
    )
    story.add_source("Source: Monthly campaign tracking data", position='right')

    return story.render()


def main():
    chart = build_story()
    output_path = 'annotated_line_story.html'
    chart.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == '__main__':
    main()
