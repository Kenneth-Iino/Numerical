from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from .dataframe import *
from .forms import DatasetUploadForm
import pandas as pd
import pickle
import os


@csrf_protect
def home(request, context = {"dataFitted": False, "y_function": ""}):
    if request.method == "GET":
        context = {"dataFitted": False, "y_function": ""}
        cache.clear()
        form = DatasetUploadForm()
        datasetUploaded = False
        df = None
        num_df = None
        os.remove("templates/table.html")
        os.remove("templates/num_table.html")

        

    elif request.method == "POST":
        
        # Retrieve serialized data from cache
        serialized_df = cache.get('dataframe_cache_key')
        serialized_num_df = cache.get('num_dataframe_cache_key')

        if  serialized_df is not None:
            form = DatasetUploadForm()
            datasetUploaded = True

            # Deserialize data back into a DataFrame
            df = pickle.loads(serialized_df)
            num_df = pickle.loads(serialized_num_df)
           

        else :
            
            try:
                context = {"dataFitted": False, "y_function": ""}
                form = DatasetUploadForm(request.POST, request.FILES)

                if form.is_valid():
                    cleaned_data = form.cleaned_data['dataset']

                    # Read the uploaded file
                    df = pd.read_csv(cleaned_data) 
                    
                    # Filter out non-numeric columns
                    num_df = processData(df)

                    
                else:
                    datasetUploaded = False  # Set datasetUploaded to False otherwise

                    return HttpResponse("Form is not valid")
                
                
            except Exception as e:
                return HttpResponse("Error uploading file: " + str(e))
            
            
            
            # If html file does not exist, create it
            if not os.path.exists("templates/table.html"):
                # Display the table
                html = df.to_html(header=False, index=False)
                text_file = open("templates/table.html", "w")
                text_file.write(html)
                text_file.close()
            if not os.path.exists("templates/num_table.html"):
                html = num_df.to_html(header=False, index=False)
                text_file = open("templates/num_table.html", "w")
                text_file.write(html)
                text_file.close()

           
            
            datasetUploaded = True  # Set datasetUploaded to True if form submitted
       

    else:
        form = DatasetUploadForm()

        datasetUploaded = False
        df = None
        num_df = None

    context.update({
        'form': form,
        'datasetUploaded': datasetUploaded,
        'df': df,
        'num_df': num_df 
    })
    
    print(context)

    if df is not None:
        # Store the dataframe in a serialized form
        serialized_df = pickle.dumps(df)
        # Store serialized data in cache with a unique key
        cache.set('dataframe_cache_key', serialized_df)

    if num_df is not None:
        # Store the numerical dataframe in a serialized form
        serialized_num_df = pickle.dumps(num_df)
        # Store serialized data in cache with a unique key
        cache.set('num_dataframe_cache_key', serialized_num_df)
    print(request)
    target = request.POST.get('target') 
    if target is not None:
        context.update(fit(num_df, target))
    
    print(context)
    return render(request, 'home.html', context)

        
def about(request):
    return render(request, 'about.html')


def fit(num_df, target):

    # Split data into X and y
    X, y = splitData(num_df, target)
    y_function, linear_weights, y_preds, sr, corr, corr_desc = fitData(X, y)
    print(X)
    #X, y = processData(df)
   # numerical_df = pd.DataFrame(X.T, columns=df.columns[:-1])
    return {
        'data_column': {
            'X': list(X.columns),
            'y': target
            },
        'dataFitted': True,
        'y': {
            'equation': y_function,
            'weights': list(linear_weights),
            'predictions': list(y_preds),
            'standard_error': sr,
            'correlation': corr,
            'correlation_description': corr_desc
            }
        }
# end

def regression(request):
    # Retrieve serialized data from cache
    serialized_num_df = cache.get('num_dataframe_cache_key')

    if  serialized_num_df is not None:

        # Deserialize data back into a DataFrame
        num_df = pickle.loads(serialized_num_df)
        num_df = pickle.loads(serialized_num_df)
        
    target = request.POST.get('target') 
    context = fit(num_df, target)
    return JsonResponse(context)

def predictData(request):
    return JsonResponse(request.POST.get('response'), safe=False)