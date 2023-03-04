# flake8: noqa



# def singleton(class_):
#     instances = {}
#     def getinstance(*args, **kwargs):
#         if class_ not in instances:
#             instances[class_] = class_(*args, **kwargs)
#         return instances[class_]
#     return getinstance

# @singleton
# class MyClass():
#     pass

# a = MyClass(a=45)



# def dec(fun):
#   def inner(*args, **kwargs):
#     fun(*args, **kwargs)
#     # print(args, kwargs)
#   return inner

# @dec
# def test_fun(g=9):
#   print(g)

# test_fun()

############################## testing login 100 times #########################

# from steps.selenium.selenium_steps import Login
# from scripts.scripts_config import Configs
# import time

# start = time.time()

# for _ in range(100):
#   Login(Config=Configs)()
#   print("{}th login".format(_))

# print("###################### Time took: {}".format(time.time() - start))



############################## testing like #########################
# from steps.selenium.selenium_steps import Like, Login, LikePosts, RetweetPosts, Retweet
# from scripts.scripts_config import Configs
# import time

# Like(post_url="https://twitter.com/RahulGandhi/status/1607943336224264193", by_all_bots=True)()
# Like(post_url="https://twitter.com/RahulGandhi/status/1607943336224264193", by_all_bots=True)()
# Login()()
# time.sleep(15)
# Like(post_url='https://twitter.com/Zii_creates/status/1578453689249181697?s=20&t=qgeepYVe_qTvhmBA6W2ZUw',
#      config=Configs)()
# time.sleep(10)


# RetweetPosts(user_profile="https://twitter.com/I_am_Based_", number_of_posts=1000)()

################################# testing Logging SocketHandlers #################################
# import logging

# logging.warning("this is a info")
# r = logging.LogRecord(name="TA", level=0,
#                       pathname="",
#                       lineno=0,
#                       msg="hello ", args="", exc_info=None)


# class streamlogging(logging.StreamHandler):

#   def __init_(self, **kwargs):
#     super().__init__(**kwargs)


# fd = open("/home/xd/Documents/Python_codes/twitter_aut/log.txt", 'w')
# sl = streamlogging(stream=fd)
# logger = logging.getLogger(name="TA")



################################# logging filehandler #################
# import logging

# logger = logging.getLogger(name="TA")
# logger.setLevel(level=logging.INFO)

# fh = logging.FileHandler('SPOT.log')
# fh.setLevel(logging.INFO)

# logger.addHandler(fh)

# logger.warning("hello")


############################################ chat gpt testing ############################
import openai as ai

# import 

# assert "openai" in openai_secret_manager.get_services()
# secrets = openai_secret_manager.get_secret("openai")

# print(secrets)

# secret = "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"
secret = "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"
ai.api_key = secret


# Set the prompt
class generate_gpt3_response():
    """
    Disallowed usage
    We don't allow the use of our models for the following:

    * Illegal activity
    * Child Sexual Abuse Material or any content that exploits or harms children
    * Generation of hateful, harassing, or violent content
    * Generation of malware
    * Activity that has high risk of physical harm
    * Activity that has high risk of economic harm
    * Fraudulent or deceptive activity
    * Adult content, adult industries, and dating apps
    * Political campaigning or lobbying
    * Activity that violates people's privacy
    * Engaging in the unauthorized practice of law, or offering tailored legal advice without a qualified person reviewing the information
    * Offering tailored financial advice without a qualified person reviewing the information
    * Telling someone that they have or do not have a certain health condition, or providing instructions on how to cure or treat a health condition
    * High risk government decision-making

    Query OpenAI GPT-3 for the specific key and get back a response
    :type user_text: str the user's text to query for
    :type print_output: boolean whether or not to print the raw output JSON
    """
    def __init__(self, user_prompt,
                 engine='text-davinci-003',
                 temperature=0.5,
                 max_tokens=50):
        self.user_prompt = user_prompt
        self.engine = engine
        self.temperature = temperature
        self.max_tokens=max_tokens

    
    completions = ai.Completion.create(
            engine=self.engine,  # Determines the quality, speed, and cost.
            temperature=0.9,            # Level of creativity in the response
            prompt=user_text,           # What the user typed in
            max_tokens=50,              # Maximum tokens in the prompt AND response
            n=1,                        # The number of completions to generate
            stop=None,                  # An optional setting to control response generation
        )

    # Displaying the output can be helpful if things go wrong
    if print_output:
        print(completions)

    # Return the first choice's text
    return completions.choices[0].text


if __name__ == '__main__':
    prompt = 'tell me about the reality of corrupt indian politics'
    response = generate_gpt3_response(prompt)
    
    print(response)