from flask import Flask, Response, render_template
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime
import numpy as np
import os
import io
import base64

app = Flask(__name__)

files = sorted(os.listdir('./total_ev'))

if pd.read_csv('./total_ev/' + files[-1])['timestamp'][0] != pd.read_csv("https://projects.fivethirtyeight.com/2020-general-data/presidential_ev_probabilities_2020.csv")['timestamp'][0]:
    df = pd.read_csv("https://projects.fivethirtyeight.com/2020-general-data/presidential_ev_probabilities_2020.csv")
    df = df.sort_values(by = 'total_ev')

    combined = pd.DataFrame({'biden_probs': df['evprob_chal'], 'trump_probs': df['evprob_inc']})
    combined.head()

    dt = datetime.datetime.today()
    df.to_csv('/total_ev/' + str(dt) + '.csv')

    files = sorted(os.listdir('./total_ev'))

    print('new', files[-1][:16])
else:
    latest_dt = datetime.datetime.strptime(files[-1][:-4], '%Y-%m-%d %H_%M_%S.%f')
    delta = datetime.datetime.now() - latest_dt
    if delta.total_seconds() // 3600 < 1:
        print('Done. Most recent update', round(delta.total_seconds()/60), 'minutes ago')
    else:
        print('Done. Most recent update', round(delta.total_seconds() // 3600), 'hours and', round((delta.total_seconds() % 3600)/60), 'minutes ago')

df1 = pd.read_csv('./total_ev/' + files[1])
df2 = pd.read_csv('./total_ev/' + files[-1])

differences_old = pd.DataFrame({'total_ev': df1['total_ev'], 'differences': df1['evprob_inc'] - df1['evprob_chal'], 'alpha': df1['evprob_inc'] + df1['evprob_chal']}).tail(269)
differences_new = pd.DataFrame({'total_ev': df2['total_ev'], 'differences': df2['evprob_inc'] - df2['evprob_chal'], 'alpha': df2['evprob_inc'] + df2['evprob_chal']}).tail(269)

x_arr_old = differences_old['differences']
x_arr_new = differences_new['differences'] 
y_arr = differences_new['total_ev']



@app.route('/', methods = ["GET"])

def plotview():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    for (x1, x2, y, alpha) in zip(x_arr_old, x_arr_new, y_arr, differences_new['alpha']):
        if x2 < x1:
            axis.plot([x1, x2], [y, y], '-', color='blue', alpha = alpha/differences_new['alpha'].max())
        else: 
            axis.plot([x1, x2], [y, y], '-', color='red', alpha = alpha/differences_new['alpha'].max())

        if x2 < 0:
            axis.plot(x2, y, 'o', color = 'blue', alpha = alpha/differences_new['alpha'].max())
        else: 
            axis.plot(x2, y, 'o', color = 'red', alpha = alpha/differences_new['alpha'].max())
    
    axis.plot([0, 0], [269, 538], '--')
    axis.plot([x_arr_new.min(), x_arr_old.max()], [269, 269], '-', color = 'black')
    
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String + base64.b64encode(pngImage.getvalue()).decode('utf8')
    
    return render_template("image.html", image = pngImageB64String)
