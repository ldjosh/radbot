import os, os.path
import tweepy, time, sys
import MySQLdb
import string
import re
from random import randint
import Image
import ImageFont
import ImageDraw
import datetime
import textwrap

db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                     user="root",  # your username
                     passwd="asuna11!",  # your password
                     db="ana")  # name of the data base

cur = db.cursor()  # you must create a Cursor object. It will let you execute all the queries you need
#argfile = str(sys.argv[1])
#enter the corresponding information from your Twitter application:
#Need to move these to db
sleeptime1 = 10
sleeptime2 = 5
attackmsg = ""
emotes = [':-D', ':-)', ':)', '8-D', '8)', '^_^', ';)', 'o.O', ' Zomgz! ', ' WOWZERS ', ' X.x ', ' LAWLS ', ' OHNOS ',
          ' OH YEAH ', ' ^_- ', ':D~', ' SMASHING ', ' AMAZING ', ' MARVELOUS ', ' FACE! ']
last = 0
killsig = 0  #are we shutting down?
killword = 'dieinafire'  #shutdown word. when seen changes killsig to 9
team = ['@ldjosh', '@tiinpa', '@dalamon', '@narfjones', '@ffsbrett']
CONSUMER_KEY = '8PK0tn1SbO5fgJAAW8B8kIkN4'  #keep the quotes, replace this with your consumer key
CONSUMER_SECRET = 'eEVgVW9WTSy8cdvV6GHkIpEIZ6Gx6kf9QZnt9aQMWST0sPGm5F'  #keep the quotes, replace this with your consumer secret key
ACCESS_KEY = '1705789242-uWZzlkHb43GMW56NuvteqNIncjEr6JZBrUK2UL0'  #keep the quotes, replace this with your access token
ACCESS_SECRET = 'Jdv86yOD33m6ThkxGWKE0XgASwSFfHUJTay4QbTNkrgwV'  #keep the quotes, replace this with your access token secret
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)


def setthesettings():
    """

    :rtype : object
    """
    team = ['@ldjosh', '@tiinpa', '@dalamon', '@narfjones', '@ffsbrett']


def listmoves():
    cur.execute("SELECT * FROM skills")

    movelist = ''
    results = cur.fetchall()
    for row in results:
        movelist = movelist + ',' + row[1]
    return movelist


def attack(move):
    cur.execute("SELECT * FROM skills where skillname = %s", move)
    attackmsg = ""
    skillname=""
    damage =0
    results = cur.fetchall()
    for row in results:
        moveid = row[0]
        skillname = row[1]
        skilltext = row[2]
        damagemax = row[3]
        damage = str(randint(1, damagemax + 1))
        thetime = time.strftime("%I:%M:%S")
        attackmsg = ' used ' + skillname + '. ' + skilltext 
    if str(skillname) == "Heal":
        damagestring = str(damage).format 
        attackmsg = attackmsg + 'Restored ' + str(damagestring) + ' HP to '
        damage = int(damage)
        damage = -damage
    return attackmsg, damage


def dealdamage(attack, damage):
    targets = re.findall(r'[@]\S*', attack)  # ['$string', '$example']
    returnmsg = ""
    hitpoints = []
    print 'Found: '
    print targets
    for target in targets:
        print "Target - attack - damage"
        print target + " " + attack + " " + damage
        if target.lower() != "@goldcointv" and target != "":
            cur.execute("UPDATE players AS p SET p.hp = p.hp-%s where name = %s",
                        (damage, target))  #update players as p set p.hp = p.hp-8 where name = '@ldjosh'
            cur.execute("Select hp from players where name = %s", target) #how much do they got left?
            for row in cur.fetchall():
                hp = row[0]
                hitpoints.append(str(hp))
                returnmsg = returnmsg + target + ' has ' + str(hp) + ' left.'
            print returnmsg

    if returnmsg == "":
        miss = 'the attack missed. loser. '
        print miss
        returnmsg = miss
    return returnmsg,targets,hitpoints


