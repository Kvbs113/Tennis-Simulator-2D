import os
import sys

sys.path.insert(0, os.path.abspath('../../'))

# -- Project information -----------------------------------------------------

project = 'Tennis Simulator'
copyright = '2026, Jakub Litwinski'
author = 'Jakub Litwinski'
release = '1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',             
    'sphinx.ext.napoleon',            
    'sphinx.ext.viewcode',            
    'sphinx.ext.graphviz',            
    'sphinx.ext.inheritance_diagram', 
]

autodoc_mock_imports = ["pygame"]

templates_path = ['_templates']
exclude_patterns = []

language = 'pl'

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

graphviz_output_format = 'svg'
inheritance_graph_attrs = dict(rankdir="TB", size='""')

graphviz_dot = r"C:\Program Files\Graphviz\bin\dot.exe"