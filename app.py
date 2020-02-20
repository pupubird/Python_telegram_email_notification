import os
import time
import check_emails
INTERVAL = 60  # 1 Minute
while True:
      
    # for windows 
    if os.name == 'nt': 
        _ = os.system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = os.system('clear') 

    check_emails.main()
    print("Next check in", INTERVAL, "seconds")
    time.sleep(INTERVAL)

  