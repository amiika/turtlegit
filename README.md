# turtlegit

## What?

turtlegit is a Linked Data endpoint backed by local git repository that stores graphs as ordered turtle (.ttl) files. 
Currently supports SPARQL Graph HTTP Protocol (GET / PUT / POST) with "text/turtle" content type.

## What next?

1. Add custom otsrdflib sorters to settings
2. Support memory based SPARQL queries (Construct & Update files)
3. Support for full SPARQL using SparqlWrapper as proxy to any 'real' triplestore
4. Support for JSON-LD Framing and storing JSON-LD frames

## Maybe then?

1. Support for creating new files using N3 forward chaining with Fuxi (or other)
2. Support for normalized json-ld (This format loses prefix mappings)
3. Support GraphQl queries (flask-graphql, rdf-graphql, etc.)
