import requests, re, csv, pprint, json
from bs4 import BeautifulSoup

def generate_raw_county_data():
	url = "https://github.com/nytimes/covid-19-data/blob/master/us-counties.csv"
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	table = soup.find_all("tr")
	table_list = [row.text for row in table]
	refined_table = [re.sub(r"\n*", "", row) for row in table_list]
	refined_table = [string.split(",") for string in refined_table]

	with open("raw_county_data.csv", "w") as fout:
		writer = csv.writer(fout)
		writer.writerows(refined_table)
	return "raw_county_data.csv"

def us_state_list():
	url = "https://en.wikipedia.org/wiki/U.S._state"
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	table = soup.find(class_ ="plainlist").text
	table_list = table.split("\n")
	for_return = [re.sub(r"\xa0", "", row) for row in table_list][1:-1]
	for_return += ["Other"]
	return for_return

def generate_refined_county_data(filename):
	with open(filename, "r") as fin:
		dictReader = csv.DictReader(fin)
		listOfDicts = [dict(row) for row in dictReader]
		# print(listOfDicts[0])
		state_dict = {}
		state_list = us_state_list()
		for state in state_list:
			state_dict[state] = {}
		# newDict ["county"] newDict ["cases"] newDict ["deaths"]
		i = 0
		for dict_row in listOfDicts:
			if dict_row["state"] not in state_list:
				if state_dict["Other"]=={}:
					state_dict["Other"] = {"Other":"Other", "cases":0, "deaths":0}
					state_dict["Other"]["cases"] = int(dict_row["cases"])
					state_dict["Other"]["deaths"] = int(dict_row["deaths"])
				else:
					state_dict["Other"]["cases"] += int(dict_row["cases"])
					state_dict["Other"]["deaths"] += int(dict_row["deaths"])
			else:
				# print(dict_row["date"] + "___" + dict_row["county"])
				if (dict_row["county"] == 'Snohomish'):
					i= int(dict_row["cases"])
				if dict_row["county"] in state_dict[dict_row["state"]]: 
					state_dict[dict_row["state"]][dict_row["county"]]["cases"] = int(dict_row["cases"])
					state_dict[dict_row["state"]][dict_row["county"]]["deaths"] = int(dict_row["deaths"])
				else:
					state_dict[dict_row["state"]][dict_row["county"]] = {}
					state_dict[dict_row["state"]][dict_row["county"]]["cases"] = int(dict_row["cases"])
					state_dict[dict_row["state"]][dict_row["county"]]["deaths"] = int(dict_row["deaths"])
		# pprint.pprint(state_dict["Alabama"])
		print(i)
		json.dump(state_dict, open("state_data.json","w"))
		return state_dict

def generate_csv_file(state_dict):
	# pprint.pprint(state_dict["Wyoming"])
	with open("state_data.csv", "w") as fin:
		writer = csv.writer(fin)
		writer.writerow(["state","county","cases","deaths"])
		for state in state_dict:
			if state != "Other":
				for county in state_dict[state]:
					writer.writerow([state, county,
						str(state_dict[state][county]["cases"]),
						str(state_dict[state][county]["deaths"])])
			else:
				writer.writerow(["Other","Other", 
					str(state_dict["Other"]["cases"]),
					str(state_dict["Other"]["deaths"])])

if __name__ == "__main__":
	raw_file = generate_raw_county_data()
	json_dict = generate_refined_county_data(raw_file)
	generate_csv_file(json_dict)