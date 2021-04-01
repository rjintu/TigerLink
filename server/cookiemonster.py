class CookieMonster:

    def __init__(self, request):
        self.request = request
    
    def getVar(self, varname):
        var = self.request.args.get(varname)
        if var is None:
            var = self.request.cookies.get(varname)
            if var is None:
                var = ''
        return var


