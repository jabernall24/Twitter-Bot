
# Twitter Bot

#### Set up SSM Parameter store
    -  Get Twitter API Keys
    - Go to AWS System Manger
    - Add your four Twiiter keys (ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
        - Navigate to the Parameter store
        - Click Create Parameter
        - Give parameter name (ACCESS_TOKEN_KEY)
        - Choose standard tier
        - Type string
        - Copy your key (ACCESS_TOKEN_KEY) into value
        - repeat for the other keys (ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
        

1. Gets user's most common tweeted out words from previous month based on a command

### Set up

1. Create Lambda Layer from ```wordcloud-twython.zip``` if you haven't yet
    - Go to AWS Lambda
    - Layers
    - Create Layer
    - Give it a name
    - Upload zip file
    - Choose Python 3.6 as the runtime


2. Create a lambda function
    - On permissions ```create a new role from AWS policy templates```
    - Give it a role name and add ```AWS KMS decryption permissions```
    - Create function
    - Add the following permission after creating it ```AmazonSSMReadOnlyAccess``` 
    - Timeout: 1 minute

3. Add Lambda layer

4. Add files
    - Create a file Twitter.py and copy the contents of Twitter.py
    - Copy the get_mentions_for_wordcloud.py into the lambda_function.py
    - Change the command from the lambda_function.py on line 14 to the command you would like to trigger your lamda function

5. Trigger function every minute
    - On Configuration Tab click Add trigger
    - On Select Trigger select ```CloudWatch Events/EventBridge```
    - Create rule with name (ex: run_every_minute)
    - Rule type Schedule Expression
    - For running every minute ```rate(1 minute)```


2. Tweet out user's most common tweeted out words from previous month by getting Twitter handle from DynamoDB Table

### Set up

1. Create Lambda Layer from ```wordcloud-twython.zip``` if you haven't yet
    - Go to AWS Lambda
    - Layers
    - Create Layer
    - Give it a name
    - Upload zip file
    - Choose Python 3.6 as the runtime

2. Create a lambda function
    - On permissions ```create a new role from AWS policy templates```
    - Give it a role name and add ```AWS KMS decryption permissions```
    - Create function
    - Add the following permission after creating it ```AmazonSSMReadOnlyAccess``` 
    - Create Policy with following
        - Service: DynamoDB
        - Actions
            - Access Level: ```Scan``` and  ```UpdateItem```
    - Attach policy
    - Timeout: 1 minute
    - Create enviroment variable TABLE_NAME with the name of your DynamoDB Table

3. Add Lambda layer

4. Add files
    - Create a file Twitter.py and copy the contents of Twitter.py
    - Copy the word_cloud_generator.py into the lambda_function.py

5. Create DynamoDB table

6. Add items to the DynamoDB table
    - The following should be in each record in the table
    - ```handle```  type String and primary key
        - The user's twitter handle
    - ```tweeted``` type Boolean
        - Indicating weather our bot has tweeted this handle yet (should create them with this field false)
        
7. Trigger function every week
    - On Configuration Tab click Add trigger
    - On Select Trigger select ```CloudWatch Events/EventBridge```
    - Create rule with name (ex: run_once_a_week)
    - Rule type Schedule Expression
    - For running every minute ```rate(7 days)```
