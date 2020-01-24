# Demo for Yelp Recommendation System

A flask app written in python to show an example of a recomendation system in action

## Using the demo
The app itself is hosted on Heroku and can be found at https://yelp-rec-demo.herokuapp.com/

### User History
The review history section classifies the user based on how other users respond to their written reviews.To use this demo, decide how many times you think reviews you have written would be tagged by other users as either funny, useful, or cool, with low numbers meaning fewer tags and higher numbers meaning more tags.

For example, if I thought my reviews would be not be cool, they would be around the middle of funny, and would be almost the most useful, I would select numbers around 1 (out of 4) for cool, 2 (out of 4) for funny and 6 (out of 7) for useful.

### Ratings History
This section classifies the type of businesses the user likes based on their ratings history. For this part of the demo, the user should input an estimate of what the would rate each business, from 1 to 5 stars. Basing this on business names is fine, but here are some short decriptions of the restaurants:

+ Yagyu is a hip ramen noodle restaurant
+ KUMI by Chef Akira Back is a fine dining asian fusion restaurant
+ Vince Neil's Tatuado | Eat, Drink, Party is a bar/restaurant with an 80's metal theme
+ Mr G's Pub & Grub is an american style pub
+ RA Sushi Bar Restaurant is an authentic sushi bar

### Results
After a few seconds the demo will return a selection of links to the yelp pages for five restaurants that it thinks that you would like based on your input. The first column contains a link the the yelp page, and the second column has the estiamte of how you would rate this restaurant, out of five stars.

## Repository contents

[app.py](../app.py) contains the majority of the code for the recomendation algorithm and the flask app.


