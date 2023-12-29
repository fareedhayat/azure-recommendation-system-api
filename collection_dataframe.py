from datetime import datetime, timezone, timedelta
import pandas as pd
from connection_string import db


userCollection = db['users']
call_logs = db['call_logs']
call_data = db['vw_call_per_day']
favoritesCollection = db['favorite_owwlls']
training_data = db['misc_meta']


def get_active_callers():
    user_activity_timeframe = training_data.find_one({'key':'CALL_ACTIVITY_TIMEFRAME'})
    value = user_activity_timeframe['value']
    time = int(value)
    current_date = datetime.now()
    desired_time = current_date - timedelta(days = time)
    query = {
    '$and': 
    [
        {
            'created_on': 
            {
                '$gt': desired_time
            }
        }, 
        {
            'status': 'Call Ended'
        }
    ]
    }
    # {
    # 'created_on': {
    #     '$gt': desired_time
    # }
    # }
    call_active_users = call_logs.find(query)
    return call_active_users

recent_call_data = get_active_callers()
cursor_user = userCollection.find({})



users_df = pd.DataFrame(list(cursor_user))

active_users_df = pd.DataFrame(recent_call_data)