import os
from datetime import datetime

class Logger:
    def __init__(self, storage_path: str,
                 index_name: str,
                 logging_enabled: str,
                 display_skipped_articles: str,
                 starting_page: int,
                 ending_page: int):
        """
        Initializes the Logger with the given configuration values.

        :param storage_path: Path where log files will be stored.
        :param index_name: The name of the index being logged.
        :param logging_enabled: Boolean string indicating whether logging is enabled.
        :param display_skipped_articles: Boolean string for whether skipped articles should be displayed.
        :param starting_page: Starting page for processing articles.
        :param ending_page: Ending page for processing articles.
        """
        self._storage_path = storage_path
        self._time_started = self._get_timestamp()
        self._time_finished = "N/A"
        self._file_path = os.path.join(self._storage_path, f"{self._time_started}.log")

        self._index_name = index_name
        self._logging_enabled = logging_enabled
        self._display_skipped_articles = display_skipped_articles
        self._starting_page = starting_page
        self._ending_page = ending_page

        self._end_message = "N/A"
        self._latest_id = "N/A"

        # Logs template initialization
        self._info_log = self._generate_info_log()
        self._fetching_log = ""
        self._embedding_log = ""
        self._upserting_log = ""
        self._runtime_log = ""

    def _generate_info_log(self):
        """
        Generates the general information log string.
        """
        return f"""
===GENERAL INFORMATION===
Timestamp Start: {self._time_started}
Timestamp End: {self._time_finished}
Message on Exit: {self._end_message}
Index Name: {self._index_name}
Logging Enabled: {self._logging_enabled}
Display skipped articles: {self._display_skipped_articles}
Starting Page: {self._starting_page}
Ending Page: {self._ending_page}
Most Recent Article's ID: {self._latest_id}
"""

    def create_log_file(self) -> bool:
        """
        Creates a log file and writes the initial log information into it.

        :return: True if the file is created successfully, False otherwise.
        """
        if not os.path.exists(self._storage_path):
            return False

        with open(self._file_path, 'w') as file:
            file.write(self._info_log)
        
        return True

    def end_log(self, message="Successful"):
        """
        Ends the log with a message and updates the log file.

        :param message: The end message to be logged.
        """
        self._time_finished = self._get_timestamp()
        self._end_message = message
        self._refresh_log()

    def store_latest_id(self, article_id: str):
        """
        Stores the latest article ID in the log and refreshes the log file.

        :param article_id: The ID of the most recent article.
        """
        self._latest_id = article_id
        self._refresh_log()

    def start_fetching_articles_section(self):
        """Starts the fetching articles section in the log."""
        self._fetching_log += "\n===FETCHING ARTICLES===\n"
        self._refresh_log()

    def start_embedding_section(self, start_page: int, end_page: int):
        """Starts the embedding section in the log."""
        self._embedding_log += f"\n===EMBEDDING PGS {start_page}-{end_page}===\n"
        self._refresh_log()

    def start_upserting_section(self, start_page: int, end_page: int):
        """Starts the upserting section in the log."""
        self._upserting_log += f"\n===UPSERTING PGS {start_page}-{end_page}===\n"
        self._refresh_log()

    def log_successful_article_fetch(self, p1: int, p2: int):
        """Logs a successful article fetch."""
        self._fetching_log += f"{self._get_timestamp()} [INFO]: Fetched pages {p1}-{p2}\n"
        self._refresh_log()

    def log_failed_article_fetch(self, p1: int, p2: int):
        """Logs a failed article fetch."""
        self._fetching_log += f"{self._get_timestamp()} [ERROR]: Could not fetch pages {p1}-{p2}\n"
        self._refresh_log()

    def log_missing_content(self, article_id):
        """Logs a missing content warning for an article."""
        self._embedding_log += f"{self._get_timestamp()} [WARNING]: Skipped article. Missing content (ID {article_id}).\n"
        self._refresh_log()

    def log_chunking_error(self, article_id):
        """Logs a chunking error warning for an article."""
        self._embedding_log += f"{self._get_timestamp()} [WARNING]: Skipped article. Failed to chunk (ID {article_id}).\n"
        self._refresh_log()

    def log_missing_id(self):
        """Logs a missing ID warning for an article."""
        self._embedding_log += f"{self._get_timestamp()} [WARNING]: Skipped article. Missing ID.\n"
        self._refresh_log()

    def log_successful_upsert(self, num_embeddings: int):
        """Logs a successful upsert operation."""
        self._upserting_log += f"{self._get_timestamp()} [INFO]: Upserted {num_embeddings} embeddings.\n"
        self._refresh_log()

    def _refresh_log(self):
        """Refreshes the entire log file with the updated information."""
        self._info_log = self._generate_info_log()
        self._runtime_log = self._fetching_log + self._embedding_log + self._upserting_log

        with open(self._file_path, 'w') as file:
            file.write(self._info_log + self._runtime_log)

    def _get_timestamp(self):
        """Generates a timestamp."""
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    def _append_to_log(self, text: str, create_newline: bool = True):
        """
        Appends text to the log file.

        :param text: The text to append.
        :param create_newline: If True, a newline will be added after the text.
        """
        with open(self._file_path, 'a') as file:
            appended_text = text + ("\n" if create_newline else "")
            self._runtime_log += appended_text
            file.write(appended_text)
