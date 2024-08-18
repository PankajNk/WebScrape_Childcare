import requests
from bs4 import BeautifulSoup
import csv
import time
import re

def convert_url(original_url):
    new_url = original_url.replace('/providers/', 'licensing-history/')
    return new_url


def fetch_link_to_scrape(id_value):
    try:
        hrefs = []
        url = f"https://childcarefind.okdhs.org/providers?zip-code={id_value}"
        response = requests.get(url)
        
        scarpe_data = BeautifulSoup(response.text, 'html.parser')
        # print(scarpe_data) #todo find not working
        elements = scarpe_data.select('a[class*="_1b0crnf1 _1q4scjf6 z-[2]"]')
        print(f"Number of elements found: {len(elements)}")

        #todo optmmize
        for element in elements:
            href = element.get('href', 'No href attribute')
            if href != 'No href attribute':
                hrefs.append(href)
        return hrefs

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []


def extract_data_from_link(urls):
    data = {}


    for url in urls:
        print(f"Processing URL: {url}")
        try:
            full_url = f'https://childcarefind.okdhs.org/{url}'
            data['URL'] = full_url
            # print(full_url)

            url_response = requests.get(full_url)
            url_data = BeautifulSoup(url_response.text, 'html.parser')

            # partcular data
            ChildCare_home = url_data.find('div', class_='_1q4scjf7').get_text(strip=True) if url_data.find('div', class_='_1q4scjf7') else None
            ChildCare_name = url_data.find('div', class_='_1q4scjf7').find_next_sibling('h1').get_text(strip=True) if url_data.find('div', class_='_1q4scjf7') else None
            program_level = url_data.find('div', class_='_1q4scjf7').find_next_sibling('h2').get_text(strip=True) if url_data.find('div', class_='_1q4scjf7') else None
            # provider = url_data.find('div', class_='_18i9ibq1 _1q4scjf0 _1umd8ia0').get_text(strip=True) if url_data.find('div', class_='_18i9ibq1 _1q4scjf0 _1umd8ia0') else None
            data['ChildCare Center'] = ChildCare_home
            data['ChildCare Name']  = ChildCare_name
            data['Program Level'] = program_level
            # print(ChildCare_home)
            # print(ChildCare_name)
            # print(program_level)


            #address ,contact,contract
            parent_div = url_data.find('div', class_='bd04r4l _1q4scjf6 _1umd8ia1')
            if parent_div:
                child_divs = parent_div.find_all('div', class_='_1umd8ia2')
                print(child_divs)
                for idx, child_div in enumerate(child_divs, start=1):
                    child_text = child_div.get_text(strip=True)
                    print(f"Text from child div #{idx}: {child_text}")
                    if idx == 1:
                        data['Contact No'] = child_text
                    elif idx == 2:
                        data['Email'] = child_text
                    elif idx == 3:
                        data['Address'] = child_text
                    elif idx == 4:
                        data['Subsidy Contract Number'] = child_text
                    # print(f"Text from child div #{idx}: {child_text}")
            
            #Provider 
            provider_div = url_data.find('div', class_='_18i9ibq1 _1q4scjf0 _1umd8ia0')
            if provider_div:
                h2 = provider_div.find('h2', class_='_1q4scjf5')
                first_last_texts = provider_div.get_text(separator=' ', strip=True).split('<br>')
                if len(first_last_texts) >= 2:
                    print("im here")
                    data['Day'] = first_last_texts[0].strip()
                    data['Hours'] = first_last_texts[1].strip()
                    print(first_last_texts[0].strip())
                # else:
                    # print(first_last_texts[0].strip())
                        # data['first'] = first_name
                        # data['last'] = last_name

            

            

            #hours 
            repeated_divs = url_data.find_all('div', class_='yuxh4x0')
            for idx, div in enumerate(repeated_divs, start=1):
                dt = div.find('dt')
                dd = div.find('dd')
                print('yes')
                print(dt.get_text(strip=True) if dt else None)
                print(dd.get_text(strip=True) if dd else None)
                # if 'Visit Date' in dt_text:
                #     data['Visit Date'] = dd_text
                # elif 'Visit Type' in dt_text:
                #     data['Visit Type'] = dd_text
                # elif 'Purpose of Visit' in dt_text:
                #     data['Purpose of Visit'] = dd_text
                # print(f"Date from div #{idx}: {data['date']}")
                # print(f"Date1 from div #{idx}: {data['date1']}")

            #ages accepted 
            repeated_li = url_data.find_all('li', class_='_18i9ibq1 _1q4scjf0')
            
            for idx, li in enumerate(repeated_li, start=1):
                age_text = li.get_text(strip=True)
                if 'Infants (0-11 months)' in age_text:
                    data['Infants (0-11 months)'] = 'yes'
                elif 'Toddlers (12-23 months; 1yr.)' in age_text:
                    data['Toddlers (12-23 months; 1yr.)'] = 'yes' 
                elif 'Preschool (24-48 months; 2-4 yrs.)' in age_text:
                    data['Preschool (24-48 months; 2-4 yrs.)'] = 'yes'
                elif 'School-age (5 years-older)' in age_text:
                    data['School-age (5 years-older)'] ='yes'


            #total capcity 
            # if section:
            #     h2 = section.find('h2', class_='_1q4scjf5')
            #     if h2:
            #         h2_text = h2.get_text(strip=True)
            #         print(h)
            #         following_text = ''.join([str(t) for t in h2.find_next_siblings(text=True)])
            #         print(f"H2 Text: {h2_text}")
            #         print(f"Text following H2: {following_text.strip()}")


            #license
            license_div = url_data.find('div', class_='_18i9ibq1 _1q4scjf0 _1ntxxnq0')
            if license_div:
                h2_element = license_div.find('h3', class_='_1q4scjf4')
                data['Licensing Specialist'] = h2_element.text.strip()
                div_pppp = license_div.find('div', class_='_1ntxxnq1')
                div_pppp_text = div_pppp.get_text(strip=True) if div_pppp else None
                sibling_div = div_pppp.find_next_sibling('div')  
                sibling_text = sibling_div.get_text(strip=True) if sibling_div else None
                # print(div_pppp_text)
                data['Licensing Specialist_contact no'] = div_pppp_text

            #license history
            license_visits = url_data.find_all('article', class_='bd04r4l _1q4scjf0 _1elult33')
            data['Visit for non-compliances OBSERVED'] = license_visits
            # print(f"Visits No {len(license_visits)}")
            license_infos = url_data.find_all('div', class_='bd04r4g _1elult32')
            #entries = url_data.find_all('div', class_='bd04r4g _1elult32')

            # A counter to generate unique keys for each visit entry
            entry_counter = 1
            # Initialize variables to store the extracted information
            visit_date = None
            visit_type = None
            purpose_of_visit = None
            
            for entry in license_infos:
                dt = entry.find('dt', class_='_1q4scjf2')
                dd = entry.find('dd')
                
                if dt and dd:
                    if dt.text == 'Visit Date':
                        visit_date = dd.text
                    elif dt.text == 'Visit Type':
                        visit_type = dd.text
                    elif dt.text == 'Purpose of Visit':
                        purpose_of_visit = dd.text

                # Once we have collected data for one full entry (Date, Type, Purpose), print it
                if visit_date and visit_type and purpose_of_visit:
                    # print(f"{visit_date}\n{visit_type}\n{purpose_of_visit}\n{convert_url(full_url)}/{visit_date}")
                    
                    key_prefix = f'visit_entry_{entry_counter}_'
                    data[f'{key_prefix}visit_date'] = visit_date
                    data[f'{key_prefix}visit_type'] = visit_type
                    data[f'{key_prefix}purpose_of_visit'] = purpose_of_visit
                    doc_link = f'{convert_url(full_url)}/{visit_date}'
                    data[f'{key_prefix}document link'] = doc_link


                    # Increment the counter for the next entry
                    entry_counter += 1

                    # Reset for the next set of license info
                    visit_date = None
                    visit_type = None
                    purpose_of_visit = None
          
            




            


            print("\n\n")
            print("...........Next................")
            
            # print(ChildCare_home)
            # print(ChildCare_name)
            # print(program_level)
           





        except requests.RequestException as e:
            print(f"An error occurred while processing {url}: {e}")
        time.sleep(1)  # delay between requests
    return data
    
if __name__ == "__main__": 

    hrefs = fetch_link_to_scrape(73008)
    if hrefs:
        extract_data_from_link(hrefs)
    else:
        print("No hrefs found to process.")
print(data)