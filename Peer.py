# Ian Kusner 
# CS202080
# 12/15/2020


# Each Peer is set up only knowing the resource it holds and the policy for that resource,
# along with where to get resources in the policy  

''' 

### MESSAGE FORMAT ###

  IF TYPE IS REQUEST:
  {'type': String, 'sender': String, 'reciever': String, 'resource': List of Dicts}
  Dicts inside list must have format {'resource': String, 'issuer': String}

  EXAMPLE:
  {
    'type': 'request', 
    'sender': 'client', 
    'reciever': 'rs' , 
    'resource': [{'resource': 'c1 , 'issuer': 'rs'}]
  }

  IF TYPE IS OFFER:
  {'type': String, 'sender': String, 'reciever':String, 'resource': Dict}
  Dict is key:value pair of {resource: what resource is}

  EXAMPLE:
  {
    'type': 'request', 
    'sender': 'client', 
    'reciever': 'rs' , 
    'resource': {'c2': 'ID810123', 'c3': 'score780'}
  }


### PEER ###
  Peer is made by including its name, e.g. 'rs' , 'as_1'

  Each peer has a resource Dict where the key is the resource and the value is what that resource is

  Each peer has a Policy. the Policy will have the same keys as the 'resource' member 
  Policy decides what is needed for resource to be sent 

  Peer has a 'credentials_recieved' which is a same format as resource Dict
  {'c4': 'alice@kent.edu'}


  ### POLICY ###

  Policy member for each Peer includes the credential(s) that it holds as the key, and the subsequent policy
  for that credential

  Policy for a crediential will be either a list of dictionaries, or will be 'True' if the credential is 
  unlocked by default 

  The dictionaries in each policy for each credential include the resource needed to unlock, and where that 
  resource is obtained (issuer)

  Format is:
  'c1': [{'resource': 'c2, 'issuer': 'as_1'}, {'resource': 'c3', 'issuer': 'as_2'}]
  or:
  'c2': True

### L KNOWLEDGE BASE ###

  Upon recieving offers for resources, the Peer will store this in the 'credentials_recieved' member
  'credentials_recieved' is a Dict with key: of resource and value: of what resource is

  EXAMPLE:
  'credentials_recieved' = {
    'c2': 'ID810123',
    'c3': 'score780'
  }

  Peer holds resource in 'resource' member

  For example 'rs' has 'c1' in its 'resource', while 'client' has 'c4' 

### OUTPUT ###

  program will output a success message if the initial request was able to be completed

  program will out an error message if there was an error with the initial request (like requesting an invalid resource)

  Change 'showMessages' flag below to show/hide the message chain of the authorization
'''
showMessages = True


# MESSAGE THAT CLIENT WILL SENT TO RS TO GET AUTH STARTED
INITIAL_MESSAGE = {'type': 'request', 'sender': 'client', 'reciever': 'rs', 'resource': [{'resource':'c1', 'issuer':'rs'}]}

# Policy and resource for each of the Peers 
rs_resource = {
  'c1': '20 % Discount'
}
rs_policy = {
  'c1': [{'resource': 'c2', 'issuer': 'as_1'},{'resource':'c3', 'issuer':'as_2'}],
}

client_resource = {
  'c4': 'alice@kent.edu'
}
client_policy = {
  'c4': True
}

as1_resource = {
  'c2': 'ID810234567X',
}
as1_policy = {
  'c2': True,
}

as2_policy = {
  'c3': [{'resource': 'c4', 'issuer':'client'}]
}

as2_resource = {
  'c3': 'score780'
}

