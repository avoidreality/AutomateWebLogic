'''
  Python/Jython by Kyle Smith 2017 - 3.0 - Logs to file on disk.


    , ; , .-'"""'-.   , ; ,
  \\|/  .'         '.  \|//
   \-;-/   ()   ()   \-;-/
   // ;               ; \\
  //__; :.         .; ;__\\
 `-----\'.'-.....-'.'/-----'
        '.'.-.-,_.'.'
          '(  (..-'
            '-'
'''


import os
import threading
import getopt
import sys
import commands


version = '3.0'
log_file = 'autodeploy.log'

class start_nm_thread(threading.Thread):
    """Class to start Node Manager from a different thread. Takes the listen address of NodeManager and a
       arbitrary name for the constructor to instatiate an object of this class.

    """
    def __init__(self, name, LAddress, domain_path):
        threading.Thread.__init__(self)
        self.name = name
        self.LAddress = LAddress
        self.domain_path = domain_path

    def run(self):
        """This is the method that is called when start() is called on this class. """
        print "Starting thread " + self.name
        s = "Starting thread " + self.name
        auto = AutoDeploy()
        auto.toDisk(s)
        self.nm_go(self.name, self.LAddress, self.domain_path)
        print "Exiting thread " + self.name
        s2 = "Exiting thread " + self.name
        auto.toDisk(s2)

    def nm_go(self,threadName, LAddress, domain_path):
        """This is the method run calls. This method attempts to start nodemanager on a host. """
        print "Attempting to start Node Manager."
        auto = AutoDeploy()
        auto.toDisk("Attempting to start Node Manager.")
        auto.toDisk("This is the listen address %s. This is the thread name: %s" % (LAddress, threadName))
        startNodeManager(verbose='false', NodeManagerHome=domain_path + os.sep + 'nodemanager', ListenAddress=LAddress)

