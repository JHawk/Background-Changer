#!/usr/bin/python

import urllib
import htmllib
from htmllib import HTMLParser
from xml.dom import minidom
import xml.parsers.expat
import time, string, sys
import os
import libxml2dom
import re
import time
import datetime

##
## FUNCTIONS
##

def archiveOldImages():
    global imageDir
    files = os.listdir(imageDir)
    
    t = time.mktime(datetime.datetime.now().timetuple())
    print "Archiving images older than ", datetime.datetime.now() + datetime.timedelta(hours=-1)
   
    for file in files:
        fileInfo = os.stat(imageDir + file)
        if fileInfo[8] < (t - 3600):
            os.remove(imageDir + file)

def download(url):
    # download the home page and read it to a string
    print "Trying to download " + url
    try:
        stream = urllib.urlopen(url)
        try:
            return stream.read()
        finally:
            stream.close()

    except IOError:
        print "Could not read stream, attempt ", attempts, "; retrying "
        time.sleep(3)

        checkAttempts()
        return download(url)

def parse(url):
    #parse out the uri for the first recent image
    html = download(url)    
    try:
        return libxml2dom.parseString(html, html=1)
    
    except TypeError, detail:
        print detail
        print "Could not parse document, attempt ", attempts, "; retrying "
        return parse(url)

    
def checkAttempts():
    global attempts
    attempts = attempts - 1
    if attempts < 1:
        print "Exceeded max attempts, quitting"
        sys.exit()

def getThirdImageB():
    
    # get a list of images
    dom = parse("http:/site_of_interest_imgboard/html")
    imglist = dom.getElementsByTagName("img")

    # remove the first two elements
    imglist.reverse()
    imglist.pop()
    imglist.pop()
    imglist.reverse()
    
    # try each image until we get one that works
    for image in imglist:
                
        # download the image
        imgUrl = image.getAttribute("src")
        imgFile = downloadAndWriteImage(imgUrl)

        if (imgFile != ""):
            return imgFile
        
    # retry to download a new page if no images work
    return getThirdImageB()

def downloadAndWriteImage(imgUrl):
    print "Image " + imgUrl + " found"

    # find the image from the thumbnail
    imgUrl = imgUrl.replace("/thumb", "/src").replace("s.", ".")
    
    # get the image filename
    imagePattern = re.compile("[0-9][0-9]+\.(jpg|gif)")
    imgMatch = imagePattern.search(imgUrl)
    try:
        imgFile = imgMatch.group()
    except AttributeError:
        print "Cannot determine file type of " + imgUrl
        return ""
    
    # download file
    image = download(imgUrl)
    
    # Make sure the image isnt a file not found page and then write to disc
    if checkImage(image):
            
            global imageDir
            print "Success"
            file = open(imageDir + imgFile, "w")
            file.write(image)
            file.close()
            
            return imgFile 
    
    # return an empty string if the check fails
    return ""


def checkImage(img):
    #Try to parse as xml - if false then return true except return false
    try:
        minidom.parseString(img)
        print "Found 404 Image ERROR...Trying next image."
        return False

    except:    
        return True

def changeWallpaper(filename):
    global imageDir
    cmd = string.join(["gconftool -s /desktop/gnome/background/picture_filename -t string \"", imageDir, filename,"\""],'')
    print cmd
    os.system(cmd)

##
## MAIN SCRIPT
##
attempts = 10
imageDir = "/home/josh/Pictures/bBackground/"

archiveOldImages()
image = getThirdImageB()
changeWallpaper(image)


