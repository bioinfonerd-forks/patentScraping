# Python script with bs4 for Patent Scraping

import sys
import requests
from bs4 import BeautifulSoup
import csv

link_list = []
count = 0

print("Keyword:")
keyword = input()
print("Company:")
company = input()

if company == '':
    modifier = '%0D%0A'
else:
    modifier = '%0D%0AAN%2F'

page = requests.get('http://www.freepatentsonline.com/result.html?p=1&edit_alert=&srch=xprtsrch&query_txt='+str(keyword)+modifier+str(company)+'&uspat=on&usapp=on&date_range=all&stemming=on&sort=chron&search=Search')
soup = BeautifulSoup(page.content, 'html.parser')


for link in soup.find_all('a'):
    link_text = str(link.get('href'))
    td = link.parent.name
    if link.parent.name == "td" and link_text[0] == "/":
        link_dict = {"patent": link.contents[0], "link": "http://www.freepatentsonline.com"+str(link_text)}
        link_list.append(link_dict)

for link in link_list:
    #print(link["patent"]+"\n("+link["link"]+")\n")
    sub_page = requests.get(link["link"])
    sub_soup = BeautifulSoup(sub_page.content, 'html.parser')
    divs = sub_soup.find_all('div', "disp_elm_text")
    for div in divs:
        previous = div.find_previous("div")
        if previous.string == "Filing Date:":
            patent_date = div.contents[0]
            link["filed"] = patent_date[13:23]
            #print("Filing Date: "+link["filed"])
        elif previous.string == "Publication Date:":
            publish_date = div.contents[0]
            link["published"] =publish_date[13:23]
            #print("Filing Date: "+link["filed"])
        elif previous.string == "Abstract:":
            abstract = div.contents[0]
            link["abstract"] = abstract
        elif previous.string == "View Patent Images:":
            pdf_div = div.contents[1]
            #pdf_link = str(pdf_div.get('href'))
            patent_pdf_url = "http://www.freepatentsonline.com"+str(pdf_div.get('href'))
            link["pdf"] = patent_pdf_url
            #print("PDF: "+link["pdf"])
        elif previous.string == "Assignee:":
            assignee_div = div.contents[0]
            link["assignee"] = assignee_div[29:]
    #print(link)
    #print('\n')
    #print("ENTER TO CONTINUE . . .")
    count += 1
    print(count)
    #temp = input()

with open(str(keyword)+'_'+str(company)+'_patents.csv', 'w') as csvfile:
    fieldnames = ['assignee','patent','filed','published','link','pdf','abstract']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(link_list)
