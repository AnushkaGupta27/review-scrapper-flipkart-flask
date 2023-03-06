from flask import Flask, request, jsonify,render_template
from flask_cors import CORS , cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import requests
import pymongo
logging.basicConfig(filename="scrapper.log", level=logging.INFO)
app=Flask(__name__)
@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")
@app.route("/review", methods=['GET','POST'])
def page():
    if request.method=='POST':
        try:
            searchStr=request.form['content'].replace(" ","")
            flipkartUrl="https://www.flipkart.com/search?q=" + searchStr
            flipkartPage= uReq(flipkartUrl)
            flipkartDump=flipkartPage.read()
            flipkartPage.close()
            flipkarthtml=bs(flipkartDump,"html.parser")
            bigbox= flipkarthtml.findAll("div" , {"class":"_1AtVbE col-12-12"})
            del bigbox[0:3]
            Box=bigbox[0]
            prodUrl="https://www.flipkart.com"+ Box.div.div.div.a['href']
            prodpage= requests.get(prodUrl)
            prodpage.encoding='utf-8'
            prodHtml=bs(prodpage.text,"html.parser")
            #print(prodHtml)
            reviewss= prodHtml.find_all('div',{'class':'_16PBlm'})
            filename= searchStr+".csv"
            fw= open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews=[]
            for i in reviewss:
                try:
                    name= i.div.div.find_all('p',{'class':'_2sc7ZR _2V5EHH'})[0].text
                except:
                    logging.info("namee")
                try:
                    rating=i.div.div.div.div.text
                except:
                    rating = 'no rating'
                    logging.info("ratingg")
                try:
                    commenthead=i.div.div.div.p.text
                except:
                    commenthead = 'No Comment Heading'
                    logging.info(commenthead)
                try:
                    comment= i.div.div.find_all('div',{'class':''})
                    custComment=comment[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict={"Product":searchStr,"Name":name,"Rating":rating,"CommentHead":commenthead,"Comment":custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            
            client = pymongo.MongoClient("mongodb+srv://anushkagupta27:8118198Mongodb@cluster0.pjlqqd5.mongodb.net/?retryWrites=true&w=majority")

            db = client['review-scrapper-flipkart-flask-app']
            collec= db['reviews_scrap']
            collec.insert_many(reviews)


            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")