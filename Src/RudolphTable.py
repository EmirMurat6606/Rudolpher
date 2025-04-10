import csv
import datetime


def get_table_nr(category: int, gender: str) -> tuple[int, int]:
    """
    Determines rudolph table number, helper function for ReadCSV constructor
    :param category: age category of the swimmer (always 9+)
    :param gender: the gender of the swimmer ("male" or "female")
    :return: tuple of two integers representing the table numbers
    """

    extra_offset = 12 if gender == "female" else 0

    if category <= 19:
        table1_nr, table2_nr = category - 8, category - 7
    else:
        table1_nr, table2_nr = 12, 12

    return table1_nr + extra_offset, table2_nr + extra_offset


class RudolphTable:
    def __init__(self, age_category: int, gender: str):
        self.table_nrs: tuple[int, int] = get_table_nr(age_category, gender)
        self.file_1 = self.csv_file()[0]
        self.file_2 = self.csv_file()[1]
        self.table_1: dict = {}
        self.table_2: dict = {}
        self.read_csv()

    def csv_file(self) -> tuple[str, str]:
        """
        Determines the CSV file name on which the table is based
        :return: file name: structure (rudolph_tables-page-[table_nr]-table-1.csv)
        """
        return (f"./RudolphTables/rudolph_tables-page-{self.table_nrs[0]}-table-1.csv",
                f"./RudolphTables/rudolph_tables-page-{self.table_nrs[1]}-table-1.csv")

    @staticmethod
    def parse_time(time_str):
        """Convert time in  format 'MM:SS.SS' to seconds as a float."""
        try:
            minutes, seconds = map(float, time_str.replace(",", ".").split(":"))
            return minutes * 60 + seconds
        except ValueError:
            return float('inf')

    def read_csv(self) -> None:
        first_file = True
        for opened_file in [self.file_1, self.file_2]:
            with open(opened_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)

                strokes = {"Freestyle": ["50m", "100m", "200m", "400m", "800m", "1500m"],
                           "Breaststroke": ["50m", "100m", "200m"], "Butterfly": ["50m", "100m", "200m"],
                           "Backstroke": ["50m", "100m", "200m"], "Medley": ["200m", "400m"]}

                organized_table = {}

                for row in reader:
                    # Get the points from the first column
                    if row[0] and row[0].isdigit():
                        points = int(row[0])  # Update points
                    else:
                        points = None

                    if points is None:
                        continue

                    index = 1
                    for stroke, distances in strokes.items():
                        for distance in distances:
                            key = f"{distance} {stroke}"
                            time = row[index] if index < len(row) - 1 else ""

                            if time:
                                time = time.replace(",", ".")
                                if key not in organized_table:
                                    organized_table[key] = {}
                                organized_table[key][time] = points
                            index += 1
                if first_file:
                    self.table_1 = organized_table
                    first_file = False
                else:
                    self.table_2 = organized_table

    def get_rudolph_points(self, stroke_distance: str, best_time: str, season_half: int) -> float:
        """
        Determine rudolph points based on stroke_distance, best_time and the season half
        :param stroke_distance: distance + stroke concatenation (example: "50m Freestyle")
        :param best_time: fastest time for the distance + stroke combination in season half
        :param season_half: the season half (0 or 1)
        :return: floating point number representing rudolph points
        """
        table: dict = {}
        if season_half == 0:
            table = self.table_1
        elif season_half == 1:
            table = self.table_2

        best_time_seconds = self.parse_time(best_time)

        # Get the Rudolph table for the given stroke_distance
        rudolph_data = sorted(table[stroke_distance].items(), key=lambda x: self.parse_time(x[0]))

        # Iterate through the table to find the closest range for interpolation
        for i in range(len(rudolph_data) - 1):
            time1, points1 = rudolph_data[i]
            time2, points2 = rudolph_data[i + 1]

            time1_seconds = self.parse_time(time1)
            time2_seconds = self.parse_time(time2)

            # Check if the best_time falls between time1 and time2
            if time1_seconds <= best_time_seconds <= time2_seconds:
                # Linear interpolation for points
                fraction = (best_time_seconds - time1_seconds) / (time2_seconds - time1_seconds)
                interpolated_points = points1 + (points2 - points1) * fraction
                return interpolated_points

        # If the time is worse than the worst time in the table, return 0 points
        if best_time_seconds > self.parse_time(rudolph_data[-1][0]):
            return 0


class Rudolpher:
    def __init__(self):
        # Relevant strokes for calculating max rudolph points
        self.relevant_strokes: list[str] = ["100m Freestyle", "200m Freestyle", "400m Freestyle", "800m Freestyle",
                                            "1500m Freestyle", "100m Breaststroke", "200m Breaststroke",
                                            "100m Butterfly", "200m Butterfly", "100m Backstroke", "200m Backstroke",
                                            "200m Medley", "400m Medley"]

    def get_max_points(self, age_category: int, gender: str, season_bests: dict) -> list[float]:
        """
        Returns max rudolph points for both 25m and 50m course
        :param age_category: age category of the swimmer (10+)
        :param gender: gender of the swimmer ("male" or "female")
        :param season_bests: dictionary with season bests of a swimmer
        :return: list of length 2 with max rudolph points for [25m, 50m] -course
        """
        cur_year: int = datetime.datetime.now().year

        rudolph_table = RudolphTable(age_category, gender)

        total: list[float] = []

        for course in ["25m", "50m"]:
            season_half: int = 0
            highest: float = 0.0
            # TODO: Expand functionality to provide proper working in both !&first half&! of the season and second half
            for year in [str(cur_year - 1), str(cur_year)]:
                for stroke in self.relevant_strokes:
                    best_time = season_bests[stroke][course][year]
                    if best_time is not None:
                        points = rudolph_table.get_rudolph_points(stroke, best_time, season_half)
                        if highest < points:
                            highest = points
                season_half = 1
            total.append(round(highest, 2))

        print(total)
        return total
