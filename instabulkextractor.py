import os
import csv
import re
import argparse
import requests
import time
from pyfiglet import Figlet
from igramscraper.instagram import Instagram

def printBanner():
        text = "insta bulk extractor"
        f = Figlet(font="slant")
        print('\n'*1)
        print(f.renderText(text))

def setProxies(instagram, http, https=False):
        proxies = {'http' : http}
        if https:
                proxies[https] = https
        instagram.set_proxies(proxies)        
def loginInstagram(instagram, path):
        abs_src = os.path.abspath(path)
        loginDetails=[]
        #Read File
        with open(abs_src) as f:   
                loginDetails = f.read().splitlines() 
        f.close()
        user = loginDetails[0]
        passw = loginDetails[1]
        try:
                instagram.with_credentials(user, passw)
                instagram.login()
                return True
        except: 
                return False

def readKeywordList(path):
        abs_src = os.path.abspath(path)
        keywordList = []
        #Read File
        with open(abs_src) as f:   
                keywordList = f.read().splitlines() 
        f.close()
        return keywordList

def exactAccountSearch(instagram, keywordList):
        #Get details from account found
        accountList =[]
        for keyword in keywordList:
                try: 
                        account = instagram.get_account(keyword)
                        accountList.append(account)
                except:
                        accountList.append("not Found")
        return accountList

def broadAccountSearch(instagram, keywordList):
       #Search for accounts matching keyword
        keywordresults = dict()
        for keyword in keywordList:
                accountList = instagram.search_accounts_by_username(keyword)
                keywordresults[keyword] = accountList
        accountList =[]
        #Get details from account found
        for key in keywordresults:
                for x in range(len(keywordresults.get(key))): 
                        account = instagram.get_account(keywordresults.get(key)[x].username)
                        accountList.append(account)
        return accountList
                
def downloadMedia(instagram, amountOfMedia, accountList, outputDir):
    for account in accountList:
            mediaList = False  
            try:
              mediaList = instagram.get_medias(account.username, amountOfMedia)
            except:
                  pass
            if mediaList:
                    path = outputDir + "/" + account.username
                    try:
                        os.mkdir(path)
                    except:
                        pass
                    for media in mediaList:
                        if media.type == "video":
                                destinationPath = path + "/" + media.identifier + ".mp4"
                                downloadPictureFromURL(media.video_standard_resolution_url, destinationPath)
                        else:   
                                destinationPath = path + "/" + media.identifier + ".png"
                                downloadPictureFromURL(media.image_high_resolution_url, destinationPath)

def downloadPictureFromURL(url, destinationPath):
        response = requests.get(url)

        file = open(destinationPath, "wb")
        file.write(response.content)
        file.close()

def printDetailsCSV(accountList, outputDir):
        import time
        timestr = time.strftime("%Y%m%d-%H%M%S")

        abs_src = outputDir + "/results_"+ timestr+ ".csv"
        with open(abs_src, 'w', newline='') as myfile:
                        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                        wr.writerow(["identifier","username","full_name","biography","profile_picture_url","external_url","media_count","followed_by_count","follows_count","is_private","is_verified", "phonenumber_in_bio"])
                        for x in range(len(accountList)):     
                                account = accountList[x]
                                if not isinstance(account, str):
                                        record = [account.identifier,account.username, account.full_name, account.biography, account.get_profile_picture_url(), account.external_url, account.media_count, account.followed_by_count, account.follows_count,  account.is_private, account.is_verified, findDutchPhoneNumber(account.biography)]
                                else:
                                        record = account
                                wr.writerow(record)
        myfile.close()

def findDutchPhoneNumber(string):
        # ^((\+|00(\s|\s?\-\s?)?)31(\s|\s?\-\s?)?(\(0\)[\-\s]?)?|0)[1-9]((\s|\s?\-\s?)?[0-9])((\s|\s?-\s?)?[0-9])((\s|\s?-\s?)?[0-9])\s?[0-9]\s?[0-9]\s?[0-9]\s?[0-9]\s?[0-9]$
        result = re.findall("([0]{1}[6]{1}[-\s]*[1-9]{1}[\s]*([0-9]{1}[\s]*){7})|([0]{1}[1-9]{1}[0-9]{1}[0-9]{1}[-\s]*[1-9]{1}[\s]*([0-9]{1}[\s]*){5})|([0]{1}[1-9]{1}[0-9]{1}[-\s]*[1-9]{1}[\s]*([0-9]{1}[\s]*){6})",string)
        try:
                result = result[0][0]
        except:
                pass
        
        return result
#################################################### ARG PARSING #########################################################################
parser = argparse.ArgumentParser(description='Scrape instagram for user information and media')
parser.add_argument('-l', '--login', required=True, metavar='PATH',help='specify the absolute file path containing login.txt (first line username, second line password')
parser.add_argument('-i', '--input', required=True, metavar='PATH',help='specify the absolute file path containing accountnames/keywords')
typesearch = parser.add_mutually_exclusive_group()
typesearch.add_argument('-e', '--exact', action="store_true", help='retrieve info from account matching exact keyword (keword kevin finds the one account kevin)')
typesearch.add_argument('-b', '--broad', action="store_true", help='retrieve info from all accounts found by keyword (keyword kevin finds all kevins)')
parser.add_argument('-o', '--output', required=True, metavar='PATH',  help='specify the absolute path to output directory for the extracted information and media')
parser.add_argument('-m', "--media", type=int, metavar='AMOUNT', help='extract given amount of media from found accounts')
parser.add_argument('-p', "--proxy", metavar='ADDR', help='specify http proxy adress: http://ip-address')
parser.add_argument('-ps', "--proxysecure", metavar='ADDR', help='specify https proxy adress: https://ip-address can either use -p or -ps or both')

def Main ():
        printBanner()
        args = parser.parse_args()
        if not (args.exact or args.broad):
                parser.error('Add search method --exact or --broad')

        instagram = Instagram()
        if loginInstagram:
                if args.proxy:
                        setProxies(instagram, args.proxy)

                inputFile = args.input
                outputDir = args.output
                print("Read inputfile")
                keywordList = readKeywordList(inputFile)

                print("Fetch Accounts")
                if args.broad:
                        accountlist = broadAccountSearch(instagram, keywordList)
                if args.exact:
                        accountlist = exactAccountSearch(instagram, keywordList)

                print("print account details to CSV")
                printDetailsCSV(accountlist, outputDir)
                if args.media: 
                        print("Fetch Media")
                        downloadMedia(instagram, args.media, accountlist, outputDir)       
        else: 
                print("problems with login")
        print("Finished")

if __name__ == '__main__':
        Main()
  



