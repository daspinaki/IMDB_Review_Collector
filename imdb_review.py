from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            imdb_url =" https://imdb.com/find?q=" + searchString
            uClient=uReq(imdb_url)
            imdbPage = uClient.read()
            uClient.close()
            imdb_html = bs(imdbPage, "html.parser")
            bigboxes = imdb_html.findAll("div", {"class": "findSection"})
            del bigboxes[1:]
            box = bigboxes[0]
            movie_link = "https://imdb.com/" + box.table.a['href']
            movieRes = requests.get(movie_link)
            movieRes.encoding='utf-8'
            imdb_html = bs(movieRes.text, "html.parser")
            print(imdb_html)
            user_review_tab = imdb_html.findAll("div", {"class": "UserReviewsHeader__Header-k61aee-0 egCnbs"})
            user_review_tab = user_review_tab[0]
            movie_review_link = "https://imdb.com/"+user_review_tab.a['href']
            movieReviewRes = requests.get(movie_review_link)
            movieReviewRes.encoding='utf-8'
            movieReviewRes_html = bs(movieReviewRes.text,"html.parser")
            commentboxes = movieReviewRes_html.find_all('div', {'class': "lister-item-content"})
            #commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    
                    #name.encode(encoding='utf-8')
                    #name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    name = commentbox.find_all('div',{'class' : 'display-name-date'})
                    name = name[0].span.a.text
                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    #rating = commentbox.div.div.div.div.text
                    rating = commentbox.div.span.span.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    #commentHead = commentbox.div.div.div.p.text
                    commentHead = commentbox.a.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    #comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    #custComment = comtag[0].div.text
                    custComment =commentbox.find_all('div',{'class':'content'})[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
