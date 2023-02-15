# E-Falcon

E-Falcon recognizes entities in a natural language text and links them to their corresponding PLATOON semantic data models.

E-Falcon is avaiable as an online API with a demo interface [https://labs.tib.eu/sdm/efalcon/](Demo)

Here is an example on how to use the API via cURL request

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"text":"Wind Farms consist of many wind turbines"}' \
  https://labs.tib.eu/sdm/efalcon/api?mode=long
```
The API folder contains the source code of E-Falcon. E-Falcon can be run using docker (please refer to the docker.txt file).

The index folder contains the necessary script to generate the index utilized by E-Falcon.
The generated index should be uploaded to an ElasticSearch instance.
