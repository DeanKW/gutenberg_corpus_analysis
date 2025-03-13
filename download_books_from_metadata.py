import os, sys
import pandas as pd
from urllib.request import urlopen
import argparse
import pickle


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from gutenberg.src.metadataparser import make_df_metadata
from gutenberg.src.bookshelves import get_bookshelves
from gutenberg.src.bookshelves import parse_bookshelves

def download_from_metadata(metadata_file, outpath):
    df = pd.read_csv(metadata_file)
    if 'id' in df.columns:
        df['id']=df['id'].str[2:]
        book_list = df['id'].tolist()
    if 'Text#' in df.columns:
        book_list = df['Text#'].tolist()
    
    for book_id in book_list:
        download_book(book_id, outpath)

def download_url(urlpath):
    try:
        # open a connection to the server
        with urlopen(urlpath, timeout=3) as connection:
            # read the contents of the html doc
            return connection.read()
    except:
        # bad url, socket timeout, http forbidden, etc.
        return None
    
def download_book(book_id, save_path):
    print(book_id)
    # construct the download url
    url = f'https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt'
    # download the content
    data = download_url(url)
    if data is None:
        return f'Failed to download {url}'
    # create local path
    save_file = os.path.join(save_path, f'PG{book_id}_raw.txt')
    # save book to file
    with open(save_file, 'wb') as file:
        file.write(data)
    return f'Saved {save_file}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='download_book_from_metadata.py',
                                     description='Download a book from Project Gutenberg')
    
    parser.add_argument('--metadata', required=True, help='Path to the metadata CSV file')
    parser.add_argument('--outpath', default='dataset',
                        help='Path to save the downloaded books')
    parser.add_argument('--skip_existing', default=False, help='Should existing books be skipped')
    args = parser.parse_args()

    if args.outpath=='dataset':
        outpath = os.path.join(args.outpath, 'raw')
        os.makedirs(args.outpath, exist_ok=True)
    
    #download_from_metadata(args.metadata, args.outpath)

    metadata_fold = os.path.join(args.outpath, 'metadata')
    os.makedirs(metadata_fold, exist_ok=True)
    # Bookshelves
    # -----------
    # Get bookshelves and their respective books and titles as dicts
    BS_dict, BS_num_to_category_str_dict = parse_bookshelves()
    with open(os.path.join(metadata_fold, 'bookshelves_ebooks_dict.pkl'), 'wb') as fp:
        pickle.dump(BS_dict, fp)
    with open(os.path.join(metadata_fold, 'bookshelves_categories_dict.pkl'), 'wb') as fp:
        pickle.dump(BS_num_to_category_str_dict, fp)