class Peers:
  def __init__(self,name,policy,resource):
    self.name = name # name of Peer (client, rs, as_1, as_2)
    self.policy = policy
    self.resource = resource
    self.credentials_recieved = {}
  
  def checkFormat(self,message):
    #check if message has all valid keys
    if not all(key in message for key in ['type', 'sender','reciever','resource']):
      print('key error')
      return True

    # check to see if 'resource' is a list of resources
    if not isinstance(message['resource'],list):
      print('list error')
      return True
    
    # check formatting of resources requested
    for r in message['resource']:
      # resource request must be a dictionary
      if(isinstance(r, dict)):
        # dictionary must have keys 'resource' and 'issuer'
        if not all(key in r for key in ['resource', 'issuer']):
          print('resource key error')
          return True

        # 'resource' and 'issuer' are strings
        if not(isinstance(r['resource'],str) & isinstance(r['issuer'],str)):
          print('resource string error')
          return True

      else:
        print('resource dict error ')
        return True
    
    #Check valid 'type'
    valid_types = ['request', 'offer', 'success', 'error']
    if message['type'] not in valid_types:
      return True
    
    # Make sure sender and reciever are strings
    if not (isinstance(message['sender'],str) & isinstance(message['reciever'] , str)):
      return True
    

  # given unresolved messsages and list of resources that correspond to an unresolved message, find which sender to return to
  def findSender(self,messages,return_list):
      for m in messages:
        resources = []
        for r in m['resource']:
          if(isinstance(r['resource'],list)):
            resources.extend(r['resource'])
          else:
            resources.append(r['resource'])
        if set(resources) == set(return_list):
          return m['sender']

  def findIssuer(self,resource, to_unlock):
    issuer = ''
    # find the issuer of the resources to request 
    for item in self.policy[to_unlock]:
      if item['resource'] == resource:
        issuer = item['issuer']
    return issuer
  
  def resolver(self,message,Mrec,Msent):
    # check formatting of initial message and make sure request is for valid resource
    if(len(Mrec) == 1):
      formatError = self.checkFormat(message)
      if formatError:
        return [{'type':'error', 'content':'600 "Bad Request" '}]
      requests = set([m['resource'] for m in message['resource']])
      available = set(list(self.resource))
      if(len(requests.difference(available)) > 0):
        return [{'type':'error', 'content':'606 "Resource Not Found" {}'.format(message['resource'])}]
      


    ### TYPE REQUEST ###
    if(message['type'] == 'request'):
      #if initial message and request to rs isnt found,
      #then return 606 error
      if(len(Mrec) == 1):
        if(message['resource'][0]['resource'] not in self.resource.keys()):
          return [{'type':'error', 'content':'606 "Resource Not Found" {}'.format(message['resource'])}]
        
      return_messages = []

      # all requested resources 
      req_resources = [r['resource'] for r in message['resource']]

      # if request is for list of credentials make req_resources a list instead of a list of list made above 
      if(len(req_resources) == 1 and isinstance(req_resources[0],list)):
        req_resources = req_resources[0]
        
      my_recieved = [request for request in Mrec if request['reciever'] == self.name and request['type'] == 'request']
      to_offer = []

      for requests in message['resource']:
        resource = requests['resource']

        held = list(self.resource.keys())
        
        have = list(self.credentials_recieved) + held

        # make resource a list if it is not
        if not isinstance(resource,list):
          resource = [resource]

        # if reciever is the issuer of the resource 
        # or the peer has the requested resources necessary to make an offer 
        if(requests['issuer'] == self.name or set(have).intersection(resource) == set(resource)):
          for r in resource:
            if r not in self.policy:
              return [{'type':'error', 'content':'601 "Unauthorized Request" {}'.format(message['resource'])}]
            
            if(isinstance(self.policy[r],list)):  
              needed_resources = [re['resource'] for re in self.policy[r]]
            else:
              needed_resources = self.policy[r]

            # if resource is unlocked by default and the peer can make an offer
            if(needed_resources != True and (set(needed_resources).intersection(have) == set(needed_resources))):
              if r in req_resources:
                to_offer.append(r)
            elif( (needed_resources == True and set(have).intersection(resource) == set(resource)) ):
              if r in req_resources:
                to_offer.append(r)
            elif(needed_resources != True):
              test = []

              # list of resources needed to be requested sorted by sender
              needed_resources = list(set(needed_resources).difference(have))
              #print('needed resources', needed_resources)
              for n in needed_resources:
                issuer = self.findIssuer(n,r)
                test.append({'resource': n, 'issuer': issuer})
              newList = sorted(test, key=lambda k: k['issuer'])

              # group all credentials of one issuer into one list
              # after, will have list of list of grouped credentials by issuer
              temp1 = []
              temp2 = []
              issuer = newList[0]['issuer']
              for i in newList:
                if i['issuer'] == issuer:
                  temp2.append(i)
                else:
                  temp1.append(temp2)
                  temp2 = [i]
                issuer = i['issuer']
              temp1.append(temp2)

              # make 'resource' part of message to send back to another peer to handle the requests
              arr_rec = []
              for t in temp1:
                to_send = []
                send_to = t[0]['issuer']
                for j in t:
                  to_send.append(j['resource'])
                if len(to_send) == 1:
                  arr_rec.append({'resource': to_send[0], 'issuer': send_to})
                else:
                  arr_rec.append({'resource': to_send, 'issuer':send_to })

              return_messages.append({'type': 'request', 'sender': self.name, 'reciever': message['sender'], 'resource': arr_rec})

        # credentials not unlocked and not held by peer, so make requests for them
        else:
            for r in resource:
              return_messages.append({'type': 'request', 'sender': self.name, 'reciever': requests['issuer'], 'resource': [{'resource': r, 'issuer': requests['issuer']}]})

      if len(to_offer) > 0:
        returned_resource = dict(map(lambda x : (x,self.resource[x]) , to_offer ))
        return_messages.append({'type': 'offer', 'sender': self.name, 'reciever': message['sender'], 'resource': returned_resource})
      
      # list of messages being sent back
      return return_messages



    ### TYPE OFFER ###
    if(message['type'] == 'offer'):

      #if offer is of resource initially requested then the auth has successfully completed 
      for r in Mrec[0]['resource']:
        lastMessage = list(message['resource'])
        firstMessage = [r['resource']]
        if(set(firstMessage) == set(lastMessage)):
          return [{'type':'success','content': message['resource']}]
      

      # add offer of resource to peers recieved credentials 
      if isinstance(message['resource'],list):
        for creds in message['resource']:
          self.credentials_recieved.update(creds)
      else:
        self.credentials_recieved.update(message['resource'])

      # requests to peer 
      my_recieved = [request for request in Mrec if request['reciever'] == self.name and request['type'] == 'request']


      # offers that peer has sent 
      offers_sent = [request for request in Msent if request['sender'] == self.name and request['type'] == 'offer']

      rec = []
      unsent = []

      # finds which requests that the peer has already sent offers for 
      for m in my_recieved:
        sender = m['sender']
        rrecieved = []
        for r in m['resource']:
          if(isinstance(r['resource'],list)):
            for c in r['resource']:
              rrecieved.append(c)
          else:
            rrecieved.append(r['resource'])
        for o in offers_sent:
          offers = set()
          if isinstance(o['resource'],list):
            resources_in_offer = [list(item)[0] for item in o['resource']]
            offers = set(resources_in_offer)
          else:
            offers = set(list(o['resource']))

          if(offers == set(rrecieved) and o['reciever'] == sender):
            unsent.append(m)
        
      # remove requests that have already been offered 
      for messages in unsent:
        try:
          my_recieved.pop(my_recieved.index(messages))
        except:
          return[{'type': 'error', 'content': 'Error processing request'}]
      
      # make list of resources by request that still need to be offered by the peer 
      for r in my_recieved:
        temp = []
        for res in r['resource']:
          if(isinstance(res['resource'],list)):
            temp.extend(res['resource'])
          else:
            temp.append(res['resource'])
        rec.append(temp)

      return_list = []

      # make list of all credentials that the peer has ( resources it's the holder of, and resources it recieved from other peers )
      held = list(self.policy.keys())
      my_creds = list(self.credentials_recieved) + held

      for r in rec:
        # if peer has all the credentials needed to complete the request 
        if(set(my_creds).intersection(set(r)) == set(r)):
            return_list.extend(list(set(my_creds).intersection(set(r))))
      # based on resources being offered, find sender of request for all those resources
      sender = self.findSender(my_recieved,return_list)
      if(sender == None and len(return_list) > 0):
        return [{'type':'error', 'content': 'error completing request'}]
      
        # either send one resource as an offer, or send a list of resources as an offer

      all_resources = {**self.resource , **self.credentials_recieved}
      returned_resource = dict(map(lambda x : (x,all_resources[x]) , return_list))

      if len(return_list) > 0:
        return [{'type':'offer', 'sender': self.name, 'reciever': sender, 'resource': returned_resource}]



