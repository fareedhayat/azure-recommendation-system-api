from typing import Union
from fastapi import FastAPI
from collection_dataframe import favoritesCollection
from helper import content_based_recommendation, filtered_fav, get_categories, get_similar_category_users, load_model_from_blob, get_call_data, get_user_recommendations, get_weights, weighted_recommendations
import json
from pprint import pprint

app = FastAPI()


def set_globvar(setModel,setResults_df,setContent_based_recommendation_df,setCall_data_df,setActive_users_ids_df):
    global Model
    global results_df 
    global content_based_recommendation_df 
    global call_data_df 
    global active_users_ids_df

    Model = setModel
    results_df = setResults_df
    content_based_recommendation_df = setContent_based_recommendation_df
    call_data_df = setCall_data_df
    active_users_ids_df = setActive_users_ids_df

def set_weights(setRatingWeight, setCallWeight, setDurationWeight):
    global rating_weight
    global call_weight
    global duration_weight
    
    rating_weight = setRatingWeight
    call_weight = setCallWeight
    duration_weight = setDurationWeight


@app.get("/")
def read_root():
    return {"Please Enter an ID Endpoint"}


@app.get("/id")
def read_item(id: Union[str, None] = None):
    # global rating_weight
    # global call_weight
    # global duration_weight

    categories = get_categories(id)
    if not categories:
        return {"No Categories Found"}
    
    # weights = get_weights()

    # for key, value in weights.items():
    #     if key == 'RECOMMENDED_RATING_WEIGHT':
    #          rating_weight = value
    #     elif key == 'CALL_DURATION_WEIGHT':
    #          duration_weight = value
    #     elif key == 'CALL_TAKEN_WEIGHT':
    #          call_weight = value

    query = {
    'user_id': id
    }
    favorite = favoritesCollection.find_one(query)
    
    ids_present = set()
    if favorite:
        favorite_owwlls = favorite.get('favorites', [])
        if id not in active_users_ids_df['0'].values and favorite_owwlls:

            similar_users = get_similar_category_users(categories, id)
            content_based_recommendations = content_based_recommendation(similar_users)
            
            filtered_data = [
                item for item in content_based_recommendations
                if item != id and item not in favorite_owwlls
            ]
            
            recommendations = []
            for user_id in filtered_data:
                recommended = get_call_data(user_id, call_data_df)
                recommendations.append(recommended)
            
            print('Content Based and Favorites')
            final_recommendations = weighted_recommendations(recommendations, rating_weight, duration_weight, call_weight)
            response_json = json.dumps(final_recommendations, indent=None)
            data =  json.loads(response_json)
            return data
    
        elif id in active_users_ids_df['0'].values and favorite_owwlls:
            Data = get_user_recommendations(id, Model,results_df, content_based_recommendation_df)
            filtered_data = [
                    item for item in Data
                    if item != id and item not in favorite_owwlls and (item not in ids_present and ids_present.add(item) is None)
                    ]
            recommendations = []
            for user_id in filtered_data:
                recommended = get_call_data(user_id, call_data_df)
                recommendations.append(recommended)
            
            print('Active User and Favorites')
            final_recommendations = weighted_recommendations(recommendations[:25], rating_weight, duration_weight, call_weight)
            pprint(final_recommendations)
            response_json = json.dumps(final_recommendations, indent=None)
            data =  json.loads(response_json)
            
            return data
    
    elif id not in active_users_ids_df['0'].values and not favorite:
            similar_users = get_similar_category_users(categories, id)
            content_based_recommendations = content_based_recommendation(similar_users)
            
            recommendations = []
            for user_id in content_based_recommendations:
                recommended = get_call_data(user_id, call_data_df)
                recommendations.append(recommended)
            
            print('Content Based and No Favorites')
            final_recommendations = weighted_recommendations(recommendations, rating_weight, duration_weight, call_weight)
            response_json = json.dumps(final_recommendations, indent=None)
            data =  json.loads(response_json)
            return data
    
    else:
            Data = get_user_recommendations(id, Model,results_df, content_based_recommendation_df)
            
            filtered_data = [
                    item for item in Data
                    if item != id and (item not in ids_present and ids_present.add(item) is None)
                    ]
            recommendations = []
            for user_id in filtered_data:
                recommended = get_call_data(user_id, call_data_df)
                recommendations.append(recommended)
            
            print('Active User and No Favorites')
            final_recommendations = weighted_recommendations(recommendations[:25], rating_weight, duration_weight, call_weight)
            response_json = json.dumps(final_recommendations, indent=None)
            data =  json.loads(response_json)
            return data
        
        
@app.get("/GetTrainedModel")
def GetTrainedModel():
    setModel, setResults_df, setContent_based_recommendation_df, setCall_data_df, setActive_users_ids_df = load_model_from_blob()
    set_globvar(setModel,setResults_df,setContent_based_recommendation_df,setCall_data_df,setActive_users_ids_df)

    return {"Variables Set Successfully"}

@app.get("/GetConfiguration")
def GetConfiguration():
    weights = get_weights()
    
    for key, value in weights.items():
        if key == 'RECOMMENDED_RATING_WEIGHT':
            rating_weight = value
        elif key == 'CALL_DURATION_WEIGHT':
            duration_weight = value
        elif key == 'CALL_TAKEN_WEIGHT':
            call_weight = value
            
    set_weights(rating_weight, duration_weight, call_weight)

    return f"Rating Weight = {rating_weight}, Duration Weight = {duration_weight} Call Weight = {call_weight}, Variables Set Successfully"