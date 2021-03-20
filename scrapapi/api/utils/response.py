from django.http import HttpResponse
import json

def getResponse(status = 200, data = {}):
  response = HttpResponse(json.dumps(data), content_type='application/json')
  response.status_code = status
  return response