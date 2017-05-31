# JRec (Fuzzy Partial Ordering Version)

Required Python Package:
CaboCha-0.69, MeCab 0.996 
NLTK 3.0.0 (not compatible with newer versions)   pip install -v nltk==3.0.0
jTransliterate
enum (for Python 2.7)
enum34 (Sometimes enum doesn't work)
requests


Initialize: interface = JRecInterface()

Get a New Article:  req = interface.request()

                    req.doc_id  //Document ID with article/paragraph/sentence details  e.g. k10010470031000_para1_s2 
                    
                                // And you can get the first 15 characters of "doc_id" to get the id for URL
                                
                    req.text    //Text
                    
User Feedback:      interface.response(True or False)

Get Json String:    s = interface.recommender_json_str()

Construct a new JRecInterface object from Json String:
                    interface_t = JRecInterface(recommender_json_str=s)

See Also: Example.py
