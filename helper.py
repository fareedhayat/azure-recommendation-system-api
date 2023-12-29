from pprint import pprint
from bson import ObjectId
from azure.storage.blob import BlobServiceClient
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import pandas as pd
import io
import ast
import random
from connection_string import db 
from collection_dataframe import users_df,active_users_df


def load_model_from_blob():
    connection_string = "DefaultEndpointsProtocol=https;AccountName=owwlla90e;AccountKey=2A7o0Ou+YrTtBo6SLikZRAs+qH8BY9c9gCqyO6B7P3dglBFIsuw4ocU1R4zTD+CiV3R/56xKUpST+AStPm+Vcg==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_name = 'model'
    blob_name = 'recommender.pkl'
    results_blob_name = 'all_results.csv'
    content_based_blob_name = 'content_based_recommendation.csv'
    call_data_blob_name = 'histogram_data.csv'
    active_users_ids_blob_name = 'active_users_ids.csv'

    container_client = blob_service_client.get_container_client(container_name)

    model_data = container_client.get_blob_client(blob_name).download_blob(timeout=800).readall()
    results_data = container_client.get_blob_client(results_blob_name).download_blob(timeout=800).readall()
    content_based_data = container_client.get_blob_client(content_based_blob_name).download_blob().readall()
    call_data = container_client.get_blob_client(call_data_blob_name).download_blob().readall()
    active_users_ids = container_client.get_blob_client(active_users_ids_blob_name).download_blob().readall()

    loaded_model = pickle.loads(model_data)
    results_df = pd.read_csv(io.BytesIO(results_data))
    content_based_df = pd.read_csv(io.BytesIO(content_based_data))
    call_data_df = pd.read_csv(io.BytesIO(call_data))
    active_users_ids_df = pd.read_csv(io.BytesIO(active_users_ids))

    return loaded_model, results_df, content_based_df, call_data_df,active_users_ids_df

def get_user_recommendations(user_id, model, results_df, content_based_df):
    activityBased = activityBased_recommendation(user_id, model, results_df)
    contentBased = contentBased_recommendation(user_id,content_based_df)
    merged_recommendations = contentBased + activityBased
    random.shuffle(merged_recommendations)

    return merged_recommendations


def activityBased_recommendation(user_id, model, results_df):
    user_data = results_df[results_df['User_ID'] == user_id]
    items_to_predict = user_data['Call_To'].tolist()
    unique_items_to_predict = list(set(items_to_predict))
    predictions = []

    for item in unique_items_to_predict:
        item_without_quotes = item.replace("'", "")
        prediction = model.predict(user_id, item)
        predictions.append({
            'Call_To': item_without_quotes,
            'Predicted_Rating': prediction.est
        })

    sorted_predictions = sorted(predictions, key=lambda x: x['Predicted_Rating'], reverse=True)

    predictions = sorted_predictions[:40]
    recommendations = [recommendation['Call_To'] for recommendation in predictions]
    return recommendations

def contentBased_recommendation(user_id, content_based_df):

    content_based = content_based_df[content_based_df['User_ID'] == user_id]

    content_based_recommendations_list = []
    if not content_based.empty:
        content_based_recommendations_str = content_based['Content_Based_recommendations'].iloc[0]
        content_based_recommendations_list = ast.literal_eval(content_based_recommendations_str)

    content_based = content_based_recommendations_list[:40]

    return content_based

def get_categories(id):
    obj_id = ObjectId(id)
    columns_for_categories = ['_id', 'Categories']
    categories_df = users_df[columns_for_categories]
    user_without_categories = categories_df['Categories'].apply(lambda x: len(x) == 0 if x is not None else False)
    user_without_categories_list = user_without_categories[user_without_categories].index.tolist()
    categories_df = categories_df[~categories_df.index.isin(user_without_categories_list)]
    categories_df = categories_df.reset_index(drop=True)
    categories_df['category_str'] = categories_df['Categories'].apply(lambda cat_list: ', '.join(cat_list).lower() if cat_list else '')
 
    for index, row in categories_df.iterrows():
        user_id = row['_id']
        if user_id == obj_id:
            categories = row['category_str']
            return categories

