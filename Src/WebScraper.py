import datetime
import time
import random
import requests

swimrankings_url = "https://www.swimrankings.net/index.php"

swimrankings_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.swimrankings.net/index.php?page=athleteSearch",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}



class WebScraper:
    def __init__(self, base_url: str = swimrankings_url, headers: dict = swimrankings_headers):
        """
        Initializes the WebScraper object.
        :param base_url: The base URL of the website to scrape
        :param headers: The headers to be used in the request
        """
        self.base_url = base_url
        self.headers = headers

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def swimmer_data(self, request_params: dict) -> str:
        """
        Retrieves the data from the website using the request parameters.
        :param request_params: The parameters to be used in the request
        :return: The response text (html string)
        """
        response = requests.get(self.base_url, params=request_params, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            raise ValueError(f"Error tijdens ophalen gegevens van {self.base_url}")

    @staticmethod
    def create_request(first_name: str, last_name: str, gender: str) -> dict:
        """
        Creates a request object using the request parameters.
        :param first_name: The first name of the swimmer
        :param last_name: The last name of the swimmer
        :param gender: gender of the swimmer
        :return: A request as a dictionary
        """
        gender_code = 1 if gender == "male" else 2

        return {"internalRequest": "athleteFind", "athlete_clubId": 43,  # Club ID (43 for Belgium)
                "athlete_gender": gender_code, "athlete_lastname": last_name, "athlete_firstname": first_name}

    def swimmer_website(self, swimrankings_id: int) -> str:
        current_year = datetime.date.today().year
        params = {
            "page": "athleteDetail",
            "athleteId": swimrankings_id,
            "result": current_year
        }

        for attempt in range(5):
            try:
                response = self.session.post(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                time.sleep(random.uniform(2, 5))
                return response.text
            except requests.exceptions.RequestException as e:
                wait_time = (2 ** attempt) + random.random()
                print(f"Attempt {attempt + 1} failed: {e}. Waiting {wait_time:.2f}s before retrying.")
                time.sleep(wait_time)

        raise ValueError("Kon de data niet ophalen na meerdere pogingen.")
