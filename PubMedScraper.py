import bs4 as bs
import ssl
import time
import http.client
import numpy as np
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.patches as mplpatches
import pickle
import socket
from scipy import stats


wordDic = {}
yearsCount = {}
for year in range(2000,2020):
    wordDic[year] = {}
    yearsCount[year] = 0
pmIDlow = 10000052 #12000000 post 2005
pmIDhigh = 29549155
wordSaveName = 'WebscraperWordDic91.p'
yearSaveName = 'WebscraperYearDic91.p'
pmidSaveName = 'WebscraperPmidList91.p'
displayFrequency = 10
numOfTitles = 50000
hitsThreshold=3

print(wordSaveName)
start = time.time()
print(time.ctime(start))
ssl._create_default_https_context = ssl._create_unverified_context
articleList = ["a","an", "the", "on","and","of","in", "of","as", "at", "is", "its",
               "for",'pubmed',"from", "by","with", "to", "\n","the","is","we",
               "using","or","are","1","2","-"]
unhelpfulWords = ['effects','against','analysis','case','de','study',
                  'study','following','during','cells',
                  'cell','use','effect','via','not','two','after','among']

"""
Parse Links
"""
# below2000TestList = []
pmidList = []
# masterPmidList = []
# # masterPmidList = pickle.load(open('masterPmidList.p', 'rb'))
# masterWordDic={}
# # masterWordDic = pickle.load(open('masterWordDic.p', 'rb'))
# masterYearDic = {}
# # masterYearDic = pickle.load(open('masterYearDic.p', 'rb'))
# hotWordDic={}
wordYearDic = {}
not21centuryCount = 0
futureYearCount = 0
attempts = 0
noPage = 0
count = 0

def scrape():
    global count, not21centuryCount, futureYearCount, attempts, noPage
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
        except socket.timeout as error:
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
            titleWordSet = set(scrapeTitle.lower().strip('".:,()[]-+').split(' '))
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


def compileWords(minFileNum, maxFileNum):
    global masterWordDic
    fileNameRoot = "WebscraperWordDic"
    for number in range(minFileNum, maxFileNum+1):
        fileName = fileNameRoot + str(number) + '.p'
        print(fileName, "is being merged with masterWordDic")
        # print("masterWordDic length = ", len(masterWordDic))
        newDic = pickle.load(open(fileName, 'rb'))
        for wordKey,numberValue in newDic.items():
            if wordKey in masterWordDic.keys():
                masterWordDic[wordKey] = list(np.add(masterWordDic[wordKey], newDic[wordKey]))
                # print("word number added")
                continue
            elif wordKey not in masterWordDic.keys():
                masterWordDic[wordKey]=newDic[wordKey]
                # print("new word added")
        # print("masterWordDic length = ", len(masterWordDic))
        pickle.dump(masterWordDic, open('masterWordDic.p', "wb"))

def compileYears(minNum, maxNum):
    global masterYearDic
    fileNameRoot = "WebscraperYearDic"
    for number in range(minNum, maxNum+1):
        fileName = fileNameRoot + str(number) + '.p'
        # print(fileName, "is being merged with masterYearDic")
        # print("masterYearDic length = ", len(masterYearDic))
        newYearDic = pickle.load(open(fileName, 'rb'))
        for key, value in newYearDic.items():
            if key in masterYearDic.keys():
                masterYearDic[key] += newYearDic[key]
            elif key not in masterYearDic.keys():
                masterYearDic[key] = newYearDic[key]
    pickle.dump(masterYearDic, open('masterYearDic.p', 'wb'))


def compilePmid(minNum, maxNum):
    global masterPmidList
    fileNameRoot = "WebscraperPmidList"
    for number in range(minNum,maxNum+1):
        fileName = fileNameRoot + str(number) + '.p'
        # print( fileName, "is being merged with masterPmidList")
        # print("masterPmidList length= ", len(masterPmidList))
        newPmidList = pickle.load(open(fileName, 'rb'))
        for pmid in newPmidList:
            masterPmidList.append(pmid)
    print("Final pmid length with dups= ", len(masterPmidList))
    print("Final pmid length without dups = ", len(set(masterPmidList)))
    pickle.dump(masterPmidList, open('masterPmidList.p', 'wb'))



# Year Histogram Graphing
def yearHistoGraph():
    yearsCount = pickle.load(open('masterYearDic.p', 'rb'))
    x_pos = 0
    yearCountMax = max(yearsCount.values()) #used for finding max y axis value
    totalCount = 0
    for yearKey in sorted(yearsCount.items(), key=lambda t: t[0]):
        totalCount += yearKey[1]
        rectangle=mplpatches.Rectangle([x_pos,0],1,yearKey[1],facecolor='blue', edgecolor='yellow',linewidth=0.3)
        yearHisto.add_patch(rectangle)
        x_pos+=1

    yearHisto.set_xlim(0,19) #only graphing 2000s years
    yearHisto.set_xticks([0.5,3.5,6.5,9.5,12.5,15.5,18.5])
    yearHisto.set_xticklabels(['2000','2003','2006','2009','2012','2015','2018'], size=7)
    yearHisto.set_xlabel("Year")
    yearHisto.set_ylim(0,yearCountMax) #(0,y_pos)
    yearHisto.set_yticks([10000,20000,30000,40000,50000,60000,70000,80000,90000,100000,110000,120000,130000,140000])
    yearHisto.set_yticklabels(['10k','20k','30k','40k','50k','60k','70k','80k','90k','100k','110k','120k','130k','140k'], size=6)
    yearHisto.set_ylabel("Number of titles scraped")
    yearHisto.tick_params(axis='both', which='both',\
                       bottom=True, labelbottom=True,\
                       left=True, labelleft=True,\
                       right=False, labelright=False,\
                       top=False, labeltop=False)
    yearHisto.set_title(str("{:,}".format(totalCount))+" titles Scraped")
    # plt.savefig('WebscraperGraph2.png')



