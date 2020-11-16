# -*- coding: utf-8 -*-
"""
Created on Tue May 12 07:34:01 2020

@author: goury
"""


################################# imported module ###################################

import re , tweepy
import bs4,requests
import subprocess, sys


from tweepy import OAuthHandler 
from textblob import TextBlob 
from matplotlib import pyplot as plt
from tkinter import *
from tkinter import ttk
from threading import Thread
from numpy import array
import os as os 
import config 


class TwitterClient(): 
    """ A class that initializes an instance with access to our keys as well as other functions
    to collect tweets, make the necessary changes and vizualize them """
    
    
    #The constructor: 
    
    def __init__(self): 
        
        consumer_key = "kOAsy1vHb4bJayFm35hpHu3GG"
        
        consumer_secret = "Es9xPRLAyXgvJkW1ja8TZ2OlQCaBaalFL2TD0TAdh5gBtl6qFE"
        
        access_token = "1259998253195673600-KCceUzT5YxQerdc3Q1FCCBYDLgDbkq"
        
        access_token_secret = "a9fRvYcxOfJmi8JGwJZ3e84hMJ5ReyXfnbsFQ6Rz9qrLi"

        #The parameters of our instances:
        
        #A list in which we put the polarity of the tweet; positive, negative or neutral 
        self.polarity = []
        
        #Variable to count the number of tweets, it is initialized to 0
        self.count = 0
        
        #search query 
        self.query = ''
        
        #Positive, negative and neutral variables to measure 
        #the polarity rate in a tweet, they are initialized to 0
        self.positive = 0
        self.negative = 0
        self.neutral = 0

        # attempt authentication 
        try: 
            
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        
        except: 
            
            print("Error: Authentication Failed") 

    def clean_tweet(self, tweet): 
        
        #Take off the unwanted characters off the tweet
        
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()) 

    #TextBlobis a Python library for processing textual data , 
    #here used for sentiment analysis
    def get_tweet_sentiment(self, tweet): 
 
        analysis = TextBlob(self.clean_tweet(tweet))
        self.polarity.append(analysis.sentiment.polarity)
        

        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            
            return 'positive'
        
        elif analysis.sentiment.polarity == 0: 
            
            return 'neutral'
        
        else: 
            
            return 'negative'

    def get_tweets(self): 

        # a list of dictionaries that conatines tweet details
        tweets = []

        try: 
            
            # call twitter api to fetch tweets 
            fetched_tweets = self.api.search(q = self.query, count = self.count)
            #Return all the information availble on tweet , such as user id , date ,location,
            #tweet text ... de type _json 

            # parsing tweets one by one 
            for tweet in fetched_tweets:
                #print(tweet)
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {} 

                # saving text of tweet 
                parsed_tweet['text'] = tweet.text
                
                # saving sentiment of tweet 
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                
                # saving followers of tweet
                parsed_tweet['followers']=tweet.user.followers_count
                
                # saving date of tweet
                parsed_tweet['Date']=tweet.created_at
                
                # saving likes of tweet
                parsed_tweet['Likes']=tweet.user.favourites_count
                
                #parsed_tweet['Names']=tweet['user']
                
                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0: 
                    
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        
                        tweets.append(parsed_tweet) 
                
                else: 
                    
                    tweets.append(parsed_tweet)
            #print(tweets)
            return tweets 

        except tweepy.TweepError as e: 
            
            # print error (if any) 
            print("Error : " + str(e))

            f = open("logbook.txt","a")

            f.write("\n"+str(e))

            f.close()
    
    
    #Pie-plot to represent tweet polarity as a function of numb er of tweets

    def plotPieChart(self):

        labels = ['Positive {:.2f} %'.format(self.positive) , 'Neutral {:.2f} %'.format(self.neutral) ,'Negative {:.2f} %'.format(self.negative)]
        
        sizes = [self.positive, self.neutral, self.negative]
        
        colors = ['purple', 'pink', 'violet']

        
        plt.figure(1)
        
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        
        plt.legend(patches, labels, loc="best")
        
        plt.title('pie - chart')
        
        plt.axis('equal')
        plt.title(' tweets as a function of polarity')
        
        plt.show()
        
    #Scatter-plot to represent tweets as a function of followers

    def scatter_plot(self):
            tweets = self.get_tweets()
            
            follower=[]
            
            for tweet in tweets:
                follower.append(tweet['followers'])
            
            #print(follower)
            
            fig = plt.figure(2)
            #plt.subplot(211)
            
            x= array(follower)
            #y= max(x)
            #plt.bar(y,x, width=0.8, align='center')
            plt.plot(x)
            
            plt.xlabel('tweet number')
            
            plt.ylabel('followers')
            plt.title(' tweets as a function of followers')
            
            plt.show()
            
    #Histogram-plot to represent tweets as a function of date
        
    def plothistogram(self):
         
        tweets = self.get_tweets()
        
        date1=[]
        
        for tweet in tweets:
             tweet['Date']=tweet['Date'].strftime("%H:%M:%S")
             date1.append(tweet['Date'])
         #print(date1)
         
         
        plt.figure()

        plt.hist(date1,bins=7, color ='green',edgecolor = 'red', hatch = '/', histtype = 'barstacked')
        plt.ylabel('number of tweets ')
        
        plt.xlabel('date')
        plt.title(' tweets as a function of date')

        plt.show()

