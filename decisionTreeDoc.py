import math
import pandas as pd
import pydot

from node import Node

pd.options.mode.chained_assignment = None  # default='warn'
from IPython.display import Image, display


class DecisionTree:
    def __init__(self, file_name, sheet_name):
        self.data_frame = pd.read_excel(file_name, sheet_name)
        self.stack_splitting = []
        self.stack_node = []
        self.stack_splitting.append(self.data_frame)
        self.root_node = Node()
        self.stack_node.append(self.root_node)

    def start(self):

        # list wszystkich atrybutów
        attributes = list(self.get_columns_from_data_frame(self.data_frame, 'atrybut'))
        # lista wszystkich przesłanek
        conditions = list(self.get_columns_from_data_frame(self.data_frame, 'przesłanka'))
        conclusion_name = 'reklama'

        # usuwamy konkluzję z przesłanek
        while conclusion_name in conditions:
            conditions.remove(conclusion_name)

        # wykonuj dopóki stos nie jest pusty
        while len(self.stack_splitting) > 0:
            # wyrzuć ze stosu i przypisz do przetwarzania
            current_data_frame = self.stack_splitting.pop(0)
            current_node = self.stack_node.pop(0)
            # wyliczenie entropii dla konkluzji
            I = self.entropy_for_conclusion(current_data_frame, [conclusion_name])
            # lista do zapisu maksymalnego zysku informacyjnego oraz atrybutu i przesłanki
            # bierzemy wiersze z danymi konkluzjami z data_frame
            rows_conclusion = self.get_rows_from_data_frame(current_data_frame, ['przesłanka'], [conclusion_name])
            max_info = [0, '', '']

            for (condition, attribute) in zip(conditions, attributes):
                # bierzemy wiersz z danym atrybutem z data_frame
                row_attribute = self.get_rows_from_data_frame(current_data_frame, ['przesłanka', 'atrybut'],
                                                              [condition, attribute])
                # obliczamy entropię dla wiersza z entropią
                E = self.entropy_for_attribute(row_attribute, rows_conclusion)
                # sprawdzamy czy zysk informacyjny był największy
                if I - E > max_info[0]:
                    max_info[0] = I - E
                    max_info[1] = condition
                    max_info[2] = attribute
            # dla największego zysku informacyjnego dzielimy data_frame względem zapisanego atrybutu
            if max_info[0] != 0:
                self.splitting_data_frame_by_condition_and_attribute(current_data_frame, current_node, max_info[1],
                                                                     max_info[2])
            else:
                current_node.name = self.get_conclusion(rows_conclusion)

        self.draw_tree_rec(self.root_node, 0)

    def get_conclusion(self, rows_conclusion):
        for (index, x) in enumerate([sum(list(i)[2:]) for i in list(rows_conclusion.values)]):
            if x > 0:
                return list(rows_conclusion.values)[index][1]

    def entropy_for_attribute(self, row_attribute, rows_conclusion):
        # tworzymy listę z przeciwnymi danymi dla danego atrybutu
        negative_attribute = [(i + 1) % 2 for i in list(row_attribute.values[0][2:])]
        # tworzymy listę z data_frame
        positive_attribute = list(row_attribute.values[0][2:])
        # tworzymy listę list z wierszy konkluzji
        conclusions = [list(i)[2:] for i in list(rows_conclusion.values)]
        # sumujemy wartości w liście przeciwnej
        sum_negative = sum(negative_attribute)
        # sumujemy wartości w liście pozytywnej
        sum_positive = sum(positive_attribute)
        # suma obu list
        sum_all = sum_positive + sum_negative
        # listy do zapisu pokryć
        sum_conclusions_positive = []
        sum_conclusions_negative = []
        sum_entropy = 0
        # h to index w liście conclusions
        for (h, conclusion) in enumerate(conclusions):
            sum_conclusions_positive.append(0)
            sum_conclusions_negative.append(0)
            for (index, value) in enumerate(conclusion):
                # sprawdzamy czy istnieje pokrycie konkluzji z listą negatywną
                if value == 1 and negative_attribute[index] == 1:
                    sum_conclusions_negative[h] += 1
                # sprawdzamy czy istnieje pokrycie konkluzji z listą pozytywną
                if value == 1 and positive_attribute[index] == 1:
                    sum_conclusions_positive[h] += 1
        # obliczamy entropię wykorzystując wyliczone pokrycia
        for (positive, negative) in zip(sum_conclusions_positive, sum_conclusions_negative):
            sum_entropy += (sum_positive / sum_all) * self.entropy_log(positive, sum_positive) + (
                        sum_negative / sum_all) * self.entropy_log(negative, sum_negative)

        return sum_entropy

    def entropy_for_conclusion(self, data_frame, conditions_names: []):
        # pobieranie wierszy z data_frame które zawierają konkluzje
        condition_rows = self.get_rows_from_data_frame(data_frame, ['przesłanka'], conditions_names)
        # tworzenie listy atrybutów dla konkluzji
        condition_attribute_list = list(self.get_columns_from_data_frame(condition_rows, 'atrybut'))
        entropy_sum = 0
        for attribute_name in condition_attribute_list:
            # pobieranie wiersza z konkretnym atrybutem
            attribute_row = self.get_rows_from_data_frame(condition_rows, ['atrybut'], [attribute_name])
            # suma wystąpień jedynki w danym wierszu
            same_data_counter = sum(list(attribute_row.values[0][2:]))
            # długość danego wiersza
            length_of_data_frame = len(attribute_row.columns) - 2
            entropy_sum += self.entropy_log(same_data_counter, length_of_data_frame)

        return entropy_sum

    def entropy_log(self, p, n):
        if p != 0 and n != 0:
            return -(p / n) * math.log2(p / n)
        else:
            return 0

    def splitting_data_frame_by_condition_and_attribute(self, data_frame, root_node: Node, condition_name,
                                                        attribute_name):
        root_node.name = str(condition_name) + " : " + str(attribute_name)
        left_node = Node()
        right_node = Node()
        # pobieramy wiersz które będzie służył jako miejsce podziału data_frame
        row_to_split_by = self.get_rows_from_data_frame(data_frame, ['przesłanka', 'atrybut'],
                                                        [condition_name, attribute_name])
        # wpisujemy dane "indexowe" do nowego data_frame
        left_data_frame = self.get_columns_from_data_frame(data_frame, ['przesłanka', 'atrybut'])
        # wpisujemy dane "indexowe" do nowego data_frame
        right_data_frame = self.get_columns_from_data_frame(data_frame, ['przesłanka', 'atrybut'])
        # analizujmy wiersz podziału
        for (row_value, column_name) in zip(row_to_split_by.values[0], list(row_to_split_by)):
            # pobieramy kolumnę z data_frame
            column = list(self.get_columns_from_data_frame(data_frame, column_name))
            # jeśli w wierszu podziału występuje 0 to zapisujemy kolumnę do left_data_frame
            # jeśli w wierszu podziału występuje 1 to zapisujemy kolumnę do right_data_frame
            if row_value == 0:
                left_data_frame[column_name] = column
            elif row_value == 1:
                right_data_frame[column_name] = column

        # sprawdzamy czy left albo right nie jest pusty
        test_left_data_frame = left_data_frame.drop(['przesłanka', 'atrybut'], axis=1)
        test_right_data_frame = right_data_frame.drop(['przesłanka', 'atrybut'], axis=1)

        # po przeanalizowaniu wiersza zapisujmy oba data_framy na stosie
        if not test_left_data_frame.empty:
            root_node.set_left_child(left_node)
            self.stack_node.append(left_node)
            self.stack_splitting.append(left_data_frame)

        if not test_right_data_frame.empty:
            root_node.set_right_child(right_node)
            self.stack_node.append(right_node)
            self.stack_splitting.append(right_data_frame)

    def get_rows_from_data_frame(self, data_frame, column_names: [], conditions: []):
        for (column_name, condition) in zip(column_names, conditions):
            data_frame = data_frame.loc[data_frame[column_name] == condition]
        return data_frame

    def get_columns_from_data_frame(self, data_frame, columns_name):
        return data_frame[columns_name]

    def draw_tree_rec(self, node: Node, level):
        if node.left_child is not None:
            self.draw_tree_rec(node.left_child, level + 1)

        if node.right_child is not None:
            self.draw_tree_rec(node.right_child, level + 1)

        print(node.name + " " + str(level))

    def drawTree(self):

        tree = pydot.Dot(graph_type='graph', strict=True)

        x = pydot.Node("A", style="filled", fillcolor="green")
        tree.add_node(x)
        x = pydot.Node("B", style="filled", fillcolor="green")
        tree.add_node(x)
        x = pydot.Node("C", style="filled", fillcolor="green")
        tree.add_node(x)

        edge = pydot.Edge("A", "B")
        tree.add_edge(edge)
        edge = pydot.Edge("A", "C")
        tree.add_edge(edge)
        tree.write("tree.dot")

        (something,) = pydot.graph_from_dot_file('something.dot')
        something.write_png('somefile.png')


