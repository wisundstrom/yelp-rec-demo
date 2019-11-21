import time
import requests
import pandas as pd
import numpy as np
from neo4j import GraphDatabase
from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def test():
    return """
<html lang = "en">
  <head>
    <title>recinpu.html</title>
    <meta charset = "UTF-8" />
  </head>
  <body>
    <h1>Get Yelp Recommendations!</h1>
    <form method="POST"]\>
       <fieldset>
          <legend>Your Review History(be honest!)</legend>
          <p>
             <label>How cool are your reviews?</label>
             <select name = "cool">
               <option value = "cool1">one</option>
               <option value = "cool2">two</option>
               <option value = "cool3">three</option>
               <option value = "cool4">four</option>
             </select>
             <br>
             <label>How funny are your reviews?</label>
             <select name = "funny">
               <option value = "funny1">one</option>
               <option value = "funny2">two</option>
               <option value = "funny3">three</option>
               <option value = "funny4">four</option>
             </select>
             <br>
             <label>How useful are your reviews?</label>
             <select name = "useful">
               <option value = "useful1">one</option>
               <option value = "useful2">two</option>
               <option value = "useful3">three</option>
               <option value = "useful4">four</option>
               <option value = "useful5">five</option>
               <option value = "useful6">six</option>
               <option value = "useful7">seven</option>
             </select>
          </p>
       </fieldset>
       <br>
       <fieldset>
           <legend>Rate some Businesses</legend>
           <p>
              <label>Yagyu Ramen</label>
              <select name = "5yZ1XmDcOEsElDeb9PlPDQ">
                <option value = "1">one star</option>
                <option value = "2">two stars</option>
                <option value = "3">three stars</option>
                <option value = "4">four stars</option>
                <option value = "5">five stars</option>
              </select>
              <br>
              <label>KUMI by Chef Akira Back</label>
              <select name = "PL3cimEUfNHlenOGSOAdJg">
                <option value = "1">one star</option>
                <option value = "2">two stars</option>
                <option value = "3">three stars</option>
                <option value = "4">four stars</option>
                <option value = "5">five stars</option>
              </select>
              <br>
              <label>Vince Neil's Tatuado | Eat, Drink, Party</label>
              <select name = "4n81G-pmC3rfhmaPsbwYKg">
                <option value = "1">one star</option>
                <option value = "2">two stars</option>
                <option value = "3">three stars</option>
                <option value = "4">four stars</option>
                <option value = "5">five stars</option>
              </select>
              <br>
              <label>Mr G's Pub & Grub</label>
              <select name = "iwGhazq9eP51PSerTrMrwg">
                <option value = "1">one star</option>
                <option value = "2">two stars</option>
                <option value = "3">three stars</option>
                <option value = "4">four stars</option>
                <option value = "5">five stars</option>
              </select>
              <br>
              <label>RA Sushi Bar Restaurant</label>
              <select name = "R3TC2oq8fQK9c9BNMZ-ynA">
                <option value = "1">one star</option>
                <option value = "2">two stars</option>
                <option value = "3">three stars</option>
                <option value = "4">four stars</option>
                <option value = "5">five stars</option>
              </select>
          </fieldset>

       </p>
    </fieldset>
    <input type="submit" value="Submit">
    </form>

  </body>
</html>
    """

@app.route('/', methods=['POST'])
def page_input():
    uri = "bolt://3.220.233.169:7687"
    driver =0# GraphDatabase.driver(uri, auth=("neo4j", "i-0e23d19f0d8795714"))

    biz_cats=pd.read_pickle("biz_cats")


    test_businesses=pd.read_pickle("test_businesses")

    sample_businesses=test_businesses.sample(30)


    user_cat_ids = [request.form['cool'], request.form['funny'], request.form['useful']]
    ratings=[]

    for key in ['5yZ1XmDcOEsElDeb9PlPDQ','PL3cimEUfNHlenOGSOAdJg','4n81G-pmC3rfhmaPsbwYKg','iwGhazq9eP51PSerTrMrwg','R3TC2oq8fQK9c9BNMZ-ynA']:
        rating = request.form[key]
        ratings.append([key,int(rating)])

    ratings_df=pd.DataFrame(ratings, columns=['b.id','r.stars'])
    user_review_dist=ratings_df.merge(biz_cats, on='b.id')
    biz_id='Os1n1_idfw9vv9kwULGJnQ'

    business_review_dist=pd.read_pickle('business_review_dist')

    biz_category_lookup=pd.read_pickle('biz_category_lookup')


    user_category_lookup=pd.read_pickle('user_category_lookup')


    pd.set_option('display.max_colwidth', -1)

    predicted_ratings=[(predict_rating(driver, user_cat_ids, user_review_dist, business_review_dist, biz_category_lookup, user_category_lookup,x),x) for x in sample_businesses['b.id']]



    recommendations=pd.DataFrame(predicted_ratings, columns=['Predicted Rating', 'Restaurant']).sort_values('Predicted Rating', ascending=False).head()
    recommendations['Restaurant']=[f'<a href="https://www.yelp.com/biz/{x}" target="_blank">{x}</a>' for x in recommendations['Restaurant'] ]



    return recommendations.to_html(escape=False)


def predict_rating(driver, user_cat_ids, user_review_dist, business_review_dist, biz_category_lookup, user_category_lookup, biz_id):

    biz_pref = biz_preference_demo(driver, user_cat_ids, business_review_dist, user_category_lookup, biz_id)
    user_pref = user_preference_demo(driver, user_review_dist, biz_category_lookup, biz_id)
    joint_prob = (biz_pref * user_pref)/sum(biz_pref * user_pref)

    return expected_rating(joint_prob)



