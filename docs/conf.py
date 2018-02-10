# encoding: utf-8
import divak

project = 'divák-tornado'
copyright = '2018, Dave Shawley'
version = divak.version
release = '.'.join(str(c) for c in divak.version_info[:2])

needs_sphinx = '1.6'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode']
templates_path = ['templates']
source_suffix = '.rst'
source_encoding = 'utf-8-sig'
master_doc = 'index'
html_theme = 'alabaster'
pygments_style = 'lovelace'
html_sidebars = {'**': ['about.html', 'navigation.html', 'searchbox.html',
                        'sourcelink.html']}
html_static_path = ['static']
html_theme_options = {
    'github_user': 'dave-shawley',
    'github_repo': 'divak-tornado',
    'github_banner': True,
    'fixed_sidebar': True,
    'extra_nav_links': {'Index': 'genindex.html'},
}
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}
