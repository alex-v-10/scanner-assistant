import requests

def get_community_data(coin_id):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        community_data = data.get('community_data', {})
        return community_data
    else:
        print(f"Error fetching data: {response.status_code}")
        return None
      
def get_coingecko_ignore_list(date, cursor):
    cursor.execute('SELECT coingecko FROM ignore_list WHERE date = ?', (date,))
    row = cursor.fetchone()
    if row and row[0]:
        return row[0].split(',')
    else:
        return []