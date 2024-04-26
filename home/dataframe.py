import pandas as pd
import numpy as np
from django.http import HttpResponse
from django.shortcuts import render


def processData(df):
    # Data Cleaning
    df = df.dropna()
    df = df.drop_duplicates()

    # Get Numerical Features
    df = df.select_dtypes(exclude='object')

    return df
   

def splitData(df, target):
     # Seperating data and label
    X = df.drop(target, axis=1)
    y = df[target]

    return X, y
    
def fitData(X, y):
    X = X.values.T
    y = y.values
    # Initialize matrix for multiple linear regression
    mat_X = np.zeros((X.shape[0]+1,X.shape[0]+1))
    mat_y = np.zeros((X.shape[0]+1))


    mat_X[0,0] = X.shape[1]
    mat_y[0] = y.sum()
    for i in range(X.shape[0]):
        x_sum =  X[i].sum()

        mat_X[i+1,0] = x_sum
        mat_X[0,i+1] = x_sum

        # X columns
        for j in range( X.shape[0]):

            x_sum = (X[i] * X[j]).sum()

            mat_X[i+1,j+1] = x_sum
            if i != j:
                mat_X[j+1,i+1] = x_sum
            # print(mat)

        # y column
        mat_y[i+1] = (y * X[i]).sum()

    linear_weights = np.linalg.solve(mat_X, mat_y).round(8)
    y_preds, sr, corr, corr_desc =  predictData(X, y, linear_weights)

    y_function = f"{round(linear_weights[0], 4)}"
    for i in range(1, len(linear_weights)):
        linear_weight = round(linear_weights[i], 4)
        if linear_weight != 0:
            y_function += " + " if linear_weight > 0 else " - "
            y_function += f"{abs(linear_weight)}" if abs(linear_weight) != 1 else ""
            y_function += f"x^{i}" if i != 1 else "x"

        else:
            continue

    return y_function, linear_weights, y_preds, sr, corr, corr_desc

def predictData(X, y, linear_weights):
    y_preds_list = []

    for i in range(X.shape[1]):
        y_pred = linear_weights[0]
        for j in range(X.shape[0]):
            y_pred += linear_weights[j+1] * X[j, i]
        y_preds_list.append(y_pred)

    # Standard Deviation
    st = ((y - y.mean()) ** 2) .sum()

    # Standard Error
    sr = ((y - y_preds_list) ** 2).sum().round(4)

    # Correlation Coefficient
    corr = np.sqrt((st-sr)/st).round(4)

    corr_desc = "Strong" if corr > 0.7 else "Moderate" if corr > 0.5 else "Weak"


    return y_preds_list, sr, corr, corr_desc