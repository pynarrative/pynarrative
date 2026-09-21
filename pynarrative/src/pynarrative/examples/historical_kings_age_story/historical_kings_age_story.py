import altair as alt
import pandas as pd
from pathlib import Path

from pynarrative import HistoricalTemplate, Story


def build_story():
    data_path = Path(__file__).with_name("kings_1500_accession_age.csv")
    data = pd.read_csv(data_path)

    story = Story(data, template=HistoricalTemplate())
    story.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("age_at_accession:Q", title="Age at Accession"),
        y=alt.Y("realm:N", title="Realm", sort='-x'),
        tooltip=["monarch:N", "realm:N", "age_at_accession:Q"]
    )

    story.add_title("Average Accession Age of 16th-Century Monarchs")
    story.add_context(
        "Across major European and Mediterranean powers in the 1500s, monarchs "
        "often reached the throne in their late teens or twenties, with a few "
        "older accessions reflecting succession dynamics and political instability.",
        position="left"
    )
    story.add_highlight("Ottoman Empire")
    story.add_source("Source: Historical reference estimates (illustrative sample)", position="right")

    return story.render()


def main():
    chart = build_story()
    output_path = "historical_kings_age_story.html"
    chart.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
