import urllib.request
import sys
args = sys.argv
print("args:{} len:{}".format(args, len(args)))


if len(args) > 1:
    HOST = args[1]
else:
    HOST = "http://ml30gen9:8080"

print("HOST is {}".format(HOST))

post_list = [
    ("{}/pirate/docreq", "oid=2&uid=1084205&url=https%3A%2F%2Ftest.bizocean.jp%2Foceanus%2Fform%2Freq.html&enc=UTF-8&sid=23cb8839206d8759&jsn=%7B%22message%22%3A%22%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%22%7D"),
]

error_count = 0
success_count = 0
try_count = 30

for i in range(try_count):

    for url, data in post_list:
        url = url.format(HOST)
        data = data.encode('utf-8')
        try:
            with urllib.request.urlopen(url=url, data=data) as page:
                if page.getcode() != 200:
                    pass
                else:
                    success_count += 1
        except Exception as e:
            pass

if success_count < 5:
    print("OK! only {}/{} success found".format(success_count, try_count))
else:
    print("NG! {} success  found".format(success_count))
