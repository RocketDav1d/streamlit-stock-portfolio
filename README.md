## streamlit stock portfolio 📈🤑

Get a glimpse of the running version here:
https://rocketdav1d-streamlit-stock-portfolio-main-page-uieq9e.streamlitapp.com/

You can find an article explaining the portfolio here

<<<<<<< HEAD
If you take a look at main_page.py you find that it mainly consits of two functions which get called at the end of the program.
Let's take a look at how these two functions work in more detail


##Metrics and Dataframe##

![](images/metrics%20%26%20dataframe.png)

####Metrics####

First of all we look at how to create the 3 metrics (Portfolio Value, Total Investment, Gain / Loss)

We start by making the get request to the positions endpoint. We then loop trough our response results in a for loop and append the data to some temporary lists. 

We only need temporary lists for the Portfolio Value and Total Investment as we can calculate Gain/Loss and Percentage Gain/Loss using those two metrics.

Then we use sum() to get the sum of all values in temp_portfoio_value and temp_total_investment_value in order to get the overall portfolio value and total investment value. 

Finally we can then calculate gain/loss and percentage gain/loss.

As a last step we then prettify the data by turning the integers into strings and adding commas as well as € and %.


####Dataframe####

Now let’s have a look at how we can create the dataframe. We are still in the same while loop inside the same function. For some of the numbers inside our dataframe we can use the data from the positions GET request above. But we also need additional data from the quotes and ohlc endpoint. 

First we use get_latest to get the bid volume for all of our positions and save it in a list called current_prices. 

Then we want the prices from yesterday and make a GET request to the ohlc endpoint. Inside the request we define our query parameters. First we specify that we want to get data from all the isin’s inside our positions. (same as in get_latest request). Then we define the period as d1, which means the data is aggregated on a daily basis. Lastly we select the fromand to date as yesterday using the datetime module.

We then want to calculate the daily gains and save them in a list. Using zip() on the current_prices and yesterday_close lists we create a list of tuples. In the first tuple is the first value from current_prices and yesterday_close and so on. We then loop through this tuple list and subtract the first item in the tuple, the current price, from the second price in the tuple which is yesterdays closing price.

Then we do the same in order to calculate total gains.

Finally we create a dictionary containing all of our data. For isin, quantity, average buy-in price and total value we can loop trough the response results of the positions endpoint (remember we’re still in the same loop as the “metrics” logic above). For current price, daily gains and total gains we respective lists we just created. 

I’m explaining why we need a dictionary soon.


You might ask yourself, how and when we are going to use streamlit to print out this data on our streamlit web page. Now! 

Here it is important to know how streamlit works when you want to constantly update information. For that we need to create a placeholder using the empty() method from streamlit OUTSIDE and ABOVE our metrics_and_dataframe function. This inserts a container into our app that can be used to hold a single element. This allows us to, for example, remove elements at any point, or replace several elements at once (using a child multi-element container 👨‍👩‍👦).


Then inside our function at the end of the while loop we use this placeholder and call the container method on it. That inserts an invisible container into our app that can be used to hold multiple elements. (this is the child multi-element container 👨‍👩‍👦 mentioned above) 

In this container we create three columns for our 3 metrics and use the metric method from streamlit to create Portfolio Value, Total Investment and Gain / Loss. We pass in percentage_gain_loss as the delta for the Gain / Loss metric.

Also we create the data table by using the table method from streamlit and put in our dictionary as the argument.


That’s it for the first part. You can already run your app to see if it works with the following command.

streamlit run main_page.py


##Graph##

![](images/portfolio%20performance%20graph%20.png)

Now we want to tackle the interactive graph. 

The graph will show the overall portfolio worth of each day. Thats why we create a dictionary in which we save all our data. The keys will be the isin’s of our positions and the values for each key will be a list containing the portfolio worth for each day. 


 Then we ask the user to select a from and to date using streamlit form and date_input methods. 

We also assign the selected from_date to a variable called from_date_outside_loop. This is necessary because we will work with and change from_date and need a variable that always stores the initial value of from_date.


Then we create the function called graph()


Now let’s take a look at whats happening here. 

When we enter the function we’ll first stumble upon an if else statement. This checks if the period between the from and to date is smaller or bigger than 60 days. With the lemon.markets you can request 60 days of data with one request, therefore the time range between from and to cannot be longer than 60 days.

1️⃣ If the period is less then 60 days the logic is quite straight forward. We loop through all the isin’s of our positions and append the results to temporary lists. Then we save this list in prices_dict and dates_dict with the isisn as the key and the list as the value.

2️⃣ Else it’s getting a bit more complicated. We also first loop trough all isin’s in our positions. But then we need a while loop to make multiple 60 day requests to the ohlc endpoint. Again we append the results to temporary lists. Different then before we now need to check if an isin and a temporay list have been saved to prices_dict and dates_dict. If yes we use the asterisks operator to save our new temp_list containing 60 days of ohlc data to the existing prices_dict and dates_dict.After that we increase from_date by 60 days each iteration and then check if the period between the from and to date is smaller than 60 days. If yes the same logic as in 1️⃣ applies and we reset from_date using the from_date_outside_loop and break out of the while loop. Now the program is in the for loop and goes into the while loop again but this time with a different isin. This continues until all isin of our positions have been looped trough.


Inside the same graph() function we then first take each closing price and multiply it with the quantity from our positions. After that we add up all closing prices from all instruments with each other and save it in a final list called portfolio_values_of_all_instruments. 

To be clear, every integer value in this list represent the total portfolio worth of one day. 


For plotting our graph we will use the line() method from plotly.express. 

This line() method takes a dataframe as input parameter. I decided to create a csv file and put it in a the input parameter but you could do the same with a pandas dataframe. 

Then we again use a placeholder variable( this variable is equal to st.empty()) and apply streamlit’s container method on it.

In the container we use streamlit’s plotly_chart() method and hand over our plotly figure as the input parameter.
