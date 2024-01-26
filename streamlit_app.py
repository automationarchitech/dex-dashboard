import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Constants
API_URL = 'https://api.geckoterminal.com/api/v2/networks/new_pools?page=1'
HEADERS = {'accept': 'application/json'}

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
    price_changes_24h = [float(change['h24']) if change['h24'] else 0 for change in df['price_change_percentage']]
    fig, ax = plt.subplots()
    ax.barh(pool_names, price_changes_24h, color='skyblue')
    ax.set_xlabel('Price Change Percentage (24h)')
    ax.set_title('Price Change Percentage (24h) by Pool')
    if log_scale:
        ax.set_xscale('log')
    plt.tight_layout()
    return fig

# Main app code
st.title('Cryptocurrency Pool Data Viewer')

# Fetch and process data
raw_data = fetch_data(API_URL, HEADERS)
if raw_data:
    df = process_data(raw_data)

    # Display data table
    st.write("Data Overview", df)

    # Toggle for log scale
    log_scale = st.checkbox('Use logarithmic scale for Price Change Percentage')

    # Visualization: Bar Chart for Price Change Percentage
    st.subheader("Price Change Percentage (24h)")
    if 'price_change_percentage' in df.columns:
        fig_price_change = plot_price_change(df, log_scale=log_scale)
        st.pyplot(fig_price_change)

    # Visualization: Pie Chart for Transaction Types
    st.subheader("Transaction Type Distribution (Last Hour)")
    if 'transactions' in df.columns:
        fig_transactions = plot_transaction_types(df)
        st.pyplot(fig_transactions)
