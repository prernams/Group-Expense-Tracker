# Group-Expense-Tracker
API - Based Application

Required Start Structure of Database is as Follows:<br/>
{"groups": [ ], "expense": [ ], "balances": [ ]}


The goal of this project is to create a simple expense tracker in which a group of people can manage their expenses and get a summary of their balance.


## Features - 

1. Ability to create a group
	- Each group should have a name and list of members
	- Whenever an expense is added within a group, the members of the expense who are not part of the group should automatically be added as a member.
	  For example - A user creates a group "Home" with members ["A", "B"] and later adds an expense which has user "C", the group members will be - ["A" "B", "C"]
2. Ability to add an expense within a group
	Structure of an expense - 
  
        {
          "name": "Fruits and Milk",
          "items": [{"name": "milk", "value": 50, "paid_by": [{"A": 40, "B": 10}], "owed_by": [{"A": 20,"B": 20, "C": 10}]},
                    {"name": "fruits", "value": 50, "paid_by": [{"A": 50}], "owed_by": [{"A": 10,"B": 30, "C": 10}]}]
        }
3. Ability to update an expense within a group
    - Structure same as add expense.
4. Ability to delete an expense within a group
5. Ability to get the balance of a group such that the balances are simplified. which means -
    - If A,B,C are in a group such that A owes B Rs 100, B owes C Rs 100, the balance summary should show that A owes C Rs 100
    - The structure should be -

    	    {
            "name": "Home",
            "balances": {
              "A": {
                "total_balance": -100.0
                "owes_to": [{"C": 100}],
                "owed_by": []
              },
              "B": {
                "total_balance": 0.0
                "owes_to": [],
                "owed_by": []
              },
              "C": {
                "total_balance": 100.0
                "owes_by": [{"A": 100}],
                "owed_to": []
              }
            }
        	}
