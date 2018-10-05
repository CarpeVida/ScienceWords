import bs4 as bs
import ssl
import time
import http.client
import numpy as np
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.patches as mplpatches
import pickle

wordDic = {}
yearsCount = {}
for year in range(2000,2020):
    wordDic[year] = {}
    yearsCount[year] = 0
pmIDlow = 10000052 #12000000 post 2005
pmIDhigh = 29549155
wordSaveName = 'WebscraperWordDic8kh.p'
yearSaveName = 'WebscraperYearDic8kh.p'
pmidSaveName = 'WebscraperPmidList8kh.p'
displayFrequency = 20
numOfTitles = 8000
hitsThreshold=3
    #27,9,12,13 words >2 at 100 titles in 3,4,4m
    #1,1 word >3 at 100 title in 3,3m
    #1,3,6 words >3 at 200 titles in 6m
    #65 words >2 at 200 titles
    # 3 w >3 at 300t in 8m
    #17w >3 at 400t in 11m
    #23,21 words >3 at 500 titles in 12,12m
    #22,14 w >3 at 500t in 20m while running two programs
    #55 words >3 at 1000 titles
    #31 words >4 at 1000 titles, #super nice display number
    #9 w >6 at 1000 titles in 23m
    #49 >6 at 2000 t in 51m, 66m double, 67double
    #54 >8 at 3000 t in 100m
    #273 w >6 at 6000 titles in 197m
    #x w > x at 6000 titles in 210m and 211m double process

# plt.style.use('BME163.mplstyle')
figWidth=7
figHeight=4     #absolute values in inches
plt.figure(figsize=(figWidth, figHeight)) #Width and Height
panel_width=3/figWidth  #relative to figWidth, in inches
panel_height=3/figHeight
heatmap=plt.axes([0.15, 0.1, panel_width, panel_height], frameon=True)
                #left, bottom, width, height
yearHisto=plt.axes([0.65, 0.1, panel_width/1.3, panel_height/1.3], frameon=True)
                #left, bottom, width, height

start = time.time()
print(time.ctime(start))
ssl._create_default_https_context = ssl._create_unverified_context
articleList = ["a","an", "the", "on","and","of","in", "of","as", "at", "is", "its",
               "for",'pubmed',"from", "by","with", "to", "\n","the","is","we",
               "using","or","are","1","2"]
unhelpfulWords = ['effects','against','analysis','case','de','study',
                  'study','following','during','cells',
                  'cell','use','effect','via','not','two','after','among']


