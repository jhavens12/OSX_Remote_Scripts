# Python version
import datetime
import os
import paramiko
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials
import gspread


g_scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', g_scope)
client = gspread.authorize(creds)
sheet = client.open('17/18 Mac Addresses').sheet1



the_pass = input("What is the password for the mac machines? ")

the_user = "Administrator"
the_date = datetime.datetime.now()

text_file = open("/Users/Havens/Documents/GitHub/OSX_Remote_Scripts/iprange.txt", "r")
list1 = text_file.readlines()

final_dictionary = {}
for hostname in list1:
    hostname = hostname.strip("\n")
    print()
    print()
    print()
    response = os.system("ping -c1 -t1 " + hostname)

    #and then check the response...
    if response == 0:
        print (hostname + ' is up!')
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname, username=the_user, password=the_pass, timeout=5)
            command_1 = "stat -f '%Su' /dev/console"
            command_2 = "scutil --get ComputerName"
            command_3 = "system_profiler SPHardwareDataType | awk '/Serial/ {print $4}'"

            stdin, stdout, stderr = client.exec_command(command_1)
            remote_username = stdout.read().decode('ascii').strip("\n")
            stdin, stdout, stderr = client.exec_command(command_2)
            remote_computername = stdout.read().decode('ascii').strip("\n")
            stdin, stdout, stderr = client.exec_command(command_3)
            remote_serialnumber = stdout.read().decode('ascii').strip("\n")

            client.close()
            print(remote_username)
            print(remote_computername)
            print(remote_serialnumber)
            timestamp = datetime.datetime.now()

            final_dictionary[timestamp] = {}
            final_dictionary[timestamp]['User'] = remote_username
            final_dictionary[timestamp]['Asset Tag'] = remote_computername
            final_dictionary[timestamp]['Serial'] = remote_serialnumber

            pprint(final_dictionary)

            report_line = [timestamp,remote_computername,remote_username,remote_serialnumber]
            sheet_data = sheet.get_all_values()
            row = str(len(sheet_data)+1)
            range_build = 'A' + row + ':D' + row
            cell_list = sheet.range(range_build)

            # Update values
            for cell,data in zip(cell_list,report_line):
                cell.value = data

            print("Updating Sheet...")

            # Send update in batch mode
            sheet.update_cells(cell_list)



        except Exception:
            print("IP is up but unable to connect - Not a mac?")

    else:
      print (hostname + ' is down!')
