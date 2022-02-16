from flask import *
import json, time, mechanize
from fake_useragent import UserAgent
from datetime import datetime, timezone
import pytz

app = Flask(__name__)

ua = UserAgent()

@app.route("/", methods = ['GET'])
def home_page():
    data_set = {'Page': "Home", "Message": 'Home page loaded.', "Timestamp": time.time()}
    json_dump = json.dumps(data_set)

    return json_dump


@app.route("/sorgu/", methods = ['GET'])
def request_page():
    gelen_sorgu  = str(request.args.get('id'))
    netice = _getPaymentInfo(gelen_sorgu)
    print(netice)
    user_query = str(request.args.get('id'))
    data_set = {'Sorgu neticesi': "UGURLU", "Cavab":netice}
    #{kod, son_odenis_meblegi, son_odenis_tarixi, yekun_borc}
    json_dump = json.dumps(data_set)

    return json_dump

def _getPaymentInfo(kod):
  

    #Azeriqaz melumatlari
    son_odenis_meblegi = ""
    son_odenis_tarixi = ""
    yekun_borc =""
    browser = mechanize.Browser()
    browser.set_handle_robots(False)

    user_agent = [('User-agent', ua.safari), ('Accept', '*/*')]

    browser.addheaders = user_agent
    browser.open("http://azeriqaz.az/az/balance")
    browser.select_form(nr=0)
    browser.form["subscriber_code"] = kod
    try:
        browser.submit()
        html = browser.response().read()
        a_dictionary = repr(html)
        odenis_starts = a_dictionary.find('<i style="font-size: 0.9em;">') + 29
        if odenis_starts > 30:
            odenis_end = odenis_starts + 10

            son_odenis_tarixi = a_dictionary[odenis_starts:odenis_end]
            if son_odenis_tarixi.find("i") > 0:
                son_odenis_tarixi = ""
                netice_item = "melumat tapilmadi..."
                
            mebleg_qalan = a_dictionary[odenis_end:odenis_end + 40]
            mebleg_start = mebleg_qalan.find("right") + 8
            mebleg_end = mebleg_qalan.find("</d")
            son_odenis_meblegi = mebleg_qalan[mebleg_start:mebleg_end]
            yb_end = a_dictionary.find('1. Bildiri')
            yb_kesim = a_dictionary[yb_end -
                                    30:yb_end]  #ht;">28.4</b></div>\r\n  <div>
            yekun_borc_starts = yb_kesim.find(">") + 1
            yekun_borc_ends = yb_kesim.find("</b>")
            yekun_borc = yb_kesim[yekun_borc_starts:yekun_borc_ends]

            '''print(
                f"                       {yekun_borc} | {son_odenis_tarixi} | {son_odenis_meblegi}"
            )'''
        

    except mechanize.HTTPError:
        print(" melumat tapilmadi...")
        yekun_borc=""
        pass
    netice_item = {'kod':kod, 'son_odenis_meblegi':son_odenis_meblegi, 'son_odenis_tarixi':son_odenis_tarixi, 'yekun_borc':yekun_borc}
    
    return netice_item


if __name__ == '__main__':
    app.run(port=7777)