def cypher(driver, query, results_columns):
    """This is wrapper for sending basic cypher queries to a neo4j server. Input is a neo4j connection
    driver, a string representing a cypher queryand a list of string for data frame column names.
    returns the dataframe of the results."""

    with driver.session() as session:
        result = session.run(query)

    result_df = pd.DataFrame(result.values(), columns=results_columns)

    return result_df


def expected_rating(rating_dist):
    """this takes a distribution of probabilities by rating from one to five and returns the
    expected value of the rating"""
    runsum = 0
    for i in [1, 2, 3, 4, 5]:
        runsum += rating_dist[i - 1] * i
    return runsum

def biz_preference_demo(driver, user_cat_ids, all_business_review_dist, user_category_lookup, biz_id):

    business_review_dist=all_business_review_dist.loc[all_business_review_dist['b.id']==biz_id].drop_duplicates()

    business_review_dist.set_index('u.id',inplace=True)

    review_stars = business_review_dist['r.stars'].value_counts()
    num_reviews = business_review_dist['r.stars'].shape[0]

    user_in_cat = []



    for cat in user_cat_ids:

        all_users=user_category_lookup.loc[user_category_lookup['rep.id']==cat]

        users=business_review_dist.merge(all_users, how='inner', right_on='u.id', left_index=True )
        user_in_cat.append(users)


    reviews_in_cat = []
    for i in range(len(user_in_cat)):


        reviews_in_cat.append(user_in_cat[i]['r.stars'])


    numerator = np.empty(5)
    for i in (1, 2, 3, 4, 5):
        try:
            numerator[i - 1] = review_stars[i]
        except BaseException:
            numerator[i - 1] = 0

    PRu = (numerator + 1) / (num_reviews + 5)


    num_cat = len(user_in_cat)
    cats_by_stars = np.empty((num_cat, 5))

    for i in range(num_cat):
        if not reviews_in_cat[i].empty:
            cat_stars = reviews_in_cat[i].value_counts()
            for j in (1, 2, 3, 4, 5):
                try:
                    cats_by_stars[i][j - 1] = cat_stars[j]
                except BaseException:
                    cats_by_stars[i][j - 1] = 0



    PRaj = ((cats_by_stars + 1) / (numerator + num_cat)).prod(axis=0)

    # we now take the product of the distributions and normalize them so they
    # sum to 1
    biz_prefs_un_normalized = PRu * PRaj

    biz_prefs = biz_prefs_un_normalized/sum(biz_prefs_un_normalized)

    return biz_prefs

def user_preference_demo(driver, user_review_dist, biz_category_lookup, biz_id):

    # send a cypher query to the server that returns all of the biz's
    # categories
    categories_df=biz_category_lookup.loc[biz_category_lookup['b.id']==biz_id]
    cat_ids=set(categories_df['c.id'].values)



    # these manipulate the biz categories and user's reviews for computation
    # later
    review_stars = user_review_dist['r.stars'].value_counts()
    num_reviews = user_review_dist['r.stars'].shape[0]



    # we initialize a blank list of businesses in the biz categories
    biz_in_cat = []
    for cat in cat_ids:
        temp=[]
        for i in range(5):
            if cat in user_review_dist['cats'].iloc[i]:
                temp.append(user_review_dist['b.id'].iloc[i])

        if temp:
            biz_in_cat.append(temp)


    reviews_in_cat = []

    for i in range(len(biz_in_cat)):
        # this loop goes through each biz category and sends a cypher query to get the reviews of
        # businesses in that category by the user
        sim_biz = []

        for temp_biz in biz_in_cat[i]:

            temp_rev=user_review_dist.loc[user_review_dist['b.id']==temp_biz]

            sim_biz.append(int(temp_rev['r.stars']))


        reviews_in_cat.append(pd.DataFrame(sim_biz, columns=['r.stars']))

    # this loop and PRu below uses laplace smoothing and the distribution of user's reviews
    # to come up with naive bayes estimated probability distribution,
    # prob(review from user = k)
    numerator = np.empty(5)
    for i in (1, 2, 3, 4, 5):
        try:
            numerator[i - 1] = review_stars[i]

        except BaseException:
            numerator[i - 1] = 0

    PRu = (numerator + 1) / (num_reviews + 5)

    # the code below uses laplace smoothing and the distribution of the biz reviews to come up with
    # a naive bayes estimate of the distribution (prob review from user =
    # k|given biz in category j)
    num_cat = len(biz_in_cat)
    cats_by_stars = np.empty((num_cat, 5))

    for i in range(num_cat):
        if not reviews_in_cat[i].empty:
            cat_stars = reviews_in_cat[i]['r.stars'].value_counts()

            for j in (1, 2, 3, 4, 5):
                try:
                    cats_by_stars[i][j - 1] = cat_stars[j]
                except BaseException:
                    cats_by_stars[i][j - 1] = 0


    PRaj = ((cats_by_stars + 1) / (numerator + num_cat)).prod(axis=0)

    # we now take the product of the distributions and normalize them so they
    # sum to 1
    user_prefs_un_normalized = PRu * PRaj

    user_prefs = user_prefs_un_normalized/sum(user_prefs_un_normalized)

    timetest2=time.time()

    return user_prefs
