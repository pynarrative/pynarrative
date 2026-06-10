import altair as alt
import pandas as pd
from pathlib import Path

from pynarrative import EnvironmentalTemplate, Story


def build_story():
    data_path = Path(__file__).with_name("plants_species_data.csv")
    data = pd.read_csv(data_path)

    story = Story(data, width=700, height=420, template=EnvironmentalTemplate())
    story.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X("species:N", title="Plant Species"),
        y=alt.Y("avg_height_cm:Q", title="Average Height (cm)"),
        tooltip=["species:N", "avg_height_cm:Q", "water_need_index:Q"],
    )

    story.add_title("Young Plant Growth Comparison")
    story.add_context(
        "This sample compares average sapling height and links each species to "
        "its water demand index for planning irrigation strategies.",
        position="left",
    )

    return story.render()


def main():
    chart = build_story()
    output_path = "environmental_plants_story.html"
    chart.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
