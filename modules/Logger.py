import os
from datetime import datetime

class Logger:
    def __init__(self, storage_path: str,
                 index_name: str,
                 logging_enabled: str,
                 display_skipped_articles: str,
                 starting_page: int,
                 ending_page: int):
        
        self._storage_path = storage_path
        self._time_started = self._get_timestamp()
        self._time_finished = "N/A"

        self._file_path = f"{self._storage_path}/{self._time_started}.log"

        self._index_name = index_name
        self._logging_enabled = logging_enabled
        self._display_skipped_articles = display_skipped_articles
        self._starting_page = starting_page
        self._ending_page = ending_page

        self._end_message = "N/A"

        self._info_log = f"""
===GENERAL INFORMATION===
Timestamp Start: {self._time_started}
Timestamp End: {self._time_finished}
Message on Exit: {self._end_message}
Index Name: {self._index_name}
Logging Enabled: {self._logging_enabled}
Display skipped articles: {self._display_skipped_articles}
Starting Page: {self._starting_page}
Ending Page: {self._ending_page}
"""
        self._fetching_log = ""
        self._embedding_log = ""
        self._upserting_log = ""
        self._runtime_log = ""
    def create_log_file(self) -> bool:
        # Make sure parent storage directory exists
        if not os.path.exists(self._storage_path):
            return False
        
        # Put template in new log file
        file = open(self._file_path, 'w')
        file.write(self._info_log)
        file.close()

        return True

    def end_log(self, message="Successful"):
        self._time_finished = self._get_timestamp()
        self._end_message = message
        self._refresh_log()
    
    def start_fetching_articles_section(self):
        self._fetching_log += "\n===FETCHING ARTICLES===\n"
        self._refresh_log()
    
    def start_embedding_section(self, start_page: int, end_page: int):
        self._embedding_log += f"\n===EMBEDDING PGS {start_page}-{end_page}===\n"
        self._refresh_log()
        
    def start_upserting_section(self, start_page: int, end_page: int):
        self._upserting_log += f"\n===UPSERTING PGS {start_page}-{end_page}===\n"
        self._refresh_log()
    
    def log_successful_article_fetch(self, p1: int, p2: int):
        self._fetching_log += f"{self._get_timestamp()} [INFO]: Fetched pages {p1}-{p2}\n"
        self._refresh_log()
        
    def log_failed_article_fetch(self, p1: int, p2: int):
        self._fetching_log += f"{self._get_timestamp()} [ERROR]: Could not fetch pages {p1}-{p2}\n"
        self._refresh_log()
    
    def log_missing_content(self, article_id):
        self._embedding_log += f"{self._get_timestamp()} [WARNING]: Skipped article. Missing content (ID {article_id}).\n"
        self._refresh_log()

    def log_chunking_error(self, article_id):
        self._embedding_log += f"{self._get_timestamp()} [WARNING]: Skipped article. Failed to chunk (ID {article_id}).\n" 
        self._refresh_log()

    def log_missing_id(self):
        self._embedding_log += f"{self._get_timestamp()} [WARNING]: Skipped article. Missing ID.\n"
        self._refresh_log()
        
    def log_successful_upsert(self, num_embeddings: int):
        self._upserting_log += f"{self._get_timestamp()} [INFO]: Upserted {num_embeddings} embeddings.\n" 
        self._refresh_log()

    def _refresh_log(self):
        self._info_log = f"""
===GENERAL INFORMATION===
Timestamp Start: {self._time_started}
Timestamp End: {self._time_finished}
Message on Exit: {self._end_message}
Index Name: {self._index_name}
Logging Enabled: {self._logging_enabled}
Display skipped articles: {self._display_skipped_articles}
Starting Page: {self._starting_page}
Ending Page: {self._ending_page}
"""
        self._runtime_log = self._fetching_log + self._embedding_log + self._upserting_log

        file = open(self._file_path, 'w')
        file.write(self._info_log + self._runtime_log)
        file.close()
    
    def _get_timestamp(self):
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    def _append_to_log(self, text: str, create_newline: bool = True):
        file = open(self._file_path, 'a')

        appended_text = text
        if create_newline:
            appended_text += "\n"

        self._runtime_log += appended_text
        file.write(appended_text)

        file.close()
        
    

