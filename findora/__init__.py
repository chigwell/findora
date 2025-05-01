import re
from .prompts import prompts
from llmatch import llmatch
from langchain_llm7 import ChatLLM7


def findora(
        search_query,
        llm=None,
        n=10,
        enhance=True,
        verbose=False,
        max_retries=15,
        language="en-US",
        location="World",
        max_iterations=55,
):
    """
    Findora is a function that searches for relevant documents based on a query.

    Parameters
    ----------
    search_query : str
        The query string to search for.
    llm : object, optional
        The language model to use for searching. If not provided, a default one will be used.
    n : int, optional
        The number of results to return. Default is 10. Max is 10.
    enhance : bool, optional
        Whether to enhance the input query. Default is True.
    verbose : bool, optional
        Whether to print verbose output. Default is False.
    max_retries : int, optional
        The maximum number of retries for the search. Default is 15.
    language : str, optional
        The target language for the search. Default is "en-US".
    location : str, optional
        The location for the search. Default is "World".
    max_iterations : int, optional
        The maximum number of iterations for the search. Default is 55.

    Returns
    -------
    list
        A list of relevant documents based on the search query.
    """
    if n > 10:
        raise ValueError("The maximum number of results is 10.")

    if len(search_query) == 0:
        raise ValueError("Search query is empty. Please provide a valid search query.")

    if len(search_query) > 1024:
        raise ValueError("Search query is too long. Maximum length is 1000 characters.")

    if llm is None:
        llm = ChatLLM7(model="searchgpt")

    is_valid_query = llmatch(
        llm=llm,
        query=prompts["check_search_query"]["system"] + "\n" +
              prompts["check_search_query"]["user"].format(search_query=search_query),
        verbose=verbose,
        max_retries=max_retries,
        pattern=prompts["check_search_query"]["pattern"],
    )
    is_valid_query = is_valid_query["extracted_data"][0]
    if is_valid_query != '1':
        raise ValueError(f"Invalid search query: {search_query}")

    if enhance:
        enhanced_query = llmatch(
            query=prompts["enhance_search_query"]["system"] + "\n" +
                  prompts["enhance_search_query"]["user"].format(
                      search_query=search_query,
                      language=language,
                      location=location
                  ),
            verbose=verbose,
            max_retries=max_retries,
            pattern=prompts["enhance_search_query"]["pattern"],
        )
        search_query = enhanced_query["extracted_data"][0]

    results = []
    seen_urls = set()
    iterations = 0

    while len(results) < n and iterations < max_iterations:
        user_message = str(
            prompts["search"]["user"].format(
                search=search_query,
                language=language,
                location=location,
                n=n
            )
        )
        if seen_urls:
            excluded_urls = list(seen_urls)[-10:]
            excluded_str = "\n".join([f"- {url}" for url in excluded_urls])
            user_message += (f"\n\nExclude these URLs from the search results "
                             f":\n{excluded_str}")

        full_query = prompts["search"]["system"] + "\n" + user_message
        curr_results = llmatch(
            llm=llm,
            query=full_query,
            verbose=verbose,
            max_retries=max_retries,
            pattern=prompts["search"]["pattern"],
        )
        curr_data = curr_results["extracted_data"][0]
        matches = re.findall(
            r"<search_result>\s*<title>(.*?)</title>\s*<url>(.*?)</url>\s*<desc>(.*?)</desc>\s*</search_result>",
            curr_data,
            re.DOTALL
        )

        new_results = []
        for title, url, desc in matches:
            url = url.strip()
            if url not in seen_urls:
                seen_urls.add(url)
                new_results.append({
                    "title": title.strip(),
                    "url": url,
                    "desc": desc.strip(),
                })

        results.extend(new_results)
        iterations += 1

        if not new_results:
            break
    if len(results) > n:
        results = results[:n]
    return results
