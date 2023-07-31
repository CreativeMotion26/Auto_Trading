from sqlalchemy import null
from textblob import TextBlob
import pandas as pd
import tweepy
import slack
import requests

# Get the Twitter API Credentials 
api_key = "Your_api_key"
api_key_secret = "your_secret_key"
access_token = "your_access_token"
access_token_secret = "your_secret_token"

# Create the authentication object 
authenticator = tweepy.OAuthHandler(api_key, api_key_secret)
authenticator.set_access_token(access_token, access_token_secret)
api = tweepy.API(authenticator, wait_on_rate_limit=True)


#Gather the 2000 tweets about Bitcoin and filter out any retweets 'RT'

search_term = '#bitcoin -filter:retweets'

#crypto_coin = "bitcoin"
#search_term = f'{crypto_coin} -filter:retweets'

#Create a Cursor object
tweets = tweepy.Cursor(api.search_tweets, q= search_term, lang="en", tweet_mode="extended").items(30)
#Store the tweets in a variable and get the full text
all_tweets = [tweet.full_text for tweet in tweets]
slack.post_message(slack.myToken,"#trading-notice","Analysis 50 Tweets")

df = pd.DataFrame(all_tweets, columns=['Tweets'])

def cleanTwt(twt):
    twt = re.sub('#[A-Za-z0-9]+', '', twt) # Remove any strings with a '#'
    twt = re.sub('\\n', '', twt) # Removes the '|\n' string 
    twt = re.sub('https?:\/\/\S+', '', twt) # Removes any hyerlinks 
    return twt 

df['Cleaned_Tweets'] = df['Tweets'].apply(cleanTwt)
print (df['Cleaned_Tweets'])
#slack.post_message(slack.myToken,"#trading-notice","top 5 tweets")
#slack.post_message(slack.myToken,"#trading-notice",df['Cleaned_Tweets'][0])
#slack.post_message(slack.myToken,"#trading-notice",df['Cleaned_Tweets'][1])
#slack.post_message(slack.myToken,"#trading-notice",df['Cleaned_Tweets'][2])
#slack.post_message(slack.myToken,"#trading-notice",df['Cleaned_Tweets'][3])
#slack.post_message(slack.myToken,"#trading-notice",df['Cleaned_Tweets'][4])

def getSubjectivity(twt):
  return TextBlob(twt).sentiment.subjectivity
def getPolarity(twt):
  return TextBlob(twt).sentiment.polarity

df['subjectivity'] = df['Cleaned_Tweets'].apply(getSubjectivity)
df['Polarity'] = df['Cleaned_Tweets'].apply(getPolarity)

score = null
def getSentiment(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Nutral'
    else:
        return 'Positive'

df['Sentiment'] = df['Polarity'].apply(getSentiment) #and df['subjectivity'] < 0.3
senti = df['Sentiment']
sub = df['subjectivity']
'''
positive = 0
negative = 0
nutral = 0
for i in df['Sentiment']:
      if senti[i] == 'Positive':
        positive += 1
      elif senti[i] == 'Negative':
        negative += 1
      else:
        nutral += 1
          
print("postive", positive)
print("negative", negative)
'''

if 'positive' > 'negative' :
    print ("Statment: Postitive")
    slack.post_message(slack.myToken,"#trading-notice","Statment: Postitive")
else:
    print ("Statement: Negative")
    slack.post_message(slack.myToken,"#trading-notice","Statment: negative")



