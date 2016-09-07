#! /usr/bin/env python3

import pronouncing as pr
import sys

f = sys.argv[1]

def find_stress(line):
    stresslist = []
    words = line.split()
    for word in words:
        word = word.strip('",.?!;:').lower()
        s = pr.stresses_for_word(word)
        if any(x == '0' for x in s):
            stresslist.append('0')
        elif len(s) != 0:
            stresslist.append(s[0])
    stress = ''.join(stresslist)
    return stress

l = "Shall I compare thee to a summer's day?"

def name_meter(stress):
    stressed_syllables = [i for i,s in enumerate(stress) if s == '1']
    return stressed_syllables

with open(f, 'r') as file:
    text = file.readlines()
    for line in text:
        print(find_stress(line))
        print(name_meter(find_stress(line)))
