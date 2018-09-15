# Question-Answering
The engine receives a question in the form of "who is the X of Y", "When was Z born" and "What is W" and returns the answer based on building a knowledge graph from Wikipedia.

Summary:
1. Receive a question in the form of "Who is the X of Y", "When was Z born" and "What is W" and converts it to SPARQL query form.
2. Extract the relevant entities from the question and finds the most relevant Wikipedia page url for that entity.
3. Crawl the Wikipedia page found in step 2 and build a knowledge graph which can be queried via SPARQL
4. Runs the generated SPARQL query from step 1 on the knowledge graph generated in step 3
5. Prints the answer to the question.
