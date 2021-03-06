import pymysql.cursors
import sys
from datetime import datetime
import re

time = ""
date = ""
person = ""

def findPerson(person):
    # Connect to the database
    connection = pymysql.connect(host='52.70.223.35',
                                user='clinicuser',
                                password='sparky',
                                database='ClinicDB',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        try:
            findPerson = "SELECT * FROM `nurses` WHERE `LastName`=%s"
            cursor.execute(findPerson, (person,))
            result = cursor.fetchall()
        except:
            print("Sorry, but we don't have a Nurse %s in this office. Make sure to look up your nurse by last name!")
            exit()

# WHO IS AVAILABLE * *
def SQL_Who(time, date):
    # Connect to the database
    connection = pymysql.connect(host='52.70.223.35',
                                user='clinicuser',
                                password='sparky',
                                database='ClinicDB',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sqlWho = "SELECT `LastName` FROM `nurses` WHERE `id` IN (SELECT `NurseID` FROM `nurse_schedule` WHERE %s BETWEEN `SlotStart` AND `SlotEnd` AND `SlotDate`=%s)"
        cursor.execute(sqlWho, (time, date))
        results = cursor.fetchall()

        results = [re.findall("\w+", str(result)) for result in results]
        converted = []
        for i in range(len(results)):
            converted.append(None)
            for j in range(len(results[i])):
                if j == 2:
                    converted[i] = results[i][j]

        if len(results) == 0:
            time = datetime.strptime(time, '%H:%M:%S').strftime('%I%p')
            print("Sorry, we couldn't find any openings at %s on %s." % (time, date))
        else:
            print("Nurses: %s" % converted)

# WHEN IS * AVAILABLE ON *
def SQL_When(person, date):
    # Connect to the database
    connection = pymysql.connect(host='52.70.223.35',
                                user='clinicuser',
                                password='sparky',
                                database='ClinicDB',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sqlWhen = "SELECT `SlotStart`, `SlotEnd` FROM `nurse_schedule` WHERE `NurseID` IN(SELECT `id` FROM `nurses` WHERE `LastName`=%s) AND `SlotDate`=%s"
        cursor.execute(sqlWhen, (person, date))
        results = cursor.fetchall()

        results = [re.findall("\d+", str(result)) for result in results]
        converted = []
        for i in range(len(results)):
            converted.append(None)
            for j in range(len(results[i])):
                if (j == 1):
                    timeStr = str(int(results[i][j])/3600).strip(".0")
                    converted[i] = "" + datetime.strptime(timeStr, '%H').strftime("%I%p")
                elif (j == 3):
                    timeStr = str(int(results[i][j])/3600).strip(".0")
                    converted[i] = converted[i] + "-" + datetime.strptime(timeStr, '%H').strftime("%I%p")
        
        if len(results) == 0:
            print("Sorry, we couldn't find any openings for %s on %s." % (person, date))
        else:
            print("Timeslot: %s" % converted)

# WHAT DAY IS * AVAILABLE AT *
def SQL_What(person, time):
    # Connect to the database
    connection = pymysql.connect(host='52.70.223.35',
                                user='clinicuser',
                                password='sparky',
                                database='ClinicDB',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        sqlWhat = "SELECT `SlotDate` FROM `nurse_schedule` WHERE `NurseID` IN (SELECT `id` FROM `nurses` WHERE `LastName`=%s) AND %s BETWEEN `SlotStart` AND `SlotEnd`"
        cursor.execute(sqlWhat, (person, time))
        results = cursor.fetchall()

        results = [re.findall("\d+", str(result)) for result in results]
        converted = []
        for i in range(len(results)):
            converted.append(None)
            for j in range(len(results[i])):
                if j == 0:
                    converted[i] = results[i][j] + "-"
                elif j == 1:
                    converted[i] = converted[i] + results[i][j] + "-"
                else:
                    converted[i] = converted[i] + results[i][j]
            
        if len(results) == 0:
            time = datetime.strptime(time, '%H:%M:%S').strftime('%I%p')
            print("Sorry, we couldn't find any openings for %s at %s." % (person, time))
        else:
            print("Slot Dates: %s" % converted)

if __name__ == "__main__":

    if len(sys.argv) == 4:
        select = sys.argv[1]

        # WHO IS AVAILABLE * *
        if select == "who":
            time = sys.argv[2]
            # Convert AM/PM to HMS
            try:  
                time = datetime.strptime(time, '%I%p').strftime('%H') 
                if int(time) < 9 or int(time) > 17:
                    print("Sorry, the clinic is only open from 9am-5pm Mon-Fri.")
                    sys.exit()
                time = datetime.strptime(time, '%H').strftime('%H:%M:%S') 
            except SystemExit:
                sys.exit()
            except:
                print("Invalid time entered.")

            date = sys.argv[3]
            # Parse date entered to get day of week.
            if len(date.split("-")) == 3:
                dates = date.split("-")
                dates = list(map(int, dates))
                weekday = datetime(dates[0], dates[1], dates[2]).weekday()

                if weekday >= 5:
                    print("Sorry, the clinic is only open from 9am-5pm Mon-Fri.")
                    exit()
            else:
                print("Invalid date entered.")
                exit()

            SQL_Who(time, date)
        
        # WHEN IS * AVAILABLE ON *
        elif select == "when":
            person = sys.argv[2]
            findPerson(person)
            date = sys.argv[3]

            # Parse date entered to get day of week.
            if len(date.split("-")) == 3:
                dates = date.split("-")
                dates = list(map(int, dates))
                weekday = datetime(dates[0], dates[1], dates[2]).weekday()

                if weekday >= 5:
                    print("Sorry, the clinic is only open from 9am-5pm Mon-Fri.")
                    exit()
            
            else:
                print("Invalid date entered.")
                exit()

            SQL_When(person, date)
        
        # WHAT DAY IS * AVAILABLE AT *
        elif select == "what":
            person = sys.argv[2]
            findPerson(person)

            time = sys.argv[3]
            try:  
                time = datetime.strptime(time, '%I%p').strftime('%H') 
                if int(time) < 9 or int(time) > 17:
                    print("Sorry, the clinic is only open from 9am-5pm Mon-Fri.")
                    sys.exit()
                time = datetime.strptime(time, '%H').strftime('%H:%M:%S') 
            except SystemExit:
                sys.exit()
            except:
                print("Invalid time entered.")
                
            SQL_What(person, time)
        else:
            print("Improper selection!")
            exit()
    else:
        print("Missing arguments!")
        exit()