#Cleartag is a fucntion to clear the search bar

def cleartag():
    
    tag.delete(0,END)
    
#Select the tweet number to search 

def Select_number_of_tweets(event = None):

    return number_of_tweets.get()

#Select the most trending topics

def Select_trending_topic(event = None):

    api.query = str(topic.get())

    tag.delete(0,END)

    tag.insert(0,api.query)



def main(): 

    #Select the tag entered by the user 
    user_input = str(tag.get())
    
    #We make sure we have a word not a letter!
    
    if(len(user_input)<2):
        
        raise ValueError("Please Enter a word!")
        
    #We select the word to search and the number of tweets setting polarity to an empty list

    api.query = str(user_input)

    api.count = Select_number_of_tweets()

    api.polarity = []
    
    #In this part , we will display our the results of Yas&ChaApp Interface
    #Let's begin
    
    Label(frame,text="Welcome to Yas&ChaApp ").grid(row=0,column=1)
    
    chaine ="The #tag to search : "+str(api.query)+" , Number of tweets to fetch : "+str(api.count)
    
    Label(frame,text=chaine).grid(row=1,column=1)

    search_button.config(text = "fetching..")
    
    #State is disabled so the user won't be able to press the button untill the work is done
    search_button.config(state = DISABLED)

    clear_button.config(text = "Wait")
    
    clear_button.config(state = DISABLED)
    
    # calling function to get tweets 
    tweets = api.get_tweets()
    
    tweets = sorted(tweets, key=lambda k: k['Likes'], reverse=True)
    
    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
    
    # percentage of positive tweets 
    api.positive = 100*len(ptweets)/len(tweets)
    
    #print("Positive tweets percentage: {:.2f} %".format(api.positive))
    
    Label(frame,text="Positive tweets percentage: {:.2f} %".format(api.positive)).grid(row=2,column=1)
    

    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
    
    
    # percentage of negative tweets
    api.negative = 100*len(ntweets)/len(tweets)
    
    #print("Negative tweets percentage: {:.2f} %".format(api.negative)) 
    Label(frame,text="Negative tweets percentage: {:.2f} %".format(api.negative)).grid(row=3,column=1)

    nttweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral'] 
    
    # percentage of neutral tweets 
    api.neutral = 100 - api.positive - api.negative
    
    #print("Neutral tweets percentage: {:.2f} %".format(api.neutral)) 
    Label(frame,text="Neutral tweets percentage: {:.2f} %".format(api.neutral)).grid(row=4,column=1) 
    
    Label(frame,text="Positive tweets:").grid(row=5,column=1)
     
    i=7
    
    # printing first 10 negative tweets
    for tweet in ptweets[:10]: 
        
        sh="Tweet : "+str(tweet['text'])+"\n Number of followers :"+str(tweet['followers'])+"\nLikes :"+str(tweet['Likes'])+ "\n Date : "+str(tweet['Date'])

        i+1
        
        Label(frame,text=sh).grid(row=i+3,column=1)
        
        i+=1
        
        j=i
        
    # printing first 10 negative tweets 
    
    Label(frame,text="Negative tweets:").grid(row=j+3,column=1)
    
    k=j+4
    
    for tweet in ntweets[:10]:
        
        sh="Tweet : "+str(tweet['text'])+"\n Number of followers :"+str(tweet['followers'])+"\nLikes :"+str(tweet['Likes'])+ "\n Date : "+str(tweet['Date'])
        
        k+=2
        
        Label(frame,text=sh).grid(row=k,column=1)
        
        k+=1
        
    # printing first 10 neutral tweets 
    
    Label(frame,text="\n\nNeutral tweets:").grid(row=k+3,column=1)
    
    l=k+4
    
    for tweet in nttweets[:10]:
        
        sh="Tweet : "+str(tweet['text'])+"\n Number of followers :"+str(tweet['followers'])+"\nLikes :"+str(tweet['Likes'])+ "\n Date : "+str(tweet['Date'])
        
        l+=2
        
        Label(frame,text=sh).grid(row=l,column=1)
        
        l+=1

    #After finishing the searching and writing work we set our buttons to normal

    search_button.config(text = "Search")
    
    search_button.config(state = NORMAL)

    clear_button.config(text = "Clear")
    
    clear_button.config(state = NORMAL)

