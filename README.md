[![PyPI version](https://badge.fury.io/py/findora.svg)](https://badge.fury.io/py/findora)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/findora)](https://pepy.tech/project/findora)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# findora

`findora` is an LLM-assisted search utility.  
Give it a plain-text query and it returns a curated list of links with titles and descriptions, after:

* validating the query with a small language-model prompt
* **optionally** enhancing that query for better recall/precision
* running iterative searches while:
  * deduplicating URLs
  * honouring language & geo preferences
  * respecting result and iteration caps

It is ideal for chat-bots, data-gathering pipelines, academic tooling, or anywhere you need a “few good links” rather than an HTML page of unstructured results.

---

## Installation

```bash
pip install findora
```

Python ≥ 3.8 is required.

---

## Quick start

```python
from findora import findora

results = findora(
    search_query="Eugene Evstafev",
    n=10,
    enhance=False,
    verbose=False,
    language="en-US",
    location="UK",
)

print(results)
```

Example output (truncated/pretty-printed):

```python
[
    {
        "title": "Eugene Evstafev – Google Scholar",
        "url": "https://scholar.google.com/citations?user=cYLfW7QAAAAJ&hl=en",
        "desc": "Eugene Evstafev, University of Cambridge. Topics include computer science …",
    },
    {
        "title": "How A24 Changed Contemporary Cinema – Medium",
        "url": "https://medium.com/@chigwel/how-a24-changed-contemporary-cinema-5dc69c0b00c2",
        "desc": "Article discussing the impact of A24 films and the 2023 Oscars success …",
    },
    …
]
```

---

## API

```python
findora(
    search_query: str,
    llm: Optional[Any] = None,   # custom ChatLLM7-compatible object
    n: int = 10,                 # max results (1 – 10)
    enhance: bool = True,        # turn query rewriting on/off
    verbose: bool = False,       # print prompt/response trace
    max_retries: int = 15,       # LLM retry budget
    language: str = "en-US",     # BCP-47 tag passed to the search prompt
    location: str = "World",     # free-text geographical hint
    max_iterations: int = 55,    # safety stop for the search loop
) -> list[dict]
```

Raises `ValueError` for:

* empty or > 1024-char queries  
* `n > 10`  
* invalid query as judged by the model.

---

## Features

* 🔍 **LLM-powered query understanding** – prevents garbage queries early.  
* ✨ **Optional query enhancement** – adds synonyms, context and localised terms.  
* 🗺 **Language & region control** – pass `language`/`location` and let the model obey.  
* 🚫 **Deduplication & “exclude” list** – zero duplicated links across iterations.  
* 🧪 **Deterministic unit-tested core** – 100 % tests pass with mocked LLMs.  

---

## Contributing

Bug reports, pull requests and feature ideas are welcome!  
Head over to the [issue tracker](https://github.com/chigwell/findora/issues) to get started.

1. Fork the repository  
2. Create a feature branch  
3. Run the test suite with **pytest**  
4. Open a PR

Please run `black` and `isort` before submitting.

---

## License

`findora` is distributed under the [MIT License](https://choosealicense.com/licenses/mit/).

---

## Links

* 🐙 GitHub &nbsp;→&nbsp; <https://github.com/chigwell/findora>  
* 📦 PyPI &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp; <https://pypi.org/project/findora/>  
* 👤 Author &nbsp;&nbsp;→&nbsp; [Eugene Evstafev](https://www.linkedin.com/in/eugene-evstafev-716669181/)