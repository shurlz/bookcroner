import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import pickle

# #######################################################################33engine
# ratings = pd.read_csv('Ratings.csv')
# users = pd.read_csv('Users.csv')
# books = pd.read_csv('Books.csv')
# data = books.merge(ratings,how='left',on='ISBN')
# books_data = data.merge(users,how='left',on='User-ID')
# books_data['Book-Author'] = books_data['Book-Author'].str.replace('DAN BROWN','Dan Brown')
# books_data = books_data[books_data['Book-Rating'] > 0]
#
# ############################################################################ model based data
# counts = pd.DataFrame(books_data['Book-Title'].value_counts())
# counts = counts[counts['Book-Title']>35]
# Books = books_data.copy()
# Books = Books[Books['Book-Title'].isin(counts.index)]
# Books['User-ID'] = Books['User-ID'].astype('int')
# def first(item):
#     array = item.split('(')
#     return array[0]
# Books['Book-Title'] = Books['Book-Title'].map(first)
# popular_rated_books = Books.pivot_table(index=['Book-Title'],columns=['User-ID'],values='Book-Rating')
# popular_rated_books = popular_rated_books.fillna(0)
# scaled_books = pd.DataFrame(MinMaxScaler().fit_transform(popular_rated_books),
#                             columns=popular_rated_books.columns,index=popular_rated_books.index)
# data_one = scaled_books.iloc[:350]
# data_two = scaled_books.iloc[350:715]
# data_three = scaled_books.iloc[715:]
#
# data_one.to_csv('data_one.csv',index=True)
# data_two.to_csv('data_two.csv',index=True)
# data_three.to_csv('data_three.csv',index=True)
# ########################################################################## books and images
# Books_and_images = Books[['Book-Title','Image-URL-S']]
# Books_and_images['Image-URL-S'] = Books_and_images['Image-URL-S'].str[:-14]
# Books_and_images = Books_and_images.drop_duplicates('Book-Title','first')
# Books_and_images = Books_and_images.set_index('Book-Title')
# Books_and_images.to_csv('Books_and_images.csv',index=True)
#
# ########################################################################## training model
# data_one = pd.read_csv('data_one.csv').set_index('Book-Title')
# data_two = pd.read_csv('data_two.csv').set_index('Book-Title')
# data_three = pd.read_csv('data_three.csv').set_index('Book-Title')
#
# books_and_images = pd.read_csv('Books_and_images.csv').set_index('Book-Title')
# book_titles = scaled_books.index
#
# ########################################################################## dumping models
# books_images = pickle.dump(books_and_images,open('books_images.pkl','wb'))
# book_titles = pickle.dump(book_titles,open('book_titles.pkl','wb'))
# Data_one = pickle.dump(data_one,open('data_one.pkl','wb'))
# Data_two = pickle.dump(data_two,open('data_two.pkl','wb'))
# Data_three = pickle.dump(data_three,open('data_three.pkl','wb'))

data_one = pickle.load(open('data_one.pkl', 'rb'))
data_two = pickle.load(open('data_two.pkl', 'rb'))
data_three = pickle.load(open('data_three.pkl', 'rb'))
book_titles = pickle.load(open('book_titles.pkl', 'rb'))
books_images = pickle.load(open('books_images.pkl', 'rb'))


def collaborative_recommender(book_title):
    nearest_neighbors_data = data_one.append(data_two)
    nearest_neighbors_data = nearest_neighbors_data.append(data_three)

    model = NearestNeighbors(n_neighbors=7)
    model.fit(nearest_neighbors_data)
    distance, indices = model.kneighbors(nearest_neighbors_data.loc[book_title].values.reshape(1, -1))
    recommended_books = []
    for values in indices:
        for value in values:
            recommended_books.append([book_titles[value], books_images.loc[book_titles[value]]['Image-URL-S']])
    recommended_books.pop(0)
    return recommended_books