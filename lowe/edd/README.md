# Automation of EDD News Releases

There's a considerable amount of data processing that needs to be done, and the script `autoedd.py` does this. The function `news_release_numbers()` does the heavy lifting. If you want to add additional MSAs, you need to call it with the `fname` argument equal to the name of the file you want to process. The code itself is quite verbose, but essentially just does a ton of data processing.


## Automation Process

1. Around 9 AM on the 3rd Friday of every month, download the data from https://www.labormarketinfo.edd.ca.gov/data/employment-by-industry.html. Download the compressed .zip file for all areas from 2010-current.
2. Delete all of the files in `lowe/edd/data`.
3. From the unzipped file, drag all of the contents into the `lowe/edd/data` folder.
4. Run `python3 edd.py` or `python edd.py` (depending on how your PATH is configured).
5. The output files will be listed in the `output` folder. Email this to the team writing the news report.

## Next Steps

Seasonally adjusted data is the key here. As of right now, the only way we have to do this is via EViews. However, a Python workaround does exist, we just haven't implemented it yet. The census bureau publishes files for X-13 Seasonal Adjustment in their website: https://www.census.gov/data/software/x13as.html. The source code is also available to be compiled (it's in FORTRAN). Once you have the correct file, you can use `statsmodels` wrapper around this to call it within Python: https://www.statsmodels.org/dev/generated/statsmodels.tsa.x13.x13_arima_analysis.html. This will enable seasonal adjustments to be used within Python, saving potentially tons of time (and this should be incorporated into the city reports as well!)

Emails can also be automated. Take a look into that to cut another step out of the process. A quick Google search for "automate emails in Python" should do the trick. Remember if you need to store credentials, **store them in your `.env` file. NOT in your scripts.** Remember, this is a PUBLIC repository, and storing your credentials in files that are pushed here WILL lead them to be stolen. People scrape public repos for credentials all the time.

If you don't want to have to wake up at 9 AM on a Friday to run this, the best strategy is to write a bash script (a script that's essentially just a list of terminal commands), and then write a **cron job** that will execute the code for you on the third Friday of every month (I'm writing this from memory, so it might not be the third Friday -- check this yourself). 
