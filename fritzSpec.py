"""
Author: Andy Tzanidakis & Yashvi Sharma
email: atzanida@caltech.edu

Purpose:
Interactive python script for dowloading spectra from SkyPortal fritz.science
"""
import numpy as np
import os, glob
import requests, json
from lxml import html
import sys
from astropy.table import Table
import logging

# Define global parameters
global TOKEN, BASEURL
GETTOKEN = ''  # ADD TOKEN from fritz.science here!
BASEURL = 'https://fritz.science/'


def api(method, endpoint, data=None):
    ''' Info : Basic API query, takes input the method (eg. GET, POST, etc.), the endpoint (i.e. API url)
               and additional data for filtering
        Returns : response in json format
        CAUTION! : If the query doesn't go through, try putting the 'data' input in 'data' or 'params'
                    argument in requests.request call
    '''
    headers = {'Authorization': f'token {GETTOKEN}'}

    response = requests.request(method, endpoint, json=data, headers=headers)

    return response.json()

def get_source_spectra(ztfname):
    """Given ZTF name, load the .json containing **all** the spectra.
    Input
    ----
    ztfname (str): ZTF id

    Output
    ----
    Spectrum response in json format
    """
    url = BASEURL + "api/sources/" + ztfname + "/spectra"
    response = api('GET',url)
    return (response)


def download_fritz_spectrum(ztf_obj):
    """ Given the ZTF id this function will opt the user to choose what spectrum to download and write it to a file directory.

    Input
    -----
    ztf_obj (str): ZTF id
    """
    for ztf_id in ztf_obj:
        # Load .json that contains all the spectra
        spec = get_source_spectra(ztf_id)

        if len(spec['data']['spectra'])==0:
            return ("Sorry, no spectra are available for this target!")
        else:
            spectrum_data = spec['data']['spectra'] # load all spectra

            for ss in enumerate(spec['data']['spectra']):
                indx, s = ss[0], ss[1] # counting index, spectrum dict.
                print ("%s)"%indx, s['observed_at'], s['instrument_name'])

            # User decides what index to download
            usr_choice = int(input("Choose #-index spectrum to download: "))
            user_spec = spectrum_data[usr_choice] # select spectrum user wants

            ell, flux = user_spec['wavelengths'], user_spec['fluxes']
            Table([ell, flux]).write('fritz_spectra/%s_%s_%s.ascii'%(ztf_id, user_spec['instrument_name'], user_spec['observed_at'].split("T")[0]),
                format='ascii.fast_no_header', overwrite=True) # write to spectra directory


def main():
    download_fritz_spectrum(sys.argv[1:])
    logging.warning('Download completed!')

if __name__ == "__main__":
    main()
