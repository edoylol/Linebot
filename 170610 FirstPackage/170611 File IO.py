""" 11 June 2017 """

""" 

Managing File I/O 
r - read
w - write
a - append (read and write)
"""

fw = open('sample.txt','w')
#fw.write('Test writing on a blank file\n')
#fw.write('I like you\n')

for x in range (1, 16) :
    fw.write('This is line'+str(x)+'\n')
fw.close()

"""
read will read the whole document
readline will read the doc line by line
readlines will read all, then you can pick which line to process by adding [index] at the variable
"""

fr = open('sample.txt','r')
text = fr.read()
print(text)
fw.close()

fr = open('sample.txt','r')
text = fr.readlines()
print(text[2])
fw.close()