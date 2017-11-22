
# coding: utf-8

import numpy as np
import pandas as pd
from pandas import DataFrame
import regex as re

class spm:
    def __init__(self, lhs_list, rhs_list, start_symbol):
        self.lhs = lhs_list
        self.rhs = rhs_list
        self.start = start_symbol
    
    def nt_extractor(self,lhs):    #Function to extract all the non terminals from the productions
        nt = list(set(lhs))
        return nt
    
    def terminal_extractor(self,rhs):
        term_temp = []          #For holding a list of lists of terminals resulting from the re.findall part
        term_list = []          #For holding a list of set of terminals
        for rs in rhs:
            tt = re.findall(r'[0-9a-km-z\+\-\/\)\*\^\(\=]', rs)
            if tt != []:
                term_temp.append(tt)
        #While extracting terminals, we exclude lambda denoted by l to be included in the set of terminals
        #term_search is a list of lists so we change it to a list of strings
        for term in term_temp:
            for sym in term:
                term_list.append(sym)
        return list(set(term_list))
    
    def first(self, lhs, rhs, first_elements):
#         print 'For the FIRST matrix we shall consider the following pairs of non-terminals and terminals:\n '
        #Create an adjacency matrix for the FIRST matrix
        n = len(first_elements)
        first_df = pd.DataFrame(columns = first_elements, index = first_elements)
        
        for i in range(len(lhs)):
            first_df.loc[lhs[i]][rhs[i][0]] = 1

        first = first_df.fillna(0)
        first_matrix = first.as_matrix()
        return first_matrix
    
    def last(self, lhs, rhs, first_elements):
        #Create an adjacency matrix for the FIRST matrix
        n = len(first_elements)
        last_df = pd.DataFrame(columns = first_elements, index = first_elements)
        
        for i in range(len(lhs)):
            last_df.loc[lhs[i]][rhs[i][-1]] = 1

        last = last_df.fillna(0)
        last_matrix = last.as_matrix()
        return last_matrix
    
    def warshall(self, matrix, n):
        A = matrix.copy()
        for k in range(n):
            # Pick all vertices as source one by one
            for i in range(n):
                # Pick all vertices as destination for the
                # above picked source
                for j in range(n):
                    # If vertex k is on a path from i to j, 
                    # then make sure that the value of reach[i][j] is 1
                    A[i][j] = A[i][j] or (A[i][k] and A[k][j])
        return A
    
    def equal(self, lhs, rhs, first_elements):
        equal_df = DataFrame(columns = first_elements, index = first_elements)
        for i in range(len(rhs)):
            if len(rhs[i]) >= 2:
                for j in range(len(rhs[i])):
                    for k in range(len(rhs[i])-1):
                        equal_df.loc[rhs[i][j]][rhs[i][k+1]] = 1
                        j = j+1
                    break                  
        equal = equal_df.fillna(0)
        equal_matrix = equal.as_matrix()
        return equal_matrix.astype(int)

    def less_than(self, first_plus, equal):
        lesser_than = np.matmul(equal, first_plus)
        return lesser_than
                        
    def greater_than(self, last_plus, equal, first_star):
        great_than = (np.transpose(last_plus).dot(equal)).dot(first_star)
        return great_than
    
    def kleen_closure(self, B_plus, n):
        I = np.identity(n)
        B_star = I + B_plus
        return B_star
    
    def spm_matrix(self, less_than, greater_than, equal, n):
        spm = np.zeros((n,n))
        #In the np.array for SPM we will denote less than sign as 1, greater than by 2, equal to by 3
        for i in range(n):
            for j in range(n):
                if less_than[i,j] == 1:
                    spm[i,j] = 1
                elif greater_than[i,j] == 1:
                    spm[i,j] = 2
                elif equal[i,j] == 1:
                    spm[i,j] = 3
        return spm
		
number_prod = raw_input('Enter the number of productions in the Grammar: ')
no_prod = int(number_prod)

#lhs_list tracks all the LHS of the productions
#rhs_list tracks the RHS of all the productions

lhs_list = []
rhs_list = []
for i in range(no_prod):
    prod = raw_input("Enter production number %d: "%(i))
    p = prod.split('->')
    lhs_list.append(p[0])
    rhs_list.append(p[1])

start_symbol = lhs_list[0]
print '\nThe given productions are:\n:'
print '========================================\n'

#Print the productions on the screen
for i in range(no_prod):
    print '%s ---> %s\n'%(lhs_list[i], rhs_list[i])

