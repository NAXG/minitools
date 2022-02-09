from mitmproxy import ctx
from bs4 import BeautifulSoup
from threading import Thread
import ffmpeg
import re

data = {}

def downloadvideo(url, keyname):
    filename = data.get(keyname)
    stream = ffmpeg.input(url)
    stream = ffmpeg.output(stream, filename + '.mp4')
    ffmpeg.run(stream)


def request(flow):
    global key_tmp
    global video
    request = flow.request
    info = ctx.log.info
    url = request.url
    path = request.path
    info(request.host)
    if request.host == "h5.dingtalk.com":
        pattern = re.compile("liveUuid=(.*)&")
        re_liveUuid = pattern.findall(path)
        re_liveUuid = "".join(re_liveUuid)
        key_tmp = re_liveUuid
        info(re_liveUuid)
    if key_tmp:
        re_live_hp = re.search("live_hp/" + key_tmp + "_merge.m3u8", path)
        if re_live_hp:
            video = url
            # downloadvideo(videourl, key_tmp)
            t1 = Thread(target=downloadvideo, args=(video, key_tmp))
            t1.start()


def response(flow):
    global data
    info = ctx.log.info
    response = flow.response
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile("<meta content=\"(.*)\" property=\"og:title\"")
    meta = soup.find_all(attrs={"property": "og:title"})
    title = pattern.findall(str(meta))
    if title:
        title = "".join(title)
        tmp = {key_tmp: title}
        data.update(tmp)
        info(data)
