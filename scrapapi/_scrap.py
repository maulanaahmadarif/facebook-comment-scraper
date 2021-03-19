from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

import json
import time

driver = webdriver.Chrome()
driver.get('https://web.facebook.com/story.php?story_fbid=3660159894068444&id=583729738378157&_rdc=1&_rdr')

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

# # WAIT
# driver.implicitly_wait(20)
time.sleep(2)

# SCROLL TO BOTTOM OF PAGE
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

time.sleep(2)

commentList = driver.find_elements(By.CSS_SELECTOR, 'ul._7a9a > li')

datas = []

counterId = 0

for cList in commentList:
  
  comment = {}

  soup = BeautifulSoup(cList.get_attribute('innerHTML'), 'html.parser')

  authorComment = soup.find(class_="_6qw4")
  textComment = soup.select_one("._3l3x > span")
  attachmentComment = soup.select_one("._2txe img")
  commentReplyLink = soup.select_one("._4sxc._42ft")
  commentDate = soup.select_one("a._6qw7 abbr")

  # print("Author: " + authorComment.text)
  # print("Date: " + commentDate.get("data-utime"))

  comment['id'] = counterId
  comment['author'] = authorComment.text
  comment['date'] = commentDate.get("data-utime")

  if textComment is not None:
    # print("Comment Text: " + textComment.text)
    comment['comment'] = textComment.text
  else:
    comment['comment'] = ''
  
  if attachmentComment is not None:
    # print("Attachment : " + attachmentComment.get('src'))
    comment['attachment'] = attachmentComment.get('src')
  else:
    comment['attachment'] = ''

  comment['replies'] = []

  counterId += 1

  if commentReplyLink is not None:
    cList.find_element(By.CSS_SELECTOR, "._4sxc._42ft").click()

    driver.implicitly_wait(10)

    replyCommentList = cList.find_elements(By.CSS_SELECTOR, "._7a9h > ul > li")

    for replyC in replyCommentList:

      replyDict = {}

      replySoup = BeautifulSoup(replyC.get_attribute('innerHTML'), 'html.parser')

      authorReplyComment = replySoup.find(class_="_6qw4")
      attachmentReplyComment = replySoup.select_one("._2txe img")
      commentReplyDate = replySoup.select_one("a._6qw7 abbr")

      # print('\tAuthor : ' + authorReplyComment.text)
      # print("\tDate: " + commentReplyDate.get("data-utime"))

      replyDict['id'] = counterId
      replyDict['author'] = authorReplyComment.text
      replyDict['date'] = commentReplyDate.get("data-utime")

      if attachmentReplyComment is not None:
        # print("\attachment : " + attachmentReplyComment.get('src'))
        replyDict['attachment'] = attachmentReplyComment.get('src')
      else:
        replyDict['attachment'] = ''
      
      readMoreLink = replySoup.select_one("._5v47.fss")
      if readMoreLink is not None:
        replyC.find_element(By.CSS_SELECTOR, "._5v47.fss").click()
        driver.implicitly_wait(10)
        readMoreHtml = replyC.find_element(By.CSS_SELECTOR, "._3l3x")
        readMoreSoup = BeautifulSoup(readMoreHtml.get_attribute('innerHTML'), 'html.parser')
        # print("\tComment Reply Text: " + readMoreSoup.text)
        replyDict['comment'] = readMoreSoup.text
      else:
        textReplyComment = replySoup.select_one("._3l3x > span")
        if textReplyComment is not None:
          # print("\tComment Reply Text: " + textReplyComment.text)
          replyDict['comment'] = textReplyComment.text
      
      comment['replies'].append(replyDict)
      counterId += 1

  datas.append(comment)

with open('data.json', 'w') as outfile:
    json.dump(datas, outfile)
