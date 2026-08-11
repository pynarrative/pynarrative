from .story import Story, story
from .templates.style import Style, DefaultStyle
from .templates.layout import Layout, DefaultLayout
from .templates.template import Template, DefaultTemplate
from .templates.simple.historical_template import HistoricalStyle, HistoricalLayout, HistoricalTemplate
from .templates.simple.environmental_template import EnvironmentalStyle, EnvironmentalLayout, EnvironmentalTemplate
from .templates.simple.minimal_template import MinimalStyle, MinimalLayout, MinimalTemplate


import re


__all__ = [
    'Story',
    'story',
    'Style',
    'DefaultStyle',
    'Layout',
    'DefaultLayout',
    'Template',
    'DefaultTemplate',
    'HistoricalStyle',
    'HistoricalLayout',
    'HistoricalTemplate',
    'EnvironmentalStyle',
    'EnvironmentalLayout',
    'EnvironmentalTemplate',
    'MinimalStyle',
    'MinimalLayout',
    'MinimalTemplate',
]


monocromatic_templates = ["Blue_", "Green_", "Beige_", "Grey_"]
bicolor_templates = ["Blue_Beige_", "Beige_Blue_", "Grey_Brown_", "Brown_Grey_"]

for template in monocromatic_templates:
    cleaned_template_name = re.sub("_", "", template)
    style = f"{cleaned_template_name}Style"
    layout = f"{cleaned_template_name}Layout"
    template_name = f"{cleaned_template_name}Template"
    __all__.append(style)
    __all__.append(layout)
    __all__.append(template_name)
    exec(f"from .templates.monocromatic.{template.lower()}template import {style}, {layout}, {template_name}")


for template in bicolor_templates:
    cleaned_template_name = re.sub("_", "", template)
    style = f"{cleaned_template_name}Style"
    layout = f"{cleaned_template_name}Layout"
    template_name = f"{cleaned_template_name}Template"
    exec(f"from .templates.bicolor.{template.lower()}template import {style}, {layout}, {template_name}")
    __all__.append(style)
    __all__.append(layout)
    __all__.append(template_name)
