import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import ast
from pandas import json_normalize
import networkx as nx

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
st.markdown("### **Who Reacts Most?**")
num_users1 = st.slider("Select the number of top users to display", 1, 30, 10, key="q1")
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
plt.title('Top Reactors')
st.pyplot(fig)

# Q2
st.markdown("### **What are the most popular emojis?**")
num_emojis = st.slider("Select the number of top emojis to display", 1, 20, 10, key="q2")
react2c = react2[['name', 'count']].groupby('name').count().reset_index().sort_values(by='count', ascending=False)
paired = sorted(zip(react2c['count'][0:num_emojis], react2c['name'][0:num_emojis]))
count_s, emoji_s = zip(*paired)

fig, ax = plt.subplots()
ax.barh(emoji_s, count_s)
for index, value in enumerate(count_s):
    ax.text(value - 55, index, str(value), va='center')
ax.set_ylabel('Emoji')
ax.set_title('Top Emojis')
st.pyplot(fig)

# Q3
st.markdown("### **Who generates the most reactions?**")
num_users2 = st.slider("Select the number of top users to display", 1, 30, 10, key="q3a")
react1b = pd.merge(react1a, users[['id', 'real_name']], left_on='user', right_on='id', how='left')
react1c = react1b.sort_values(by='sum_counts', ascending=False)
paired = sorted(zip(react1c['sum_counts'][0:num_users2], react1c['real_name'][0:num_users2]))
count_s, user_s = zip(*paired)

fig, ax = plt.subplots()
ax.barh(user_s, count_s)
for index, value in enumerate(count_s):
    ax.text(value - 35, index, str(value), va='center')
ax.set_ylabel('Name')
ax.set_title('Top Reaction Generators - Total')
st.pyplot(fig)

num_users3 = st.slider("Select the number of top users to display", 1, 30, 10, key="q3b")
mess1 = data[['user', 'ts']].groupby('user').count().reset_index().sort_values(by='ts', ascending=False).dropna()
mess1.rename(columns={'ts': 'mess_count'}, inplace=True)
react1a.rename(columns={'sum_counts': 'react_count'}, inplace=True)
mess1a = pd.merge(pd.merge(react1a, mess1, on='user', how='left'), users[['id', 'real_name']], left_on='user', right_on='id', how='left')
mess1a['re_per_mes'] = round(mess1a['react_count'] / mess1a['mess_count'], 2)
mess1a = mess1a[['real_name', 're_per_mes']]
mess1a['real_name'] = mess1a['real_name'].astype(str)
mess1b = mess1a.sort_values(by='re_per_mes', ascending=False)
paired = sorted(zip(mess1b['re_per_mes'][0:num_users3], mess1b['real_name'][0:num_users3]))
count_s, user_s = zip(*paired)

fig, ax = plt.subplots()
ax.barh(user_s, count_s)
for index, value in enumerate(count_s):
    ax.text(value - 2, index, str(value), va='center')
ax.set_ylabel('Name')
ax.set_title('Top Reaction Generators - Reactions Per Message')
st.pyplot(fig)

# Q4
st.markdown("### **Who replies to messages most?**")
num_users4 = st.slider("Select the number of top users to display", 1, 30, 10, key="q4")
reply = data[['user', 'parent_user_id']].dropna().groupby('user').count().reset_index().sort_values(by='parent_user_id', ascending=False)
reply.rename(columns={'parent_user_id': 'reply_count'}, inplace=True)
reply1 = pd.merge(reply, users[['id', 'real_name']], left_on='user', right_on='id', how='left')

paired = sorted(zip(reply1['reply_count'][0:num_users4], reply1['real_name'][0:num_users4]))
count_s, user_s = zip(*paired)
fig, ax = plt.subplots()
ax.barh(user_s, count_s)
for index, value in enumerate(count_s):
    ax.text(value - 2.4, index, str(value), va='center')
ax.set_ylabel('Name')
ax.set_title('Top Repliers')
st.pyplot(fig)

