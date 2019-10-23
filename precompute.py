
test_businesses=pd.read_pickle("test_businesses")

all_business_review_dist=pd.read_pickle('business_review_dist')

user_category_lookup=pd.read_pickle('user_category_lookup')




for biz_id in sample_businesses['b.id']:

    business_review_dist=all_business_review_dist.loc[all_business_review_dist['b.id']==biz_id].drop_duplicates()

    business_review_dist.set_index('u.id',inplace=True)

    review_stars = business_review_dist['r.stars'].value_counts()
    num_reviews = business_review_dist['r.stars'].shape[0]


    user_in_cat = []

    for funny in ["funny1","funny2","funny3","funny3"]:

        all_users=user_category_lookup.loc[user_category_lookup['rep.id']==cat]
        users=business_review_dist.merge(all_users, how='inner', right_on='u.id', left_index=True )

    for funny in ["funny1","funny2","funny3","funny3"]:

        all_users=user_category_lookup.loc[user_category_lookup['rep.id']==cat]
        users=business_review_dist.merge(all_users, how='inner', right_on='u.id', left_index=True )
