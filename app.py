import os
import time
import check_emails
INTERVAL = 300  # 5 Minutes
while True:
      
    # for windows 
    if os.name == 'nt': 
        _ = os.system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = os.system('clear') 

    try:
        check_emails.main()
    except Exception:
        pass
    print("Next check in", INTERVAL, "seconds")
    time.sleep(INTERVAL)

  