"""
#for search results
for paragraph in soup.find_all('a'):
    # print(paragraph.string)
    count+=1
    if count < 220 or count > 270:
        continue
    else:
        asciiText = paragraph.text.encode('ascii', 'ignore') #converts ASCii to string
        if asciiText == 'Similar articles' or "Free" in asciiText:
            continue
        else:
            wordList = asciiText.split(' ')
            # print(type(asciiText))
            for word in wordList:
                if word not in articleList and word in wordDic:
                    wordDic[word] += 1
                else:
                    wordDic[word] = 0
            # print(asciiText)
            # sortedFreqList = sorted(wordDic, key=lambda wordDic:wordDic[1])
sorted_list = sorted(wordDic.items(), key=itemgetter(1))
print(sorted_list)


            # print()
            # print(count)

#for pasting text files

for line in fileinput.input():
    count += 1
    wordList = line.split(' ')
    if count > 5001:
        break
        print("FREEE MEEE")
    for word in wordList:
        if word == "STOP":
            break
        if word not in articleList and word in wordDic:
            wordDic[word] += 1
        else:
            wordDic[word] = 0
    print(count)
sorted_list = sorted(wordDic.items(), key=itemgetter(1))
print(sorted_list)
"""
# url(Pubmed+str(num))
"""
Parse Links
"""
# below2000TestList = []
pmidList = []
masterPmidList = [] #pickle.load(open('masterPmidList.p', 'rb'))
hotWordDic={}
count = 0
wordYearDic = {}
not21centuryCount = 0
futureYearCount = 0
attempts = 0
noPage = 0
while count < numOfTitles:
    num = np.random.randint(pmIDlow,pmIDhigh)
    if num in masterPmidList:
        continue
    attempts += 1
    t0 = time.time()
    linkText = "https://www.ncbi.nlm.nih.gov/pubmed/" + str(num)
    #goes through pubmed papers and returns a dictionary of titles
    #Nature probably works too: https://www.nature.com/articles/ncomms15690
    try:
        sauce = urllib.request.urlopen(linkText).read()
        soup = bs.BeautifulSoup(sauce, 'lxml')
    except (http.client.IncompleteRead, urllib.error.HTTPError,urllib.error.URLError) as error:
        if "HTTP" in str(error):
            noPage += 1
        if noPage%displayFrequency == 0:
            print(error)
        continue

    """
    Parse Years
    """
    year = 0
    for divText in soup.find_all('div', class_="cit"):
        yearString = str(divText.text)
        try:#to catch non-year characters or pre-1900 years
            yearStringIndex = yearString.find('20') #if not found, = -1
            if yearStringIndex != -1: #20 found
                year = int(yearString[yearStringIndex:yearStringIndex+4])

                if 2019> year > 1999: #Triggers type error if Weird character
                    yearsCount[year] += 1
                    break
                else: #20 item valid number, but not in year range
                    # year = 13
                    not21centuryCount += 1
                    break
                    # yearStringIndex = yearString.find('19') #check for '19'
                    # year = int(yearString[yearStringIndex:yearStringIndex+4])
            elif yearStringIndex == -1: #no '20' found, probably 1900s
                # year = 1900
                not21centuryCount += 1
                break
                # yearStringIndex = yearString.find('19') #check for '19'
                # year = int(yearString[yearStringIndex:yearStringIndex+4])
                # below2000TestList.append(yearString)
        except(TypeError): #non int parsable character found
                    # year = 1
                    not21centuryCount += 1
                    break
        except(ValueError, IndexError):  #20 found, weird character
            year = 0
            break
    # if year<2000:
    #     below2000TestList.append(year)
    #     not21centuryCount += 1
        # if year not in yearsCount:
        #     yearsCount[year]=1
        # elif year in yearsCount:
        #     yearsCount[year]+=1
        # continue
    if year>2019:
        futureYearCount += 1
        continue
    if not 2020>year>1999:
        continue
        # print(yearsCount)
    """
    Parse Titles
    """
    for paragraph in soup.find_all('h1'):
        scrapeTitle = paragraph.text  #converts byte tag to string
        titleWordSet = set(scrapeTitle.lower().strip('.:,()[]-+').split(' '))
            #set prevents duplicate word saves
            #case insensitive, remove weird characters
        if "pubmed" in titleWordSet: #skips pubmed title line
            continue
        if count%displayFrequency==0:
            print(count, linkText)
        count+=1
        pmidList.append(num)
        for word in titleWordSet:
            if word not in articleList and word not in unhelpfulWords:
                try:
                    if word in wordDic[year]:
                        wordDic[year][word] += 1
                        wordYearDic[word][year-2000] += 1
                        if sum(wordYearDic[word])>=hitsThreshold:
                                    hotWordDic[word] = wordYearDic[word]
                    else:
                        wordDic[year][word] = 1
                        wordYearDic[word] = [0]* 20
                        wordYearDic[word][year-2000] += 1
                except(KeyError): #year not in wordDic, pre-2000
                    # below2000TestList.append(yearString)
                    # below2000TestList.append(year)
                    break
            else:
                continue
    if count%(displayFrequency*5) ==0:
        elapsed = (time.time() - t0)
        pickle.dump(wordYearDic, open(wordSaveName, "wb+"))
        pickle.dump(yearsCount, open(yearSaveName, "wb+"))
        pickle.dump(pmidList, open(pmidSaveName, "wb+"))
        print((elapsed),"sec for this link")
