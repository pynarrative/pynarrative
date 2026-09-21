import altair as alt
import pandas as pd

from pynarrative import Story


def build_story():
    data = pd.read_csv('data.csv')
    data_long = data.melt(
        id_vars=['Year'],
        value_vars=['ITA_arrivals', 'FOR_arrivals'],
        var_name='segment',
        value_name='arrivals'
    )

    story = Story(data_long, width=700, height=360)
    story.mark_line(point=True).encode(
        x=alt.X("Year:Q", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("arrivals:Q", title="Arrivals"),
        color=alt.Color(
            "segment:N",
            title="",
            
        ),
    )

    story.add_title(
        "Our City in Transition",
        "Tourism Crisis and Recovery in Pisa"
    )
    story.add_context(
        "From 2005 to 2019, Pisa gradually evolved into a predominantly international tourism destination, with foreign arrivals steadily surpassing domestic visitors. This shift strengthened the city’s role as a global gateway and reshaped its urban economy, particularly in the historic center, where commercial activities and public spaces became increasingly oriented toward international flows. By 2019, Pisa’s economic vitality and urban dynamics were closely linked to sustained international mobility. ",
        position="left",
    )

    story.add_annotation(
        text="COVID-19 shock (2020): International travel restrictions triggered a dramatic decline in foreign arrivals, revealing the city’s reliance on global mobility.",
        x=2020,
        y=157065,
        dx=-400,
        dy=-150
    )
    
    story.add_source("Source: Regione Toscana", position="left")

    story.add_next_steps(
        steps=["Our City’s Vitality Depends on International Flows: We see that local businesses and services recover when international visitors return.",
               "Recovery Brings Back Urban Pressure: As tourism rebounds, congestion and competition for space affect our daily mobility and access to the city center.",
               "Greater Balance Is Needed for the Future: The renewed reliance on foreign tourism shows the importance of making the city more resilient and less dependent on external shocks."],
        position="bottom",
        title="Lessons for the City and Its Citizens"
    )

    return story.render().configure_axis(grid=False).configure_view(strokeWidth=0)


def main():
    chart = build_story()
    output_path = "pisa_tourist_arrivals.html"
    chart.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
