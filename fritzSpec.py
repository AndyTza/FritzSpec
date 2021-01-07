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
import matplotlib.pyplot as plt

# Define global parameters
global TOKEN, BASEURL
GETTOKEN = ''  # ADD TOKEN from fritz.science here!
BASEURL = 'https://fritz.science/'

def api(method, endpoint, data=None):
    """Info : Basic API query, takes input the method (eg. GET, POST, etc.), the endpoint (i.e. API url)
               and additional data for filtering
        Returns : response in json format
    """
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
    Spectrum response in .json format
    """
    url = BASEURL + "api/sources/" + ztfname + "/spectra"
    response = api('GET',url)
    return (response)

def download_fritz_spectrum(ztf_obj, plot=False):
    """ Given the ZTF object ID this function will opt the user to choose what spectrum to download and write it to a file directory.
        The user can also decide if they want to preview the plot (via matplotlib) before downloading.

    Input
    -----
    ztf_obj (str): ZTF Object ID
    plot (bool): If user opts to plot the spectrum, a matplotlib spectrum will be generated for the user
    """
    for ztf_id in ztf_obj:
        # Load .json that contains all the spectra
        spec = get_source_spectra(ztf_id)
        if spec['status']=="error":
            return (logging.warning(' Oh no, it looks like your ZTF_id input was invalid, please try again! '))

        if len(spec['data']['spectra'])==0:
            return (logging.warning('Sorry, no spectra are available for this target!'))
        else:
            spectrum_data = spec['data']['spectra'] # load all spectra

            for ss in enumerate(spec['data']['spectra']):
                indx, s = ss[0], ss[1] # counting index, spectrum dict.
                print ("{}) {} {}".format(indx, s['observed_at'], s['instrument_name']))

            # User decides what index to download
            usr_choice = input("Choose #-index spectrum to download [-q to exit]: ")

            if usr_choice!="-q":
                user_spec = spectrum_data[int(usr_choice)] # select spectrum user wants

                ell, flux = user_spec['wavelengths'], user_spec['fluxes']
                if plot:
                    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10,5))
                    ax.plot(ell, flux, lw=0.8, color='k')
                    ax.set_xlabel(r"$\lambda$ [Å]", fontsize=18)
                    ax.set_ylabel(r"Normalized Flux", fontsize=18)
                    ax.set_title(r"{} {} {}".format(ztf_id, user_spec['instrument_name'], user_spec['observed_at'].split("T")[0]), fontsize=18)
                    plt.show()

                # Store data as astropy table & write
                Table([ell, flux]).write('fritz_spectra/%s_%s_%s.ascii'%(ztf_id, user_spec['instrument_name'], user_spec['observed_at'].split("T")[0]),
                    format='ascii.fast_no_header', overwrite=True) # write to spectra directory
                logging.warning('Download completed!')

def main():
    if sys.argv[2:][0]=='-h':
        download_fritz_spectrum(sys.argv[1:], plot=True)
    else:
        download_fritz_spectrum(sys.argv[1:], plot=False)

if __name__ == "__main__":
    main()
