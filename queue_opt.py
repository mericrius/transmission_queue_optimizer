import time, logging, json, os.path
from datetime import datetime, timedelta
from transmission_rpc import Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

with open('settings.json', 'r') as fp:
    jsonSettings = json.load(fp)

ID, PASS = jsonSettings['ID'], jsonSettings['PASS']
IP, PORT = jsonSettings['IP'], jsonSettings['PORT']

client = Client(host=IP, port=PORT, username=ID, password=PASS)

def getDownloading() -> dict:
    torrents = client.get_torrents()
    torrents = [t for t in torrents if t.progress < 100.0]
    torrents = [t for t in torrents if t.status == 'downloading']

    return {t.id: (t.name, t.left_until_done) for t in torrents}

if __name__ == '__main__':
    logger.info("Queue Optimizer Started")

    if os.path.isfile('status.json'):
        with open('status.json', 'r') as fp:
            jsonStatus = json.load(fp)

        WatchTimer = datetime.now() - datetime.fromisoformat(jsonStatus['Excuted Time'])
        WatchTimer = WatchTimer.seconds
        jsonStatus.pop('Excuted Time')
        prevDownloading = {int(key):jsonStatus[key] for key in jsonStatus}

        status = getDownloading()
        status['Excuted Time'] = datetime.now().isoformat()
        with open('status.json', 'w', encoding='utf-8') as fp:
            json.dump(status, fp, indent=4, ensure_ascii=False)
        status.pop('Excuted Time')

        downloadSpeed = {key:(prevDownloading[key][1] - status[key][1])/WatchTimer for key in status if key in prevDownloading}

        speedTotal = sum(downloadSpeed.values())
        logger.info(f"Download Speed: {speedTotal/1024/1024:5.2f} MB/s")

        if speedTotal > 1024*1024*4:
            SpeedMinimum = 0
        elif speedTotal > 1024*1024*3:
            SpeedMinimum = 10*1024
        elif speedTotal > 1024*1024*2:
            SpeedMinimum = 50*1024
        elif speedTotal > 1024*1024*1:
            SpeedMinimum = 100*1024
        else:
            SpeedMinimum = 200*1024

        bottomKey = [key for key in downloadSpeed if downloadSpeed[key] < SpeedMinimum]

        for key in bottomKey:
            client.stop_torrent(key)
            logger.info(f"Stopping Torrent: {key}/{status[key][0]}")
            time.sleep(1.0)
            client.queue_bottom(key)
            logger.info(f"Move to bottom: {key}/{status[key][0]}")
            time.sleep(1.0)
            client.start_torrent(key)
            logger.info(f"Restarting Torrent: {key}/{status[key][0]}")
            time.sleep(1.0)

    else:
        status = getDownloading()
        status['Excuted Time'] = datetime.now().isoformat()
        with open('status.json', 'w', encoding='utf-8') as fp:
            json.dump(status, fp, indent=4, ensure_ascii=False)
        logger.info(f"Save downloading status to status.json")
