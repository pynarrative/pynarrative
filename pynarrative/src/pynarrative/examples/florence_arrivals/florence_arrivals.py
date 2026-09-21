import altair as alt
import pandas as pd

from pynarrative import Story


def build_story():
    arrivals = 5270527
    museum_visits = 1430131

    data = pd.DataFrame({
        "segment": ["Tourist arrivals", "Municipal museum visits"],
        "value": [arrivals, museum_visits],
    })

    story = Story(data, width=600, height=400)
    story.mark_bar(size=200).encode(
        x=alt.X("segment:N", title="", axis=alt.Axis(labelAngle=0)),
        y=alt.Y(
            "value:Q",
            title="People",
            axis=alt.Axis(format=","),
        ),
        color=alt.Color("segment:N", legend=None),
    )
    value_labels = alt.Chart(data).mark_text(
        dy=-10,
        fontSize=13,
        fontWeight="bold",
        color="#1f2a44",
    ).encode(
        x=alt.X("segment:N"),
        y=alt.Y("value:Q"),
        text=alt.Text("value:Q", format=","),
    )
    story.chart = alt.layer(story.chart, value_labels)

    story.add_title("Tourist Demand and Cultural Absorption in Florence 2017")
    story.add_context(
        "In 2017, Florence recorded over 5.2 million tourist arrivals, while municipal museums "
        "registered approximately 1.4 million visits, revealing a structural gap between overall "
        "urban tourism demand and the portion absorbed by institutional cultural infrastructure.",
        position="left",
    )
    story.add_next_steps(
        steps=[
            "Cultural venues absorb only part of tourism demand. A large share of visitors remains distributed across public spaces beyond institutional infrastructure.",
            "Urban space is a shared and limited resource. Tourist flows, residents, and daily activities coexist and compete within the same areas.",
            "Understanding interaction improves urban awareness. Recognizing how different urban uses overlap helps citizens interpret everyday congestion and livability challenges.",
        ],
        title="Lesson learned for citizens",
    )
    story.add_source("Source: Open Data Toscana", position="left")

    return story.render().configure_axis(grid=False).configure_view(strokeWidth=0)


def main():
    chart = build_story()
    output_path = "florence_arrivals.html"
    chart.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
