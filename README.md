# Twitter Automation  [![flake8](https://github.com/yasirfaizahmed/twitter_automation/actions/workflows/flake8.yml/badge.svg)](https://github.com/yasirfaizahmed/twitter_automation/actions/workflows/flake8.yml)     ![flake8](https://img.shields.io/badge/lines%20of%20code-1229-blueviolet)

   Twitter Automation is a robust and flexible automation framework, written in Python, that uses tools like Selenium, OpenCV, PyAutoGUI, and OpenAI GPT-3 to perform various actions on Twitter. With Twitter Automation, users can tweet, retweet, like, and comment on tweets without using the Tweepy API. This independence allows for greater customization and control over Twitter automation.

## Key Features
- Tweet a tweet using GPT-3 with a user-provided prompt and tags
- Retweet and like tweets
- Comment on tweets
- Independent of Tweepy API
- Utilizes Selenium for web automation, OpenCV for image processing, PyAutoGUI for GUI automation, and OpenAI GPT-3 for natural language processing.

## Technical Details
Twitter Automation is built on top of cutting-edge technologies, including:
- OpenAI GPT-3 for natural language processing, powering the tweet generation functionality
- Selenium for web automation, allowing users to perform various actions on the Twitter website
- OpenCV for image processing, enabling Twitter Automation to recognize specific elements on the Twitter website
- PyAutoGUI for GUI automation, allowing Twitter Automation to simulate user input and interactions

## Getting Started

`cd twitter_automation`

`sudo apt update`

install the python packages

`python3 -m pip install -r requirements.txt`

install the dependencies

`sudo apt-get install $(cat package.txt)`

install the chrome web-driver from https://chromedriver.chromium.org/downloads
unzip and set the environment variable as `DIVER_PATH` as the path of the chromedriver binary-file like shown.

`export DRIVER_PATH='/path/to/the/chromedriver'`


also add the METADATA.json file path to your environment using

`export METADATA='/path/to/metadata.json'`

metadata.json is a file that you have to write it on your own, its a file that contains the credentials of the twitter userprofile/bots using which you
are going to use this framework APIs
just create a metadata.json file and use the format like below

      {
        "bot1": {
          "EMAIL_KEY": "username1.dummymail.com",
          "USERNAME_KEY": "twitterhandle1",
          "PASSWORD_KEY": "password1"
        },
        "bot2": {
          "EMAIL_KEY": "username2.dummymail.com",
          "USERNAME_KEY": "twitterhandle2",
          "PASSWORD_KEY": "password2"
        }
      }

NOTE: 
if you want to use Openai gpt-3's response as tweet content then you will also be needing a Openai API key, add the key to your environment using
`export API_KEY='your key'`

## Conclusion
Overall, Twitter Automation is a powerful automation framework that allows for greater control and customization over Twitter automation. With its use of cutting-edge technologies, users can perform a variety of actions on Twitter without the limitations of the Tweepy API.
