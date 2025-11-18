from bs4 import BeautifulSoup, Comment
from minify_html import minify

class DOMManager:

    def minify_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove unnecessary tags
        for tag in soup.find_all(['style', 'script', 'meta', 'link']):
            tag.decompose()

        # Remove comments
        for element in soup(text=lambda text: isinstance(text, Comment)):
            element.extract()

        # Remove attributes except for form-related elements and href
        for tag in soup.find_all(True):
            if tag.name not in ['form', 'input', 'select', 'textarea', 'button', 'a']:
                tag.attrs = {}
            else:
                if tag.name == 'a':
                    href = tag.attrs.get('href')
                    tag.attrs = {'href': href} if href else {}

        # Minify HTML by removing whitespace
        clean_content = str(soup).replace('\n', '').replace('\r', '').strip()

        minified_html = minified_html = minify(clean_content)

        return minified_html