from flask import Flask
from flask import request
from SA import trans
app = Flask(__name__)

content = '''
<form action="/compile" method='post'>
<p>
<textarea rows="30" cols="40" name="code">
</textarea>
<input type="submit" value="Send">
</p>
</form>
'''

@app.route('/')
def hello():
    return content

@app.route('/compile',methods=['POST'])
def compile():
    if request.method == 'POST':
        return trans(str(request.form.get('code')).replace('\r\n','\n')).replace('\n','<br />')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
