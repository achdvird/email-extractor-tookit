# email-extractor-tookit
emails.py is a scanner. It reads lists of website addresses from text files, visits each site's homepage plus its /contacto and /contact pages, and picks out any email addresses written on those pages. It then saves every unique email it found into one CSV file.

The files
emails.py: the scanner itself.
sites.txt: the first list of sites (about 240).
sites2.txt: the second list (745 more).
emails_found.csv: the result. The program creates it when it finishes.

All three files must be in the same folder.

How to use it in Termux

1. One-time setup

pkg install python
pip install requests

If pip shows an "externally managed environment" error, add --break-system-packages to the pip command.

2. Put the files in one folder

Copy emails.py, sites.txt and sites2.txt to the same folder on your phone. If they are in your Downloads, run termux-setup-storage once, then:

cd ~/storage/downloads

3. Run it

python emails.py

You will see how many sites it loaded from each file, then a live counter like 412/2900 pages checked, 37 emails found.

4. Get the results

When it ends, it prints how many unique emails it saved. Open emails_found.csv in any spreadsheet app, or view it with:

cat emails_found.csv
