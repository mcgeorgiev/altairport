# curl http://localhost:5000/post -d "destination=SSH" -d "source=GLA" -X POST -v

from flask import Flask, request
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('source')
parser.add_argument('destination')

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}

INPUT = {}


# gets the single item
class Todo(Resource):
    def get(self, todo_id):
        #abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

# gets the list
class TodoList(Resource):
    def get(self):
        return TODOS

class PostData(Resource):
    def post(self):
        args = parser.parse_args()
        INPUT = args
        return INPUT, 201

api.add_resource(PostData, '/post')
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')



if __name__ == '__main__':
    app.run(debug=True)
