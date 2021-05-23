SUCCESS_RESPONSE = {'success': True}
NOT_SUCCESS_RESPONSE = {'success': True}
TOO_MANY_DATA = {'detail': 'Too many data are sent'}
UNVALID_DATA = {'detail': 'Unvalid data'}
ALREADY_EXIST = {'detail': 'It already exists'}

class ResponseMessage:

    def __init__(self):
        self.message = {}
    
    def add(self, content):
        for key in content.keys():
            self.message[key] = content[key]
        
        return self
    
    def build(self):
        return self.message