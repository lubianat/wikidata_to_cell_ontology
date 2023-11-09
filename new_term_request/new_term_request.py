import requests
from wdcuration import query_wikidata

# Function to run SPARQL query and get results
def run_sparql_query(qid):
    # SPARQL query with placeholders for the QID
    sparql_query = """
    SELECT  
    (GROUP_CONCAT(DISTINCT ?aliases; SEPARATOR="; ") as ?alias) 
    ?label 
    (CONCAT("PMID:", ?pmid_num) as ?pmid) 
    ?anatomical_location  
    ?uberon_id
    (GROUP_CONCAT(DISTINCT ?superclasses; SEPARATOR="; ") as ?superclass) 
    (GROUP_CONCAT(DISTINCT ?cl_ids; SEPARATOR="; ") as ?cl_id) 
     ?wikipedia_link WHERE {
      BIND(wd:Q934475 as ?cell_type)  # replace QID with the actual cell type QID
      ?cell_type rdfs:label ?label .
      OPTIONAL {?cell_type skos:altLabel ?aliases .}
      OPTIONAL {?cell_type p:P31 [ prov:wasDerivedFrom [ pr:P248 ?reference ] ].
                ?reference wdt:P698 ?pmid_num .} 
      OPTIONAL {
        ?cell_type wdt:P927 ?anatomical_structure .
        ?anatomical_structure rdfs:label ?anatomical_location .
        ?anatomical_structure wdt:P1554 ?uberon_id . 
      }
      OPTIONAL {
        ?cell_type wdt:P279 ?parent .
        ?parent rdfs:label ?superclasses .
        ?parent wdt:P7963 ?cl_ids . 
      }
      ?wikipedia_link schema:isPartOf <https://en.wikipedia.org/>;
        schema:about ?cell_type; 
      FILTER(LANG(?label) = "en")
      FILTER(LANG(?aliases) = "en")

      FILTER(LANG(?anatomical_location) = "en")
      FILTER(LANG(?superclasses) = "en")
    }
    GROUP BY ?label ?pmid ?pmid_num ?anatomical_location  ?uberon_id ?wikipedia_link 
    """
    sparql_query = sparql_query.replace("QID", qid)

    return query_wikidata(sparql_query)

def create_ntr_markdown():
    orcid = "0000-0003-2473-2313"
    qid = "Q934475"

    # Get the SPARQL query results
    result = run_sparql_query(qid)[0]

    def get_parents(result):
        parents = result['superclass'].split("; ")
        parent_ids = result['cl_id'].split("; ")
        parent_text = ""
        for i, parent in enumerate(parents):
            parent_text += f"    {parent} ([{parent_ids[i]}](https://www.ebi.ac.uk/ols4/ontologies/cl/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F{parent_ids[i]}?lang=en))\n" 
        return parent_text
    
    ntr_markdown = f"""
    **Preferred term label**
    {result['label']}

    **Synonyms**
    {result.get('alias', {})}
    (synonyms from http://www.wikidata.org/entity/{qid})

    **Definition**
    Definition needed. {result.get('pmid', {})}

    **Parent cell type term**
    {get_parents(result)}

    **Anatomical structure where the cell type is found**
    {result['anatomical_location']}([UBERON:{result.get('uberon_id', {})}](https://www.ebi.ac.uk/ols4/ontologies/uberon/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FUBERON:{result.get('uberon_id', {})}?lang=en))\n" 

    **Your ORCID**
    https://orcid.org/{orcid}

    **Additional notes or concerns**
    Wikipedia reference: {result.get('wikipedia_link', {})}
    """
    
    # Print the NTR markdown
    print(ntr_markdown)

# Run the function to create the NTR markdown
create_ntr_markdown()
