# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify,render_template,make_response
import main
import json
from flask_cors import CORS
           

app = Flask(__name__)  
CORS(app)              

@app.route('/api', methods=["POST"])
def process_biofalcon():
    text=request.json['text']
    if 'exp' in request.args:
        if 'rules' in request.json:
            rules=request.json['rules']
    else:
        if 'rules' in request.json:
                rules=request.json['rules']
        else:
            rules=[1,2,3,4,5,8,9,10,12,13,14]
    mode=request.args.get('mode')
    if text=='':
        return '{"entities":-1}'
        
    if 'k' in request.args:
        k=int(request.args['k'])
    else:
        k=1
    if mode=="short":
            entities=main.process_word_E(text,k)
            return jsonify (
                entities=entities
                )
    elif mode=="long":
            entities=main.process_text_E_R(text,rules,k)
            return jsonify (
                entities=entities
                )         
            
      
@app.route('/')
def render_static_home():
    return render_template('index.html')      

@app.route('/api-use')
def render_static_api():
    return render_template('api-use.html')   

@app.route('/description')
def render_static_description():
    return render_template('description.html')   
 

    
if __name__ == '__main__':
    hostName="0.0.0.0"
    apiPort=5005
    app.run(debug=False,host=hostName,port=apiPort)
