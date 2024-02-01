import requests
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns  # Add this line to import seaborn

from utils import parse_crypto_pools

# Constantss
API_URL = 'https://api.geckoterminal.com/api/v2/networks/new_pools?page=1'
HEADERS = {'accept': 'application/json'}

# Set the page to wide mode
st.set_page_config(layout="wide")

# Function to fetch data from the API
@st.cache_data
def fetch_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f'Failed to retrieve data. Status code: {response.status_code}')
        return None

# Function to process the JSON data into a DataFrame
def process_data(data):
    return pd.DataFrame([pool['attributes'] for pool in data['data']])

# Function to get top 3 pairs with the greatest 1-hour volume change
def get_top_volume_changes(df, column_name='price_change_percentage_h1'):
    # Ensure the column is of type float
    df[column_name] = df[column_name].astype(float)
    # Sort the DataFrame based on the volume change column
    top_changes = df.sort_values(by=column_name, ascending=False).head(3)
    return top_changes[['name', column_name]]

# Function to create a pie chart for transaction types
def plot_transaction_types(df):
    trans_types = pd.DataFrame(df['transactions'].tolist()).h1.apply(pd.Series)
    buys = trans_types['buys'].sum()
    sells = trans_types['sells'].sum()
    fig, ax = plt.subplots()
    ax.pie([buys, sells], labels=['Buys', 'Sells'], autopct='%1.1f%%')
    plt.tight_layout()
    return fig

def plot_price_change(df, log_scale=False):
    pool_names = df['name']
    # Directly use the float values from the series
    price_changes_24h = [float(change) if change else 0 for change in df['price_change_percentage_h1']]
    fig, ax = plt.subplots()
    sns.barplot(x='price_change_percentage_h1', y='name', data=df, ax=ax)
    ax.set(xlabel='Price Change Percentage (24h)', title='Price Change Percentage (24h) by Pool')
    if log_scale:
        ax.set_xscale('log')
    # Add tooltips using mplcursors
    import mplcursors
    mplcursors.cursor(hover=True)
    plt.tight_layout()
    return fig

# Main app code
st.title('Cryptocurrency Pool Data Viewer')

# Fetch and process data
raw_data = fetch_data(API_URL, HEADERS)
if raw_data:
    df = pd.DataFrame(parse_crypto_pools(raw_data))

    top_volume_changes = get_top_volume_changes(df)

    # Display the top 3 volume changes
    st.subheader('Top 3 Pairs by 1-Hour Volume Change')
    for index, row in top_volume_changes.iterrows():
        st.metric(label=row['name'], value=f"{row['price_change_percentage_h1']:.2f}%")


    # Create two columns for the data table and the bar chart
    col1, col2 = st.columns(2)

    with col1:
        # Display data table in the first column
        st.write("Data Overview", df)

    # # Toggle for log scale
    # log_scale = st.checkbox('Use logarithmic scale for Price Change Percentage')

    with col2:
        # Visualization: Bar Chart for Price Change Percentage in the second column
        st.subheader("Price Change Percentage (24h)")
        if 'price_change_percentage_h1' in df.columns:
            fig_price_change = plot_price_change(df)
            st.pyplot(fig_price_change)
