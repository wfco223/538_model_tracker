from flask import Flask, Response, render_template, make_response
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime
import numpy as np
import os
import io
import base64
import pytz


app = Flask(__name__)

@app.route('/', methods = ["GET"])

def plotview():
    
    files = sorted(os.listdir('/var/data/probs/'))
    
    message, probs_path = update_probs()
    
    plot_path = make_plot(files[0], probs_path)
    
    return render_template("image.html", mess = message)

def update_probs():
   
    files = sorted(os.listdir('/var/data/probs/'))
    
    if pd.read_csv('/var/data/probs/' + files[-1])['timestamp'][0] != pd.read_csv("https://projects.fivethirtyeight.com/2020-general-data/presidential_ev_probabilities_2020.csv")['timestamp'][0]:
        df = pd.read_csv("https://projects.fivethirtyeight.com/2020-general-data/presidential_ev_probabilities_2020.csv")
        df = df.sort_values(by = 'total_ev')

        combined = pd.DataFrame({'biden_probs': df['evprob_chal'], 'trump_probs': df['evprob_inc']})
        combined.head()
        
        new_ts = df['timestamp'][0]
        new_ts_rearr = new_ts[12:16] + new_ts[9:12] + new_ts[16:20] + " " + new_ts[0:8]
        df.to_csv('/var/data/probs/' + new_ts_rearr + '.csv')

        files = sorted(os.listdir('/var/data/probs/'))

        message = ('New update. Model last updated at ' + files[-1][:-4], '/var/data/probs/' + new_ts_rearr + '.csv')
        
    else:
        message = ('No update. Most recent update at ' + files[-1][:13] + str(int(files[-1][13]) - 1) + files[-1][14:-4] + '.', '/var/data/probs/' + files[-1])
            
    return(message)
        
def make_plot(path_1, path_2):
    
    plt.plot([0, 0], [268, 538], '--', color = 'black')
    
    df1 = pd.read_csv('/var/data/probs/' + path_1)
    df2 = pd.read_csv(path_2)

    differences_old = pd.DataFrame({'total_ev': df1['total_ev'], 'differences': df1['evprob_inc'] - df1['evprob_chal'], 'alpha': df1['evprob_inc'] + df1['evprob_chal']}).tail(269)
    differences_new = pd.DataFrame({'total_ev': df2['total_ev'], 'differences': df2['evprob_inc'] - df2['evprob_chal'], 'alpha': df2['evprob_inc'] + df2['evprob_chal']}).tail(269)

    x_arr_old = differences_old['differences']
    x_arr_new = differences_new['differences'] 
    y_arr = differences_new['total_ev']
        
    for (x1, x2, y, alpha) in zip(x_arr_old, x_arr_new, y_arr, differences_new['alpha']):
        if x2 < x1:
            plt.plot([x1, x2], [y, y], '-', color='blue', alpha = alpha/differences_new['alpha'].max())
        else: 
            plt.plot([x1, x2], [y, y], '-', color='red', alpha = alpha/differences_new['alpha'].max())

        if x2 < 0:
            plt.plot(x2, y, 'o', color = 'blue', alpha = alpha/differences_new['alpha'].max())
        else: 
            plt.plot(x2, y, 'o', color = 'red', alpha = alpha/differences_new['alpha'].max())
        
        s = 'ev: ' + str(y) + ' net prob: ' + str(round(x2 * 100, 2)) + '%'
            
        if x2 <= -.01:
            print(s)
            plt.text(x2, y, s)
                
        elif x2 > .01:
            print(s)
            plt.text(x2, y, s)
            
    path = '/var/data/plots' + df2['timestamp'][0] + '.png'
    plt.savefig(path)
                
    plt.savefig('static/images/plot.png')
    filepath = 'static/images/plot.png'
    
    return filepath
    
