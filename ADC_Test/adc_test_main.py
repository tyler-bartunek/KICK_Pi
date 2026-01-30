#Imports: basic functionality
import ADS1x15


#Configure and set the ADS object
def connect_ads(i2cbus_number):

    #Set it up at the default address and specified bus number 
    ads = ADS1x15.ADS1115(i2cbus_number)

    #Set the gain to accept up to $\pm$ 4.096V and have acceptable resolution
    ads.setGain(ads.PGA_4_096V)

    #Set the mode: CONTINUOUS
    ads.set_mode(ads.MODE_CONTINUOUS)

    #Set the data rate: fastest
    ads.setDataRate(ads.DR_ADS111X_860)

    return ads

#Get a reading from the device
def read_ads(ads):

    value = 0

    ads.requestADC(0)

    if ADS.isReady() :
        value = ADS.getValue()
        ADS.requestADC(0)

    return value


###################################################################################################################
################################################## Main ###########################################################
###################################################################################################################
def main():

    #Initialize the ADS object on I2C line 1 at the fastest data rate, continuous
    try:
        ads = connect_ads(1)
    except OSError:
        print("Check ADC connections or device")
        exit()


    try:

        while True:
            print(read_ads(ads))

    except KeyboardInterrupt:

        print("Operation terminated by user")


    return None



if __name__ == "__main__":

    main()