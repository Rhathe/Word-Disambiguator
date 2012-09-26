#Word Disambiguation for NLP
#Ramon Sandoval

import re, os, string, math, operator, nltk
import itertools
from nltk.corpus import wordnet as wn
from nltk.tokenize import *

#tokenize based on alphanumeric, dashes, underscores, and periods
tokenizer = RegexpTokenizer('[a-zA-Z0-9\.\-\_\']+')

#Use nltk's default stop list
stop = nltk.corpus.stopwords.words('english')

#Number of words to left or right of word to check against for senses. Since it checkes both sides,
#total number of words checked is 2*surNum
surNum = 6

#Points given to a match in words in both dictionaries of senses
glossValue = 0.1

#Get the accuracy by total amount right divided by total number of words tagged
#Returns amount right, amount of words, and acuracy
def getStats(testName,resultName):
	testfp = open(testName, 'rb')
	resultfp = open(resultName, 'rb')
		
	testData = testfp.read()
	resultData = resultfp.read()
		
	right = 0
	count = 0
	for a,b in itertools.izip(testData,resultData):
		count += 1
		if a == b:
			right += 1
		
	acc = [right,count,right/(count*1.0)]
	return acc

#Clean the xml data
def removeTags(data):
	p = re.compile('<wf cmd=ignore.*</wf>\n')
	ignoreData = p.sub('',data)
	p = re.compile('<punc>.*</punc>\n')
	ignoreData = p.sub('',ignoreData)
	p = re.compile('<wf.*ot.*>.*</wf>\n')
	ignoreData = p.sub('',ignoreData)
	p = re.compile('<p.*>\n')
	ignoreData = p.sub('',ignoreData)
	p = re.compile('</p.*>\n')
	ignoreData = p.sub('',ignoreData)
	p = re.compile('<s.*>\n')
	ignoreData = p.sub('',ignoreData)
	p = re.compile('</s.*>\n')
	ignoreData = p.sub('',ignoreData)
	p = re.compile('<c.*>\n')
	ignoreData = p.sub('',ignoreData)
	p = re.compile('</c.*>\n')
	ignoreData = p.sub('',ignoreData)
	p = re.compile('<.*?>')
	return p.sub('', ignoreData)

#Get sense key data from tagged words
def getID(data):
	ids = re.findall('lexsn=[^ >]+', data)
	newIDs = re.sub('lexsn=','','\n'.join(ids))
	return newIDs

#Get score of how many words in two sense's dictionaries match
def glossRelatedness(a,b):
	score = 0
	aDef = tokenizer.tokenize(a.definition)
	aDef = [w for w in aDef if w not in stop]
	bDef = tokenizer.tokenize(b.definition)
	bDef = [w for w in bDef if w not in stop]

	for c in aDef:
		for d in bDef:
			if c == d:
				score += glossValue
	return score


#Get Similarity Scores For Two Synsets
def twinTest(aa,bb,score):
	if bb == "notag":
		return
	for i in range(len(aa)):
		for b in bb:
			value = aa[i].path_similarity(b)
			if value:
				score[i] += value
			score[i] += glossRelatedness(aa[i],b)

#Get Overall Score for a Synset
def scoreIt(synList):
	indexList = [-1]*len(synList)
	for i in range(len(synList)):
		if synList[i] == "notag":
			indexList[i] = "notag"
			continue
		score = [1]*len(synList[i])
		if i:
			jIter = min(i,surNum)
			for j in range(jIter):
				twinTest(synList[i],synList[i-(j+1)],score)
		k = (len(synList)-1)-i
		if k:
			jIter = min(k,surNum)
			for j in range(jIter):
				twinTest(synList[i],synList[i+(j+1)],score)
		if score:
			indexList[i] = score.index(max(score))
	return indexList

#----------------------------------------------------------------------
										
fileOrInput = raw_input("Enter file? (Y/N)(Default to Y): ")
fpName = "blah"
sentence = 0

if not (fileOrInput == 'N' or fileOrInput == 'n'):
	fpName = raw_input("Please enter input file name: ")
else:
	sentence = raw_input("Enter a sentence: ")


#----Default files if nothing is entered---
if not fpName:
	fpName = './semcor1.6/brown1/tagfiles/br-a01'
#------------------------------------------
	
data = "blah"

#File for the the cleaned pre-determined sense-key tags
test = open('test', 'wb')

#File for the result of the function
result = open('result', 'wb')

if not (fileOrInput == 'N' or fileOrInput == 'n'):
	fp = open(fpName, 'rb')
	data = fp.read()
	test.write(getID(data))
	data = removeTags(data)
else:
	data = sentence

tokens = tokenizer.tokenize(data)
text = nltk.Text(tokens)
words = [w.lower() for w in text]
#posWords = nltk.pos_tag(words)
#print posWords

synList = []

#Check if words are in WordNet corpus
for a in words:
	tempSynset = wn.synsets(a)
	if not tempSynset:
		tempSynset = "notag"
	synList.append(tempSynset)

indexList = scoreIt(synList)

#Write results to file and/or terminal
p = re.compile('[^%]*%')
for i in range(len(words)):
	a = words[i]
	b = synList[i]
	c = indexList[i]
	print a
	
	if c == "notag":
		s = "notag"
		result.write(s+"\n")
		print s
	elif not c == -1:
		s = b[c].lemmas[0].key
		result.write(p.sub('', s)+"\n")
		print s
		print b[c].name + ": " + b[c].definition

	print "\n"

result.close()
test.close()

if not sentence:
	print getStats('test','result')

