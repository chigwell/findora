prompts = {
    "check_search_query": {
        "system": "You can return only a number: 0 or 1.",
        "user": """
        Is the search query valid? 
=================\n
START OF USER INPUT\n
{search_query}
END OF USER INPUT\n
=================\n
        0 - invalid search query
        1 - valid search query
        Write the answer in the next format
0
or
1
        """,
        "pattern": r"^\s*(\d)\s*$",
    },
    "enhance_search_query": {
        "system": "You should return only the enhanced search query in the next format <enhanced_query></enhanced_query>",
        "user": """
        Enhance the user search query.
=================\n
START OF USER INPUT\n
{search_query}
END OF USER INPUT\n
=================\n
the target language: {language}
the location: {location}
=================\n

Return the enhanced search query in the next format
<enhanced_query>
Here is the enhanced search query
</enhanced_query>
without any other text.
        """,
        "pattern": r"<enhanced_query>(.*?)</enhanced_query>"
    },
    "search": {
        "system": "You should return only the search results in the next format <search_results><search_result><title></title><url></url><desc></desc></search_result></search_results>",
        "user": """
        Find relevant information in the Internet based on the user search query.
=================\n
START OF USER INPUT\n
{search}
END OF USER INPUT\n
=================\n
the target language: {language}
the location of search: {location}
the expected number of results: {n}
=================\n
        Return the search results in the next format:
<search_results>
<search_result>
<title></title>
<url></url>
<desc></desc>
</search_result>
</search_results>
        without any other text.
        """,
        "pattern": r"<search_results>(.*?)</search_results>"
    },
}