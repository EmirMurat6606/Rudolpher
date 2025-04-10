from bs4 import BeautifulSoup
from collections import defaultdict
import re


class HTMLParser:

    @staticmethod
    def get_athlete_info(html_text: str, club_name: str = "BEL - Temse Schelde Zwemmers") -> tuple[int, int]:
        """
        Parses a query response in HTML format and extracts the athlete ID and birth year
        for a specific club.

        :param html_text: The response from the query in HTML format
        :param club_name: The name of the club to filter athletes by
        :return: A tuple (athlete_id, birth_year) both integers
        """
        soup = BeautifulSoup(html_text, 'html.parser')  # Parse the HTML

        # Find all rows of athletes
        athlete_rows = soup.find_all('tr', class_=['athleteSearch0', 'athleteSearch1'])

        for row in athlete_rows:
            # Find the club name in the current row
            club_cell = row.find('td', class_='club')
            if club_cell and club_name in club_cell.text:
                # Extract athlete ID from the link
                link = row.find('a', href=True)
                if link and 'athleteId=' in link['href']:
                    athlete_id = link['href'].split('athleteId=')[-1]
                else:
                    raise ValueError("Athlete ID niet gevonden voor de club.")

                # Extract birth year from the date cell
                date_cell = row.find('td', class_='date')
                if date_cell:
                    birth_year = date_cell.text.strip()
                else:
                    raise ValueError("Geboortejaar niet gevonden voor de club.")

                # Ensure both values are valid
                if athlete_id and birth_year.isdigit():
                    return int(athlete_id), int(birth_year)

        # Raise an error if no athlete matches the club name
        raise ValueError(f"Geen atleet gevonden voor de club '{club_name}'.")


    @staticmethod
    def parse_results(html_content) -> dict:
        # Function to create a nested dictionary
        def get_nested_dict():
            return defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

        # Data structure to store the results
        data = get_nested_dict()

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Search for the table rows containing the results
        rows = soup.find_all('tr', class_='athleteResult0') + soup.find_all('tr', class_='athleteResult1')

        # Gather the results from the table rows
        for row in rows:
            date = row.find('td', class_='date').get_text(strip=True)
            course = row.find('td', class_='course').get_text(strip=True)
            time_tag = row.find('a', class_='time')
            time_str = time_tag.get_text(strip=True) if time_tag else None

            # Check if the time tag contains the splits
            splits_data = None
            if time_tag and 'onmouseover' in time_tag.attrs:
                # "onmouseover" attribute contains the splits data
                onmouseover_data = time_tag['onmouseover']
                # Time data with regex
                splits_data = re.findall(
                    r'<tr><td class=\'split0\'>([^<]+)</td><td class=\'split1\'>([^<]+)</td><td class=\'split2\'>([^<]+)</td></tr>',
                    onmouseover_data)

            # Take stroke and distance from the event link
            event_header = row.find_previous('th', class_='event')
            event = event_header.get_text(strip=True) if event_header else None

            if event and date and time_str:
                # Take the year from the date
                year = date.split()[-1]

                # Determine stroke (event) and course
                event_key = event
                course_key = course

                # Update the fastest time if the current time is faster
                if data[event_key][course_key][year] is None or time_str < data[event_key][course_key][year]:
                    data[event_key][course_key][year] = time_str

        return data

