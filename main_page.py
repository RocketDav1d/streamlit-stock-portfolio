import streamlit as st
import time
from calendar import c
from re import I
from urllib import response
import os
from datetime import datetime, timedelta
import pandas as pd
from lemon import api
from dotenv import load_dotenv
import datetime
from datetime import date, timedelta
import csv
import plotly.express as px

load_dotenv()
TRADING_API_KEY = os.environ.get("TRADING_API_KEY")
MARKET_API_KEY = os.environ.get("MARKET_API_KEY")
client = api.create(
    market_data_api_token=MARKET_API_KEY,
    trading_api_token=TRADING_API_KEY,
    env='paper' 
)
response = client.trading.positions.get()
number_positions = len(response.results)

st.title('Stock Portfolio 🤑📈')


placeholder = st.empty()
placeholder_1 = st.empty()


def dataset():
    while True:
        while True:
            #--------- numbers -----------
            response = client.trading.positions.get()
            temp_portfolio_value = []
            temp_total_investment_value = []

            for i in response.results:
                temp_portfolio_value.append(i.estimated_price_total)
                portfolio_value = sum(temp_portfolio_value)

                temp = (i.buy_price_avg * i.quantity)
                temp_total_investment_value.append(temp)
                total_investment_value = sum(temp_total_investment_value)


            gain_loss = total_investment_value - portfolio_value
            percentage_gain_loss = (gain_loss / total_investment_value) * 100

            portfolio_value = (str(portfolio_value)[:4] + "." + str(portfolio_value)[4:] + "€")
            total_investment_value = (str(total_investment_value)[:4] + "." + str(total_investment_value)[4:] + "€")
            gain_loss = (str(gain_loss)[:4] + "." + str(gain_loss)[4:] + "€")
            percentage_gain_loss =  (str(round(percentage_gain_loss)) + " %")

            
        #-----------table --------------

            quotes = client.market_data.quotes.get_latest(
            isin=[x.isin for x in response.results]
            )
            current_prices = [i.b_v for i in quotes.results]

            yesterday_close = client.market_data.ohlc.get(
                    isin=[x.isin for x in response.results],
                    period='d1',
                    from_=(datetime.datetime.now() - timedelta(days=1)).isoformat(),
                    to=(datetime.datetime.now() - timedelta(days=1)).isoformat()
            )
            daily_gains = [int(x) - int(y.c) for x, y in zip(current_prices, yesterday_close.results)]
            total_gains = [int(x.buy_price_avg) - int(y) for x, y in zip(response.results, current_prices)]


            dict = {
                    "isin": [x.isin for x in response.results], 
                    "quantity": [x.quantity for x in response.results], 
                    "average buy-in price": [x.buy_price_avg for x in response.results], 
                    "total value": [x.estimated_price_total for x in response.results], 
                    "current price": [x for x in current_prices], 
                    # "daily gain": [x for x in daily_gains],
                    "total gain": [x for x in total_gains]
                    }



            
            with placeholder.container():
                
                p_v, t_i, g_l= st.columns(3)

                p_v.metric(label="Portfolio Value", value=portfolio_value, delta=None)
                t_i.metric(label="Total Investment", value=total_investment_value, delta=None)
                g_l.metric(label="Gain / Loss", value=gain_loss, delta=percentage_gain_loss, delta_color="normal")

                st.table(dict)


                time.sleep(10)






today = date.today()
isins = [x.isin for x in response.results]
prices_dict = {}
dates_dict = {}



with st.form("form1"):
    from_date = st.date_input(
        "From",
        datetime.date.today()
    )
    to_date = to_date = st.date_input(
        "To",
        datetime.date.today()
        )
    submit = st.form_submit_button(label="submit")

from_date_outside_loop = from_date


def update_chart(from_date, to_date):
        if ((to_date - from_date).days < 60):
            for isin in isins:
                ohlc_response = client.market_data.ohlc.get(
                    isin=isin,
                    period='d1',
                    from_=from_date,
                    to=to_date
                    )
                temp_prices = []
                temp_dates = []
                for i in ohlc_response.results:
                    temp_prices.append(i.c)
                    temp_dates.append(i.t.date())

                prices_dict[isin] = temp_prices
                dates_dict[isin] = temp_dates
        else:
                    for isin in isins:
                        print(isin)
                        while True:
                            print(from_date)
                            ohlc_response = client.market_data.ohlc.get(
                            isin=isin,
                            period='d1',
                            from_=from_date,
                            to=from_date + timedelta(days=60)
                            )

                            temp_prices = []
                            temp_dates = []

                            for i in ohlc_response.results:
                                temp_prices.append(i.c)
                                temp_dates.append(i.t.date())

                            if isin in prices_dict.keys() and dates_dict.keys():
                                prices_dict[isin] = [*prices_dict[isin], *temp_prices]
                                dates_dict[isin] = [*dates_dict[isin], *temp_dates]
                            else:
                                prices_dict[isin] = temp_prices
                                dates_dict[isin] = temp_dates

                            from_date += timedelta(days=60)

                            if (to_date - from_date).days < 60: 
                                ohlc_response = client.market_data.ohlc.get(
                                isin=isin,
                                period='d1',
                                from_=from_date,
                                to=to_date
                                )
                                temp_prices = []
                                temp_dates = []

                                for i in ohlc_response.results:
                                    temp_prices.append(i.c)
                                    temp_dates.append(i.t.date())

                                prices_dict[isin] = [*prices_dict[isin], *temp_prices]
                                dates_dict[isin] = [*dates_dict[isin], *temp_dates]

                                from_date = from_date_outside_loop
                                
                                break



        prices_times_quantity_dict = {}
        for position in response.results:
            for c_list in prices_dict.values():
                temp_list = []
                for closing_price in c_list:
                    total_daily_value_of_instrument = closing_price * position.quantity
                    temp_list.append(total_daily_value_of_instrument)

                prices_times_quantity_dict[position.isin] = temp_list
        dict_by_index = {}
        for instrument in prices_times_quantity_dict.values():
            for index, closing_price in enumerate(instrument):
                temp_list = []
                temp_list.append(closing_price)
                if index in dict_by_index.keys():
                    dict_by_index[index] = [*dict_by_index[index], *temp_list]
                else:
                    dict_by_index[index] = temp_list
        portfolio_values_of_all_instruments = []
        for instrument in dict_by_index.values():
            portfolio_values_of_all_instruments.append(sum(instrument))



        with open("data.csv", 'w') as f:
            # create the csv writer
            writer = csv.writer(f)

            writer.writerow(["dates", "Portfolio Performance"])

            for i in range(len(portfolio_values_of_all_instruments)):
                writer.writerow([dates_dict["DE0007664039"][i], portfolio_values_of_all_instruments[i]])

        df = pd.read_csv('data.csv')
        print(df)

        fig = px.line(df, x='dates', y="Portfolio Performance")

        with placeholder_1.container():
            st.plotly_chart(figure_or_data=fig)



if submit:
    update_chart(from_date=from_date, to_date=to_date)
dataset()