class AutoDeploy(object):
    """This class deploys managed servers to WebLogic.  """
    def __init__(self):
        """Creates AutoDeploy object """
        
    def editing(self):
        """Start an edit session."""
        edit()
        startEdit()

    def activating(self):
        """Save and activate changes."""
        save()
        activate()

    def zap(self, serverName, earName):
        """Try at least 2 times to delete the managed server.  """
        count = 0
        undeployed = False
        print "Trying to undeploy the following managed server %s. This is try number: %d" % (str(serverName), (count + 1))
        self.toDisk("Trying to undeploy the following managed server %s. This is try number: %d" % (str(serverName), (count + 1)))
        while (count < 2 and not undeployed):
            try:
               self.editing()
               progress = undeploy(serverName, block='true')
      
               if (progress.isFailed()):
                   print "Undeployment failed for %s!" % serverName
                   self.toDisk("Undeployment failed for %s!" % serverName)
                   progress.printStatus()
                   count = count + 1
                   #self.loopToContinue()
                   self.activating()
                   progress.printStatus()
               else:
                   print "Undeployment successful for %s!" % serverName
                   self.toDisk("Undeployment successful for %s!" % serverName)
                   progress.printStatus()
                   undeployed = True
                   self.activating()
                   progress.printStatus()
                   #verify manually that the undeployment was successful
                   #self.loopToContinue()
            except:
                print "Exception thrown during undeployment for server %s!" % serverName
                self.toDisk("Exception thrown during undeployment for server %s!" % serverName)
                java.lang.Thread.sleep(1000)
                count = count + 1
                self.activating()

        #if it was not deleted based on the managed server name try deleting based on the ear name.
        ear_count = 0
        if (not undeployed and count >= 1):
          while (not undeployed and ear_count < 2):
            try:
                self.editing()
                progress = undeploy(earName, block='true')

                if (progress.isFailed()):
                    print "Undeployment failed for ear: %s!" % str(earName)
                    self.toDisk("Undeployment failed for ear: %s!" % str(earName))
                    progress.printStatus()
                    ear_count = ear_count + 1
                    #self.loopToContinue()
                    self.activating()
                    progress.printStatus()
                else:
                    print "Undeployment success for ear: %s!" % str(earName)
                    self.toDisk("Undeployment success for ear: %s!" % str(earName))
                    undeployed = True
                    progress.printStatus()
                    #verify manually that the undeployment was successful
                    #self.loopToContinue()
                    self.activating()
                    progress.printStatus()
                
                #print "Undeployment of %s successful!" % serverName


            except Exception, e:
                print "This exception was thrown trying to deploy %s: %s" % (str(serverName), str(e))
                self.toDisk("This exception was thrown trying to deploy %s: %s" % (str(serverName), str(e)))
                java.lang.Thread.sleep(1000)
                ear_count = ear_count + 1
                self.activating()
   

    def AdminConnect(self, username, password, hostname):
       """ Connect to the admin server based on the past in username, password, and hostname. """
       connect(username, password, "t3://" + hostname + ':7001')
       self.toDisk("=" * 60)
       self.toDisk("Connected to the admin server of the following machine: %s" % hostname)
       self.toDisk("=" * 60)
       print "=" * 60
       print "Connected to the admin server of the following machine: %s" % hostname
       print "=" * 60


    #Node manager shell scripts needs to be started first
    def connectToNodeManager(self, username, password, host, domain, domain_path):
      """ Connect to the Node Manager server with the username, password, and domain parameters. """
      r = nm()
      if not r:

         try:
            #try to connect
            nmConnect(username, password, host, domainName=domain)
         except Exception, e:
            print "Exception thrown trying to connect to nodemanager: %s" % str(e)
            self.toDisk("Exception thrown trying to connect to nodemanager: %s" % str(e))
            #try to start node manager on the OS in a different thread
            nm_thread = start_nm_thread("AutoD", host, domain_path)
            nm_thread.start() 

        
         else:
            self.toDisk("Connected to Node Manager")
            self.toDisk("=" * 60)
            self.toDisk("Successfully connected to Node Manager at the following host: %s at the following domain: %s." % (str(host), str(domain)))
            self.toDisk("=" * 60)              
            print "Connected to Node Manager"
            print "=" * 60
            print "Successfully connected to Node Manager at the following host: %s at the following domain: %s." % (str(host), str(domain))
            print "=" * 60
            return

    
         count = 0
         r = nm()
         while (not r and  count < 5):
            r = nm()
            if r:
                break
            print "Trying to connect again in 30 seconds. This is try number: %d" % (count + 1)
            self.toDisk("Trying to connect again in 30 seconds. This is try number: %d" % (count + 1))
            java.lang.Thread.sleep(30000)
            #try to connect
            try:
                nmConnect(username, password, host, domainName=domain)
            
            except Exception, e:
                print "Exception thrown trying to connect to node manager at host: %s : %s" % (host, str(e))
                self.toDisk("Exception thrown trying to connect to node manager at host: %s : %s" % (host, str(e)))
                count = count + 1
  
         self.toDisk("=" * 60)
         self.toDisk("Successfully connected to Node Manager at the following host: %s at the following domain: %s." % (str(host), str(domain)))
         self.toDisk("=" * 60)
         print "=" * 60
         print "Successfully connected to Node Manager at the following host: %s at the following domain: %s." % (str(host), str(domain))
         print "=" * 60
  
    def GetMsStatus(self, server):
      """ Pass a server name to this function and determine its state """
      print "Getting status of server %s " % server
  
      try:
        domainRuntime() #change wlst shell to this
    
        s = '/ServerRuntimes/' + server
        cd(s)
      except Exception, e:
        print 'oh no :/ This exception was thrown: %s' % str(e)
        self.toDisk('oh no :/ This exception was thrown: %s' % str(e))
        return "EXCEPTION"
	
      return cmo.getState()
  
    def printState(self, server='RiteCommon'):
      """Pass in the name of the server as a string and obtain the state of the managed server. """
      state(server)
  

    #node manager needs to be started first for this to work
    def startMS(self, server='RiteCommon'):
      """Prints status data and starts a managed server. server argument is a string. Depends on being connected to NodeManager. """

      self.printState(server)
      count = 1
      while ((self.GetMsStatus(server) != "RUNNING") and (count < 6)):
          print "Trying to start server: %s. This is try number: %d" % (server, count)
          self.toDisk("Trying to start server: %s. This is try number: %d" % (server, count))
          nmStart(server, 'Server')
          self.toDisk("The state of server is %s" % self.GetMsStatus(server)) # try to print the state of the server to disk for logging purposes
          java.lang.Thread.sleep(2000) # sleep 2 seconds between tries
          count = count + 1

  
      
      self.printState(server)


    def start2(self, server='RiteCommon'):
      """Prints status data and starts a managed server with start command and not Node Manager. Server argument is a string. """

      self.printState(server)
      count = 1
      while ((self.GetMsStatus(server) != "RUNNING") and (count < 6)):
          print "Trying to start server: %s. This is try number: %d" % (server, count)
          self.toDisk("Trying to start server: %s. This is try number: %d" % (server, count))
          try:
              start(server, 'Server', block='true')
              self.toDisk("%s started" % server)
          except Exception, e:
              print "Exception trying to start server [%s]. This is the exception: %s" % (server, str(e))
              self.toDisk("Exception trying to start server [%s]. This is the exception: %s" % (server, str(e)))
              
          java.lang.Thread.sleep(2000) # sleep 2 seconds between tries
          count = count + 1
      
      self.printState(server)

    def stopMS(self, server='RiteCommon'):
      """Stop the managed server passed in as an argument. The server argument takes a string type. """
      if(self.GetMsStatus(server) == "SHUTDOWN" or self.GetMsStatus(server) == "EXCEPTION"):
         print "Server already shutdown."
         self.toDisk("Server already shutdown.")
         self.printState(server)
         return
      self.printState(server)

      count = 0
      shut = False #control while loop with this boolean - editing() threw an exception 1 time. Try to keep going after exception.
      while(not shut and count < 4):
        try:
          self.editing()
          shutdown(server, force="true", ignoreSessions="true")
          self.toDisk("%s is shutdown" % server)
          shut = true
      
        except WLSTException, e:
            print "Exception thrown trying to shutdown server: %s. This is the exception: %s" % (server, str(e))
            self.toDisk("Exception thrown trying to shutdown server: %s. This is the exception: %s" % (server, str(e)))
            count = count + 1
            print "Going to try again to shutdown the server"
            self.toDisk("Exception thrown trying to shutdown server: %s. This is the exception: %s" % (server, str(e)))
            self.activating()

      if (count >= 4):
          print "[%s] probably not shutdown" % server
          self.toDisk("[%s] probably not shutdown" % server)
          return
      else:
          self.activating()
      
      self.printState(server)


    def deleteEar(self, serverName, earName):
      """Delete the ear passed in as a string argument. """
      print "Preparing to delete server %s with ear name %s. " % (serverName,earName)
      self.zap(serverName, earName)
  

    def up(self, appName, path, targets):
      """Upload the app to WebLogic given the 1) appName, 2) path, and 3) target. These arguments are passed as strings.
         The app and target seem to be the same. The path is the path to where the new ear is located.
      """ 
 
      d = False
      count = 0
      print "Starting deployment of: %s this is try number: %d" % (str(appName), (count + 1))
      self.toDisk("Starting deployment of: %s this is try number: %d" % (str(appName), (count + 1)))
      while (not d and count < 4):
        try:
          self.editing()
          progress = deploy(appName, path, targets, timeout=90000, block='true', upload='true')
          if (not progress.isFailed()):
              print "The deployment is a success for %s." % appName
              self.toDisk("The deployment is a success for %s." % appName)
              d = True
              progress.printStatus()
              self.activating()
              progress.printStatus()
              return
          if (progress.isFailed()):
              print "The deployment for %s failed." % appName
              self.toDisk("The deployment for %s failed." % appName)
              progress.printStatus()
              count = count + 1
              self.activating()
              progress.printStatus()
        except:
          count = count + 1
          print "Sleeping for 2 seconds..."
          self.toDisk("Sleeping for 2 seconds...")
          java.lang.Thread.sleep(2000) #sleep for 2 java seconds
          print "Trying to deploy again - exception thrown in upload of new release for: %s" % str(appName)
          self.toDisk("Trying to deploy again - exception thrown in upload of new release for: %s" % str(appName))
          self.activating()

      if (count >= 4):
          print "Deployment  of server [%s] probably not successful." % str(appName)
          self.toDisk("Deployment  of server [%s] probably not successful." % str(appName))
          return
      
      print "Done deploying: %s" % appName
      self.toDisk("Done deploying: %s" % appName)

    def loopToContinue(self):
        """This method asks the user if they want to continue or not. This is useful for debugging. """
        #pause before starting the servers
        answer = raw_input("Do you want to continue now with the release? ")
    
        if (answer.upper().startswith('N')):
            print "The program is exiting now."
            self.toDisk("The program is exiting now.")
            exit('0')

    
        
        while(not(answer.upper().startswith('Y'))):
            answer = raw_input("Do you want to continue now with the release? ")
            if (answer.upper().startswith('N')):
               print "The program is exiting now."
               self.toDisk("The program is exiting now.")
               exit('0')

    def default(self):
        """This method is the default behavior of the program. The method stops, deletes, installs, and starts managed servers """
        #read in csv first
        f = open('ServerData.csv')
        L = f.readlines()

        for line in L:
            print "String repr = %s" % repr(line)
            if line.startswith('\r\n') or line.startswith('\n'):
                print "Blank line found..."
                self.toDisk("Blank line found...")
                continue
            else:
                print "Processing CSV data..."
                self.toDisk("Processing CSV data...")
                line_s = line.split(",")
                machine = line_s[0].strip()
                domain_path = line_s[4].strip()
                username = line_s[5].strip()
                password = line_s[6].strip()
                managed_server = line_s[7].strip()
                domain = line_s[3].strip()
                build_path = line_s[11].strip()
                ear = line_s[9].strip()
                ear_name = line_s[10].strip()
                full_path = build_path + os.sep + ear_name 
    

                print "The machine is: %s" % machine
                self.toDisk("The machine is: %s" % machine)
                print "The domain_path is: %s" % domain_path
                self.toDisk("The domain_path is: %s" % domain_path)
                print "The username is: %s" % username
                self.toDisk("The username is: %s" % username)
                print "The password is: %s" % password
                self.toDisk("The password is: %s" % password)
                print "The managed_server is: %s" % managed_server
                self.toDisk("The managed_server is: %s" % managed_server)
                print "The domain is: %s" % domain
                self.toDisk("The domain is: %s" % domain)
                print "The build_path is: %s" % build_path
                self.toDisk("The build_path is: %s" % build_path)
                print "The ear is: %s" % ear
                self.toDisk("The ear is: %s" % ear)
                print "The ear_name is: %s" % ear_name
                self.toDisk("The ear_name is: %s" % ear_name)
                print "The full_path is: %s" % full_path
                self.toDisk("The full_path is: %s" % full_path)
                print ""
                self.toDisk("")
    
            
                self.AdminConnect(username, password, machine) #connect to the Admin server
                self.connectToNodeManager(username, password, machine, domain, domain_path)
            
  
    
                s = managed_server
                self.toDisk("*" * 60)
                self.toDisk("The current server is: '%s'" % s)
                self.toDisk("*" * 60)
                print "*" * 60
                print "The current server is: '%s'" % s
                print "*" * 60
    
                self.stopMS(s)
                self.deleteEar(s,ear)
                self.up(s, full_path, s)

    
                #self.loopToContinue()
    
        
                self.startMS(s) 

                #see if connected to node manager and if so disconnect
                x = nm()
                if x:
                    nmDisconnect()

            

        print "Finito :)"
        self.toDisk("Finito :)")


    def deployU(self):
        """This method is the default behavior of the program. The method stops, deletes, installs, and starts managed servers """
        #read in csv first
        f = open('ServerData.csv')
        L = f.readlines()

        for line in L:
            print "String repr = %s" % repr(line)
            if line.startswith('\r\n') or line.startswith('\n'):
                print "Blank line found..."
                self.toDisk("Blank line found...")
                continue
            else:
                print "Processing CSV data..."
                self.toDisk("Processing CSV data...")
                line_s = line.split(",")
                machine = line_s[0].strip()
                domain_path = line_s[4].strip()
                username = line_s[5].strip()
                password = line_s[6].strip()
                managed_server = line_s[7].strip()
                domain = line_s[3].strip()
                build_path = line_s[11].strip()
                ear = line_s[9].strip()
                ear_name = line_s[10].strip()
                full_path = build_path + os.sep + ear_name 
    

                print "The machine is: %s" % machine
                self.toDisk("The machine is: %s" % machine)
                print "The domain_path is: %s" % domain_path
                self.toDisk("The domain_path is: %s" % domain_path)
                print "The username is: %s" % username
                self.toDisk("The username is: %s" % username)
                print "The password is: %s" % password
                self.toDisk("The password is: %s" % password)
                print "The managed_server is: %s" % managed_server
                self.toDisk("The managed_server is: %s" % managed_server)
                print "The domain is: %s" % domain
                self.toDisk("The domain is: %s" % domain)
                print "The build_path is: %s" % build_path
                self.toDisk("The build_path is: %s" % build_path)
                print "The ear is: %s" % ear
                self.toDisk("The ear is: %s" % ear)
                print "The ear_name is: %s" % ear_name
                self.toDisk("The ear_name is: %s" % ear_name)
                print "The full_path is: %s" % full_path
                self.toDisk("The full_path is: %s" % full_path)
                print ""
                self.toDisk("")
    
            
                self.AdminConnect(username, password, machine) #connect to the Admin server

                #start NodeManager in the U environment
                #try to start node manager on the OS in a different thread
                x = commands.getstatusoutput(r'ps -ef | grep NodeManager') #returns a tuple
                if "weblogic.NodeManager" in x[1]: #search the second item in the tuple this contains the text from my exp
                    print "NodeManager appears to be running..."
                    self.toDisk("NodeManager appears to be running...")
                else:
                    nm_thread = start_nm_thread("U_NodeManager_Thread", 'localhost', domain_path)
                    nm_thread.start()

                    #sleep for 30 seconds and wait node manager to start
                    java.lang.Thread.sleep(30000) 
            
           
                s = managed_server
                self.toDisk("*" * 60)
                self.toDisk("The current server is: '%s'" % s)
                self.toDisk("*" * 60)
                print "*" * 60
                print "The current server is: '%s'" % s
                print "*" * 60
    
                self.stopMS(s)
                self.deleteEar(s,ear)
                self.up(s, full_path, s)

    
                #self.loopToContinue()
    
    
                self.start2(s) #call this form of start for U env release.

            
            

        print "Finito in U :)"
        self.toDisk("Finito in U :)")


    def deployT(self):
        """This method deploys to the test environment. The method stops, deletes, and installs managed servers. """
        #read in csv first
        f = open('ServerData.csv')
        L = f.readlines()

        for line in L:
            print "String repr = %s" % repr(line)
            if line.startswith('\r\n') or line.startswith('\n'):
                print "Blank line found..."
                self.toDisk("Blank line found...")
                continue
            else:
                print "Processing CSV data..."
                line_s = line.split(",")
                machine = line_s[0].strip()
                domain_path = line_s[4].strip()
                username = line_s[5].strip()
                password = line_s[6].strip()
                managed_server = line_s[7].strip()
                domain = line_s[3].strip()
                build_path = line_s[11].strip()
                ear = line_s[9].strip()
                ear_name = line_s[10].strip()
                full_path = build_path + os.sep + ear_name 
    

                print "The machine is: %s" % machine
                self.toDisk("The machine is: %s" % machine)
                print "The domain_path is: %s" % domain_path
                self.toDisk("The domain_path is: %s" % domain_path)
                print "The username is: %s" % username
                self.toDisk("The username is: %s" % username)
                print "The password is: %s" % password
                self.toDisk("The password is: %s" % password)
                print "The managed_server is: %s" % managed_server
                self.toDisk("The managed_server is: %s" % managed_server)
                print "The domain is: %s" % domain
                self.toDisk("The domain is: %s" % domain)
                print "The build_path is: %s" % build_path
                self.toDisk("The build_path is: %s" % build_path)
                print "The ear is: %s" % ear
                self.toDisk("The ear is: %s" % ear)
                print "The ear_name is: %s" % ear_name
                self.toDisk("The ear_name is: %s" % ear_name)
                print "The full_path is: %s" % full_path
                self.toDisk("The full_path is: %s" % full_path)
                print ""
                self.toDisk("")
    
            
                self.AdminConnect(username, password, machine) #connect to the Admin server
                self.connectToNodeManager(username, password, machine, domain, domain_path)
         
           
                s = managed_server
                self.toDisk("*" * 60)
                self.toDisk("The current server is: '%s'" % s)
                self.toDisk("*" * 60)
                print "*" * 60
                print "The current server is: '%s'" % s
                print "*" * 60
    
                self.stopMS(s)
                self.deleteEar(s,ear)
                self.up(s, full_path, s)

    
                #self.loopToContinue()
    
    
        print "Finito in Test :)"
        self.toDisk("Finito in Test :)")


    def stop(self):
        """Stop all the servers in the CSV. """
        #read in csv first
        f = open('ServerData.csv')
        L = f.readlines()

        for line in L:
            print "String repr = %s" % repr(line)
            if line.startswith('\r\n') or line.startswith('\n'):
                print "Blank line found..."
                self.toDisk("Blank line found...")
                continue
            else:
                print "Processing CSV data..."
                line_s = line.split(",")
                machine = line_s[0].strip()
                domain_path = line_s[4].strip()
                username = line_s[5].strip()
                password = line_s[6].strip()
                managed_server = line_s[7].strip()
                domain = line_s[3].strip()
                build_path = line_s[11].strip()
                ear = line_s[9].strip()
                ear_name = line_s[10].strip()
                full_path = build_path + os.sep + ear_name 
    

                print "The machine is: %s" % machine
                self.toDisk("The machine is: %s" % machine)
                print "The domain_path is: %s" % domain_path
                self.toDisk("The domain_path is: %s" % domain_path)
                print "The username is: %s" % username
                self.toDisk("The username is: %s" % username)
                print "The password is: %s" % password
                self.toDisk("The password is: %s" % password)
                print "The managed_server is: %s" % managed_server
                self.toDisk("The managed_server is: %s" % managed_server)
                print "The domain is: %s" % domain
                self.toDisk("The domain is: %s" % domain)
                print "The build_path is: %s" % build_path
                self.toDisk("The build_path is: %s" % build_path)
                print "The ear is: %s" % ear
                self.toDisk("The ear is: %s" % ear)
                print "The ear_name is: %s" % ear_name
                self.toDisk("The ear_name is: %s" % ear_name)
                print "The full_path is: %s" % full_path
                self.toDisk("The full_path is: %s" % full_path)
                print ""
                self.toDisk("")
            
                self.AdminConnect(username, password, machine) #connect to the Admin server
                self.connectToNodeManager(username, password, machine, domain, domain_path)
            
  
    
                s = managed_server
                self.toDisk("*" * 60)
                self.toDisk("The current server is: '%s'" % s)
                self.toDisk("*" * 60)
                print "*" * 60
                print "The current server is: '%s'" % s
                print "*" * 60

                self.stopMS(s)

        print "Done stopping all the servers."
        self.toDisk("Done stopping all the servers.")


    def stopU(self):
        """Stop all the servers in the CSV. """
        #read in csv first
        f = open('ServerData.csv')
        L = f.readlines()

        for line in L:
            print "String repr = %s" % repr(line)
            if line.startswith('\r\n') or line.startswith('\n'):
                print "Blank line found..."
                self.toDisk("Blank line found...")
                continue
            else:
                print "Processing CSV data..."
                line_s = line.split(",")
                machine = line_s[0].strip()
                domain_path = line_s[4].strip()
                username = line_s[5].strip()
                password = line_s[6].strip()
                managed_server = line_s[7].strip()
                domain = line_s[3].strip()
                build_path = line_s[11].strip()
                ear = line_s[9].strip()
                ear_name = line_s[10].strip()
                full_path = build_path + os.sep + ear_name 
    

                print "The machine is: %s" % machine
                self.toDisk("The machine is: %s" % machine)
                print "The domain_path is: %s" % domain_path
                self.toDisk("The domain_path is: %s" % domain_path)
                print "The username is: %s" % username
                self.toDisk("The username is: %s" % username)
                print "The password is: %s" % password
                self.toDisk("The password is: %s" % password)
                print "The managed_server is: %s" % managed_server
                self.toDisk("The managed_server is: %s" % managed_server)
                print "The domain is: %s" % domain
                self.toDisk("The domain is: %s" % domain)
                print "The build_path is: %s" % build_path
                self.toDisk("The build_path is: %s" % build_path)
                print "The ear is: %s" % ear
                self.toDisk("The ear is: %s" % ear)
                print "The ear_name is: %s" % ear_name
                self.toDisk("The ear_name is: %s" % ear_name)
                print "The full_path is: %s" % full_path
                self.toDisk("The full_path is: %s" % full_path)
                print ""
                self.toDisk("")
            
                self.AdminConnect(username, password, machine) #connect to the Admin server
            
    
                s = managed_server
                self.toDisk("*" * 60)
                self.toDisk("The current server is: '%s'" % s)
                self.toDisk("*" * 60)
                print "*" * 60
                print "The current server is: '%s'" % s
                print "*" * 60

                self.stopMS(s)

        print "Done stopping all the servers."
        self.toDisk("Done stopping all the servers.")
        

        

    def start(self):
        """Start all the servers in the CSV. """
        #read in csv first
        f = open('ServerData.csv')
        L = f.readlines()

        for line in L:
            print "String repr = %s" % repr(line)
            if line.startswith('\r\n') or line.startswith('\n'):
                print "Blank line found..."
                self.toDisk("Blank line found...")
                continue
            else:
                print "Processing CSV data..."
                line_s = line.split(",")
                machine = line_s[0].strip()
                domain_path = line_s[4].strip()
                username = line_s[5].strip()
                password = line_s[6].strip()
                managed_server = line_s[7].strip()
                domain = line_s[3].strip()
                build_path = line_s[11].strip()
                ear = line_s[9].strip()
                ear_name = line_s[10].strip()
                full_path = build_path + os.sep + ear_name 
    

                print "The machine is: %s" % machine
                self.toDisk("The machine is: %s" % machine)
                print "The domain_path is: %s" % domain_path
                self.toDisk("The domain_path is: %s" % domain_path)
                print "The username is: %s" % username
                self.toDisk("The username is: %s" % username)
                print "The password is: %s" % password
                self.toDisk("The password is: %s" % password)
                print "The managed_server is: %s" % managed_server
                self.toDisk("The managed_server is: %s" % managed_server)
                print "The domain is: %s" % domain
                self.toDisk("The domain is: %s" % domain)
                print "The build_path is: %s" % build_path
                self.toDisk("The build_path is: %s" % build_path)
                print "The ear is: %s" % ear
                self.toDisk("The ear is: %s" % ear)
                print "The ear_name is: %s" % ear_name
                self.toDisk("The ear_name is: %s" % ear_name)
                print "The full_path is: %s" % full_path
                self.toDisk("The full_path is: %s" % full_path)
                print ""
                self.toDisk("")
    
            
                self.AdminConnect(username, password, machine) #connect to the Admin server
                self.connectToNodeManager(username, password, machine, domain, domain_path)
            
  
    
                s = managed_server
                self.toDisk("*" * 60)
                self.toDisk("The current server is: '%s'" % s)
                self.toDisk("*" * 60)
                print "*" * 60
                print "The current server is: '%s'" % s
                print "*" * 60

                self.startMS(s)

        print "Done starting all the servers."
        self.toDisk("Done starting all the servers.")

    def startU(self):
        """Start all the servers in the CSV. """
        #read in csv first
        f = open('ServerData.csv')
        L = f.readlines()

        for line in L:
            print "String repr = %s" % repr(line)
            if line.startswith('\r\n') or line.startswith('\n'):
                print "Blank line found..."
                self.toDisk("Blank line found...")
                continue
            else:
                print "Processing CSV data..."
                line_s = line.split(",")
                machine = line_s[0].strip()
                domain_path = line_s[4].strip()
                username = line_s[5].strip()
                password = line_s[6].strip()
                managed_server = line_s[7].strip()
                domain = line_s[3].strip()
                build_path = line_s[11].strip()
                ear = line_s[9].strip()
                ear_name = line_s[10].strip()
                full_path = build_path + os.sep + ear_name 
    

                print "The machine is: %s" % machine
                self.toDisk("The machine is: %s" % machine)
                print "The domain_path is: %s" % domain_path
                self.toDisk("The domain_path is: %s" % domain_path)
                print "The username is: %s" % username
                self.toDisk("The username is: %s" % username)
                print "The password is: %s" % password
                self.toDisk("The password is: %s" % password)
                print "The managed_server is: %s" % managed_server
                self.toDisk("The managed_server is: %s" % managed_server)
                print "The domain is: %s" % domain
                self.toDisk("The domain is: %s" % domain)
                print "The build_path is: %s" % build_path
                self.toDisk("The build_path is: %s" % build_path)
                print "The ear is: %s" % ear
                self.toDisk("The ear is: %s" % ear)
                print "The ear_name is: %s" % ear_name
                self.toDisk("The ear_name is: %s" % ear_name)
                print "The full_path is: %s" % full_path
                self.toDisk("The full_path is: %s" % full_path)
                print ""
                self.toDisk("")
    
            
                self.AdminConnect(username, password, machine) #connect to the Admin server

                #start NodeManager in the U environment
                #try to start node manager on the OS in a different thread
                x = commands.getstatusoutput(r'ps -ef | grep NodeManager') #returns a tuple
                if "weblogic.NodeManager" in x[1]: #search the second item in the tuple this contains the text from my exp
                    print "NodeManager appears to be running..."
                    self.toDisk("NodeManager appears to be running...")
                else:
                    nm_thread = start_nm_thread("U_NodeManager_Thread", 'localhost', domain_path)
                    nm_thread.start()

                    #sleep for 30 seconds and wait node manager to start
                    java.lang.Thread.sleep(30000) 
  
    
                s = managed_server
                self.toDisk("*" * 60)
                self.toDisk("The current server is: '%s'" % s)
                self.toDisk("*" * 60)
                print "*" * 60
                print "The current server is: '%s'" % s
                print "*" * 60

                self.start2(s) #call this method that will handle exceptions and try to start with 'start command in U env

        print "Done starting all the servers in U environment."
        self.toDisk("Done starting all the servers in U environment.")


    def help(self):
        """Print how to use this program. """
        print """
                                                                                                          
   _|_|                _|                _|_|_|                        _|                      
 _|    _|  _|    _|  _|_|_|_|    _|_|    _|    _|    _|_|    _|_|_|    _|    _|_|    _|    _|  
 _|_|_|_|  _|    _|    _|      _|    _|  _|    _|  _|_|_|_|  _|    _|  _|  _|    _|  _|    _|  
 _|    _|  _|    _|    _|      _|    _|  _|    _|  _|        _|    _|  _|  _|    _|  _|    _|  
 _|    _|    _|_|_|      _|_|    _|_|    _|_|_|      _|_|_|  _|_|_|    _|    _|_|      _|_|_|  
                                                             _|                            _|  
                                                             _|                        _|_|    




        """
        print "Version: %s" % version
        print "HELP! Help me get my feet back on the ground..."
        print "Run the program like so for the default deploy mode:"
        print "%s -d" % (sys.argv[0])
        print "To obtain the help screen run the following command:"
        print "%s -h" % (sys.argv[0])
        print "To start all the servers in the CSV run the script like so."
        print "%s --start" % (sys.argv[0])
        print "To stop all the servers in the CSV run the script like so."
        print "%s --stop" % (sys.argv[0])
        print "To stop all the servers in a U environment (no NodeManager) run the script like so."
        print "%s --stopU" % (sys.argv[0])
        print "To start all the servers in the CSV in a U environment (no NodeManager) run the script like so."
        print "%s --startU" % (sys.argv[0])
        print "To deploy the all the apps in a U environment (without NodeManager) run the script like so."
        print "%s --deployU" % (sys.argv[0])
        print "To deploy to test:"
        print "%s -t" % (sys.argv[0])


    def toDiskStart(self):
        """Write title of log file to disk """
        f = open(log_file, 'w')
        f.write("""

                                                                                                          
   _|_|                _|                _|_|_|                        _|                      
 _|    _|  _|    _|  _|_|_|_|    _|_|    _|    _|    _|_|    _|_|_|    _|    _|_|    _|    _|  
 _|_|_|_|  _|    _|    _|      _|    _|  _|    _|  _|_|_|_|  _|    _|  _|  _|    _|  _|    _|  
 _|    _|  _|    _|    _|      _|    _|  _|    _|  _|        _|    _|  _|  _|    _|  _|    _|  
 _|    _|    _|_|_|      _|_|    _|_|    _|_|_|      _|_|_|  _|_|_|    _|    _|_|      _|_|_|  
                                                             _|                            _|  
                                                             _|                        _|_|    




        


            """)
        import time
        f.write("Script starting at: %s\n" % str(time.asctime()))
        f.write("This is AutoDeploy version: %s\n" % version)
        f.close()

    def toDisk(self, string):
        """This will write the string passed in to the log file (log_file) - a global type of variable. """
        f = open(log_file, 'a')
        f.write(string + "\n")
        f.close()
        
        
