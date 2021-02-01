from modules import mediawiki as mw
import requests, logging, sys, time
exit = sys.exit
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s[%(name)s] %(message)s")
log = logging.getLogger("MainScript")

def fileget(fname):
    try:
        with open(fname,"r") as f:
            return f.read().rstrip('\n')
    except FileNotFoundError:
        log.error("No " + fname)
        return False

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

def main(S):
    uname = fileget("uname.txt")
    passwd = fileget("passwd.txt")
    root = fileget("root.txt")
    ppfix = fileget("pageprefix.txt")
    delay = fileget("delay.txt")
    if uname == False or passwd == False or ppfix == False:
        exit(3)
    if root == False:
        log.warning("root.txt not found! Using \"https://zh.wikipedia.org/w/api.php\".")
        root = "https://zh.wikipedia.org/w/api.php"
    if delay == False:
        log.warning("delay.txt not found! Using \"5\"")
        delay == 5
    else:
        delay = int(delay)
    mw.chroot(root)
    token = mw.token(S,"login")[0]
    status = mw.login(S,token,uname,passwd)
    del passwd
    if status[0] == True:
        log.info("Logged in!")
    else:
        log.error("Login Failed.")
        exit(2)
    uname = status[1]
    listpage = "User:" + uname + "/settings/list"
    listcontent = mw.getpage(S,listpage)[0]
    blist = []
    for x in listcontent.splitlines():
        blist.insert(-1,remove_prefix(x,"*"))
    log.info("Account List: " + str(blist))
    from requests_html import HTMLSession
    HS = HTMLSession()
    for y in blist:
        try:
            log.info("Processing " + y)
            tdata = mw.token(S,"csrf")
            starttimestamp = tdata[1]
            basetimestamp = mw.getpage(S,ppfix + "/" + y)[1]
            token = tdata[0]
            r = HS.get("https://space.bilibili.com/" + y)
            r.html.render()
            fans = r.html.find(".space-fans")[0].text
            log.info(y + ": " + fans)
            EDIT = mw.edit(S,token,ppfix + "/" + y,fans,y,True,basetimestamp,starttimestamp,False)
            if EDIT[0] == False:
                log.error("error while editing " + title + ": " + EDIT[1])
                log.error(EDIT[2])
            time.sleep(delay)
        except Exception as e:
            log.error("Error while processing " + y)
            log.error(str(e))
            pass

if __name__ == '__main__':
    main(requests.Session())
