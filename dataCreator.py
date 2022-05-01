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

        self.conditions_attributes = (['zmęczenie', 'mocne'],
                                    ['zmęczenie', 'średnie'],
                                    ['zmęczenie', 'słabe'],
                                    ['zadanie w pracy', 'bardzo ważne'],
                                    ['zadanie w pracy', 'średnio ważne'],
                                    ['zadanie w pracy', 'mało ważne'],
                                    ['odpoczynek dnia następnego', 'możliwy'],
                                    ['odpoczynek dnia następnego', 'niemożliwy'],
                                    ['godzina zakończenia pracy', '14-15'],
                                    ['godzina zakończenia pracy', '15-16'],
                                    ['godzina zakończenia pracy', '16-17'],
                                    ['pogoda', 'deszczowo'],
                                    ['pogoda', 'mroźnie'],
                                    ['pogoda', 'słonecznie'],
                                    ['pogoda', 'pochmurnie'],
                                    ['czas wolny po pracy', 'powrót do pracy'],
                                    ['czas wolny po pracy', 'sen'],
                                    ['czas wolny po pracy', 'spacer'])

    def write_created_data_to_excel(self):
        row = 1
        col = 2

        for condition, attribute in self.conditions_attributes:
            self.worksheet.write(row, 0, condition)
            self.worksheet.write(row, 1, attribute)
            row = row + 1

        for temp_possibilities in self.all_possibilities:
            self.worksheet.write(0, col, 'kombinacja_' + str(col-1))

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
