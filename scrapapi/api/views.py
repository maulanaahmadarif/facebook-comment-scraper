from django.shortcuts import render, get_object_or_404
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import json
import time

from api.utils.helper import isValidURL
from api.utils.response import getResponse
from api.utils.scrape import commentScrap

def index(request):
  limit = None
  offset = 0
  reply = False
  url = None

  if 'limit' in request.GET:
    limit = int(request.GET['limit']) if request.GET['limit'].isnumeric() else None

  if 'offset' in request.GET:
    offset = int(request.GET['offset']) if request.GET['offset'].isnumeric() else 0

  if 'reply' in request.GET:
    reply = bool(request.GET['reply'] == 'true')

  if 'url' in request.GET:
    url = request.GET['url']
    if not isValidURL(url):
      context = {
        'message': 'url is not valid',
        'status': 400
      }
      response = getResponse(400, context)
      return response
  else:
    context = {
      'message': 'url is empty',
      'status': 400
    }
    response = getResponse(400, context)
    return response

  # DEPENDING ON OS YOU ARE WORKING,
  # PLEASE DOWNLOAD WEBDRIVER BASE ON OS
  # AND MAKE SURE THE VERSION IS MATCHING WITH
  # BROWSER VERSION YOU ARE WORKING
  # PLEASE FIND THE DETAIL OF WEBDRIVER INSTALATION BELOW
  # INSTALATION => https://www.selenium.dev/documentation/en/webdriver/driver_requirements/
  # CHROME => https://sites.google.com/a/chromium.org/chromedriver/downloads
  driver = webdriver.Chrome()

  driver.get(url)

  # REMOVE POPUP
  container = driver.find_element_by_class_name(u"_5hn6")
  driver.execute_script("arguments[0].style.display = 'none';", container)

  # CLICK SHOW COMMENT
  link = driver.find_element(By.CSS_SELECTOR, '.userContentWrapper ._3hg-')
  link.click()

  # WAIT TO FETCH THE COMMENT
  driver.implicitly_wait(20)

  # CLICK COMMENT FILTER SELECTION
  commentFilter = driver.find_element(By.CSS_SELECTOR, '._7a99._21q1._p')
  commentFilter.click()

  # WAIT
  driver.implicitly_wait(20)

  # SELECT ALL COMMENT
  selectAllComment = driver.find_elements(By.CSS_SELECTOR, '._54ni')[2]
  selectAllComment.click()

  # WAIT
  driver.implicitly_wait(20)

  # EXPAND ALL REMAINING COMMENT
  remainingComment = driver.find_element(By.CSS_SELECTOR, '._7a94._7a9d ._4sxc._42ft')
  remainingComment.click()

  # WAIT
  time.sleep(2)

  # SCROLL TO BOTTOM OF PAGE
  driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

  time.sleep(2)

  commentList = driver.find_elements(By.CSS_SELECTOR, 'ul._7a9a > li')

  datas = []

  idCounter = 1

  limit = len(commentList) if limit is None else limit

  if offset < len(commentList):
    for n in range(offset, (limit + offset)):

      if (n + 1) > len(commentList):
        break
      
      comment = {}

      cList = commentList[n]

      soup = BeautifulSoup(cList.get_attribute('innerHTML'), 'html.parser')

      id, author, date, text, attachment = commentScrap(soup, idCounter)

      comment['id'] = id
      comment['author'] = author
      comment['date'] = date
      comment['text'] = text
      comment['attachment'] = attachment

      commentReplyLink = soup.select_one("._4sxc._42ft")

      idCounter += 1

      if reply:
        comment['replies'] = []

        if commentReplyLink is not None:
          cList.find_element(By.CSS_SELECTOR, "._4sxc._42ft").click()

          driver.implicitly_wait(10)

          replyCommentList = cList.find_elements(By.CSS_SELECTOR, "._7a9h > ul > li")

          for replyC in replyCommentList:

            replyDict = {}

            replySoup = BeautifulSoup(replyC.get_attribute('innerHTML'), 'html.parser')

            id, author, date, _, attachment = commentScrap(replySoup, idCounter)

            replyDict['id'] = id
            replyDict['author'] = author
            replyDict['date'] = date
            replyDict['attachment'] = attachment
            
            readMoreLink = replySoup.select_one("._5v47.fss")

            if readMoreLink is not None:
              replyC.find_element(By.CSS_SELECTOR, "._5v47.fss").click()
              driver.implicitly_wait(10)
              readMoreHtml = replyC.find_element(By.CSS_SELECTOR, "._3l3x")
              readMoreSoup = BeautifulSoup(readMoreHtml.get_attribute('innerHTML'), 'html.parser')
              replyDict['comment'] = readMoreSoup.text
            else:
              textReplyComment = replySoup.select_one("._3l3x > span")
              if textReplyComment is not None:
                replyDict['comment'] = textReplyComment.text
            
            comment['replies'].append(replyDict)

            idCounter += 1

      datas.append(comment)

  jsonResp = {
    'meta': {
      'status': 200,
      'total': len(datas),
      'reply': reply
    },
    'data': datas
  }

  with open('response-post.json', 'w') as outfile:
      json.dump(datas, outfile)

  response = getResponse(200, jsonResp)
  return response