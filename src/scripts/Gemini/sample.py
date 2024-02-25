import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display, display_markdown
from IPython.display import Markdown

import os


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Used to securely store your API key
# from google.colab import userdata

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.

GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
print(GOOGLE_API_KEY)

genai.configure(api_key=GOOGLE_API_KEY)

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

model = genai.GenerativeModel('gemini-pro')

# %%time
response = model.generate_content("""The following code has an error in a single line. Could you please fix it? It is supposed to compute the n^th fibonacci number.
                                  Make sure the code is in C++.
                                  int fibonacci(int n) {
                                        if (n <= 1) {
                                            return 1;
                                        }
                                        return fibonacci(n-1)-fibonacci(n-2);
                                  }
                                  """)

display(response.text)

# %%