#Threads. When an application is launched, the system creates a thread 
#of execution for the application, called "main." 
#This thread is very important because it is in charge of dispatching events
#to the appropriate user interface widgets, including drawing events

def main_thread():

    thread = Thread(target = main)
    
    thread.start()

def get_html(url):

    #requests is a module that helps us getting a web page from an url
    
    response = requests.get(url)

    return response

#get_detail returns trendings hashtags collected from the official site of twitter

def get_detail():

    try:

        url = "https://trends24.in/"

        response = get_html(url)
        
        #The BeautifulSoup constructor function takes in two string arguments:

        #The HTML string to be parsed.
        # The name of a parser.

        bs = bs4.BeautifulSoup(response.text,'html.parser')
        
        #
        #find_all() method which returns a collection of elements

        tag = bs.find("div",class_ = "trend-card").find_all("a")

        trending = []

        for i in tag:

            trending.append(i.get_text())

        return trending

    except Exception as e:
        
        print(e)

        f = open("logbook.txt","a")

        f.write("\n"+str(e))

        f.close()



def open_twitter():

    twitter_url = "https://twitter.com/"

    if sys.platform.startswith('linux'):
        
        subprocess.Popen(['xdg-open', twitter_url],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    elif sys.platform.startswith('win32'):
        
        os.startfile(twitter_url)
    
    elif sys.platform.startswith('cygwin'):
        
        os.startfile(twitter_url)
    
    elif sys.platform.startswith('darwin'):
        
        subprocess.Popen(['open', twitter_url],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        
        subprocess.Popen(['xdg-open', twitter_url],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  

if __name__ == "__main__": 

    # calling main function 

    # creating object of TwitterClient Class 
    api = TwitterClient()
    
    #Creating our interface
    root = Tk()

    #Title
    root.title("Yas&ChaApp")

    #Fixed size
    root.geometry("900x800")
    
    root.resizable(width = False , height = False)
    
    root.configure(background = "salmon1")

    label1 = Label(root,text="Yas&ChaApp",fg="salmon3",bg="plum2",font=("",15,"bold"))
    
    label1.pack(side=TOP,pady=20)
    
    #TopFrame for Twitter link and trending tags

    topframe = Frame(root,background="salmon1")
    
    topframe.pack()

    twitter_button = Button(topframe,text='Open Twitter',command = open_twitter)

    twitter_button.pack(side = LEFT,padx = (100,60))

    frame = Frame(topframe,background="salmon1")

    frame.pack(side = LEFT)

    label6 = Label(frame,text="TOP SUBJECTS",fg="pink",bg="salmon3",font=("",12,"bold"))

    label6.pack(side = TOP , pady = 10)
    
    #Tkinter Combobox est la liste déroulante dans laquelle l’utilisateur peut choisir.
    #C’est une combinaison de Entry et de widgets drop-down

    topic = StringVar()

    trending_topics = ttk.Combobox(frame , textvariable = topic , width = 20, height = 10)

    #tmp = ["game","movies","politics","lockdown","bitcoin"]

    trending_topics['values'] = get_detail()

    trending_topics.pack()

    trending_topics.current(0)
    
    #Here we link the Select_number_of_tweets function with 
    #the combobox virtual event when the user selects an item from the drop-down list.

    trending_topics.bind("<<ComboboxSelected>>",Select_trending_topic)

    label3 = Label(root,text="Enter #tag ",fg="pink",bg="salmon3",font=("",12,"bold"))
    
    label3.pack(side=TOP,pady=10)

    tag = Entry(root,justify=CENTER,font = ("verdana","15","bold"))
    
    tag.pack(side = TOP)
    
    #MiddleFrame  
    middleframe = Frame(root,background="salmon1")
    
    middleframe.pack()

    search_button = Button(middleframe,text="Search",fg="white",bg="Indianred1",height=1,width=10,font=("verdana",10,"bold"),command = main_thread)
    
    search_button.pack(side = LEFT,padx=5,pady=5)

    clear_button = Button(middleframe,text="Clear",fg="white",bg="Indianred1",height=1,width=10,font=("verdana",10,"bold"),command = cleartag)
    
    clear_button.pack(side = LEFT,padx=5,pady=5)

    label4 = Label(root,text="Select the number of tweets to search",fg="pink",bg="salmon3",font=("",12,"bold"))
    
    label4.pack(side=TOP,pady=10)

    Values = (50,75,100,150,200,250,500,750,1000)

    number_of_tweets = IntVar() 

    choices = ttk.Combobox(root,textvariable = number_of_tweets,height=10)

    choices['values'] = Values
    
    choices.pack()

    choices.current(2)

    choices.bind("<<ComboboxSelected>>",Select_number_of_tweets)

    #label5 = Label(root,text="Select appropriate diagram to dislpay ",fg="pink",bg="salmon3",font=("",12,"bold"))
    
    #label5.pack(side=TOP,pady=10)

    #BottomFrame 
    bottomFrame = Frame(root,background="salmon1",width=700,height=150)
    
    bottomFrame.pack(side = TOP,pady = 20)

    piechart_button = Button(bottomFrame,text = 'Pie plot',command = api.plotPieChart)
    
    piechart_button.pack(side = LEFT,padx=20)

    scatterplot_button = Button(bottomFrame,text = 'Scatter plot',command = api.scatter_plot)
    
    scatterplot_button.pack(side = LEFT,padx=20)

    histogram_button = Button(bottomFrame,text = 'Plothistogram',command = api.plothistogram)
    
    histogram_button.pack(side = LEFT,padx=20)
    
    #LowerFrame for the dispaly box
    lower_frame = Frame(root, bg='maroon4', bd=10)
    
    lower_frame.place(rely=0.53, relwidth=1, relheight=0.3)

    label = Label(lower_frame,anchor='nw',justify='left')
    
    label.place(relwidth=1, relheight=1)
    
    
    #Scrollbar function
    def myfunction(event):
        
        canvas.configure(scrollregion=canvas.bbox("all"),width=200,height=200)
    
    canvas = Canvas(lower_frame)
    
    frame=Frame(canvas)
    
    myscrollbar=Scrollbar(lower_frame,orient="vertical",command=canvas.yview)
    
    canvas.configure(yscrollcommand=myscrollbar.set)

    myscrollbar.pack(side="right",fill="y")
    
    canvas.place(relwidth=1, relheight=1)
    
    canvas.create_window((0,0),window=frame,anchor='nw')
    
    frame.bind("<Configure>",myfunction)
    
    #Closing our window using a button
    def close_window (): 
    
        root.destroy()

    QuitFrame=Frame(root, bg='pink')
    
    QuitFrame.place(rely=0.3,relx=0.86, relwidth=0.13, relheight=0.04)
    
    button = Button ( QuitFrame, text = "See you Next Time !", bg='blue', fg='white', command = close_window)
    
    button.pack(side='right')
        
    root.iconbitmap(r'C:\Users\goury\Downloads\favicon.ico')

    root.mainloop()