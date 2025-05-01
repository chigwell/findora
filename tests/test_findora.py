import unittest
from unittest.mock import patch, MagicMock
from findora import findora

mock_prompts = {
    "check_search_query": {
        "system": "System prompt check",
        "user": "User prompt check {search_query}",
        "pattern": "pattern_check"
    },
    "enhance_search_query": {
        "system": "System prompt enhance",
        "user": "User prompt enhance {search_query} {language} {location}",
        "pattern": "pattern_enhance"
    },
    "search": {
        "system": "System prompt search",
        "user": "User prompt search {search} {language} {location} {n}",
        "pattern": "pattern_search"
    }
}

class TestFindora(unittest.TestCase):

    # Patch 'llmatch' and 'ChatLLM7' where they are looked up (in the 'findora' module)
    # Also patch 'prompts' if it's imported within findora
    @patch('findora.llmatch')
    @patch('findora.ChatLLM7')
    @patch('findora.prompts', mock_prompts) # Patch prompts dictionary
    def test_successful_search_no_enhance(self, MockChatLLM7, mock_llmatch):
        """Tests a successful search without query enhancement."""
        # --- Mock Configuration ---
        # Mock the LLM instance
        mock_llm_instance = MockChatLLM7.return_value
        mock_llm_instance.model = "searchgpt" # Or whatever is expected

        # Configure mock_llmatch return values for different calls
        mock_llmatch.side_effect = [
            # 1. Call for check_search_query (returns '1' for valid)
            {"extracted_data": ['1']},
            # 2. Call for search (returns 3 results)
            {"extracted_data": [
                """
                <search_result> <title>Result 1</title> <url>http://example.com/1</url> <desc>Desc 1</desc> </search_result>
                <search_result> <title>Result 2</title> <url>http://example.com/2</url> <desc>Desc 2</desc> </search_result>
                <search_result> <title>Result 3</title> <url>http://example.com/3</url> <desc>Desc 3</desc> </search_result>
                """
            ]}
        ]

        # --- Function Call ---
        results = findora(search_query="test query", n=3, enhance=False, verbose=False)

        # --- Assertions ---
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], "Result 1")
        self.assertEqual(results[0]['url'], "http://example.com/1")
        self.assertEqual(results[1]['url'], "http://example.com/2")
        self.assertEqual(results[2]['url'], "http://example.com/3")

        # Check that llmatch was called correctly
        self.assertEqual(mock_llmatch.call_count, 2)
        # Check the first call (check_search_query)
        call1_args, call1_kwargs = mock_llmatch.call_args_list[0]
        self.assertIn("User prompt check test query", call1_kwargs['query'])
        self.assertEqual(call1_kwargs['pattern'], "pattern_check")
        # Check the second call (search)
        call2_args, call2_kwargs = mock_llmatch.call_args_list[1]
        self.assertIn("User prompt search test query en-US World 3", call2_kwargs['query'])
        self.assertEqual(call2_kwargs['pattern'], "pattern_search")
        # Check that ChatLLM7 was instantiated if llm=None
        MockChatLLM7.assert_called_once_with(model="searchgpt")


    @patch('findora.llmatch')
    @patch('findora.ChatLLM7')
    @patch('findora.prompts', mock_prompts)
    def test_successful_search_with_enhance(self, MockChatLLM7, mock_llmatch):
        """Tests a successful search with query enhancement."""
        mock_llm_instance = MockChatLLM7.return_value

        mock_llmatch.side_effect = [
            # 1. Call for check_search_query (returns '1' for valid)
            {"extracted_data": ['1']},
            # 2. Call for enhance_search_query
            {"extracted_data": ["enhanced test query"]},
            # 3. Call for search (returns 2 results)
            {"extracted_data": [
                """
                <search_result> <title>Enhanced Result 1</title> <url>http://enhanced.com/1</url> <desc>Enhanced Desc 1</desc> </search_result>
                <search_result> <title>Enhanced Result 2</title> <url>http://enhanced.com/2</url> <desc>Enhanced Desc 2</desc> </search_result>
                """
            ]}
        ]

        results = findora(search_query="test query", n=2, enhance=True, verbose=False, language="fr-FR", location="France")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], "Enhanced Result 1")
        self.assertEqual(results[0]['url'], "http://enhanced.com/1")
        self.assertEqual(results[1]['url'], "http://enhanced.com/2")

        # Check llmatch calls
        self.assertEqual(mock_llmatch.call_count, 3)
        # Check enhance call
        call2_args, call2_kwargs = mock_llmatch.call_args_list[1]
        self.assertIn("User prompt enhance test query fr-FR France", call2_kwargs['query'])
        self.assertEqual(call2_kwargs['pattern'], "pattern_enhance")
        # Check search call (uses enhanced query)
        call3_args, call3_kwargs = mock_llmatch.call_args_list[2]
        self.assertIn("User prompt search enhanced test query fr-FR France 2", call3_kwargs['query'])
        self.assertEqual(call3_kwargs['pattern'], "pattern_search")
        MockChatLLM7.assert_called_once_with(model="searchgpt")

    @patch('findora.llmatch')
    @patch('findora.ChatLLM7')
    @patch('findora.prompts', mock_prompts)
    def test_invalid_query_check(self, MockChatLLM7, mock_llmatch):
        """Tests the case where the initial query check fails."""
        mock_llm_instance = MockChatLLM7.return_value
        mock_llmatch.return_value = {"extracted_data": ['0']} # Simulate invalid query

        with self.assertRaisesRegex(ValueError, "Invalid search query: bad query"):
            findora(search_query="bad query", enhance=False)

        self.assertEqual(mock_llmatch.call_count, 1)
        call1_args, call1_kwargs = mock_llmatch.call_args_list[0]
        self.assertIn("User prompt check bad query", call1_kwargs['query'])
        MockChatLLM7.assert_called_once_with(model="searchgpt")


    @patch('findora.llmatch')
    @patch('findora.ChatLLM7')
    @patch('findora.prompts', mock_prompts)
    def test_empty_query(self, MockChatLLM7, mock_llmatch):
        """Tests providing an empty search query."""
        with self.assertRaisesRegex(ValueError, "Search query is empty"):
            findora(search_query="")
        # No LLM calls should be made
        MockChatLLM7.assert_not_called()
        mock_llmatch.assert_not_called()

    @patch('findora.llmatch')
    @patch('findora.ChatLLM7')
    @patch('findora.prompts', mock_prompts)
    def test_long_query(self, MockChatLLM7, mock_llmatch):
        """Tests providing a search query that is too long."""
        long_query = "a" * 1025
        with self.assertRaisesRegex(ValueError, "Search query is too long"):
            findora(search_query=long_query)
        # No LLM calls should be made
        MockChatLLM7.assert_not_called()
        mock_llmatch.assert_not_called()

    @patch('findora.llmatch')
    @patch('findora.ChatLLM7')
    @patch('findora.prompts', mock_prompts)
    def test_n_too_large(self, MockChatLLM7, mock_llmatch):
        """Tests requesting more than 10 results."""
        with self.assertRaisesRegex(ValueError, "The maximum number of results is 10"):
            findora(search_query="test", n=11)
        # No LLM calls should be made
        MockChatLLM7.assert_not_called()
        mock_llmatch.assert_not_called()

    @patch('findora.llmatch')
    @patch('findora.ChatLLM7')
    @patch('findora.prompts', mock_prompts)
    def test_max_iterations_reached(self, MockChatLLM7, mock_llmatch):
        """Tests reaching the maximum number of search iterations."""
        mock_llm_instance = MockChatLLM7.return_value

        # Simulate valid query check
        mock_check = {"extracted_data": ['1']}
        # Simulate search returning one *new* result each time
        mock_search_results = [
            {"extracted_data": [f"<search_result><title>R{i}</title><url>http://a.com/{i}</url><desc>D{i}</desc></search_result>"]}
            for i in range(6) # Will run 5 times to get 5 results
        ]

        mock_llmatch.side_effect = [mock_check] + mock_search_results

        # Set max_iterations lower than needed to get n=5 results
        results = findora(search_query="test iter", n=5, enhance=False, max_iterations=3)

        # Should only get 3 results because max_iterations is 3
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['url'], "http://a.com/0")
        self.assertEqual(results[1]['url'], "http://a.com/1")
        self.assertEqual(results[2]['url'], "http://a.com/2")

        # Check calls: 1 check + 3 search iterations
        self.assertEqual(mock_llmatch.call_count, 1 + 3)

    @patch("findora.llmatch")
    @patch("findora.ChatLLM7")
    @patch("findora.prompts", mock_prompts)
    def test_duplicate_url_handling(self, MockChatLLM7, mock_llmatch):
        """Tests that duplicate URLs are not included and that iteration stops
        once a search returns no new URLs."""
        mock_llm_instance = MockChatLLM7.return_value

        mock_llmatch.side_effect = [
            # 1. Query-validity check
            {"extracted_data": ["1"]},
            # 2. First search – two unique results
            {
                "extracted_data": [
                    """
                    <search_result><title>Result 1</title><url>http://example.com/1</url><desc>Desc 1</desc></search_result>
                    <search_result><title>Result 2</title><url>http://example.com/2</url><desc>Desc 2</desc></search_result>
                    """
                ]
            },
            # 3. Second search – one duplicate, one new
            {
                "extracted_data": [
                    """
                    <search_result><title>Result 2 Repeat</title><url>http://example.com/2</url><desc>Desc 2 Repeat</desc></search_result>
                    <search_result><title>Result 3</title><url>http://example.com/3</url><desc>Desc 3</desc></search_result>
                    """
                ]
            },
            # 4. Third search – *all* duplicates → no new URLs, loop stops
            {
                "extracted_data": [
                    """
                    <search_result><title>Result 1 Again</title><url>http://example.com/1</url><desc>Dup</desc></search_result>
                    """
                ]
            },
        ]

        results = findora(
            search_query="test duplicates",
            n=5,
            enhance=False,
            max_iterations=5,
        )

        # ---- Assertions ----------------------------------------------------
        assert len(results) == 3
        assert {r["url"] for r in results} == {
            "http://example.com/1",
            "http://example.com/2",
            "http://example.com/3",
        }

        # 1 check + 3 search calls
        assert mock_llmatch.call_count == 4

        # Verify the *last* search was asked to exclude all seen URLs
        _, last_kwargs = mock_llmatch.call_args_list[3]
        assert "Exclude these URLs" in last_kwargs["query"]
        for url in ("http://example.com/1", "http://example.com/2", "http://example.com/3"):
            assert f"- {url}" in last_kwargs["query"]


    @patch('findora.llmatch')
    @patch('findora.ChatLLM7')
    @patch('findora.prompts', mock_prompts)
    def test_no_new_results_stops_iteration(self, MockChatLLM7, mock_llmatch):
        """Tests that iteration stops if a search call returns no new URLs."""
        mock_llm_instance = MockChatLLM7.return_value

        mock_llmatch.side_effect = [
            # 1. Check query
            {"extracted_data": ['1']},
            # 2. First search call - 2 results
            {"extracted_data": [
                """
                <search_result> <title>Result 1</title> <url>http://example.com/1</url> <desc>Desc 1</desc> </search_result>
                <search_result> <title>Result 2</title> <url>http://example.com/2</url> <desc>Desc 2</desc> </search_result>
                """
            ]},
            # 3. Second search call - returns only already seen URLs
             {"extracted_data": [
                 """
                 <search_result> <title>Result 1 Repeat</title> <url>http://example.com/1</url> <desc>Desc 1 Repeat</desc> </search_result>
                 """
             ]},
             # This call should not happen
             {"extracted_data": ["<search_result><title>Wont see</title><url>http://no.com</url><desc>Wont see</desc></search_result>"]}
        ]

        results = findora(search_query="test stop", n=5, enhance=False, max_iterations=10)

        # Should only have the first 2 results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['url'], "http://example.com/1")
        self.assertEqual(results[1]['url'], "http://example.com/2")

        # Check calls: 1 check + 2 search iterations (stops after the second search yields no new results)
        self.assertEqual(mock_llmatch.call_count, 1 + 2)


    @patch('findora.llmatch')
    @patch('findora.ChatLLM7', new_callable=MagicMock) # Use MagicMock directly for the class
    @patch('findora.prompts', mock_prompts)
    def test_custom_llm_provided(self, MockChatLLM7, mock_llmatch):
        """Tests providing a custom LLM object."""
        # Create a mock LLM instance to pass in
        custom_llm = MagicMock()

        # Configure llmatch mocks
        mock_llmatch.side_effect = [
            {"extracted_data": ['1']}, # Valid query
            {"extracted_data": ["<search_result><title>R1</title><url>u1</url><desc>d1</desc></search_result>"]} # Search result
        ]

        results = findora(search_query="test custom llm", llm=custom_llm, n=1, enhance=False)

        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['url'], 'u1')

        # Check that the provided LLM was used in llmatch calls
        self.assertEqual(mock_llmatch.call_count, 2)
        call1_args, call1_kwargs = mock_llmatch.call_args_list[0]
        self.assertEqual(call1_kwargs['llm'], custom_llm) # Check first call
        call2_args, call2_kwargs = mock_llmatch.call_args_list[1]
        self.assertEqual(call2_kwargs['llm'], custom_llm) # Check second call

        # Check that ChatLLM7 was NOT instantiated
        MockChatLLM7.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

