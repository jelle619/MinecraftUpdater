from urllib import urlopen, urlretrieve
import json
import os
import time
import shutil
import hashlib
import time

def log(string, logfile):
    print(string)
    logfile.write(string + "\n")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
response = urlopen(url)
res = response.read()
data = json.loads(res.decode('UTF-8'))

minecraft_ver = data['latest']['release']

logFile = open("update.log", "a+")

if os.path.exists('../server.jar'):
    sha = hashlib.sha1()
    f = open("../server.jar", 'rb')
    sha.update(f.read())
    cur_ver = sha.hexdigest()
else:
    cur_ver = ""

for version in data['versions']:
    if version['id'] == minecraft_ver:
        jsonlink = version['url']
        jarres = urlopen(jsonlink).read()
        jardata = json.loads(jarres.decode('UTF-8'))
        jarsha = jardata['downloads']['server']['sha1']

        log('Your sha1 is ' + cur_ver + '. Latest version is ' + str(minecraft_ver) + " with sha1 of " + jarsha, logFile)

        if cur_ver != jarsha:
            log('Updating server', logFile)
            link = jardata['downloads']['server']['url']
            log('Downloading jar from ' + link, logFile)
            urlretrieve(link, 'server.jar')
            log('Downloaded', logFile)
            os.system('screen -S minecraft -X stuff \'say The server will restart in 30 seconds.^M\'')
            log('Shutdown in 30 seconds', logFile)

            for i in range(20, 9, -10):
                time.sleep(10)
                os.system('screen -S minecraft -X stuff \'say Restart in ' + str(i) + ' seconds.^M\'')

            for i in range(9, 0, -1):
                time.sleep(1)
                os.system('screen -S minecraft -X stuff \'say Restart in ' + str(i) + ' seconds.^M\'')
            time.sleep(1)

            log('Stopping server', logFile)
            os.system('screen -S minecraft -X stuff \'stop^M\'')
            time.sleep(5)
            log('Backing up world...', logFile)
            if not os.path.exists("backup"):
                os.makedirs("backup")

            backupPath = "backups/world" +"_backup_" + str(int(time.time()/1000)) + "_sha=" + cur_ver
            shutil.copytree("../world", backupPath)

            log('Backup complete, now updating server jar', logFile)
            if os.path.exists('../server.jar'):
                os.remove('../server.jar')

            os.rename('server.jar', '../server.jar')
            log('Starting server', logFile)
            logFile.close()
            os.chdir("..")
            os.system('screen -S minecraft -d -m java -Xmx2048M -Xms512M -jar server.jar')

        else:
            log('Your server jar is already the latest version', logFile)
            logFile.close()

        break

