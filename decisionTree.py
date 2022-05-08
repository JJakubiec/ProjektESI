import math
import pandas as pd
import pydot
from node import Node
from warnings import simplefilter
from graphviz import render
pd.options.mode.chained_assignment = None  # default='warn'
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


class DecisionTree:
    def __init__(self, file_name, sheet_name):
        # wczytywanie danych z pliku i przypisanie ich do atrybutu klasy
        self.data_frame = pd.read_excel(file_name, sheet_name)
        # kolejka do przetrzymywania podzielonych data framów
        self.fifo_splitting = []
        # kolejka do przetrzymywania utworzonych nodów
        self.fifo_node = []
        # pierwszy element w kolejce to cały data_frame
        self.fifo_splitting.append(self.data_frame)
        # do tego noda będą przypinane liście
        self.root_node = Node()
        # pierwszy node w kolejce to root_node
        self.fifo_node.append(self.root_node)

    def start(self):
        # lista nazw wszystkich atrybutów
        attributes = list(self.get_columns_from_data_frame(self.data_frame, 'atrybut'))
        # lista nazw wszystkich przesłanek
        conditions = list(self.get_columns_from_data_frame(self.data_frame, 'przesłanka'))
        # nazwa konkluzji
        conclusion_name = 'czas wolny po pracy'
        # usuwanie nazw konkluzji z listy nazw wszystkich przesłanek
        while conclusion_name in conditions:
            conditions.remove(conclusion_name)
        # wykonuj dopóki kolejka nie jest pusta
        while len(self.fifo_splitting) > 0:
            # pobieranie pierwszego data_frame z kolejki
            current_data_frame = self.fifo_splitting.pop(0)
            # pobieranie pierwszego noda z kolejki
            current_node = self.fifo_node.pop(0)
            # wyliczanie entropii dla konkluzji
            i = self.entropy_for_conclusion(current_data_frame, [conclusion_name])
            # pobieranie wszystkich wierszy dla konkluzji
            rows_conclusion = self.get_rows_from_data_frame(current_data_frame, ['przesłanka'], [conclusion_name])
            # lista do przechowywania informacji o maksymalnym zysku informacyjnym
            max_info = [0, '', '']
            for (condition, attribute) in zip(conditions, attributes):
                # pobieranie wiersza z daną przesłanką i atrybutem
                row_attribute = self.get_rows_from_data_frame(current_data_frame, ['przesłanka', 'atrybut'], [condition, attribute])
                # wyliczanie entropii dla pobranego wiersza
                e = self.entropy_for_attribute(row_attribute, rows_conclusion)
                # sprawdzenie czy zysk informacyjny jest największy
                if i - e > max_info[0]:
                    max_info[0] = i - e
                    max_info[1] = condition
                    max_info[2] = attribute
            # jeśli największy uzyskany zysk informacyjny jest różny od 0 to dzielimy data_frame
            if max_info[0] != 0:
                # dzielenie data_framu
                self.splitting_data_frame_by_condition_and_attribute(current_data_frame, current_node, max_info[1], max_info[2])
            else:
                # jeśli największy zysk informacyjny jest równy 0 to zapisujemy nazwę konkluzji do noda i nie dzielimy
                current_node.name = self.get_conclusion(rows_conclusion)
        # gdy w kolejce nie mamy już niczego do przetworzenia to rysujemy drzewo
        self.draw_tree()

    # pobieramy nazwę konkluzji
    def get_conclusion(self, rows_conclusion):
        for (index, x) in enumerate([sum(list(i)[2:]) for i in list(rows_conclusion.values)]):
            if x > 0:
                return list(rows_conclusion.values)[index][1]

    # wyliczanie entropii dla każdego atrybutu
    def entropy_for_attribute(self, row_attribute, rows_conclusion):
        # wartości dla danego atrybutu
        compared_attribute_values = list(row_attribute.values[0][2:])
        # wartości dla wszystkich konkluzji
        conclusions = [list(i)[2:] for i in list(rows_conclusion.values)]
        # sumy gdy atrybut jest pozytywny i negatywny
        sum_negative = 0
        sum_positive = 0
        # rozpiętość listy wartości dla danego atrybutu
        all_val = len(compared_attribute_values)
        # list które przetrzymują sumy przy porównywaniu konkluzji i atrybutu dla danej konkluzji
        sum_conclusions_positive = []
        sum_conclusions_negative = []
        sum_entropy = 0
        # h to index konkluzji, conclusion to konkluzja która jest aktualnbie porównywana
        for (h, conclusion) in enumerate(conclusions):
            sum_conclusions_positive.append(0)
            sum_conclusions_negative.append(0)
            # index to index wartości w konkluzji która jest porównywana, value to wartość z konkluzji
            for (index, value) in enumerate(conclusion):
                # sprawdzanie zgodności dla negatywnego i pozytywnego atrybutu
                if value == 1 and compared_attribute_values[index] == 0:
                    sum_negative += 1
                    sum_conclusions_negative[h] += 1
                if value == 1 and compared_attribute_values[index] == 1:
                    sum_positive += 1
                    sum_conclusions_positive[h] += 1
        # dla atrybutu pozytywnego i negatywnego wyliczamy entropie
        # i sumujemy entropie
        for (positive, negative) in zip(sum_conclusions_positive, sum_conclusions_negative):
            sum_entropy += (sum_positive/all_val)*self.entropy_log(positive, sum_positive) + (sum_negative/all_val)*self.entropy_log(negative, sum_negative)

        return sum_entropy

    # wyliczanie entropii dla konkluzji
    def entropy_for_conclusion(self, data_frame, conclusion_name: []):
        # pobieranie wierszy które w kolumnie przesłanka mają nazwę danej przesłanki
        conclusion_rows = self.get_rows_from_data_frame(data_frame, ['przesłanka'], conclusion_name)
        # pobieranie listy nazw atrybutów dla danej przesłanki
        conclusion_attribute_rows = list(self.get_columns_from_data_frame(conclusion_rows, 'atrybut'))
        entropy_sum = 0
        # dla każdego elementu z listy (wiersza konkluzji) oblicz fragment entropii
        for attribute_name in conclusion_attribute_rows:
            # pobieranie wiersza który w kolumnie atrybut ma nazwę atrybutu
            attribute_row = self.get_rows_from_data_frame(conclusion_rows, ['atrybut'], [attribute_name])
            # obliczanie ile jest w tym wierszu jedynek
            same_data_counter = sum(list(attribute_row.values[0][2:]))
            # jak długi jest ten wiersz
            length_of_data_frame = len(attribute_row.columns) - 2
            # obliczanie fragmentu entropii dla jednego wiersza przesłanki
            entropy_sum += self.entropy_log(same_data_counter, length_of_data_frame)

        return entropy_sum

    # obliczanie entropii
    def entropy_log(self, p, n):
        if p != 0 and n != 0:
            return -(p/n)*math.log2(p/n)
        else:
            return 0

    # rozdzlielanie data_framu i przypisywanie do przesłanek noda jego dzieci
    def splitting_data_frame_by_condition_and_attribute(self, data_frame, root_node: Node, condition_name, attribute_name):
        # nadawanie nazwy nodowi
        root_node.name = str(condition_name) + " : " + str(attribute_name)
        # lewe dziecko
        left_node = Node()
        # prawe dziecko
        right_node = Node()
        # pobieranie wiersza który będzie elementem podziału
        row_to_split_by = self.get_rows_from_data_frame(data_frame, ['przesłanka', 'atrybut'], [condition_name, attribute_name])
        # przepinanie kolumn z nazwami atrybutów i przesłanek
        left_data_frame = self.get_columns_from_data_frame(data_frame, ['przesłanka', 'atrybut'])
        right_data_frame = self.get_columns_from_data_frame(data_frame, ['przesłanka', 'atrybut'])
        # przypisanie kolumn w oparciu o wartości w danym wierszu
        for (row_value, column_name) in zip(row_to_split_by.values[0], list(row_to_split_by)):
            column = list(self.get_columns_from_data_frame(data_frame, column_name))
            if row_value == 0:
                left_data_frame[column_name] = column
            elif row_value == 1:
                right_data_frame[column_name] = column

        # usuwanie kolumn przesłanka, atrybut
        test_left_data_frame = left_data_frame.drop(['przesłanka', 'atrybut'], axis=1)
        test_right_data_frame = right_data_frame.drop(['przesłanka', 'atrybut'], axis=1)
        # sprawdzanie czy data_framy po podziale nie są puste aby w razie czego nie przypisywać ich jako dziecko
        if not test_left_data_frame.empty:
            root_node.set_left_child(left_node)
            self.fifo_node.append(left_node)
            self.fifo_splitting.append(left_data_frame)

        if not test_right_data_frame.empty:
            root_node.set_right_child(right_node)
            self.fifo_node.append(right_node)
            self.fifo_splitting.append(right_data_frame)

    # pobieranie wierszy z data_frame
    def get_rows_from_data_frame(self, data_frame, column_names: [], conditions: []):
        for (column_name, condition) in zip(column_names, conditions):
            data_frame = data_frame.loc[data_frame[column_name] == condition]
        return data_frame
    # pobieranie kolumn z data_frame
    def get_columns_from_data_frame(self, data_frame, columns_name):
        return data_frame[columns_name]

    # rekurencyjne rysowanie drzewa
    def draw_tree_rec(self, node: Node, uid, tree, parent_node, left_right_child):
        # uid dla odróżnienia nodów od siebie przy przypisywaniu krawędzi
        uid_piece = str(left_right_child)
        if uid_piece == 'tak':
            uid_piece = str(1)
        else:
            uid_piece = str(0)

        if node.left_child is not None:
            e = pydot.Edge(str(uid) + "\n" + parent_node.name, str(uid) + uid_piece + "\n" + node.name, label=left_right_child)
            tree.add_edge(e)
            self.draw_tree_rec(node.left_child, str(uid) + uid_piece, tree, node, 'nie')

        if node.right_child is not None:
            e = pydot.Edge(str(uid) + "\n" + parent_node.name, str(uid) + uid_piece + "\n" + node.name, label=left_right_child)
            tree.add_edge(e)
            self.draw_tree_rec(node.right_child, str(uid) + uid_piece, tree, node, 'tak')

        if node.right_child is None and node.left_child is None:
            e = pydot.Edge(str(uid) + "\n" + parent_node.name, str(uid) + uid_piece + "\n" + node.name, label=left_right_child)
            tree.add_edge(e)

    def draw_tree(self):

        tree = pydot.Dot(graph_type='digraph', strict=True)

        r = Node()
        r.name = "head"
        self.draw_tree_rec(self.root_node, 0, tree, r, 'nie')

        tree.write("tree.dot")
        render('dot', 'png', 'tree.dot')

