import pandas as pd
import streamlit as st
import requests
import numpy as np
import lime
import matplotlib.pyplot as plt
from datetime import date


def request_prediction(model_url, payload):
    response = requests.post(model_url, json=payload)
    
    if response.status_code != 200:
        raise Exception(
            'Request failed with status ', response.status_code, '\n', response.text
        )
    return response.json()

def NumberOfDays(date1):
    """Computes the number of days passed since a giver date"""
    return (date.today() - date1).days

URL_online = "https://scoring-oc7.herokuapp.com/getPrediction"
URL_local = "http://127.0.0.1:8000/getPrediction"

def main():

    st.title('Credit Prediction')
    id_number = st.number_input(
                label='Client ID',
                min_value=100002
        )
    id_number = int(id_number)
    show_info = st.checkbox(label='Display client details')

    submitted = st.button('Submit')

    if submitted:

        with st.spinner('Loading...'):
            
            payload = {'id': id_number}

            response = request_prediction(URL_online, payload)
            if response['Status'] == 'Error':
                st.write(response['Message'])
            
            else:

                st.write('Prediction :', response['Prediction'])
                st.write('Probability of class 0 :', response['Prediction probabilities'][0])
                st.write('Probability of class 1 :', response['Prediction probabilities'][1])
                if response['Prediction'] == 1:
                    st.write('Credit Granted')
                else:
                    st.write('Credit Denied')

                st.write('Details')

                feature_list = [i for i in response['User info']]
                names = []
                colors = []

                for i in response['Explainer list']:
                    names.append(i[0])

                for i in range(len(response['Explainer map']['Feature_idx'])):
                    colors.append('green' if response['Explainer map']['Scaled_value'][i] > 0 else 'red')

                values = [i for i in response['Explainer map']['Scaled_value']]


                names.reverse()
                values.reverse()
                colors.reverse()

                fig = plt.figure(figsize=(12, 8))

                plt.barh(range(len(names)), values, tick_label=names, color=colors)
                plt.title('Most impactful parameters')

                plt.grid()
                st.pyplot(fig)

                st.write('Details')

                j=1
                fig = plt.figure(figsize=(12, 7))
                for i in response['Distributions']:
                    ax = fig.add_subplot(2, 3, j)
                    h = ax.hist(response['Distributions'][i], bins=40)
                    plt.axvline(response['User info'][i][str(id_number)], c='k')
                    ax.set_title(i)
                    j += 1

                st.pyplot(fig)


                if show_info:
                    st.write('Client Details:')

                    st.json(response['User info'])

            st.success('Completed')    

            

        
if __name__ == '__main__':
    main()