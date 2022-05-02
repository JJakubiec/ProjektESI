import xlsxwriter
from random import randrange

class DataCreator:
    def __init__(self, file_name, sheet_name):
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.workbook = xlsxwriter.Workbook(self.file_name)
        self.worksheet = self.workbook.add_worksheet(self.sheet_name)
        self.all_possibilities = []
        self.possibilities = [[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                              [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                              [[1, 0], [0, 1]],
                              [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                              [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]]

        self.conditions_attributes = (['zmeczenie', 'mocne'],
                                    ['zmeczenie', 'srednie'],
                                    ['zmeczenie', 'slabe'],
                                    ['zadanie w pracy', 'bardzo wazne'],
                                    ['zadanie w pracy', 'srednio wazne'],
                                    ['zadanie w pracy', 'malo wazne'],
                                    ['odpoczynek dnia nastepnego', 'mozliwy'],
                                    ['odpoczynek dnia nastepnego', 'niemozliwy'],
                                    ['godzina zakonczenia pracy', '14-15'],
                                    ['godzina zakonczenia pracy', '15-16'],
                                    ['godzina zakonczenia pracy', '16-17'],
                                    ['pogoda', 'deszczowo'],
                                    ['pogoda', 'mroznie'],
                                    ['pogoda', 'slonecznie'],
                                    ['pogoda', 'pochmurnie'],
                                    ['czas wolny po pracy', 'powrot do pracy'],
                                    ['czas wolny po pracy', 'sen'],
                                    ['czas wolny po pracy', 'spacer'])

    def write_created_data_to_excel(self):
        row = 1
        col = 2

        self.worksheet.write(0, 0, "przesłanka")
        self.worksheet.write(0, 1, "atrybut")

        for condition, attribute in self.conditions_attributes:
            self.worksheet.write(row, 0, condition)
            self.worksheet.write(row, 1, attribute)
            row = row + 1

        for temp_possibilities in self.all_possibilities:
            self.worksheet.write(0, col, col-1)

            row = 1
            for outer in temp_possibilities:
                for inner in outer:
                    self.worksheet.write(row, col, inner)
                    row = row + 1

            temp_rand = row + randrange(3)

            for k in range(1, 4):
                self.worksheet.write(row, col, 0)
                row = row + 1

            self.worksheet.write(temp_rand, col, 1)

            col = col + 1

        self.workbook.close()

    def create_data(self, level, output: list):
        if level < len(self.possibilities):
            for row_index in self.possibilities[level]:
                output.append(row_index)
                self.create_data(level + 1, output)
                output.pop()
        else:
            self.all_possibilities.append(output[:])
