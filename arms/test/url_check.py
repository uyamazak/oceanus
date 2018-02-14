import urllib.request
import sys
args = sys.argv
print("args:{} len:{}".format(args, len(args)))


if len(args) > 1:
    HOST = args[1]
else:
    HOST = "http://ml30gen9:8080"

print("HOST is {}".format(HOST))
get_list = [
    "{}/swallow?oid=test&evt=pageview&uid=1000000&ref=https%3A%2F%2Ftest.bizocean.jp%2F&tit=%E8%AB%8B%E6%B1%82%E6%9B%B8003%20%E3%82%B7%E3%83%B3%E3%83%97%E3%83%AB%E3%81%AA%E8%AB%8B%E6%B1%82%E6%9B%B8%EF%BD%9C%E3%83%86%E3%83%B3%E3%83%97%E3%83%AC%E3%83%BC%E3%83%88%E3%81%AE%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89%E3%81%AF%E3%80%90%E6%9B%B8%E5%BC%8F%E3%81%AE%E7%8E%8B%E6%A7%98%E3%80%91&url=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fdetail%2F100532%2F&enc=UTF-8&scr=1920x1080&vie=1903x499&sid=23cb8839206d8759",
    "{}/swallow?oid=test&evt=search_not_found&uid=10000000&ref=https%3A%2F%2Fwww.bizocean.jp%2Fdoc%2Fdetail%2F100532%2F&tit=%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%E3%81%AE%E6%A4%9C%E7%B4%A2%E7%B5%90%E6%9E%9C%EF%BD%9C%E7%84%A1%E6%96%99%E3%83%86%E3%83%B3%E3%83%97%E3%83%AC%E3%83%BC%E3%83%88%E3%80%81%E3%83%95%E3%82%A9%E3%83%BC%E3%83%9E%E3%83%83%E3%83%88%E3%81%AE%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89%E3%81%AF%E3%80%90%E6%9B%B8%E5%BC%8F%E3%81%AE%E7%8E%8B%E6%A7%98%E3%80%91&url=https%3A%2F%2Fwww.bizocean.jp%2Fdoc%2Fsearch%2Fall%2F-%2F%3Fkeyword%3D%25E3%2583%259D%25E3%2582%25B1%25E3%2583%25A2%25E3%2583%25B3%26price_segment%3Dboth&enc=UTF-8&scr=1920x1080&vie=1903x733&jsn=%7B%22kwd%22%3A%22%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%22%7D&sid=ffffffffffffffff",
    "{}/swallow?oid=test&evt=emailopen&url=https%3A%2F%2Fkrs.bz%2Fbizocean&tit=85&uid=1000000&sid=1000000&jsn=%7B%22aiid%22%3A%2225%22%2C%22acid%22%3A%2256%22%7D&enc=UTF-8",
    "{}/swallow?oid=test&evt=emailclick&uid=1000000&tit=85&url=https%3A%2F%2Fpx.a8.net%2Fsvt%2Fejp%3Fa8mat%3D2NR6CY%2B76ZKXE%2B33NG%2B6KESX&enc=utf-8&scr=1280x600&vie=1280x483&jsn=%7B%22aiid%22%3A%2225%22%2C%22acid%22%3A%2256%22%7D&sid=ffffffffffffffff",
    "{}/swallow?oid=test&evt=movie&uid=1000000&ref=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fdownload%2Fcomplete%2F100532%2F&url=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fvideo%2Fplayer%2F&enc=UTF-8&scr=1920x1080&vie=655x1519&jsn=%7B%22memberId%22%3A%221084205%22%2C%22viewingTime%22%3A95.481%2C%22videoCode%22%3A%22Mo2neRfrsjE%22%2C%22status%22%3A%22ENDED%22%2C%22url%22%3A%22https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fdownload%2Fcomplete%2F100532%2F%22%2C%22playDatetime%22%3A%222016-09-20%2011%3A25%3A56%22%7D&sid=ffffffffffffffff",
    "{}/swallow/bizocean?oid=2&evt=linkclick&uid=1084205&ref=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fsearch%2Fall%2F-%2F%3Fkeyword%3D%25E3%2583%259D%25E3%2582%25B1%25E3%2583%25A2%25E3%2583%25B3%26cx%3D%26cof%3D&tit=%5Btext%5D%E3%81%93%E3%81%A1%E3%82%89%E3%81%8B%E3%82%89%E6%9B%B8%E5%BC%8F%E4%BD%9C%E6%88%90%E3%83%AA%E3%82%AF%E3%82%A8%E3%82%B9%E3%83%88%E3%82%92%E3%81%8A%E9%80%81%E3%82%8A%E3%81%8F%E3%81%A0%E3%81%95%E3%81%84%E3%80%82&url=%2Foceanus%2Fform%2Freq.html&enc=UTF-8&scr=1920x1080&vie=1903x538&jsn=%7B%22pageX%22%3A820%2C%22pageY%22%3A390%2C%22kwd%22%3A%22%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%22%7D&sid=23cb8839206d8759",
    "{}/swallow/thedeepones?oid=2&evt=linkclick&uid=1084205&ref=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fsearch%2Fall%2F-%2F%3Fkeyword%3D%25E3%2583%259D%25E3%2582%25B1%25E3%2583%25A2%25E3%2583%25B3%26cx%3D%26cof%3D&tit=%5Btext%5D%E3%81%93%E3%81%A1%E3%82%89%E3%81%8B%E3%82%89%E6%9B%B8%E5%BC%8F%E4%BD%9C%E6%88%90%E3%83%AA%E3%82%AF%E3%82%A8%E3%82%B9%E3%83%88%E3%82%92%E3%81%8A%E9%80%81%E3%82%8A%E3%81%8F%E3%81%A0%E3%81%95%E3%81%84%E3%80%82&url=%2Foceanus%2Fform%2Freq.html&enc=UTF-8&scr=1920x1080&vie=1903x538&jsn=%7B%22pageX%22%3A820%2C%22pageY%22%3A390%2C%22kwd%22%3A%22%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3%22%7D&sid=23cb8839206d8759",
    "{}/robots.txt",
    "{}/favicon.ico",
    "{}/lb",
    "{}/rstatus",
]

