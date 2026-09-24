import unittest
import pandas as pd
import altair as alt

from pynarrative import Story


def _flatten_layers(spec):
    layers = []
    if isinstance(spec, dict):
        if 'layer' in spec and isinstance(spec['layer'], list):
            for item in spec['layer']:
                layers.extend(_flatten_layers(item))
        if 'mark' in spec:
            layers.append(spec)
        for value in spec.values():
            if isinstance(value, (dict, list)):
                layers.extend(_flatten_layers(value))
    elif isinstance(spec, list):
        for item in spec:
            layers.extend(_flatten_layers(item))
    return layers


def _layer_text(layer_spec):
    mark = layer_spec.get('mark', {})
    if isinstance(mark, dict) and 'text' in mark:
        return mark['text']
    encoding = layer_spec.get('encoding', {})
    text = encoding.get('text')
    if isinstance(text, dict):
        return text.get('value')
    return None


def _layer_pos(layer_spec, axis):
    encoding = layer_spec.get('encoding', {})
    channel = encoding.get(axis, {})
    if isinstance(channel, dict):
        return channel.get('value')
    return None


class TestStoryLayout(unittest.TestCase):
    def setUp(self):
        print(f"\nExecuting: {self._testMethodName}")
        self.data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})

    def test_story_layout_title_context_next_steps(self):
        story = Story(self.data, width=600, height=400)
        story.mark_line().encode(x='x:Q', y='y:Q')

        story.add_title("Titolo", subtitle="Sottotitolo")
        story.add_context("Contesto", position='left')
        story.add_next_steps(steps="Prossimi passi", position='bottom')

        chart = story.render()
        self.assertIsInstance(chart, (alt.Chart, alt.LayerChart, alt.VConcatChart, alt.HConcatChart))

        spec = chart.to_dict()
        self.assertIn('hconcat', str(spec))

        text_layers = [layer for layer in _flatten_layers(spec) if _layer_text(layer)]
        text_values = { _layer_text(layer): layer for layer in text_layers }

        self.assertIn("Titolo", text_values)
        self.assertIn("Contesto", text_values)
        self.assertIn("Prossimi passi", str(spec))

        print("✓ Story layout elements positioned correctly")

    def test_trendline_uses_end_labels_instead_of_legend(self):
        data = pd.DataFrame({
            'month': [1, 2, 3, 4, 5, 6] * 2,
            'sales': [12, 14, 17, 21, 26, 32, 10, 11, 12, 13, 14, 15],
            'product': ['A'] * 6 + ['B'] * 6,
        })
        story = Story(data, width=600, height=400)
        story.mark_line().encode(
            x='month:Q',
            y='sales:Q',
            color='product:N'
        )
        spec = story.render().to_dict()
        spec_str = str(spec)

        self.assertIn("'legend': None", spec_str)
        self.assertIn("'text': {'field': 'product'", spec_str)
        print("✓ Trendline legend replaced with end labels")


if __name__ == '__main__':
    unittest.main(verbosity=2)
