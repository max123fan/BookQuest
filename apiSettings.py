class ApiSettings:
    def __init__(self):
        self.initial_fetch_limit = 30  # Get more candidates initially
        self.num_books = 10     # Return top 5 after sorting
        self.popularity_weight = 0.2    # Adjust balance between relevance/popularity (0-1)
        self.min_ratings = 20   # Adjust balance between relevance/popularity (0-1)
        self.min_avg_rating = 3.0   # Adjust balance between relevance/popularity (0-1)

        self.STOP_WORDS = [
            "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
            "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "can't", "cannot",
            "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few",
            "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll",
            "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
            "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most",
            "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
            "ours", "ourselves", "out", "over", "own", "same", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
            "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
            "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
            "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
            "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
            "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
            "yourselves", "please",

            "book", "books", "novel", "novels", "story", "stories", "edition", "editions", "author", "authors", "volume", "volumes",
            "chapter", "chapters", "series"
        ]


        self.LANGUAGE_CODES = {
            # Key terms : OpenLibrary code
            'english': 'eng',
            'german': 'ger',
            'french': 'fre',
            'spanish': 'spa',
            'chinese': 'chi',
            'italian': 'ita',
            'russian': 'rus',
            'portuguese': 'por',
            'japanese': 'jpn',
            'polish': 'pol',
            'dutch': 'dut',
            'hebrew': 'heb',
            'arabic': 'ara',
            'greek': 'gre',
            'hungarian': 'hun',
            'korean': 'kor'
        }

        self.NUM_RESULTS_WORDS = ["results", "recommendations", "show", "recommend"]

        self.YEAR_FILTER_WORDS = {
            "old": (1800, 0.2),
            "classic": (1900, 0.2),
            "classics": (1900, 0.2),
            "modern": (2010, 0.3),
            "contemporary": (2020, 0.3),
            "new": (2025, 0.3),
            "recent": (2025, 0.3),
            -1: (2015, 0.2) #none
        }

        self.STOP_WORDS.extend(self.NUM_RESULTS_WORDS)



        '''fields = (
            "key,title,author_name,first_publish_year,number_of_pages_median,"
            "ratings_average,ratings_count,cover_i"
        )'''

        self.default_doc = {'key': None, 'author_name' : None, "first_publish_year" : "No info", 
                            "number_of_pages_median" : "No info", "ratings_average": 0.0, "ratings_count": 0, "cover_i": None}