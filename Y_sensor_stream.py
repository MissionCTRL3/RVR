import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import asyncio
from sphero_sdk import SpheroRvrAsync
from sphero_sdk import SerialAsyncDal
from sphero_sdk import Colors
from sphero_sdk import RvrLedGroups
from sphero_sdk import RvrStreamingServices

loop = asyncio.get_event_loop()

rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

async def accelerometer_handler(accelerometer_data):
    #get accelerometer data stream and strip some stuff out
    accel = str(accelerometer_data).strip("{'Accelerometer': } ")
    #create a list and split at the comma
    accel_list = accel.split(",")
    #get just the Y axsis value and stripping out the 'Y': 
    accel = str(accel_list[2]).strip("'Y': ")
    #convert to a float
    accelY = float(accel)

    if accelY <= -0.45:
        print(accelY)
        await ledColor()
        
    if accelY >= -0.45:
        print("Lift the front of RVR up")
        print(accelY)
        await ledColor2()

async def ledColor():
    await rvr.set_all_leds(
        led_group=RvrLedGroups.headlight_left.value | RvrLedGroups.headlight_right.value,
        led_brightness_values=[
            255, 0, 0,
            255, 0, 0
        ]
    )

async def ledColor2():
    await rvr.set_all_leds(
        led_group=RvrLedGroups.headlight_left.value | RvrLedGroups.headlight_right.value,
        led_brightness_values=[
            0, 247, 66,
            0, 247, 66
        ]
    )

async def main():
    """ This program demonstrates how to enable a single sensor to stream.
    """

    await rvr.wake()

    # Give RVR time to wake up
    await asyncio.sleep(2)

    await rvr.sensor_control.add_sensor_data_handler(
        service=RvrStreamingServices.accelerometer,
        handler=accelerometer_handler
    )

    await rvr.sensor_control.start(interval=500)

    # The asyncio loop will run forever to allow infinite streaming.


if __name__ == '__main__':
    try:
        asyncio.ensure_future(
            main()
        )
        loop.run_forever()

    except KeyboardInterrupt:
        print('\nProgram terminated with keyboard interrupt.')

        loop.run_until_complete(
            asyncio.gather(
                rvr.sensor_control.clear(),
                rvr.close()
            )
        )

    finally:
        if loop.is_running():
            loop.close()

