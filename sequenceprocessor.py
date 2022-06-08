import numpy as np
class Node:
    def __init__(self, data=None, next=None):
        self.data = data
        self.next = next

class Linkedlist:
    def __init__(self):
        self.head = None

    def insert_at_end(self,data):
        if self.head is None:
            self.head = Node(data, None)
            return
        itr = self.head
        while itr.next:
            itr = itr.next
        itr.next = Node(data, None)

    def get_length(self,data):
        length = len(data)
        return length

    def levenshtein_editdistance(self,originalans, studentans, scoring=True):
        # Initialize matrix of zeros
        s = originalans
        t = studentans
        rows = self.get_length(s) + 1
        cols = self.get_length(t) + 1
        distance = np.zeros((rows, cols), dtype=int)

        # Populate matrix of zeros with the indices of each character of both strings
        for i in range(1, rows):
            for k in range(1, cols):
                distance[i][0] = i
                distance[0][k] = k
        '''Iterate over the matrix to compute the cost(deletions,insertions and substitutions)
          If they are same in the two strings in a given position [i,j] then the cost is 0
          In order to align the results with those of the Python Levenshtein package,the ratio cost of a substitution is 1'''
        for col in range(1, cols):
            for row in range(1, rows):
                if s[row - 1] == t[col - 1]:
                    cost = 0
                else:
                    if scoring == True:
                        cost = 1
                distance[row][col] = min(distance[row - 1][col] + 1,  # Cost of deletions
                                         distance[row][col - 1] + 1,  # Cost of insertions
                                         distance[row - 1][col - 1] + cost)  # Cost of substitutions
        if scoring == True:
            #Computation of the Levenshtein Distance Ratio
            scoring = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
            return scoring * 100

    def insert_values(self, datalist):
        self.head = None
        for data in datalist:
            self.insert_at_end(data)


    def initial_manipulation(self,columns):
        if self.head is None:
            print('Empty')
        itr = self.head
        while itr:
            for i in columns:
                a = str(itr.data)
                if self.levenshtein_editdistance(i,a) > 88:
                    itr.data = i
            itr = itr.next

    def data_manipulation(self,columns):
        columns = columns
        if self.head is None:
            print('Empty')
        itr = self.head
        while itr:
            for i in columns:
                a = str(itr.data)
                if self.levenshtein_editdistance(i, a) > 60:
                    if itr.next is not None:
                        check = str(itr.data)+str(itr.next.data)
                        if self.levenshtein_editdistance(i,check) > 94:
                            itr.data = i
                            if itr.next.next is not None:
                                itr.next = itr.next.next
                            else:
                                itr.next = None
            itr = itr.next

    def print(self):
        if self.head is None:
            print('Empty')
            return
        itr = self.head
        llstr = ''
        while itr:
            llstr += str(itr.data)+' '
            itr = itr.next
        return llstr