import requests
import openpyxl
import urllib.request
import pandas as pd
import sqlite3
from flask import Flask, jsonify
from flask import request
url = 'https://ohiodnr.gov/static/documents/oil-gas/production/20110309_2020_1%20-%204.xls'
filename = 'production_data.xls'

response = requests.get(url)
with open(filename, 'wb') as file:
    file.write(response.content) 


#domain xls file loaded from the environment 
data = pd.read_excel('domain_ecxel.xls')


annual_data = data.groupby('API WELL  NUMBER').sum()

annual_data.to_excel('annual.xls',engine='openpyxl')




conn = sqlite3.connect('annual_DB.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS annual_DB (
                    API_WELL_NUMBER TEXT,
                    oil INTEGER,
                    gas INTEGER,
                    brine INTEGER
                  )''')


annual = pd.read_excel('annual.xls')

annual_csv=pd.read_csv('annual_data.csv')


for row in annual_csv.itertuples(index=False):
    cursor.execute("INSERT INTO annual_DB (API_WELL_NUMBER, oil, gas, brine) VALUES (?,?,?,?)", row)


conn.commit()
conn.close()





app = Flask(__name__)

@app.route('/home')
def get_data():
    well = request.args.get("well")

    conn = sqlite3.connect('annual_DB.db')
    cursor = conn.cursor()

    
    cursor.execute('SELECT oil, gas, brine FROM annual_DB WHERE API_WELL_NUMBER = ?', (well,))
    result = cursor.fetchone()

    

    if result:
        data = {
                'brine': result[2],
                'gas': result[1], 
                'oil': result[0] 
                }
                
        return jsonify(data)
    else:
        return 'Data not found for the specified well.'

if __name__ == '__main__':
    app.run(port=8080)
