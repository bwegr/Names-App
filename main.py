import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import ast
from pandas import json_normalize

# Assuming 'data' and 'users' are DataFrame available in your context

# Data extraction
data = pd.read_csv("https://raw.githubusercontent.com/bwegr/stat386project/main/all.csv")
users = pd.read_csv("https://raw.githubusercontent.com/bwegr/stat386project/main/users.csv")

# Function definitions
def num_and_sum(s):
    pattern = r"'count': (\d+)"
    counts = [int(num) for num in re.findall(pattern, s)]
    return sum(counts)

def convert_string_to_dict(s):
    data = ast.literal_eval(s)
    result = {'name': [], 'users': [], 'count': []}
    for item in data:
        result['name'].extend([item['name']] * item['count'])
        result['users'].extend(item['users'])
        result['count'].extend([item['count']] * item['count'])
    return result

# Streamlit App
st.title("BYU MBA Slack Data")
st.write("The visualizations below correspond to all communication in public channels of the BYU MBA Slack workspace during the month of October 2023. Use the sliders to change how many of the top users for each category you wish to see")

# Q1
num_users1 = st.slider("Select the number of top users to display", 1, 50, 10)
react1 = pd.DataFrame(data[data['reactions'].notna()][['user', 'reactions']])
react1['sum_counts'] = react1['reactions'].astype(str).apply(num_and_sum)
react1a = react1.groupby('user')['sum_counts'].sum().reset_index()

list_of_dic = react1['reactions'].astype(str).apply(convert_string_to_dict).tolist()
react2 = pd.DataFrame({'name': [], 'users': [], 'count': []})
for i in list_of_dic:
    max_length = max(len(lst) for lst in i.values())
    for key in i:
        i[key].extend([None] * (max_length - len(i[key])))
    df = pd.DataFrame(i)
    react2 = pd.concat([react2, df], ignore_index=True)

react2b = pd.merge(react2, users[['id', 'real_name']], left_on='users', right_on='id', how='left')

react2a = react2b[['real_name', 'count']].groupby('real_name').count().reset_index().sort_values(by='count', ascending=False)
paired = sorted(zip(react2a['count'][0:num_users1], react2a['real_name'][0:num_users1]))
count_s, users_s = zip(*paired)

fig, ax = plt.subplots()
ax.barh(users_s, count_s)
for index, value in enumerate(count_s):
    ax.text(value-12, index, str(value), va='center')
plt.xlabel('Messages Reacted To')
plt.ylabel('Name')
plt.title('Top Reactors (Oct 2023)')
st.pyplot(fig)

# Q2
num_emojis = st.slider("Select the number of top emojis to display", 1, 20, 10)
react2c = react2[['name', 'count']].groupby('name').count().reset_index().sort_values(by='count', ascending=False)
paired = sorted(zip(react2c['count'][0:num_emojis], react2c['name'][0:num_emojis]))
count_s, emoji_s = zip(*paired)

fig, ax = plt.subplots()
ax.barh(emoji_s, count_s)
for index, value in enumerate(count_s):
    ax.text(value - 55, index, str(value), va='center')
ax.set_ylabel('Emoji')
ax.set_title('Top Emojis (Oct 2023)')
st.pyplot(fig)




