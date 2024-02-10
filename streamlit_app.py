import requests
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns  # Add this line to import seaborn
import streamlit_shadcn_ui as ui

from utils import parse_crypto_pools

# Constants
API_BASE_URL = 'https://api.geckoterminal.com/api/v2'
NEW_POOLS_ENDPOINT = '/networks/new_pools?page=1'
TOKENS_ENDPOINT = '/tokens/info_recently_updated'
HEADERS = {'accept': 'application/json'}
PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/200x200.png?text=Crypto+Icon"


# Set the page to wide mode
st.set_page_config(layout="wide")

# Function to fetch recently updated token data
# @st.cache
# def fetch_token_data():
#     response = requests.get('https://api.geckoterminal.com/api/v2/tokens/info_recently_updated')
#     if response.status_code == 200:
#         return response.json()['data']
#     else:
#         st.error(f'Failed to retrieve token data. Status code: {response.status_code}')
#         return []

# Function to fetch data from the API
@st.cache_data
def fetch_data(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f'Failed to retrieve data from {url}. Status code: {response.status_code}')
        return None

# Function to process the JSON data into a DataFrame
def process_data(data):
    def flatten(d, parent_key='', sep='_'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    # Flatten each pool's attributes and create a DataFrame
    flat_data = [flatten(pool['attributes']) for pool in data['data']]
    return pd.DataFrame(flat_data)

# Function to get top 3 pairs with the greatest 1-hour volume change
def get_top_changes(df, column_name='price_change_percentage_h1'):
    # Ensure the column is of type float
    df[column_name] = df[column_name].astype(float)
    # Sort the DataFrame based on the volume change column
    top_changes = df.sort_values(by=column_name, ascending=False).head(3)
    # Include the 'transactions' column in the returned DataFrame
    return top_changes[['name', column_name, 'transactions_h1_sells', 'transactions_h1_buys']]

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

    return fig

def page_one():
    st.title('Cryptocurrency Pool Data Viewer - Page 1')
    trigger_btn = ui.button(text="Trigger Button", key="trigger_btn")
    ui.alert_dialog(show=trigger_btn, title="Alert Dialog", description="This is an alert dialog", confirm_label="OK", cancel_label="Cancel", key="alert_dialog1")
    # Main app code
    st.title('Cryptocurrency Pool Data Viewer')

    # Fetch and process data
    raw_data = fetch_data(NEW_POOLS_ENDPOINT)
    if raw_data:
        df = process_data(raw_data)

        top_volume_changes = get_top_changes(df, 'price_change_percentage_h1')

        # Display the top 3 price changes
        st.subheader('⭐️ Top 3 Pairs by 1-Hour Price Change')
        columns = st.columns(3)  # Create three columns for the top 3 changes
        for index, (col, row) in enumerate(zip(columns, top_volume_changes.iterrows())):
            with col:
                st.metric(label=row[1]['name'], value=f"{row[1]['price_change_percentage_h1']:.2f}%")
                st.text(f"Buys in last hour: {row[1]['transactions_h1_buys']}")
                st.text(f"Sells in last hour: {row[1]['transactions_h1_sells']}")


        # Create two columns for the data table and the bar chart
        col1, col2 = st.columns(2)

        with col1:
            # Display data table in the first column
            st.subheader('🏓 Data Overview')
            st.write("", df)

        with col2:
            # Visualization: Bar Chart for Price Change Percentage in the second column
            st.subheader("📊 Price Change Percentage (24h)")
            if 'price_change_percentage_h1' in df.columns:
                fig_price_change = plot_price_change(df)
                st.pyplot(fig_price_change)

def page_two():
    st.title('Cryptocurrency Token Data Viewer - Page 2')
    
    # Fetch token data
    token_data = fetch_data(TOKENS_ENDPOINT)
    if token_data:
        token_data = token_data['data']
    
    # Display each token in a separate card
    for index, token in enumerate(token_data):
        attributes = token['attributes']
        # Generate a unique key for each card, using 'id' if available, or index as a fallback
        card_key = f"card_{attributes.get('id', f'fallback_{index}')}"
        with ui.card(key=card_key):
            # Check if the image URL is valid
            image_url = attributes['image_url']
            ui.element("h4", className="text-md font-semibold", children=["GT Score"])
            ui.element("p", children=[str(attributes['gt_score'])])
            # print("Image URL:", image_url, "Status Code:", requests.head(image_url).status_code)
            if image_url and requests.head(image_url).status_code == 200:
                ui.element("img", src=image_url, className="w-48 h-48")  # Adjust the width and height as needed
            else:
                # Display a placeholder image if the image URL is not valid
                placeholder_image_url = "https://via.placeholder.com/200x200.png?text=Crypto+Icon"
                ui.element("img", src=placeholder_image_url, className="w-20 h-20")  # Adjust the width and height as needed
            
            ui.element("h3", className="text-lg font-bold", children=[attributes['name']])
            ui.element("p", children=[attributes['description']])
            
            # Display websites as links
            with ui.element("div", className="flex flex-wrap gap-2"):
                for website in attributes['websites']:
                    ui.link_button(url=website, text=website, key=f"link_{website}")
            
            ui.element("metric", label='GT Score', value=attributes['gt_score'])


# Sidebar navigation
st.sidebar.title('Navigation')
page = st.sidebar.radio('Select a page:', ['Page 1', 'Page 2'])

if page == 'Page 1':
    page_one()
elif page == 'Page 2':
    page_two()