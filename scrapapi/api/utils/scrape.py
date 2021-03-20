def commentScrap(dom, idCounter):
  authorComment = dom.find(class_="_6qw4")
  textComment = dom.select_one("._3l3x > span")
  attachmentComment = dom.select_one("._2txe img")
  commentDate = dom.select_one("a._6qw7 abbr")

  tComment = ''
  aComment = ''

  if textComment is not None:
    tComment = textComment.text
  else:
    tComment = ''
  
  if attachmentComment is not None:
    aComment = attachmentComment.get('src')
  else:
    aComment = ''

  return idCounter, authorComment.text, commentDate.get("data-utime"), tComment, aComment