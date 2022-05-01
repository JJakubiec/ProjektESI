import pandas as pd


class DataValidator:
    def __init__(self, file_name, sheet_name):
        self.df = pd.read_excel(file_name, sheet_name).loc[0:19, :]
        self.file_name = file_name
        self.sheet_name = sheet_name

    def check_if_valid(self):
        for first in range(1, 216):
            output_first = 0
            for p in self.df['kombinacja_' + str(first)]:
                output_first = output_first * 10
                output_first = output_first + p

            for second in range(first + 1, 216):
                output_second = 0

                for p in self.df['kombinacja_' + str(second)]:
                    output_second = output_second * 10
                    output_second = output_second + p

                if output_first == output_second:
                    print('Problem z kolumnami ' + str(first) + " " + str(second))