def MakeAScreenShot(bg, players, mob, hp, mp, thp, tmp, msg, extra):
    screenshot = Image.new("RGBA", (640, 480), "white")
    bg = Image.open("sprites/bg/" + bg + ".PNG")  #background image
    screenshot.paste(bg, (0, 0))
    fontx = ImageFont.truetype("sprites/dc.ttf", 25)
    fonty = ImageFont.truetype("sprites/dc.ttf", 12)
    fontz = ImageFont.truetype("sprites/dc.ttf", 20)

    drawing = ImageDraw.Draw(screenshot)
    if players != "":  #do we gots playas?
        player = 0
        for player in players:  #put'em on the screen homie!
            playerx = Image.open("sprites/players/" + player + ".PNG")
            screenshot.paste(playerx, (0, 0), playerx)
        #print "it's player: " + player
    if mob != "":  #do we gots monstas?
        bob = 0
        for bob in mob:  #put'em on the screen too homie!
            bobx = Image.open("sprites/mobs/" + bob + ".png")
            screenshot.paste(bobx, (0, 0), bobx)
        #print "it's bob: " + bob
    if hp != "":
        pbar = Image.open("sprites/assets/hp1.png")
        screenshot.paste(pbar, (0, 0), pbar)
        drawing.text((110, 240), hp, (0, 0, 0), fonty)  #
        drawing.text((110, 255), mp, (0, 0, 0), fonty)  #duh
    if thp != "":
        tbar = Image.open("sprites/assets/hp2.png")
        screenshot.paste(tbar, (0, 0), tbar)
        drawing.text((478, 198), thp, (255, 255, 255), fonty)  #
        drawing.text((478, 213), tmp, (255, 255, 255), fonty)  #duh
    tbox = Image.open("sprites/assets/textbox.png")
    screenshot.paste(tbox, (0, 0), tbox)
    margin = 110
    offset = 80
    for line in textwrap.wrap(msg, width=40):
        drawing.text((margin, offset), line, font=fontx, fill="#aa0000")
        offset += fontx.getsize(line)[1]
    #drawing.text((110,80),msg,(255,255,255),fontx) #message text
    if extra != "":
        if extra <1:
            heart = Image.open("sprites/assets/heart.png")
            screenshot.paste(heart,(0,0),heart)
            drawing.text((125, 350), str(extra), font=fontz, fill="#00FF00")
        if extra>0:
            heart  = Image.open("sprites/assets/pow.png")
            screenshot.paste(heart,(0,0),heart)
            drawing.text((425, 350), str(extra), font=fontz, fill="#00FF00")
    #filename = datetime.datetime.now().strftime("%S%f")
    filename = len([name for name in os.listdir('.') if os.path.isfile(name)])
    print len([name for name in os.listdir('.') if os.path.isfile(name)])
    screenshot.save("o/" + str(filename) + ".png", "PNG")
    return filename


def main():
    uptime = datetime.datetime.now().strftime("%I%M%S%f%m%d%Y")
    api.update_status('@ldjosh Alive Call ' + uptime)
    killsig = 0
    last = 0
    while (killsig < 1):
        try:
            for player in team:  #run the loop for everybody in the party
                getmoves = listmoves()  #get valid moves
                mentions = api.user_timeline(player)  #look at the partymembers timeline
                cur.execute("select max(last) from tweets")  #what was the last thing we did?
                for row in cur.fetchall():  #
                    newlast = row[0]  # the twitter id of the last thing we responded to
                for mention in mentions:  #
                    #print dir(mention)
                    #print mention.text
                    #print mention.user.screen_name
                    tag = randint(1, 17)  #little junk to make the tweet unique
                    if (mention.id > newlast):  #is this newer than the last thing we answered
                        validmoves = string.split(getmoves, ",")  #split moves into an array
                        for move in validmoves:  #check for each move
                            if move.lower() in mention.text.lower() and (len(move) > 3):
                                attackmsg, damagedone = attack(move)
                                hpleft,validtargets,targethps = dealdamage(mention.text, damagedone)
                                getafile = ""
                                mob = ["1", "3"]
                                myteam = ["1", "2", "3"]
                                ssmsg = str(player) + attackmsg + hpleft
                                getafile = MakeAScreenShot("1", myteam, mob, "99", "50", "12", "5", ssmsg,
                                                           damagedone)
                                api.update_status(player + " " + "http://ana.goldcointv.com/o/" + str(getafile) + ".png")
                                last = mention.id
                                print "last is now: " + str(last)
                                print "newlast was: " + str(newlast)
                                newlast = last
                                time.sleep(10)

                        if '@goldcointv' in mention.text.lower() and killword in mention.text:
                            killsig = 9
                            thetime = time.strftime("%I:%M:%S")
                            last = mention.id
                            time.sleep(sleeptime2)
                            api.update_status(str(thetime) + ' Ding dong! ' + str(last) + ' - goodbye !')
                        if '@goldcointv' in mention.text.lower() and 'move list' in mention.text:
                            time.sleep(sleeptime2)
                            api.update_status(
                                'Moves for @' + mention.user.screen_name + ' include ' + getmoves + str(emotes[tag]))
                            last = mention.id

                if newlast < last:
                    cur.execute('''UPDATE tweets SET last=%s where id=1 ''', (last))

                time.sleep(sleeptime1)

        except tweepy.TweepError as e:
            print "error code:" + e.response.status
            if e.response.status == 429 or e.response.status == "429":
                api.update_status('ratelimit hit. sleep 60')
                time.sleep(sleeptime2)


setthesettings()
main()