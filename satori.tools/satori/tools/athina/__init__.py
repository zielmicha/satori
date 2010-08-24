# vim:ts=4:sts=4:sw=4:expandtab

def athina_import():
    import os,sys,getpass
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] DIR')
    parser.add_option('-U', '--user',
        default='',
        action='store',
        type='string',
        help='Username')
    parser.add_option('-P', '--password',
        default='',
        action='store',
        type='string',
        help='Password')
    parser.add_option('-N', '--name',
        default='',
        action='store',
        type='string',
        help='Contest name')
    (options, args) = parser.parse_args()
    if len(args) != 1:
	    parser.error('incorrect number of arguments')
    base_dir = args[0]
    if not os.path.exists(os.path.join(base_dir, 'server', 'contest', 'users')):
    	raise parser.error('provided path is invalid')

    def get_path(*args):
        return os.path.join(base_dir, 'server', 'contest', *args)

    if not options.user:
    	options.user = getpass.getuser()
    print 'User: ', options.user
    if not options.password:
        options.password = getpass.getpass('Password: ')
    print 'Password: ', '*' * len(options.password)
    while not options.name:
        options.name = raw_input('Contest name: ')
    print 'Contest name: ', options.name

    users = {}
    for login in os.listdir(get_path('users')):
        with open(get_path('users', login, 'fullname'), 'r') as f:
            fullname = f.readline()
        with open(get_path('users', login, 'password'), 'r') as f:
            password = f.readline()
        if login == 'admin':
        	login = options.name + '_' + login
        users[login] = {
            'login'    : login,
            'fullname' : fullname,
            'password' : password,
        }
    submits = {}
    for d in range(10):
        for submit in os.listdir(get_path('data', str(d))):
            with open(get_path('data', str(d), submit), 'r') as f:
            	data = f.read()
            with open(get_path('filename', str(d), submit), 'r') as f:
            	filename = f.readline()
            with open(get_path('problem', str(d), submit), 'r') as f:
            	problem = f.readline()
            with open(get_path('time', str(d), submit), 'r') as f:
            	time = f.readline()
            with open(get_path('user', str(d), submit), 'r') as f:
            	user = f.readline()
            if user == 'admin':
        	    user = options.name + '_' + user
            submit = int(submit)
            submits[submit] = {
                'submit'   : submit,
                'data'     : data,
                'filename' : filename,
                'problem'  : problem,
                'time'     : time,
                'user'     : user,
            }
    problems = {}
    for dir in os.listdir(get_path()):
        if not os.path.isdir(get_path(dir)):
        	continue
        if not os.path.exists(get_path(dir, 'testcount')):
        	continue
        with open(get_path(dir, 'testcount')) as f:
            testcount = int(f.readline()) + 1
        with open(get_path(dir, 'sizelimit')) as f:
            sizelimit = int(f.readline())
        if os.path.exists(get_path(dir, 'checker')):
        	checker = get_path(dir, 'checker')
        else:
        	checker = None
        if os.path.exists(get_path(dir, 'judge')):
        	judge = get_path(dir, 'judge')
        else:
        	judge = None
        tests = {}
        for t in range(testcount):
        	input = get_path(dir, str(t) + '.in')
            if not os.path.exists(input):
            	input = None
        	output = get_path(dir, str(t) + '.out')
            if not os.path.exists(output):
            	output = None
        	memlimit = get_path(dir, str(t) + '.mem')
            if os.path.exists(memlimit):
                with open(memlimit, 'r') as f:
                    memlimit = int(f.readline())
            else:
            	memlimit = None
        	timelimit = get_path(dir, str(t) + '.tle')
            if os.path.exists(timelimit):
                with open(timelimit, 'r') as f:
                    timelimit = int(f.readline())
            else:
            	timelimit = None
            tests[t] = {
            	'test'      : t,
                'input'     : input,
                'output'    : output,
                'memlimit'  : memlimit,
                'timelimit' : timelimit,
            }
        problems[dir] = {
        	'problem'   : dir,
            'testcount' : testcount,
            'sizelimit' : sizelimit,
            'checker'   : checker,
            'judge'     : judge,
            'tests'     : tests,
        }

#    print 'users:    ', users
#    print 'problems: ', problems
#    print 'submits:  ', submits


    from satori.client.common import Security, Privilege, set_token, User, Contest, Problem, TestSuite, Test, Submit
    try:
        Security.register(options.user, options.password, options.user)
    except:
        pass

    set_token(Security.login(options.user, options.password))

    try:
        Privilege.create_global(role=Security.whoami(), right='MANAGE_CONTESTS')
    except:
        pass

    

    try:
        contest = Contest.create_contest(name=options.name)
    except:
        contest = Contest.filter(name=options.name)[0]

    for login, user in users.iteritems():
    	print ' -> user ', login
        try:
            user['object'] = Security.register(login=user['login'], password=user['password'], fullname=user['fullname'])
        except:
            user['object'] = User.filter(login=user['login'])[0]
        try:
            user['contestant'] = contest.create_contestant([user['object']])
        except:
            user['contestant'] = contest.find_contestant(user['object'])

    print users

    for name, problem in problems.iteritems():
    	print ' -> problem ', name
        for num, test in problem['tests']:
            print '   -> test ', num

    for id, submit in submits.iteritems():
    	print ' -> submit ', id