spm_matrix = spm(lhs_list, rhs_list, start_symbol)
non_terminals = spm_matrix.nt_extractor(lhs_list)
terminals = spm_matrix.terminal_extractor(rhs_list)
#first_elements will be a list of the set of terminals and non terminals that will be used to create the SPM matrix
first_elements = list(set(terminals + non_terminals))
n = len(first_elements)
print '\n\n'
print 'The non-terminals in the grammar are: ',non_terminals
print 'The terminals in the grammar are: ', terminals
print 'The start symbol of the grammar is: %s\n\n'%(lhs_list[0])    

#FIRST matrix
first = spm_matrix.first(lhs_list, rhs_list, first_elements)
first_new = DataFrame(first, columns = first_elements, index = first_elements)
print 'FIRST matrix is given by:\n'
print 'FIRST elements are:\n'
print '=========================================\n'
for i in first_elements:
    for j in first_elements:
        if first_new.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print first_new
print '\n'

#FIRST+ matrix
first_plus = spm_matrix.warshall(first, n)
print 'FIRST+ matrix is given by:\n'
print 'FIRST+ elements are:\n'
print '=========================================\n'
first_plus_new = DataFrame(first_plus, columns = first_elements, index = first_elements)
for i in first_elements:
    for j in first_elements:
        if first_plus_new.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print first_plus_new
print '\n'


#FIRST* matrix
first_star = spm_matrix.kleen_closure(first_plus, n)
first_star_new = DataFrame(first_star, columns = first_elements, index = first_elements)
print 'FIRST* matrix is given by:\n'
print 'FIRST* elements are:\n'
print '=========================================\n' 
for i in first_elements:
    for j in first_elements:
        if first_star_new.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print first_star_new
print '\n'

#LAST matrix
last = spm_matrix.last(lhs_list, rhs_list, first_elements)
last_new = DataFrame(last, columns = first_elements, index = first_elements)
print 'LAST matrix is given by:\n'
print 'LAST elements are:\n'
print '=========================================\n'
for i in first_elements:
    for j in first_elements:
        if last_new.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print last_new
print '\n'

#LAST+ matrix
last_plus = spm_matrix.warshall(last, n)
last_plus_new = DataFrame(last_plus, columns = first_elements, index = first_elements)
print 'LAST+ matrix is given by:\n'
print 'LAST+ elements are:\n'
print '=========================================\n'
for i in first_elements:
    for j in first_elements:
        if last_plus_new.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print last_plus_new
print '\n'


#LAST* matrix
last_star = spm_matrix.kleen_closure(last_plus, n)
last_star_new = DataFrame(last_star, columns = first_elements, index = first_elements)
print 'LAST* matrix is given by:\n'
print 'LAST* elements are:\n'
print '=========================================\n'
for i in first_elements:
    for j in first_elements:
        if last_star_new.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print last_star_new
print '\n'

#EQUAL matrix
equal = spm_matrix.equal(lhs_list, rhs_list, first_elements)
print 'EQUAL matrix is given by:\n'
print 'EQUAL elements are:\n'
print '=========================================\n' 
equalto = DataFrame(equal, columns = first_elements, index = first_elements)
equalto2 = equalto.replace(1, '+-')
for i in first_elements:
    for j in first_elements:
        if equalto2.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print equalto2
print '\n'


#LESS THAN MATRIX
less_than = spm_matrix.less_than(first_plus, equal)
print 'LESS THAN matrix is given by:\n'
print 'LESS THAN elements are:\n'
print '=========================================\n' 
less_than1 = DataFrame(less_than, columns = first_elements, index = first_elements)
less_than2 = less_than1.replace(1, '<')
for i in first_elements:
    for j in first_elements:
        if less_than2.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print less_than2
print '\n'

#GREATER THAN MATRIX
greater_than = spm_matrix.greater_than(last_plus, equal, first_star)
print 'GREATER THAN matrix is given by:\n'
print 'GREATER THAN elements are:\n'
print '=========================================\n' 
great_than1 = DataFrame(greater_than, columns = first_elements, index = first_elements)
great_than2 = great_than1.replace(1, '>')
for i in first_elements:
    for j in first_elements:
        if great_than2.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print great_than2
print '\n'

#SPM MATRIX
spm = spm_matrix.spm_matrix(less_than, greater_than, equal, n)
print 'SPM matrix is given by:\n'
print 'SPM elements are:\n'
print '=========================================\n' 
spm_matrix = DataFrame(spm, columns = first_elements, index = first_elements)
s = spm_matrix.replace(1,'<')
s2 = s.replace(2,'>')
s3 = s2.replace(3,'=')
for i in first_elements:
    for j in first_elements:
        if s3.loc[i][j] != 0:
            print '(%s, %s)'%(i, j)
print s3
print '\n'





