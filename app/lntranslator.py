import requests

'''
GET request to take all langs JSON
'''
def get_all_languages():
  header = {
      'Authorization' : 'a_c7JdV4d6dZbkhUkNywVLpmJfsqJXSmPE4dboafFPwOrGq2ct3ridv5DkwRnHAGASOLZcvLIoF67VKQUn'
  }
  LANGS = {}
  url = 'https://api-b2b.backenster.com/b1/api/v3/getLanguages?platform=api&code=en_GB'
  a = requests.get(url, headers=header).json()
  for lang in a['result']:
      LANGS[lang['full_code']] = lang['englishName']
  return LANGS
'''
url func:
https://api-b2b.backenster.com/b1/api/v3/translate
func translate takes POST request
input this json   
{
  "from": "en_GB",
  "to": "de_DE",
  "data": "London is the capital and largest city of England and of the United Kingdom.",
  "platform": "api"
}
'''

tr_url = 'https://api-b2b.backenster.com/b1/api/v3/translate'
def translate_this(query, src_lang, to_lang):
    header = {
      'Authorization' : 'a_c7JdV4d6dZbkhUkNywVLpmJfsqJXSmPE4dboafFPwOrGq2ct3ridv5DkwRnHAGASOLZcvLIoF67VKQUn'
    }
    json_data = {
      "from": src_lang,
      "to": to_lang,
      "data": query,
      "platform": "api"
    }
    response = requests.post(tr_url, headers=header, json=json_data)
    return response.json()['result']
