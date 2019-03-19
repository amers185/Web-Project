# @Author Max Bremer @Author Owen Szafran @Author Syed Usama Amer
# 2/6/2018
# Python Code to return database queries based on inputs of data categories and values
import psycopg2
import getpass
import flask
from flask import render_template, request
import json
import sys

app = flask.Flask(__name__)

#The DataSource class is responsible for handling the input pulled from the site,
#and turning it into functional SQL queries.
class DataSource:
    cursor = None
    connection = None
    def initialize(self):
        db = 'bremerw'
        usr = 'bremerw'
        pswd = 'glass794banana'
        try:
            self.connection = psycopg2.connect(database=db, user=usr, password=pswd, host='localhost')
        except Exception as e:
            print('Connection error: ', e)
            exit()

        try:
            self.cursor = self.connection.cursor()
        except Exception as e:
            print('Cursor error', e)
            self.connection.close()
            exit()


    def closeCursor(self):
        self.connection.close()
    #Concatenates all search terms into one SQL statement
    #@Param the array of search categories and values
    #@Return String SQL statement
    def formSearch(self, searchArray):
        returnString = "SELECT * FROM sightings WHERE "
        for string in searchArray:
            returnString = returnString + string + " AND "
        if len(searchArray)>0:
            returnString = returnString[0:len(returnString)-5]
        else:
            returnString = ""
        print(returnString)
        return self.searchQuery(returnString)
    
    #@Return all database queries where the given phrase is found somewhere within the comments
    #@Param a list of tuples, whereby the concerned category and the corresponding value is input.
    def keywordSearch(self, column, value):
        query = column + " LIKE '%" + value + "%'"
        return query
    
    #@Return all database queries where the data in a given category fits within the given range for that category.
    #@Param a list of triples, the first object in each duple being a category,
    #the second a minimum value and the third a maximum.
    def searchInRange(self, column, minimum, maximum):
        query = column + " BETWEEN " + minimum + " AND " + maximum
        return query
    
    #@Return all database queries where the data in a given category matches the given value in that category.
    #@Param a list of tuples, the first object in each duple being a category, the second a value.
    def searchByEquals (self, column, value):
        query = column + "='" + value + "'" 
        return query

    #@Return all database queries where the data in a given category matches the given value in that category.
    #@Param a list of tuples, in this case the hours and minutes.
    def searchByTime(self, hour, minutes):
        if hour[0:1]=="0":
            hour = hour[1:]
        query = "dateTime LIKE '%" + hour + ":" + minutes + "'"
        return query

    #@Return all database queries where a the data in a given category matches the given value in that category.
    #@Param a list of tuples, in this case the day, month and year. 
    def searchByDate(self, day, month, year):
        query = "dateTime LIKE '" + month + "/" + day + "/" + year + "%'"
        return query
    
    #@Return the query results which have been formatted into a String.
    #@Param is the query entered by the user. 
    def searchQuery(self, query):
        if query=="":
            return [("noParam", "", "", "", "", "", "", "", "")]
        else:
            self.cursor.execute(query)
            result = []
            for row in self.cursor.fetchall():
                result.append(row)
            return result
        
    #Parses entered date and time values into the format of the database file
    def parseDateTime(self, day, month, year, hour, minutes):
        return self.searchByEquals([("dateTime", month + "/" + day + "/" + year + " " + hour + ":" + minutes)])


ds = DataSource()
ds.initialize()
#def main():
#    data = DataSource()
#    data.initialize()
#    print(data.keywordSearch("comments", "UFO"))
#    print("/////////////////////////////////////////////////////////////////////// \n")
#    print(data.searchInRange("latitude", "0", "5"))
#    print("/////////////////////////////////////////////////////////////////////// \n")
#    print(data.searchByEquals([("duration", "10")]))
#    print("/////////////////////////////////////////////////////////////////////// \n")
#    print(data.searchByEquals([("longitude", "0"), ("latitude", "0"), ("state", "florida")]))
#    print("/////////////////////////////////////////////////////////////////////// \n")
#    print(data.searchByTime("22", "00"))
#    print("/////////////////////////////////////////////////////////////////////// \n")
#    print(data.searchByDate("1", "2", "1998"))
#    data.closeCursor()                              

@app.route('/')
def main():
    return render_template('index.html')

#Pulls data from different inputs and parses the values and categories into an array of strings.
#This array is then passed to DataSource to be turned into one SQL SELECT statement.
@app.route('/results', methods=['POST'])
def queryResults():
    searchArray = []
    keyword = request.form['keywordSearch']
    if keyword != "":
        searchData = ds.keywordSearch('comments', keyword)
        searchArray.append(searchData)
    
    minLat = request.form['minLat']
    maxLat = request.form['maxLat']
    if minLat != "" and maxLat != "":
        latData = ds.searchInRange('latitude', minLat, maxLat)
        searchArray.append(latData)
        
    minLong = request.form['minLong']
    maxLong = request.form['maxLong']
    if minLong != "" and maxLong != "":
        longData = ds.searchInRange('longitude', minLong, maxLong)
        searchArray.append(longData)

    country = request.form['country']
    country = country.lower()
    if country != "":
        countryData = ds.searchByEquals('country', country)
        searchArray.append(countryData)

    state = request.form['state']
    state = state.lower()
    if state != "":
        stateData = ds.searchByEquals('state', state)
        searchArray.append(stateData)

    city = request.form['city']
    city = city.lower()
    if city != "":
        cityData = ds.searchByEquals('city', city)
        searchArray.append(cityData)

    duration = request.form['duration']
    if duration != "":
        durationData = ds.searchByEquals('duration', duration)
        searchArray.append(durationData)

    shape = request.form['shape']
    if shape != "":
        shapeData = ds.searchByEquals('shape', shape)
        searchArray.append(shapeData)

    date = request.form['date']
    if date != "":
        dateData = ds.searchByDate(date[8:], date[5:7], date[0:4])
        searchArray.append(dateData)

    time = request.form['time']
    if time != "":
        print(time)
        timeData = ds.searchByTime(time[0:2], time[3:])
        searchArray.append(timeData)
        
    returnData = ds.formSearch(searchArray)
    #A bit of custom sanitization for the data for the purposes of aesthetics and readability.
    for row in returnData:
        index = returnData.index(row)
        row = list(row)
        if type(row[6]) is str and row[6] != None:
            row[6] = row[6].replace("&#44", ",").replace("&#39", "'").replace("&#33", "!").replace("&quot;", '"').replace("&amp;", "&")
        if type(row[2]) is str and row[2] != None:
            row[2] = row[2].upper()
        if type(row[3]) is str and row[3] != None:
            row[3] = row[3].upper()
        row = tuple(row)
        returnData[index] = row
    #Checks if parameters have been entered, if none have, @Return the noParameters.html page,
    #Checks if there are no results, if there are none, @Return the noResults.html page,
    #Otherwise @Return queryPage.html
    if len(returnData)==0:
        return render_template('noResults.html')
    elif returnData[0][0]=="noParam":
        return render_template('noParameters.html')
    else:
        return render_template('queryPage.html', result=returnData)
                            
    
      

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {0} host port'.format(sys.argv[0]), file=sys.stderr)
        exit()
    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)
