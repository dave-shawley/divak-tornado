import divak

project = 'divak-tornado'
copyright = '2018, Dave Shawley'
version = divak.version
release = '.'.join(str(c) for c in divak.version_info[:2])

needs_sphinx = '1.6'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
              'sphinx.ext.viewcode']
templates_path = []
source_suffix = '.rst'
source_encoding = 'utf-8-sig'
master_doc = 'index'
pygments_style = 'sphinx'
html_sidebars = {'**': ['about.html', 'navigation.html', 'searchbox.html']}
html_theme_options = {
    'github_user': 'dave-shawley',
    'github_repo': 'divak-tornado',
    'github_banner': True,
}
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}
