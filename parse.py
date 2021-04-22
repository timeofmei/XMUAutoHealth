import httpx
from lxml.etree import HTML
import execjs
import ujson
import datetime
import time

def login(account, password):
    url = "https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu"
    loginResp = httpx.get(url)
    if loginResp.status_code != 200:
        return
    loginPage = HTML(loginResp.text)
    lt = loginPage.xpath("//input[@name='lt']/@value")[0]
    salt = loginPage.xpath("//*[@id='pwdDefaultEncryptSalt']/@value")[0]
    with open("./encrypt.js") as f:
        encFunc = execjs.compile(f.read())
        passwordEnc = encFunc.call("encryptAES", password, salt)
    data = {
        "username": account,
        "password": password,
        "passwordEncrypt": passwordEnc,
        "lt": lt,
        "dllt": "userNamePasswordLogin",
        "execution": "e1s1",
        "_eventId": "submit",
        "rmShown": "1",
        "pwdDefaultEncryptSalt": salt
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "referer": "https://ids.xmu.edu.cn/",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }
    mainResp1 = httpx.post(url, data=data, cookies=dict(loginResp.cookies), headers=headers, allow_redirects=False)
    cookies = {
        "SAAS_S_ID": "xmu",
        "iPlanetDirectoryPro": mainResp1.cookies["iPlanetDirectoryPro"],
        "JSESSIONID": loginResp.cookies["JSESSIONID"]
    }
    mainResp2 = httpx.get(mainResp1.headers["location"], headers=headers, cookies=cookies)
    cookies.update({"SAAS_U": mainResp2.cookies["SAAS_U"]})
    headers.update({"x-requested-with":"XMLHttpRequest"})
    formResp = httpx.get("https://xmuxg.xmu.edu.cn/api/formEngine/business/1378/myFormInstance", headers=headers, cookies=cookies)
    form = ujson.loads(formResp.text)
    for component in form["data"]["formData"]:
        if component["title"] == "Can you hereby declare that all the information provided is all true and accurate and there is no concealment, false information or omission. 本人是否承诺所填报的全部内容均属实、准确，不存在任何隐瞒和不实的情况，更无遗漏之处。":
            component["value"]["stringValue"] = "是 Yes"
            component["value"]["changeValue"] = "是 Yes"
        if component["title"] == "打卡时间（无需填写，保存后会自动更新）":
            dt = str(datetime.datetime.now())
            dt = dt[:dt.index(".")]
            component["value"]["stringValue"] = dt
            component["value"]["changeValue"] = dt
    r = {"formData": form["data"]["formData"], "playerId": "owner"}
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "referer": "https://xmuxg.xmu.edu.cn/app/214",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.42",
        "x-requested-with": "XMLHttpRequest"
    }
    cookies = {
        "SAAS_S_ID": "xmu",
        "iPlanetDirectoryPro": mainResp1.cookies["iPlanetDirectoryPro"],
        "SAAS_U": mainResp2.cookies["SAAS_U"],
        "uid": "crystalgly"
    }
    resultResp = httpx.post(f"https://xmuxg.xmu.edu.cn/api/formEngine/formInstance/{form['data']['id']}", headers=headers, cookies=cookies, data=ujson.dumps(r, ensure_ascii=False))
    if ujson.loads(resultResp.text)["state"]:
        return True


if __name__ == "__main__":
    while True:
        time.sleep(1800)
        if (time.gmtime().tm_hour + 8) == 9:
            login("account", "password")
