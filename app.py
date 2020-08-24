from flask import Flask
app = Flask(__name__)

@app.route('/')

def app(arg_1, arg_2):

  import pandas as pd
  import matplotlib.pyplot as plt
  import datetime
  import numpy as np
  import os

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
  differences = pd.DataFrame({'total_ev': df2['total_ev'], 'differences': df2['evprob_inc'] - df2['evprob_chal']})
  differences = differences.tail(269)

  differences_old = pd.DataFrame({'total_ev': df1['total_ev'], 'differences': df1['evprob_inc'] - df1['evprob_chal'], 'alpha': df1['evprob_inc'] + df1['evprob_chal']}).tail(269)
  differences_new = pd.DataFrame({'total_ev': df2['total_ev'], 'differences': df2['evprob_inc'] - df2['evprob_chal'], 'alpha': df2['evprob_inc'] + df2['evprob_chal']}).tail(269)

  x_arr_old = differences_old['differences']
  x_arr_new = differences_new['differences'] 
  y_arr = differences_new['total_ev']

  fig = plt.figure(figsize=(10, 20))

  for (x1, x2, y, alpha) in zip(x_arr_old, x_arr_new, y_arr, differences_new['alpha']):
      if x2 < x1:
        plt.plot([x1, x2], [y, y], '-', color='blue', alpha = alpha/differences_new['alpha'].max())
      else: 
        plt.plot([x1, x2], [y, y], '-', color='red', alpha = alpha/differences_new['alpha'].max())

      if x2 < 0:
        plt.plot(x2, y, 'o', color = 'blue', alpha = alpha/differences_new['alpha'].max())
      else: 
        plt.plot(x2, y, 'o', color = 'red', alpha = alpha/differences_new['alpha'].max())

  plt.plot([0, 0], [269, 538], '--')
  plt.plot([x_arr_new.min(), x_arr_old.max()], [269, 269], '-', color = 'black')

  pre = datetime.datetime.strptime(files[1][:-4], '%Y-%m-%d %H_%M_%S.%f')
  post = datetime.datetime.strptime(files[-1][:-4], '%Y-%m-%d %H_%M_%S.%f')
  
  message = "pre:  " + str(pre) + '\n' + 'post: ' + str(post) + "\n" + str(post - pre)
  return(message)
