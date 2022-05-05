import time
import requests
import random
import asyncio


async def dev(device):
    status = ["unknown", "working", "error"]
    while 1:
        now = status[random.randint(0, 2)]
        requests.post(url="http://8.130.20.66:8010/updatestatus",json={"device":device,
                                                                     "devicename":device,
                                                                     "humidity":random.randrange(100,900,1)/10,
                                                                     "temperature":random.randrange(00,400,1)/10,
                                                                     "status":status})
        await asyncio.sleep(5)

async def main():
    for i in range(10):
        asyncio.create_task(dev("device" + str(i)))

    while 1:
        await asyncio.sleep(0)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.run(main())
    loop.run_forever()