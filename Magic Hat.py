import smtplib
import logging
import secret

# Setup logfile in case program crashes
logging.basicConfig(filename='Magic Hat Log File.log',level=logging.INFO)

# Read in Gifters list of dicts "database"
import json
with open ('Gifternames.json', 'r') as f:
    Gifters = json.load(f)

try:
    giftList = open('./Output.txt', 'w+')
except Exception as ex:
    logging.error(ex)
    print (ex)
    print ('Failed to open Output file, please exit program')

#Find collisions
def search(values, searchFor):
    for k in values:
        logging.debug(">>>Looking for " + searchFor + ", checking " + values[k])
        if searchFor in values[k]:
            logging.debug(">>>Matched! " + searchFor + " and " + values[k])
            return True
    return False

#Create new gifting list
def giftList ():
    from random import shuffle

    gifterNames = [name['Name'] for name in Gifters]
    gifterEmails = [email['Email'] for email in Gifters]
    gifteeNames = [name['Name'] for name in Gifters]

    ShuffleCount = 0
    #Shuffle until we get a valid dataset
    while (True):
        ShuffleCount += 1
        logging.debug("******************Shuffling " + str(ShuffleCount))
        shuffle (gifteeNames)

        #Check if anyone is gifting to themself
        duplicates = [i for i, j in zip(gifterNames,gifteeNames) if i == j]
        if not duplicates:
            #Check to ensure no illegal gifting
            invalid = False
            for i, (gifter, giftee) in enumerate(zip(gifterNames, gifteeNames)):
                logging.debug("Let's see if " + gifter + " can give to " + giftee)            
                if (search(Gifters[i], giftee)):
                    logging.debug(gifter + " can't give to " + giftee + ", reshuffling for attempt #" + str(ShuffleCount))
                    invalid = True
                    break
            if (invalid == False):
                logging.info("We found a good list! (After only %d attempts)" % ShuffleCount)
                break

    subject = "Secret Santa 2020"
	
    try:
        giftList = open('./Output', 'w+')
    except Exception as ex:
        logging.error(ex)
        logging.error("Unable to open output file")
        return
    for i, (gifter, giftee) in enumerate(zip(gifterNames, gifteeNames)):
        #print (gifter + " --> " + giftee)
        giftList.write(gifter + " --> " + giftee + "\n")
        sent_to = str(gifterEmails[i])
        body = "Hello " + gifter + ",\n\nThe magic hat has decided that you will be gifting to " + giftee + " this year!\n\nThis is an automated message, but please feel free to reply if you have any questions or need " + giftee + "'s address.\n\n-One of Santa's Helpers"

        message = "From: "+sent_from+"\r\nTo: "+sent_to+"\r\nSubject: "+subject+"\r\n\r\n"+body
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.set_debuglevel(1)
            server.starttls()
            server.login(sent_from, API_key)
            server.sendmail(sent_from, sent_to, message)
            server.close()
            logging.info('Email sent to ' + gifter +'!')
            print ('Email sent to ' + gifter +'!')
        except Exception as ex:
            logging.error(ex)
            logging.error("Unable to send email to: " + gifter)
            print ("Unable to send email to: " + gifter)
            return
    print ("All emails successfully sent out!")
    giftList.close()
    return
    
#View current gifters
def viewGifters ():
    print ("Here are the current Gifters:\n")
    for gifter in Gifters:
        print (gifter['Name'])
    print ("There are " + str(len(Gifters)) + " total gifters this year")
    return

while (True):
    print ("\n\nWhat would you like to do?")
    print ("1: Create new gift list")
    print ("2: View current Gifters")
    print ("3: Exit\n")

    #Get user input, ask until valid input
    while (True):
        try:
            choice = int(input("Enter your selection: "))
            break
        except ValueError:
            print ("Please enter an integer selection\n")

    if (choice == 1):
        giftList()
    elif (choice == 2):
        viewGifters()
    elif (choice == 3):
        print ("Thank you, shutting down")
        break
    else:
        print ("That was not a valid selection, please try again")

    
    