post_list = [
    ("{}/pirate/movieform", "name=%E3%83%86%E3%82%B9%E3%83%88%E6%8B%85%E5%BD%93%E8%80%85&cname=%E3%83%86%E3%82%B9%E3%83%88%E8%B2%B4%E7%A4%BE%E5%90%8D&tel=03-5148-1212&email=yu_yamazaki%40bizocean.co.jp&oid=test&uid=1000000&url=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fvideo%2Fquestionnaire_oceanus%2F&enc=UTF-8&sid=23cb8839206d8759&jsn=%7B%22agreement%22%3A%22on%22%7D"),
]

once_get_list = [
        "{}/swallow/bizocean?oid=test&evt=pageview&uid=1084205&ref=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fcontact%2F&tit=%E3%81%8A%E5%95%8F%E3%81%84%E5%90%88%E3%82%8F%E3%81%9B%E5%AE%8C%E4%BA%86%EF%BD%9Cbizocean%20-%20%E3%81%82%E3%82%89%E3%82%86%E3%82%8B%E3%83%93%E3%82%B8%E3%83%8D%E3%82%B9%E3%82%B3%E3%83%B3%E3%83%86%E3%83%B3%E3%83%84%E3%82%92%E6%8F%90%E4%BE%9B%E3%81%99%E3%82%8B%EF%BC%81&url=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fcontact%2Finquiry%2Fcomplete%2F&enc=UTF-8&scr=1920x1080&vie=1903x510&sid=86895a04e5a59600",
        "{}/pierce/shortener?evt=redirect&uid=12345&url=https://www.bizocean.jp&rad=111.111.111.111&oid=2",
        "{}/gaze/mailaction?evt=open&uid=12345",
        ]

once_post_list =[
        ("{}/pirate/namecard", "name=%E3%83%86%E3%82%B9%E3%83%88%E6%8B%85%E5%BD%93%E8%80%85&cname=%E3%83%86%E3%82%B9%E3%83%88%E8%B2%B4%E7%A4%BE%E5%90%8D&tel=03-5148-1212&email=yu_yamazaki%40bizocean.co.jp&oid=test&uid=1000000&url=https%3A%2F%2Ftest.bizocean.jp%2Fdoc%2Fvideo%2Fquestionnaire_oceanus%2F&enc=UTF-8&sid=23cb8839206d8759&jsn=%7B%22agreement%22%3A%22on%22%7D"),
        ("{}/pirate/docreq", "oid=2&uid=1084205&url=https%3A%2F%2Ftest.bizocean.jp%2Foceanus%2Fform%2Freq.html&enc=UTF-8&sid=23cb8839206d8759&jsn=%7B%22message%22%3A%22%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%22%7D"),
        ]

error_count = 0

for url in once_get_list:
    url = url.format(HOST)
    try:
        with urllib.request.urlopen(url) as page:
            if page.getcode() != 200:
                print("error")
            else:
                pass
    except Exception as e:
        print("error:{}\n{}".format(url, e))
        error_count += 1

for url, data in once_post_list:
    url = url.format(HOST)
    data = data.encode('utf-8')
    try:
        with urllib.request.urlopen(url=url, data=data) as page:
            if page.getcode() != 200:
                print("error")
                error_count += 1
            else:
                pass
                #print("ok")
    except Exception as e:
        print("error:{}\n{}".format(url, e))
        error_count += 1

for i in range(25):
    for url in get_list:
        url = url.format(HOST)
        try:
            with urllib.request.urlopen(url) as page:
                if page.getcode() != 200:
                    print("error")
                else:
                    pass
                    #print("ok")
        except Exception as e:
            print("error:{}\n{}".format(url, e))
            error_count += 1

    for url, data in post_list:
        url = url.format(HOST)
        data = data.encode('utf-8')
        try:
            with urllib.request.urlopen(url=url, data=data) as page:
                if page.getcode() != 200:
                    print("error")
                    error_count += 1
                else:
                    pass
                    #print("ok")
        except Exception as e:
            print("error:{}\n{}".format(url, e))
            error_count += 1

if error_count == 0:
    print("OK! no errors found")
else:
    print("NG! {} errors found".format(error_count))
