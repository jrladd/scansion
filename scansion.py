#!/usr/bin/env python

#----------------#
# All lines in EEBO: ./scansion.py ../../data/eebo_tcp_MARCH_2015/just_lines/
#----------------#

from nltk.corpus import cmudict
from nltk.corpus import stopwords
import sys, glob, codecs
import Levenshtein as lev
from collections import defaultdict

i = sys.argv[1]
output = sys.argv[2]
prondict = cmudict.dict()
cmuwords= cmudict.words()

def just_stress(word): #Find a word in cmudict and return the numerical stresses for that word
	prons = prondict[word]
	stress=[]
	if len(prons) > 1: #For one-syllable words, prefer a 0 over a 1 (if one of prondict's options is a 0)
		possibles=[]
		for s in prons:
			possible_stress=''.join([''.join([char for char in syllable if char.isdigit()]) for syllable in s])
			possibles.append(possible_stress)
		if len(possibles[0]) == 1:
			if any(l == '0' for l in possibles):
				stress.append('0')
			else:
				stress.append('1')
		else:
			stress.extend(possibles[0])
	else:
		for syllable in prons[0]:
			for char in syllable:
				if char.isdigit():
					stress.append(char)
	stress=''.join(stress)
	return stress

def find_word(word): #Deal with words not in prondict
	distances={v: lev.distance(word, v) for v in cmuwords}
	best_match=min(distances, key=distances.get)
	return just_stress(best_match)

def stressByLine(line): #Return the stress pattern for a line of poetry, using the above prondict lookup
	line_stress=''
	words=line.split()
	words=[w.lower().strip('-,.?!:"').replace("'d", "ed") for w in words]
	for word in words:
		if word in prondict:
			ws = just_stress(word)
			line_stress=line_stress+ws
		elif '--' in word: #Attempt at fixing the problem with dashes, not fully solved
			dehyphenated=word.split('--')
			for w in dehyphenated:
				w=w.strip(',.?!:"')
				if w in prondict:
					ws = just_stress(w)
					line_stress=line_stress+ws
				else:
					ws = find_word(word)
					line_stress=line_stress+ws
		elif '-' in word: #If a word is hyphenated, look for its components separately
			dehyphenated=word.split('-')
			for w in dehyphenated:
				if w in prondict:
					ws = just_stress(w)
					line_stress=line_stress+ws
				else:
					ws = find_word(word)
					line_stress=line_stress+ws
		else: #If the word is unknown, look up the most similar word in prondict
			ws = find_word(word)
			line_stress=line_stress+ws


	return line_stress

def test_iambic_lines(poem): #Test for iambic pentameter specifically
	results=[]
	for line in poem:
		line_result=[]
		line_result.append(line.strip('\n'))
		stress=str(stressByLine(line))
		line_result.append(stress)
		if len(stress) >= 9 and len(stress) <= 11 and lev.distance('0101010101',stress) <= 4: #Tests meter at the level of the line, but 5 is a very low threshold for matching.
			line_result.append('MATCH')
		else:
			line_result.append('OUCH')
		results.append(line_result)
	return results


def find_meter(meterResults): #A quick way of finding the dominant metrical form in any group of lines (without a bias toward existing verse forms, as above).
	meter_dict={}
	for v in meterResults:
		if isinstance(v, str):
			if v not in meter_dict:
				meter_dict[v] = 1
			else:
				meter_dict[v] += 1
		else:
			v = tuple(v)
			if v not in meter_dict:
				meter_dict[v] = 1
			else:
				meter_dict[v] += 1
	#return meter_dict
	m = max(meter_dict, key=meter_dict.get)
	return 'I think this poem is in ' + m + '.\n\n' + 'Based on this list: ' + str(meter_dict)



def name_meter(stress):
	if stress == '':
		return ''

	else:
		feet = {}
		length = {}
		feet['iambic'] = 0
		feet['trochaic'] = 0
		feet['anapestic'] = 0
		feet['dactylic'] = 0
		length[1] = 'monometer'
		length[2] = 'dimeter'
		length[3] = 'trimeter'
		length[4] = 'tetrameter'
		length[5] = 'pentameter'
		length[6] = 'hexameter'
		length[7] = 'heptameter'
		length[8] = 'octameter'
		length[9] = 'enneameter'
		for i,s in enumerate(stress):
			z = i+1
			if i > 2 and s == '0' and z % 3 == 0 and stress[i-1] == '0' and stress[i-2] == '1':
				feet['dactylic'] += 1

			elif i > 2 and s == '1' and z % 3 == 0 and stress[i-1] == '0' and stress[i-2] == '0':
				feet['anapestic'] += 1

			elif i < len(stress)-1 and i % 2 == 0 and s == '0' and stress[i+1] == '1':
				feet['iambic'] += 1

			elif i < len(stress)-1 and i % 2 == 0 and s == '1' and stress[i+1] == '0':
				feet['trochaic'] += 1



		highest = max(feet.values())

		bestFeet = [k for k,v in feet.items() if v == highest]

		names = []
		for bf in bestFeet:
			if bf == 'iambic' or bf == 'trochaic':
				numberOfFeet = len(stress) / 2

			elif bf == 'anapestic' or bf == 'dactylic':
				numberOfFeet = len(stress) / 3

			try:
				names.append(bf + ' ' + length[numberOfFeet])
			except KeyError:
				names.append('Unknown: probably too many syllables')


		if len(names) == 1:
			return names[0]

		elif len(names) == 4:
			return "Unsure of metrical foot (Spondaic!)"

		else:
			orNames =[]
			for n in names:
				orNames.append(n)

			return orNames


def create_scansion_list(input):
	scansion_list = []
	if input.endswith('.txt'):
		lines=codecs.open(input, 'r', 'utf-8').readlines()
		all_meter = []
		for line in lines:
			st = stressByLine(line)
			meter = name_meter(st)
			all_meter.append(meter)
			scansion_list.append(st + ' ' + str(meter) + '\n')
		scansion_list.append('Total number of lines: '+str(len(lines)) + '\n')
		scansion_list.append(find_meter(all_meter) + '\n')
	elif input.endswith('/'):
		files=glob.glob(input+'*.txt')
		all_lines=[]
		all_meter = []
		for f in files:
			lines=codecs.open(f, 'r', 'utf-8').readlines()
			all_lines.extend(lines)
			scansion_list.append(f)
			for line in lines:
				s=stressByLine(line)
				meter = name_meter(s)
				all_meter.append(meter)
				scansion_list.append(s + ' ' + str(meter) + '\n')
		scansion_list.append('Total number of lines: '+str(len(all_lines)) + '\n')
		scansion_list.append(find_meter(all_meter) + '\n')
	else:
		print "Input must be a .txt file, or a directory ending with '/'."
	return scansion_list

sl = create_scansion_list(i)

with open(output, 'wb') as scansionfile:
	scansionfile.writelines(sl)