if __name__ == "main" or "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdt", ["stop", "stopU", "start", "startU", "deploy", "deployU", "help"] )
   

        for opt, arg in opts:
            if opt in ('-h', '--help'):
               auto_d = AutoDeploy()
               auto_d.help()
            elif opt in ('-d', '--deploy'):        
                auto_d = AutoDeploy()
                auto_d.toDiskStart()
                auto_d.default()
            elif opt == '--stop':
                auto_d = AutoDeploy()
                auto_d.toDiskStart()
                auto_d.stop()
            elif opt == '--stopU':
                auto_d = AutoDeploy()
                auto_d.toDiskStart()
                auto_d.stopU()
            elif opt == '--start':
                auto_d = AutoDeploy()
                auto_d.toDiskStart()
                auto_d.start()
            elif opt == "--startU":
                auto_d = AutoDeploy()
                auto_d.toDiskStart()
                auto_d.startU()
            elif opt == "--deployU":
                auto_d = AutoDeploy()
                auto_d.toDiskStart()
                auto_d.deployU()
            elif opt == '-t':
                auto_d = AutoDeploy()
                auto_d.toDiskStart()
                auto_d.deployT()
            
                

    except getopt.GetoptError:
        print "For help running the program type the following:"
        print "%s -h " % (sys.argv[0])
  
    


