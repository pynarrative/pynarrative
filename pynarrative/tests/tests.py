import unittest
import pandas as pd
import altair as alt
from pynarrative import Story

class TestStoryInitialization(unittest.TestCase):
    def setUp(self):
        print(f"\nExecuting: {self._testMethodName}")
        
    def test_basic_initialization(self):
        """Story basic initialization test."""
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        story = Story(data, width=600, height=400)
        self.assertIsInstance(story.chart, alt.Chart)
        self.assertEqual(story.chart.width, 600)
        self.assertEqual(story.chart.height, 400)
        print("✓ Base initialization successful")

    def test_initialization_without_data(self):
        """Story initialization test without data."""
        story = Story(width=500, height=300)
        self.assertIsInstance(story.chart, alt.Chart)
        self.assertIsNone(story.chart.data)
        print("✓ No-data initialization successful")

    def test_custom_font_and_size(self):
        """Initialization test with custom font and size."""
        story = Story(font='Helvetica', base_font_size=18)
        self.assertEqual(story.font, 'Helvetica')
        self.assertEqual(story.base_font_size, 18)
        print("✓ Custom font initialization successful")

    def test_default_values(self):
        """Test initialization defaults."""
        story = Story()
        self.assertEqual(story.font, 'Helvetica')
        self.assertEqual(story.base_font_size, 16)
        print("✓ Default values correct")

class TestStoryElements(unittest.TestCase):
    def setUp(self):
        print(f"\nExecuting: {self._testMethodName}")
        self.data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        self.story = Story(self.data)

    def test_add_title(self):
        """Title addition test."""
        self.story.add_title("Main Title", subtitle="Subtitle")
        last_layer = self.story.story_layers[-1]
        self.assertEqual(last_layer['type'], 'title')
        self.assertEqual(last_layer['title'], "Main Title")
        print("✓ Title added successfully")

    def test_add_context(self):
        """Add context test."""
        self.story.add_context("Context text", position="top")
        last_layer = self.story.story_layers[-1]
        self.assertEqual(last_layer['type'], 'context')
        self.assertEqual(last_layer['text'], "Context text")
        print("✓ Context added successfully")

class TestNextStep(unittest.TestCase):
    def setUp(self):
        print(f"\nExecuting: {self._testMethodName}")
        self.story = Story()

    def test_basic_next_step(self):
        """Basic next-step testing."""
        self.story.add_next_steps("Click here")
        last_layer = self.story.story_layers[-1]
        self.assertEqual(last_layer['type'], 'special_cta')
        print("✓ Basic NS added successfully")

    def test_line_steps_next_step(self):
        """Next-step test with line steps."""
        texts = ["Step 1", "Step 2", "Step 3"]
        self.story.add_next_steps(texts)
        last_layer = self.story.story_layers[-1]
        self.assertEqual(last_layer['type'], 'special_cta')
        self.assertTrue(isinstance(last_layer['chart'], (alt.Chart, alt.LayerChart)))
        print("✓ Line steps NS added successfully")

class TestBarHighlight(unittest.TestCase):
    def setUp(self):
        print(f"\nExecuting: {self._testMethodName}")
        self.data = pd.DataFrame(
            {'category': ['A', 'B', 'C'], 'value': [10, 20, 15]}
        )
        self.story = Story(self.data)
        self.story.mark_bar().encode(
            x='category:N',
            y='value:Q'
        )

    def test_add_highlight(self):
        """Bar highlight test."""
        self.story.add_highlight('B')
        self.assertTrue(hasattr(self.story.chart.encoding, 'color'))
        print("✓ Bar highlight applied successfully")


class TestAnnotations(unittest.TestCase):
    def setUp(self):
        print(f"\nExecuting: {self._testMethodName}")
        data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [10, 12, 15, 13]})
        self.story = Story(data)
        self.story.mark_line().encode(x='x:Q', y='y:Q')

    def test_add_annotation(self):
        """Annotation layer test."""
        self.story.add_annotation(x=3, y=15, text="Peak value", title="Important")
        last_layer = self.story.story_layers[-1]
        self.assertEqual(last_layer['type'], 'annotation')
        print("✓ Annotation added successfully")

class TestErrorHandling(unittest.TestCase):
    def setUp(self):
        print(f"\nExecuting: {self._testMethodName}")
        self.story = Story()

    def test_invalid_inputs(self):
        """Test gestione input non validi."""
        with self.assertRaises(ValueError):
            self.story.add_next_steps([])
        print("✓ Empty line steps caught")

        with self.assertRaises(ValueError):
            self.story.add_next_steps(steps={"bad": "input"})
        print("✓ Invalid steps input caught")

class TestConfiguration(unittest.TestCase):
    def setUp(self):
        print(f"\nExecuting: {self._testMethodName}")
        self.story = Story()

    def test_configure_view(self):
        """Test configurazione della vista."""
        self.story.configure_view(strokeWidth=0, fill='#f0f0f0')
        self.assertIn('view', self.story.config)
        self.assertEqual(self.story.config['view']['strokeWidth'], 0)
        self.assertEqual(self.story.config['view']['fill'], '#f0f0f0')
        print("✓ View configuration works")

if __name__ == '__main__':
    print("\n=== Starting Story Tests ===")
    unittest.main(verbosity=2)
