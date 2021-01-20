from deep_translator import (GoogleTranslator,
                             PonsTranslator,
                             LingueeTranslator,
                             MyMemoryTranslator,
                             YandexTranslator,
                             DeepL,
                             QCRI,
                             single_detection,
                             batch_detection)


def translate_this(query, src_lang=None, to_lang='en'):
    translation = ''
    if src_lang == None: 
        src_lang = single_detection(query, api_key='66d86088869a1a46156d6bf92e8ed377') 
    elif src_lang == 'en' and to_lang == 'ar':
        translation = QCRI("9f604502f8563e060872d811b53ae401").translate(source='en', target='ar', domain="news", text=text)
    else:
        try:
            a = a / 0 # Костыль чтобы выключить пока меморитраслятор, т.к. в нем меньше список поддерживаемых языков
            mymem = MyMemoryTranslator(source=src_lang, target=to_lang, de='nikolay.nikishev@icloud.com') #
            translation = mymem.translate(query)
        except:
            translation = GoogleTranslator(source=src_lang, target=to_lang).translate(text=query)
                
    return f'{translation}'