# Q5
st.markdown("### **Who generates the most replies?**")
num_users5 = st.slider("Select the number of top users to display", 1, 30, 10, key="q5")
reply2 = data[['parent_user_id', 'ts']].dropna().groupby('parent_user_id').count().reset_index().sort_values(by='ts', ascending=False)
reply2.rename(columns={'parent_user_id': 'user', 'ts': 'replies_gen'}, inplace=True)
reply2a = pd.merge(reply2, users[['id', 'real_name']], left_on='user', right_on='id', how='left')
paired = sorted(zip(reply2a['replies_gen'][0:num_users5], reply2a['real_name'][0:num_users5]))
count_s, user_s = zip(*paired)

fig, ax = plt.subplots()
ax.barh(user_s, count_s)
for index, value in enumerate(count_s):
    ax.text(value - 3.4, index, str(value), va='center')
ax.set_ylabel('Name')
ax.set_title('Top Reply Generators')
st.pyplot(fig)

# Q6
st.markdown("### **Who generates the fastest replies?**")
num_users6 = st.slider("Select the number of top users to display", 1, 30, 10, key="q6")
reply3 = data[['parent_user_id', 'thread_ts', 'ts']].dropna()
reply3['reply_time'] = (reply3['thread_ts'] - reply3['ts']) / 60 * -1
reply3 = reply3.groupby('parent_user_id')['reply_time'].mean().reset_index().sort_values(by='reply_time', ascending=True)
reply3.rename(columns={'parent_user_id': 'user', 'reply_time': 'avg_reply_time'}, inplace=True)
reply3a = pd.merge(reply3, users[['id', 'real_name']], left_on='user', right_on='id', how='left').dropna()
reply3a['real_name'] = reply3a['real_name'].astype(str)
reply3a['avg_reply_time'] = round(reply3a['avg_reply_time'], 2)
paired = sorted(zip(reply3a['avg_reply_time'][0:num_users6], reply3a['real_name'][0:num_users6]), reverse=True)
count_s, user_s = zip(*paired)

fig, ax = plt.subplots()
ax.barh(user_s, count_s)
for index, value in enumerate(count_s):
    ax.text(value, index, str(value), va='center')
ax.set_xlabel('Avg Reply Time in Minutes')
ax.set_ylabel('Name')
ax.set_title('Top Fastest Reply Generators (Oct 2023)')
st.pyplot(fig)

# Q7
st.markdown("### **What kind of networks exist among replies?**")
fig_size = st.slider("Select the figure size for the network graph", 5, 20, 12, key="q7")
replynet = data[['user', 'parent_user_id']].dropna().reset_index()[['user', 'parent_user_id']].drop_duplicates()
replynet = replynet[replynet['user'] != replynet['parent_user_id']]
replynet = pd.merge(replynet, users[['id', 'real_name']], left_on='user', right_on='id', how='left').dropna()
replynet.rename(columns={'real_name': 'reply_name'}, inplace=True)
replynet = pd.merge(replynet.drop('id', axis=1), users[['id', 'real_name']], left_on='parent_user_id', right_on='id', how='left').dropna()
replynet.rename(columns={'real_name': 'parent_name'}, inplace=True)
replynet['reply_name'] = replynet['reply_name'].astype(str)
replynet['parent_name'] = replynet['parent_name'].astype(str)
replynet = replynet[['parent_name', 'reply_name']]

G = nx.Graph()
for _, row in replynet.iterrows():
    user, parent_user = row['reply_name'], row['parent_name']
    G.add_node(user)
    G.add_node(parent_user)
    G.add_edge(user, parent_user)

fig, ax = plt.subplots(figsize=(fig_size, fig_size))
pos = nx.kamada_kawai_layout(G)  # You can experiment with different layouts
nx.draw(G, pos, ax=ax, node_size=150, font_size=3, font_color="red", node_color="blue", alpha=1)
label_pos = {key: [value[0], value[1]-0.04] for key, value in pos.items()}  # Adjust label positions
nx.draw_networkx_labels(G, label_pos, ax=ax, font_size=6, font_color="red")
st.pyplot(fig)