"""
"""
# Year Histogram Graphing
"""
normHotDic = {}
x_pos = 0
yearCountMax = max(yearsCount.values()) #used for finding max y axis value
for yearKey in sorted(yearsCount.items(), key=lambda t: t[0]):
    rectangle=mplpatches.Rectangle([x_pos,0],1,yearKey[1],facecolor='blue', edgecolor='yellow',linewidth=0.3)
    yearHisto.add_patch(rectangle)
    x_pos+=1

yearHisto.set_xlim(0,19) #only graphing 2000s years
yearHisto.set_xticks([0.5,2.5,4.5,6.5,8.5,10.5,12.5,14.5,16.5,18.5])
yearHisto.set_xticklabels(['2000','2002','2004','2006','2008','2010','2012','2014','2016','2018'], size=7)
yearHisto.set_xlabel("Year")
yearHisto.set_ylim(0,yearCountMax) #(0,y_pos)
yearHisto.set_ylabel("Number of titles scraped")
yearHisto.tick_params(axis='both', which='both',\
                   bottom='on', labelbottom='on',\
                   left='on', labelleft='on',\
                   right='off', labelright='off',\
                   top='off', labeltop='off')

"""
# Heatmap Graphing
"""
            #start, stop, number of values
R=np.linspace(255/255,56/255,101)
G=np.linspace(225/255,66/255,101)
B=np.linspace(40/255,157/255,101)  #100 entry list between 0 and <1
y_pos=0
normDicList = {}
hotWordList = []
for key in hotWordDic.keys(): # go through keys
    tempList = np.array(hotWordDic[key])
    hotWordList.append(key)
    normDicList[key] = list(((tempList-min(tempList))/(max(tempList)-min(tempList)))*100)
    x_pos=0
    for point in normDicList[key]: #year wordcount list, normalized 1-100
        # print(point)
                                        # xy, width, height,
        rectangle=mplpatches.Rectangle([x_pos,y_pos],1,1,facecolor=(R[int(point)],G[int(point)],B[int(point)]),linewidth=0.1)
        heatmap.add_patch(rectangle)
        x_pos+=1
    y_pos+=1

yTickList = np.arange(0.5, (len(hotWordList)+0.5))
heatmap.set_xlim(0,19)
heatmap.set_xticks([0.5,2.5,4.5,6.5,8.5,10.5,
                   12.5,14.5,16.5,18.5])
heatmap.set_xticklabels(['2000','2002','2004','2006',
                        '2008','2010','2012','2014',
                        '2016','2018'],size=8)
heatmap.set_xlabel("Year")
heatmap.set_ylim(0,len(hotWordDic)) #(0,y_pos)
heatmap.set_yticks(yTickList)
heatmap.set_yticklabels(hotWordList)
heatmap.set_ylabel("Words")
heatmap.tick_params(axis='both', which='both',\
                   bottom='on', labelbottom='on',\
                   left='on', labelleft='on',\
                   right='off', labelright='off',\
                   top='off', labeltop='off')

plt.savefig('WebscraperGraphTest.png')
"""
end = time.time()
print(time.ctime(end), ", runtime was " + str(float(int((end - start)/6))/10) + " minutes")
print("\n")
if futureYearCount != 0:
    print("Future years: ", futureYearCount)
print("NoPage Error: ", noPage,"Pre-2000: ", not21centuryCount)
print("Found "+ str(count) + " titles out of " + str(attempts) + " attempts")
print(str(len(hotWordDic))+" words appeared at least "+str(hitsThreshold)+" times")
print(yearSaveName, wordSaveName)
print("\n")


# file = open("WebscraperOutput.txt", "w+")
# file.write("LowID: "+ str(pmIDlow) + " HighID: " +str(pmIDhigh) +" Titles: " + str(count)
#            + " Fails: " + str(attempts)+ " \n"+ str(orderedYearDic) +"\n "+ str(hotWordDic))
pickle.dump(wordYearDic, open(wordSaveName, "wb+"))
pickle.dump(yearsCount, open(yearSaveName, "wb+"))
pickle.dump(pmidList, open(pmidSaveName, "wb+"))


# file.close()
# //timestamp as filename
