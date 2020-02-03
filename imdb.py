from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url = requests.get(url)
    url_soup = BeautifulSoup(url.content,"html.parser")
    
    #Find the key to get the information
    url_scrap = url_soup.find_all('div', class_ = 'lister-item mode-advanced')

    movie = []

    for x in url_scrap:
        if x.find('div', class_ = 'ratings-metascore') != None:
            title = x.h3.a.text
            year = x.h3.find('span', class_ = 'lister-item-year text-muted unbold').text
            rate = float(x.strong.text)
            meta = int(x.find('span', class_ = 'metascore').text)
            vote = int(x.find('span', attrs = {'name':'nv'})['data-value'])

            movie.append((title, year, rate, vote, meta)) 
    
    fin = pd.DataFrame(movie, columns = ('Title', 'Release', 'Rating', 'Voting', 'Metascore'))
    fin.loc[:,'Release'] = fin['Release'].str[-5:-1].astype(int)
	
	#end of data wranggling
    return fin


@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31&count=100') #insert url here

    #This part for rendering matplotlib
    fig, axes = plt.subplots(nrows = 1, ncols =2, figsize =(16,4))
    ax1, ax2 = fig.axes
    ax1.hist(df['Rating'], bins = 10, range = (0,10)) # bin range = 1
    ax1.set_title('Movie Rating')
    ax2.hist(df['Metascore'], bins = 10, range = (0,100)) # bin range = 10
    ax2.set_title('Movie Metascore')
    for ax in fig.axes:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    return df.to_html()


if __name__ == "__main__": 
    app.run(debug = True)