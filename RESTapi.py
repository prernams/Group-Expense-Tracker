# Loading required Libraries
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
import json
from ast import literal_eval

# Creating the Flask Application
app = Flask(__name__)
api = Api(app)

# Default Page - Shows entire DB


class Welcome(Resource):
    def get(self):
        with open('data.json', 'r') as openfile:
            json_object = json.load(openfile)
        # return data and 200 OK code
        return {'Database': json_object}, 200


# To view or add all expenses
class expense(Resource):

    # Managing Balance among Group Members
    def update_balance(grp, paid_, owed_):
        with open('data.json', 'r') as openfile:
            data = json.load(openfile)
        to_pay_name = []
        to_pay_val = []
        paid_names = []
        owed_names = []

        # Group the names of people who have paid
        for i in paid_:
            if(list(i.keys())[0] not in paid_names):
                paid_names.append(list(i.keys())[0])

        # Group the names of people who owe i.e All people involved in the transaction
        for i in owed_:
            if(list(i.keys())[0] not in owed_names):
                owed_names.append(list(i.keys())[0])

        # Set of all names
        names = paid_names+owed_names

        # index of the member in the balances DB
        this_grp = 0

        for this_grp in range(0, len(data['balances'])):
            if(grp == data['balances'][this_grp]['name']):
                break

        for mem in set(names):
            # Seperating ans storing the paid and owed arrays
            for p in owed_:
                if(mem == list(p.keys())[0]):
                    # How much the person owes to that product
                    still_owed = p[mem]
                    owed = p

            for p in paid_:
                if(mem == list(p.keys())[0]):
                    paid = p

            in_g = 0  # to check if balances collection exists for that member
            for i in data['balances'][this_grp]["balances"]:
                if(mem in list(i.keys())[0]):
                    in_g = 1

            # if not already present, CREATE
            if(in_g == 0):
                new_data = {
                    mem:
                    {
                        "total_balance": 0,
                        "owes_to": [],
                        "owed_by": []
                    }
                }
                data['balances'][this_grp]["balances"].append(new_data)

            # if member has paid more than owed, make a list of how much others have to pay to them
            if(mem in paid_names and owed[mem] < paid[mem]):
                to_pay_name.append(mem)
                to_pay_val.append(paid[mem]-owed[mem])

            # Sort this list in descending order
            to_pay_name = list(reversed([x for _, x in sorted(
                zip(to_pay_val, to_pay_name))]))
            to_pay_val = list(reversed(sorted(to_pay_val)))

        for mem in set(names):
            total = 0

            # Similar to what I did earlier
            for p in owed_:
                if(mem == list(p.keys())[0]):
                    still_owed = p[mem]
                    owed = p
            for p in paid_:
                if(mem == list(p.keys())[0]):
                    paid = p

            if(mem not in paid_names or paid[mem] < owed[mem]):
                x = 0
                while(still_owed > 0 and len(to_pay_val) > 0):

                    # Check if the first person in the to_pay array can cover for the owes of the member
                    if(still_owed <= to_pay_val[x]):

                        # Create tuples to add to their records Accordingly
                        temp1 = {mem: to_pay_val[x]}
                        temp2 = {to_pay_name[x]: to_pay_val[x]}

                        # Adding these tuples to the DB
                        for i in data['balances'][this_grp]["balances"]:
                            if(to_pay_name[x] == list(i.keys())[0]):
                                i[to_pay_name[x]]["owed_by"].append(temp1)
                                i[to_pay_name[x]]["total_balance"] += to_pay_val[x]
                            if(mem == list(i.keys())[0]):
                                i[mem]["owes_to"].append(temp2)
                                i[mem]["total_balance"] -= to_pay_val[x]

                        # Decrease the Capacity of the first in the to_pay array
                        to_pay_val[x] -= still_owed
                        still_owed = 0
                        break
                    else:
                        temp1 = {mem: to_pay_val[x]}
                        temp2 = {to_pay_name[x]: to_pay_val[x]}
                        still_owed -= to_pay_val[x]
                        for i in data['balances'][this_grp]["balances"]:
                            if(to_pay_name[x] == list(i.keys())[0]):
                                i[to_pay_name[x]]["owed_by"].append(temp1)
                                i[to_pay_name[x]]["total_balance"] += to_pay_val[x]
                            if(mem == list(i.keys())[0]):
                                i[mem]["owes_to"].append(temp2)
                                i[mem]["total_balance"] -= to_pay_val[x]
                        a = to_pay_name.pop(x)
                        a = to_pay_val.pop(x)

        return data

    # Displays all expenses
    def get(self):
        with open('data.json', 'r') as openfile:
            json_object = json.load(openfile)
        # return data and 200 OK code
        return {'data': json_object['expense']}, 200

    # To add new expenses
    def post(self):
        data = ""
        with open('data.json', 'r') as openfile:
            data = json.load(openfile)
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('group', required=True)  # add args
        parser.add_argument('item', required=True)
        parser.add_argument('value', required=True)
        parser.add_argument('paid_by', required=True)
        parser.add_argument('owed_by', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        s1 = literal_eval(args['paid_by'])  # Formatting string arrays
        s2 = literal_eval(args['owed_by'])

        # Group the names of people who have paid and who all owe
        paid_names = []
        owed_names = []

        for i in s1:
            if(list(i.keys())[0] not in paid_names):
                paid_names.append(list(i.keys())[0])
        for i in s2:
            if(list(i.keys())[0] not in owed_names):
                owed_names.append(list(i.keys())[0])
        names = paid_names+owed_names

        in_g = 0  # Check if group given exists.
        for grp in data['groups']:
            if(grp['name'] == args['group']):
                in_g = 1
                # Make sure all members involved in expense are in the mentioned group.If not, Add them.
                for mem in set(names):
                    if(mem not in list(grp['Members'])):
                        a = grp['Members']
                        a.append(mem)
                        grp['Members'] = a

        if(in_g == 0):
            return {
                'message': f"'{args['group']}' not in created groups"
            }, 409

        # Creating the new collection to be added
        new_data = {
            'name': args['group'],
            "items":
            [{
                "name": args['item'],
                "value": args['value'],
                "paid_by": s1,
                "owed_by": s2
            }]
        }

        b = 0  # Checking of expenses in that group exists. if yes, we need a different structure of the data collection
        for exp in data['expense']:
            if exp['name'] == args['group']:
                b = 1
                new_data = {
                    "name": args['item'],
                    "value": args['value'],
                    "paid_by": s1,
                    "owed_by": s2
                }
                exp['items'].append(new_data)  # Add to already existing items

        if b == 0:
            # Add a fresk colloction with group name
            data['expense'].append(new_data)

        # add the newly provided values
        with open("data.json", "w") as outfile:
            json.dump(data, outfile)

        # Update balances and write these to the DB too.
        data = expense.update_balance(args['group'], s1, s2)
        with open("data.json", "w") as outfile:
            json.dump(data, outfile)
        return {'data': data['expense']}, 200  # return data with 200 OK

    def put(self):
        data = ""
        with open('data.json', 'r') as openfile:
            data = json.load(openfile)
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('group', required=True)  # add args
        parser.add_argument('item', required=True)
        parser.add_argument('value', required=False)
        parser.add_argument('paid_by', required=False)
        parser.add_argument('owed_by', required=False)
        args = parser.parse_args()  # parse arguments to dictionary

        if(args['paid_by']):
            s1 = literal_eval(args['paid_by'])
            s1 = s1[0]
        if(args['owed_by']):
            s2 = literal_eval(args['owed_by'])
            s2 = s2[0]

        in_g = 0  # to check if the mentioned group exists
        for grp in data['groups']:
            if(grp['name'] == args['group']):
                in_g = 1
                a = []
                if(args['paid_by']):
                    a += list(s1.keys())
                if(args['owed_by']):
                    a += list(s2.keys())
                for mem in a:
                    # Add members to group of not alreafy present
                    if(mem not in list(grp['Members'])):
                        a = grp['Members']
                        a.append(mem)
                        grp['Members'] = a

        if(in_g == 0):  # if group does not exist, return an error saying so.
            return {
                'message': f"'{args['group']}' not in created groups"
            }, 409

        in_g = 0

        # Updating all provided values
        for exp in data['expense']:
            if(exp['name'] == args['group']):
                in_g = 1
                for item in exp['items']:
                    if(item['name'] == args['item']):
                        if(args['value']):
                            item['value'] = args['value']
                        if(args['paid_by']):
                            item['paid_by'] = s1
                        if(args['owed_by']):
                            item['owed_by'] = s2
        if(in_g == 0):
            return {
                'message': f"'{args['group']}' not in created groups"
            }, 409

        with open("data.json", "w") as outfile:
            json.dump(data, outfile)
        return {'data': data['expense']}, 200  # return data with 200 OK

    def delete(self):
        data = ""
        with open('data.json', 'r') as openfile:
            data = json.load(openfile)
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('group', required=True)  # add args
        parser.add_argument('item', required=True)
        parser.add_argument('value', required=False)
        parser.add_argument('paid_by', required=False)
        parser.add_argument('owed_by', required=False)
        args = parser.parse_args()  # parse arguments to dictionary
        s1 = []
        s2 = []
        if(args['paid_by']):
            s1 = literal_eval(args['paid_by'])
        if(args['owed_by']):
            s2 = literal_eval(args['owed_by'])
        in_g = 0
        for grp in data['expense']:
            if(grp['name'] == args['group']):
                in_g = 1

        if(in_g == 0):
            return {
                'message': "Record Not Found"
            }, 404

        # Checking if all provided values match, and then deleting the rows
        for exp in data['expense']:
            if(exp['name'] == args['group']):
                for item in exp['items']:
                    if(item['name'] == args['item']):
                        if(args['value']):
                            if(item['value'] != args['value']):
                                continue
                        if(args['paid_by']):
                            if(item['paid_by'] != s1):
                                continue
                        if(args['owed_by']):
                            if(item['owed_by'] != s2):
                                continue
                    index = exp['items'].index(item)
                    m = exp['items'].pop(index)
        with open("data.json", "w") as outfile:
            json.dump(data, outfile)
        data = expense.update_balance(args["group"], s1, s2)
        with open("data.json", "w") as outfile:
            json.dump(data, outfile)
        return {'data': data['expense']}, 200  # return data with 200 OK

# To display Balances


class balance(Resource):
    def get(self):
        f = open('data.json')
        data = json.load(f)
        return {'Balances': data['balances']}, 200

# To manage groups of users


class create_group(Resource):
    def get(self):
        f = open('data.json')
        data = json.load(f)
        return {'Groups': data['groups']}, 200

    # Creating new groups
    def post(self):
        data = ""
        with open('data.json', 'r') as openfile:
            data = json.load(openfile)
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('name', required=True)  # add args
        parser.add_argument('Members', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        # Creating the new Collection for Balances
        new_data = {
            'name': args['name'],
            "balances": []
        }
        data['balances'].append(new_data)

        # if group aready exists, Throw an error
        if data['groups'] != {} and args['name'] in list(data['groups']):
            return {
                'message': f"'{args['name']}' already exists."
            }, 409

        else:
            a = args['Members'][1:-1]
            a = a.split(',')

            # create new dataframe containing new values
            new_data = {
                'name': args['name'],
                'Members': a
            }

            data['groups'].append(new_data)

            # add the newly provided values
            with open("data.json", "w") as outfile:
                json.dump(data, outfile)
            return {'data': data['groups']}, 200  # return data with 200 OK


# Define functionality for each endpoint
api.add_resource(Welcome, '/')
api.add_resource(create_group, '/group')
api.add_resource(expense, '/expense')
api.add_resource(balance, '/balance')

if __name__ == '__main__':
    app.run()  # Run the flask app.