# Heatmap Graphing
def heatmapGraph():
            #start, stop, number of values
    R=np.linspace(255/255,56/255,101)
    G=np.linspace(225/255,66/255,101)
    B=np.linspace(40/255,157/255,101)  #100 entry list between 0 and <1
    y_pos=0
    normDicList = {}
    sortNormDicList = {}
    hotWordList = []
    yearList = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    excludeList = ['-', 'impact']
    includeList = []#'crispr','kras', 'acid', 'rat','mouse', 'single', 'exercise', 'p53','brain','heart']
    regressionLimits=0.98
    minHitCount = 200
    testCount = 0

    for key in masterWordDic.keys(): # go through keys
        # testCount += 1
        # if testCount == 500:
        #     break
        if key not in includeList:
            tempList = masterWordDic[key]
            slope, intercept, r_value, p_value, std_err = stats.linregress(yearList[10:17], tempList[10:17])
            if (max(masterWordDic[key]) < minHitCount) or (key in excludeList) or (-regressionLimits<r_value <regressionLimits):
                continue
        hotWordDic[key] = masterWordDic[key]
        print(key, hotWordDic[key])
    for key, value in sorted(hotWordDic.items(),key=lambda i:sum(i[1])):
        print (key, value)
        tempList = masterWordDic[key]
        sortNormDicList[key] = list(((tempList-min(tempList))/(max(tempList)-min(tempList)))*100)
        wordCount = sum(masterWordDic[key])
        hotWordList.append(str(key)+' '+ str("{:,}".format(wordCount)))
    for graphWord in sortNormDicList.keys():
        x_pos=0
        for point in sortNormDicList[graphWord]: #year wordcount list, normalized 1-100
                                            # xy, width, height,
            rectangle=mplpatches.Rectangle([x_pos,y_pos],1,1,facecolor=(R[int(point)],G[int(point)],B[int(point)]),linewidth=0.1)
            heatmap.add_patch(rectangle)
            x_pos+=1
        y_pos+=1

    yTickList = np.arange(0.5, (len(hotWordList)+0.5))
    heatmap.set_xlim(0,18)
    heatmap.set_xticks([0.5,2.5,4.5,6.5,8.5,10.5,
                       12.5,14.5,16.5])
    heatmap.set_xticklabels(['2000','2002','2004','2006',
                            '2008','2010','2012','2014',
                            '2016'],size=8)
    heatmap.set_xlabel("Year")
    heatmap.set_ylim(0,len(hotWordDic)) #(0,y_pos)
    heatmap.set_yticks(yTickList)
    heatmap.set_yticklabels(hotWordList, size =6)
    heatmap.set_ylabel("Words, total count")
    heatmap.tick_params(axis='both', which='both',\
                       bottom=True, labelbottom=True,\
                       left=True, labelleft=True,\
                       right=False, labelright=False,\
                       top=False, labeltop=False)
    heatmap.set_title("Normalized word frequency by year\n"+"words found > "+str(minHitCount)+" times and have regerssion R of >|"+str(regressionLimits)+"|")


def runStats():
    end = time.time()
    print(time.ctime(end), ", runtime was " + str(float(int((end - start)/6))/10) + " minutes")
    print("\n")
    if futureYearCount != 0:
        print("Future years: ", futureYearCount)
    # print("NoPage Error: ", noPage,"Pre-2000: ", not21centuryCount)
    # print("Found "+ str(count) + " titles out of " + str(attempts) + " attempts")
    # print(str(len(hotWordDic))+" words appeared at least "+str(hitsThreshold)+" times")
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

def main():

    # scrape()
    # compileWords(1,90)
    # compilePmid(1,90)
    # compileYears(1,90)
    # test = pickle.load(open('masterYearDic.p', 'rb'))
    # print(test)
    yearHistoGraph()
    heatmapGraph()
    plt.savefig('WebscraperGraph3.png')
    runStats()

masterPmidList = []
# masterPmidList = pickle.load(open('masterPmidList.p', 'rb'))
# masterWordDic = {}
masterWordDic = pickle.load(open('masterWordDic.p', 'rb'))
# masterYearDic = {}
masterYearDic = pickle.load(open('masterYearDic.p', 'rb'))
hotWordDic = {}
# plt.style.use('BME163.mplstyle')
figWidth=11
figHeight=6     #absolute values in inches
plt.figure(figsize=(figWidth, figHeight)) #Width and Height
panel_width=4/figWidth  #relative to figWidth, in inches
panel_height=4.7/figHeight
heatmap=plt.axes([0.15, 0.1, panel_width, panel_height], frameon=True)
                #left, bottom, width, height
yearHisto=plt.axes([0.65, 0.1, panel_width/1.3, panel_height/1.3], frameon=True)
                #left, bottom, width, height

main()
