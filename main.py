from dataCreator import *
from dataValidator import *
from decisionTree import *

if __name__ == '__main__':

    # file_name = "data.xlsx"
    # sheet_name = "sheet"

    file_name = "data.xlsx"
    sheet_name = "sheet"

    # dataCreator = DataCreator(file_name, sheet_name)
    # dataCreator.create_data(0, [])
    # dataCreator.write_created_data_to_excel()

    # dataValidator = DataValidator(file_name, sheet_name)
    # dataValidator.check_if_valid()

    decisionTree = DecisionTree(file_name, sheet_name)
    decisionTree.start()
