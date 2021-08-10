import requests
import os
import pandas as pd
import config
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json


def process_csvs(drive):
    '''
    Function to create csvs and upload them to google drive
    '''

    products_link, products_sotcks_link, products_full_link = '', '', ''

    ####################Process products####################

    products_df, products_stocks_df, products_full_df = None, None, None

    # Fetch response from Big Buy API
    products_response = requests.get(config.BIGBUY_PRODUCTS_ENDPOINT,
                                        headers={'Authorization': f'Bearer {config.BIGBUY_TOKEN}'})
    # Check if response is successful
    if products_response.status_code == 200:
        print("Processing products")
        products_json = products_response.json()

        # Convert json in to data frame
        products_df = pd.DataFrame(products_json)
        # Remove unwanted columns
        for column in config.products_columns_to_exclude:
            if column in products_df.columns:
                products_df = products_df.drop(config.products_columns_to_exclude, axis=1)

        # Save as csv file
        products_df.to_csv("products.csv")

    else:
        print(products_response)
        print("Error retrieving products")

    ####################Process products stocks####################

    # Fetch response from Big Buy API
    products_stocks_response = requests.get(config.BIGBUY_PRODUCTS_STOCKS_ENDPOINT,
                                            headers={'Authorization': f'Bearer {config.BIGBUY_TOKEN}'})

    # Check if response is successful
    if products_stocks_response.status_code == 200:
        print("Processing products stocks")
        products_stocks_json = products_stocks_response.json()

        # Products stocks list to save into csv later
        products_stocks_list = []
        # Loop through products stocks json
        for product_stock in products_stocks_json:
            # Add stock_quantity column in json
            product_stock['stock_quantity'] = product_stock['stocks'][0]['quantity']
            # Add stock_minHandlingDays quantity column in json
            product_stock['stock_minHandlingDays'] = product_stock['stocks'][0]['minHandlingDays']
            # Add stock_maxHandlingDays quantity column in json
            product_stock['stock_maxHandlingDays'] = product_stock['stocks'][0]['maxHandlingDays']
            # remove stocks column having list from json
            del product_stock['stocks']
            # Add processed json in to products stocks list
            products_stocks_list.append(product_stock)

        # Convert list to a pandas data frame
        products_stocks_df = pd.DataFrame(products_stocks_list)
        # Remove unwanted columns
        for column in config.product_stocks_columns_to_exclude:
            if column in products_stocks_df.columns:
                products_stocks_df = products_stocks_df.drop(config.product_stocks_columns_to_exclude, axis=1)

        # Save as a csv file
        products_stocks_df.to_csv("products_stocks.csv")
    else:
        print(products_stocks_response)
        print("Error retrieving products stocks")

    try:
        # check if the products.csv and products_stocks.csv exists.
        if products_df and products_stocks_df:
            print('products_df or products_stocks_df is corrupted.')
    except Exception as ex:
        try:
            # check if retailPrice and InShopPrice exists in the products.csv.
            if 'sku' in products_df.columns and 'retailPrice' in products_df.columns and 'inShopsPrice' in products_df.columns:
                print("Processing products Full")

                dummy_products_df = products_df
                dummy_products_stocks_df = products_stocks_df

                for c in dummy_products_df.columns:
                    if c in ['sku', 'retailPrice', 'inShopsPrice']:
                        pass
                    else:
                        dummy_products_df = dummy_products_df.drop(c, axis=1)

                # merging the columns in products_stocks.csv
                products_full_df = pd.merge(dummy_products_stocks_df, dummy_products_df, on=['sku'])

                # making another merged csv, named as products_full.csv for further processing.
                products_full_df.to_csv('products_full.csv')

        except Exception as ex:
            print(ex)


    product_drive_file, product_stock_drive_file, products_full_drive_file = None, None, None

    # If Big Guy API response is successful, Start google drive functions
    if products_response.status_code == 200 and products_stocks_response.status_code == 200:
        # Get list of files in drive folder
        drive_file_list = drive.ListFile({'q': f"'{config.GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false"}).GetList()
        # If files exists in folder
        if drive_file_list:
            # Loop through files
            for file in drive_file_list:
                # Check if file name matches with products.csv
                if file['title'] == 'products.csv':
                    # Delete pre existing file
                    product_drive_file = drive.CreateFile({'id': file['id']})
                    product_drive_file.SetContentFile('products.csv')
                    print("Uploading products.csv to google drive")
                    product_drive_file.Upload()

                # Check if file name matches with products.csv
                if file['title'] == 'products_stocks.csv':
                    # Delete pre existing file
                    product_stock_drive_file = drive.CreateFile({'id': file['id']})
                    product_stock_drive_file.SetContentFile('products_stocks.csv')
                    print("Uploading products_stocks.csv to google drive")
                    product_stock_drive_file.Upload()

                # Check if file name matches with products_full.csv
                if file['title'] == 'products_full.csv':
                    # Delete pre existing file
                    products_full_drive_file = drive.CreateFile({'id': file['id']})
                    products_full_drive_file.SetContentFile('products_full.csv')
                    print("Uploading products_full.csv to google drive")
                    products_full_drive_file.Upload()
        else:
            try:
                # Upload products.csv to drive
                product_drive_file = drive.CreateFile({'parents': [{'id': config.GOOGLE_DRIVE_FOLDER_ID}]})
                product_drive_file.SetContentFile('products.csv')
                print("Uploading products.csv to google drive")
                product_drive_file.Upload()
            except Exception as e:
                print(e)
                print("Error while uploading products.csv")

            try:
                # Upload products_stocks.csv to drive
                product_stock_drive_file = drive.CreateFile({'parents': [{'id': config.GOOGLE_DRIVE_FOLDER_ID}]})
                product_stock_drive_file.SetContentFile('products_stocks.csv')
                print("Uploading products_stocks.csv to google drive")
                product_stock_drive_file.Upload()
            except Exception as e:
                print(e)
                print("Error while uploading product_stocks.csv")
            try:
                # Upload products_full.csv to drive
                products_full_drive_file = drive.CreateFile({'parents': [{'id': config.GOOGLE_DRIVE_FOLDER_ID}]})
                products_full_drive_file.SetContentFile('products_full.csv')
                print("Uploading products_full.csv to google drive")
                products_full_drive_file.Upload()
            except Exception as e:
                print(e)
                print("Error while uploading products_full.csv")

        # If products.csv exists
        if product_drive_file:
            # To obtain the google drive link modify the link as follows
            products_file_link = product_drive_file['alternateLink']
            products_file_link = products_file_link.split('?')[0]
            products_file_link = products_file_link.split('/')[-2]
            products_file_link = 'https://docs.google.com/uc?export=download&id=' + products_file_link
            print("Products file link: ", products_file_link)
            products_link = products_file_link

        # If products_stocks.csv exists
        if product_stock_drive_file:
            # To obtain the google drive link modify the link as follows
            products_stocks_file_link = product_stock_drive_file['alternateLink']
            products_stocks_file_link = products_stocks_file_link.split('?')[0]
            products_stocks_file_link = products_stocks_file_link.split('/')[-2]
            products_stocks_file_link = 'https://docs.google.com/uc?export=download&id=' + products_stocks_file_link
            print("Products Stocks file link: ", products_stocks_file_link)
            products_sotcks_link = products_stocks_file_link

        # If products_full.csv exists
        if products_full_drive_file:
            # To obtain the google drive link modify the link as follows
            products_full_file_link = products_full_drive_file['alternateLink']
            products_full_file_link = products_full_file_link.split('?')[0]
            products_full_file_link = products_full_file_link.split('/')[-2]
            products_full_file_link = 'https://docs.google.com/uc?export=download&id=' + products_full_file_link
            print("products full file link: ", products_full_file_link)
            products_full_link = products_full_file_link

        links_ = {'products_link': str(products_link), 'products_sotcks_link': str(products_sotcks_link), 'products_full_link': str(products_full_link)}

        with open('./utils/links.json', 'w') as fl:
            json.dump(links_, fl)

        # Remove both files from system
        try:
            os.remove('products.csv')
        except Exception as ex:
            print(ex)
            pass
        try:
            os.remove('products_stocks.csv')
        except Exception as ex:
            print(ex)
        try:
            os.remove('products_full.csv')
        except Exception as ex:
            print(ex)

        print("Processing Done!")


if __name__ == '__main__':
    '''
    Main handler function
    '''

    drive = None

    print('wait is over ...')

    # Google drive authentication
    try:
        G_Auth = GoogleAuth()
        # Try to load saved client credentials
        G_Auth.LoadCredentialsFile("./utils/credentials.json")
        if G_Auth.credentials is None:
            # Authenticate if they're not there
            G_Auth.LocalWebserverAuth()
        elif G_Auth.access_token_expired:
            # Refresh them if expired
            G_Auth.Refresh()
        else:
            # Initialize the saved creds
            G_Auth.Authorize()
        # Save the current credentials to a file
        G_Auth.SaveCredentialsFile(
            "./utils/credentials.json")

        drive = GoogleDrive(G_Auth)

    except Exception as ex:
        print(ex)
        print("Error authenticating google cloud api")
        exit()

    # Check if folder id exists in config.py
    if config.GOOGLE_DRIVE_FOLDER_ID:
        process_csvs(drive)
    else:
        print("Please specify folder id in config.py")

    print('waiting for next ...')




