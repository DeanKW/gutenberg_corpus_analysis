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

def download_from_metadata(metadata_file: str,  raw_outpath: str):
    """Downloads books' raw text files from Project Gutenberg based on metadata file
    Args:
        metadata_file (str): Path to metadata csv
        raw_outpath (str): Folder to save raw text files

    Raises:
        ValueError: If no valid ID column found in metadata file
    """
    df = pd.read_csv(metadata_file)
    if 'id' in df.columns:
        df['id']=df['id'].str[2:]
        book_list = df['id'].tolist()
    if 'Text#' in df.columns:
        book_list = df['Text#'].tolist()
    else:
        raise ValueError('No valid ID column found in metadata file')

    for book_id in book_list:
        download_book(book_id, raw_outpath)

def download_url(urlpath: str):
    """Downloads a file from a url

    Args:
        urlpath (str): The file to download

    Returns:
        _type_: _description_
    """
    try:
        # open a connection to the server
        with urlopen(urlpath, timeout=3) as connection:
            # read the contents of the html doc
            return connection.read()
    except:
        # TODO: Make this specific
        # bad url, socket timeout, http forbidden, etc.
        return None
    
def download_book(book_id: int, save_path: str):
    """Downloads a book from Project Gutenberg based on its ID

    Saves the book as PG{book_id}_raw.txt in the save_path folder,
    in order to match the Standard Project Gutenberg Corpus format.

    Note that this skips the .mirror step

    Args:
        book_id (int): The ID of the book to be downloaded
        save_path (str): the folder to save the book in

    Returns:
        str: Description of success or failure
    """
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
                        help='Path to gutenberg data folder')
    parser.add_argument('--skip_existing', default=False, help='Should existing books be skipped')
    args = parser.parse_args()

    
    raw_outpath = os.path.join(args.outpath, 'raw')
    os.makedirs(raw_outpath, exist_ok=True)

    download_from_metadata(args.metadata, raw_outpath)

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