# task

Create a chatbot, that will be able to query infromation on natural disaster from the csv file.
In order to do that, create an MCP server, that will query CSV file with Pandas and return user responses to their question from chat.

# mcp module
the target of this module is to provide the relevant data from csv based on user queries in natural language. the goal is to identify optimal search algorythom to return the most relevant data to the user.

# UI module
here the queried data must be presennted to the user.
- text description must be presented
- + some graphical representation, which might be a chart or a table wathever llm thinks is appropriate. your goal is to identify the way to generate this data. maybe you could render HTML by llm and insert it into the UI which user will see it's totally up to you. based on the data identify the relevant graphical representation and render it accordingly.

# data
in the docs folder 2 files exists
- docs/1900_2021_DISASTERS_Example.csv - analyze this file to understand the data structure and come up with effective way to query it
- docs/1900_2021_DISASTERS_FULL.csv - this is a huge csv which contains all the rows, use it only for final production version when query algorythoms are optimized.

## user queries
put to the readme the best queries which alows to fully show the dataset by providing a graphical representation and text description of the data. (for that if you want you can carefully read the big docs/1900_2021_DISASTERS_FULL.csv)

# tests
cover backend mcp part by tests 80% minimum

# technical details
language: mcp -> python, UI -> any lang
architecture: the MCP is the only api. so from front using langchain tool we can access the csv data. no rest or other communication ways.
the example of how to use llm and which provider you can check in the project: https://github.com/bntdeep/LLMThreatsAnalysis.git
