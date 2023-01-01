import urllib.request as urllib
from bs4 import BeautifulSoup as bs4
import requests, os, random, re, json, os, time
import _thread, threading, csv
from datetime import datetime
from string import punctuation

enc = "iso-8859-15"
path_txt = "E:/File_Manager/Projects/Python\Doc Files/TXT"
path_csv = r"E:\File_Manager\Projects\Python\Doc Files\CSV"

user_agents = [agent for agent in open(f"{path_txt}/user-agents.txt", encoding=enc).read().split("\n")]

stop_words = {word.lower() for word in re.sub(r"(\n+|'|,)", " ", open(f"{path_txt}/stop_words.txt", encoding=enc).read()).split(" ")}

url = "https://www.nairaland.com/"
url_list = [url+"/news/1", url+"/news/2", "https://www.nairaland.com/news/3"]

def make_req(url, user_agents):
    user_agent = random.choice(user_agents)
    header = {"User-Agent":user_agent}
    
    while True:
        try:
            ses_req = requests.Session()
            req = urllib.Request(url, None, header)
            res = urllib.urlopen(req).read()
            break
        except Exception as e: 
            print(e)
    
    soup = bs4(res, "html.parser")
    return soup
    
def get_urls(url_list, user_agents):
    topic_links = {}
    
    for url in url_list:
        soup = make_req(url, user_agents)
        items  = soup.select ("td > a")
        date_items = soup.select("td > a, td > a ~ b")
        #print(date_items)
        
        for item in items:
            #print(item)
            
            if "www.nairaland" in item.attrs["href"]:
                index = date_items.index(item)

                date = f"{date_items[index + 1].text}  {date_items[index + 2].text} {date_items[index + 3].text}"
                #print(date_items[index + 3])
                topic_links[item.attrs["href"]] = date
    #print(topic_links)
    return topic_links

    
def get_nth_topics(url_list, user_agents):
    topic_links = get_urls(url_list, user_agents)
    filename = "nl_dataset.csv"
    dic = {}
    csvFile = open(f"{path_csv}/{filename}", encoding=enc)
    csvFileRead = csvFile.read()
    csvFile.close()
    
    csvFileWrite = open(f"{path_csv}/{filename}", "a")
    csvObj = csv.writer(csvFileWrite)
    counter = 0
    start = time.time()
    
    for i, topic_url in enumerate(topic_links):
        #print(topic_url)
        if topic_url not in csvFileRead:
            try:
                if counter%30 == 0:
                    print(f"[Running: {int(time.time() - start )} second(s) - {counter} items and more..]  Please wait...")
                full_url = topic_url
                moved_date = topic_links[topic_url]

                soup = make_req(topic_url, user_agents)
                topic_url = topic_url.replace(url[:-1], "")
                all_links_in_td = soup.select("td.bold.l.pu a")
                auth_name = all_links_in_td[4].text
                
                topic = soup.select(r"a[href~='{}']".format(topic_url))
                view = soup.select("p.bold")
                view = re.search(r"\([0-9]+\s{1}Views\)", view[0].text)[0][1:-7]
                comments = soup.select("a")
          
                for comment in comments:    
                    if re.search(r"\([0-9]+\)", comment.prettify()) and topic_url in comment.attrs["href"]:
                        num_of_comm = int(comment.text[1:-1]) * 30
               
                category = soup.select("h2")
                category = re.search(r"- [A-Z /a-z]+ - Nairaland", category[0].text)
                if category:
                    category = category[0][2:-12]
                
                time_moved = moved_date.split()[0]
                day_moved = moved_date.split()[2]
                month_moved = moved_date.split()[1]
                year_moved = moved_date.split()[3]
                full_date_moved = day_moved + "-" + month_moved + "-" + year_moved
                day_name_moved = datetime.strptime(f"{month_moved} {day_moved}, \
                {year_moved}", "%b %d, %Y").strftime("%a")
                
                date = soup.select("span.s")
                date = date[0].text
                time_created = date.split()[0]
                year = time.strftime("%Y")
                day = time.strftime("%d")
                month = time.strftime("%b")
               
                if len(date.split()) > 1:
                    day = date.split()[3]
                    month = date.split()[2].replace(",", "")

                if "," in date:
                    year = date.split()[-1]

                day = day.replace(',', '')
                month = month.replace(',', '')
                print(day)

                day_name_created = datetime.strptime(f"{month} {day}, {year}", \
                "%b %d, %Y").strftime("%a")
                
                date_created = day + "-" + month + "-" + year
                date_accessed = time.strftime("%d-%b-%Y")
                time_accessed = time.strftime("%I:%M%p").lower()
                
                datetime_created = time.strptime(f"{date_created}-{time_created}", \
                "%d-%b-%Y-%I:%M%p")
                datetime_moved = time.strptime(f"{full_date_moved}-{time_moved}", \
                "%d-%b-%Y-%I:%M%p")
                
                datetime_created = time.mktime(datetime_created)
                datetime_moved  = time.mktime(datetime_moved)
                    
                if topic:
                    topic = topic[0].text
                    key_words = {}
                    filtered_topic = ""
                    
                    for letter in topic:
                        if letter not in punctuation:
                            filtered_topic += letter
                    
                    filtered_topic = re.sub(r"(\s+|[0-9]+|-|'')", " ", filtered_topic)
                    key_words = list({key.lower() for key in filtered_topic.split() if key.lower() not in stop_words})
                    
                    if full_url not in csvFileRead:
                        counter += 1
                        #print("not there...")
                        
                        #appending to csv file
                        csvObj.writerow([topic, category, int(view), int(num_of_comm), key_words, \
                        auth_name, day_name_created, date_created, time_created, \
                        day_name_moved, full_date_moved, time_moved, date_accessed, \
                        time_accessed, datetime_created, datetime_moved, full_url])
                                
            except Exception as e:
                print(e)
   
    record = "records" if counter > 1 else "record"
    csvFileWrite.close()
    print(f"New {counter} {record} added in {int(time.time() - start)} seconds")
    print("<operation successful>")

def main():
    get_nth_topics(url_list, user_agents)

if __name__ == "__main__":
    print("testing speaker...")
    #main()
