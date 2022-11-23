class IP:
    b1 = 0
    b2 = 0
    b3 = 0
    b4 = 0

    def __init__(self, ip):
        self.ip = ip
        self.b1, self.b2, self.b3, self.b4 = ip.split('.')
        self.b1 = int(self.b1)
        self.b2 = int(self.b2)
        self.b3 = int(self.b3)
        self.b4 = int(self.b4)
        if self.between(self.b1) and self.between(self.b2) and self.between(self.b3) and self.between(self.b4):
            self.correct = True
        else:
            self.correct = False

    def between(self, i1):
        return 0 <= i1 <= 255

    def __str__(self):
        return str(self.ip)

    def __repr__(self):
        return self.ip

    def __eq__(self, other):
        return self.ip == other.ip

    def __hash__(self):
        return hash(self.ip)


class Port:
    
    def __init__(self, port: int):
        if self.between(port):
            self.port = port
            self.correct = True
        else:
            self.port = 50118
            self.correct = False

    def between(self, i1):
        return 1 <= i1 <= 65535

    def __str__(self):
        return str(self.port)

    def __repr__(self):
        return self.port

    def __eq__(self, other):
        return self.port == other.port

    def __hash__(self):
        return hash(self.port)