def get_similar_category_users(categories, user_id):
    columns_for_categories = ['_id', 'Categories']
    categories_df = users_df[columns_for_categories]
    user_without_categories = categories_df['Categories'].apply(lambda x: len(x) == 0 if x is not None else False)
    user_without_categories_list = user_without_categories[user_without_categories].index.tolist()
 
    categories_df = categories_df[~categories_df.index.isin(user_without_categories_list)]
    categories_df = categories_df.reset_index(drop=True)
 
    categories_df['category_str'] = categories_df['Categories'].apply(lambda cat_list: ', '.join(cat_list).lower() if cat_list else '')
    vectorizer = TfidfVectorizer()
    category_vectors = vectorizer.fit_transform(categories_df['category_str'])
    input_vector = vectorizer.transform([categories])
 
    similarities = cosine_similarity(input_vector, category_vectors)[0]
 
    similar_users_indices = similarities.argsort()[::-1]
    top_ten = similar_users_indices[:100]
    similar_users_ids = categories_df.loc[top_ten, '_id'].astype(str)
 
    return similar_users_ids

def content_based_recommendation(similar_users):
  filtered_users = []
  user_ids = users_df['_id'].astype(str).tolist()
  for user in similar_users:
    if user in user_ids:
        index = user_ids.index(user)
        role = users_df.loc[index, 'role']['name']
        if role == 'Owwll':
          filtered_users.append(user)
  active_owwlls = []
  existing_ids = active_users_df['call_to'].astype(str)
  for user in filtered_users:
    if user in existing_ids.values:
      active_owwlls.append(user)
  return active_owwlls

def filtered_fav(content_based_recommendations,favorite_owwlls,call_data_df):
    recommendations = []
    filtered_data = [
                item for item in content_based_recommendations
                if item != id and item not in favorite_owwlls
            ]
    for user_id in filtered_data:
             recommended = get_call_data(user_id, call_data_df)
             recommendations.append(recommended)
    return recommendations


def get_call_data(user_id, data_df):
    user_data = data_df[data_df['User_ID'] == user_id]
    profileData = {
        'Name': user_data['Name'].iloc[0] if not user_data.empty else '',
        'Title': user_data['Title'].iloc[0] if not user_data.empty else '',
        'Rating': float(user_data['Rating'].iloc[0]) if not user_data.empty else 0.0,
        'Expertise': user_data['Expertise'].iloc[0] if not user_data.empty else '',
        'Profile URL': user_data['Profile URL'].iloc[0] if not user_data.empty else '',
        'Calls Taken': int(user_data['Calls Taken'].iloc[0]) if not user_data.empty else 0,
        'Total Call Duration': float(user_data['Total Call Duration'].iloc[0]) if not user_data.empty else 0.0
    }
    if not user_data.empty:
        call_data_str = user_data['Call_Data'].iloc[0]
        call_data_list = ast.literal_eval(call_data_str)
        call_activity = {
            'ID': user_id,
            'Profile_Data': profileData,
            'Call_Data': call_data_list
        }
        return call_activity
    else:
        return {
            'ID': user_id,
            'Profile_Data': profileData,
            'Call_Data': []
        }


def get_weights():

    training_data = db['misc_meta']
    user_WEIGHTAGE = training_data.find({'category':'RECOMMEND_WEIGHTAGE'})
    result = {}
    
    for item in user_WEIGHTAGE:
        key = item['key']
        value = item['value']
        value = float(value)
        result[key] = value

    return result
    
    
def weighted_recommendations(recommendations, rating_weight, duration_weight, call_weight):
    pprint(recommendations)
    durations = [item["Profile_Data"]["Total Call Duration"] for item in recommendations]
    ratings = [item["Profile_Data"]["Rating"] for item in recommendations]
    calls_taken = [item["Profile_Data"]["Calls Taken"] for item in recommendations]
   
    min_duration = min(durations)
    max_duration = max(durations)
    min_calls = min(calls_taken)
    max_calls = max(calls_taken)
    min_rating = 1
    max_rating = 5
    
    
    if max_duration != min_duration:
        scaled_durations = [(x - min_duration) / (max_duration - min_duration) for x in durations]
    else:
        scaled_durations = [0.0] * len(durations)
        
    if max_rating != min_rating:
        scaled_ratings = [(x - min_rating) / (max_rating - min_rating) for x in ratings]
    else:
        scaled_ratings = [0.5] * len(ratings)
        
    if max_calls != min_calls:
        scaled_calls = [(x - min_calls) / (max_calls - min_calls) for x in calls_taken]
    else:
        scaled_calls = [0.5] * len(calls_taken)

    
    
    
    weighted_scores = [(rating_weight * norm_rating) + (duration_weight * norm_duration) + (call_weight * norm_calls) for norm_rating, norm_duration, norm_calls in zip(scaled_ratings, scaled_durations, scaled_calls)]

    combined_data = list(zip(recommendations, weighted_scores))

    sorted_recommendations = sorted(combined_data, key=lambda x: x[1], reverse=True)

    
    return [item[0] for item in sorted_recommendations[:25]]