if __name__ == "__main__":
    client = Peers(
      name='client',
      policy= client_policy,
      resource= client_resource
      )
    rs = Peers(
      name='rs',
      policy= rs_policy,
      resource= rs_resource
        
      )
    as_1 = Peers(
      name='as_1',
      policy= as1_policy,
      resource= as1_resource
      )
    as_2 = Peers(
      name='as_2',
      policy= as2_policy,
      resource= as2_resource
      )

    # initial message send by client 
    queue = [INITIAL_MESSAGE]

    Mrec = []
    Msent = []

    # send message to appropriate reciever
    # returns false if process loop should stop
    # otherwise returns nothing and keeps going
    def processMessage(m):
      if 'reciever' not in m:
        print('600 "Bad Request" ')
        return False

      Mrec.append(m)
      sent = []
      if m['reciever'] == 'client':
        sent = client.resolver(m,Mrec,Msent)
      elif m['reciever'] == 'rs':
        sent = rs.resolver(m,Mrec,Msent)
      elif m['reciever'] == 'as_1':
        sent = as_1.resolver(m,Mrec,Msent)
      elif m['reciever'] == 'as_2':
        sent = as_2.resolver(m,Mrec,Msent)
      else:
        print('600 "Bad Request" ')
        return False


      # process where to send messages sent from resolver 
      if sent != None:
        for s in sent:
          if s['type'] == 'success':
            print('{} was successfully recieved\n'.format(*s['content'].values()))
            return False
          elif s['type'] == 'error':
            print(s['content'] + '\n')
            return False
          else:
            queue.append(s)
            Msent.append(s)

    while(queue != []):
      m = queue.pop(0)

      # auth either succeeded or an error was encountered 
      if processMessage(m) == False:
        break;

    if(showMessages):
      print('Messages:',*Mrec, sep='\n')